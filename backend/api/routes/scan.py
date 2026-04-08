import os
import shutil
from fastapi import APIRouter, HTTPException, Request, UploadFile, File
from models.schemas import ScanRequest, ScanResponse
from services.analyzer import AsyncAnalyzer
from services.supabase_client import supabase_manager
import logging

router = APIRouter()
analyzer = AsyncAnalyzer()

@router.post("/scan", response_model=ScanResponse)
async def perform_scan(request: Request, payload: ScanRequest):
    import time
    start_time = time.time()
    try:
        if not payload.apps:
            raise HTTPException(status_code=400, detail="No applications provided for scanning.")

        logging.info(f"🚀 RECEIVED SCAN REQUEST: Processing {len(payload.apps)} apps...")
        results = await analyzer.analyze_batch(payload.apps)
        
        duration = time.time() - start_time
        logging.info(f"✅ SCAN COMPLETED: Processed {len(payload.apps)} apps in {duration:.2f} seconds")

        safe_count = 0
        risky_count = 0
        risky_apps_list = []

        for result in results:
            if result.is_safe:
                safe_count += 1
            else:
                risky_count += 1
                risky_apps_list.append(result)

        total_scanned = safe_count + risky_count
        
        # Calculate a normalized security score depending on risk distribution
        penalty = (risky_count / max(1, total_scanned)) * 200
        overall_score = max(0, int(100 - penalty))            
            
        # Log session mapping exactly to scan_sessions
        session_id = None
        user_uuid = None # Extracted from auth contexts when integrated
        try:
            session_id = supabase_manager.log_scan_session(
                user_id=user_uuid, 
                scan_type='full_system', 
                total_apps=total_scanned, 
                threats_found=risky_count
            )
            
            if session_id:
                # Log independent reports
                for i, r in enumerate(results):
                    original_app = payload.apps[i]
                    supabase_manager.log_app_security_report(
                        scan_id=session_id,
                        package_name=r.package_name,
                        app_name=r.app_name,
                        app_version=original_app.version_name or "1.0",
                        hash_sha256=original_app.hash_sha256 or "unknown",
                        security_score=r.risk_score,
                        is_malicious=r.is_malicious,
                        risk_level=r.risk_level,
                        threat_details=r.threat_details
                    )

        except Exception as e:
            logging.warning(f"Failed to log session: {e}")

        return ScanResponse(
            total_scanned=total_scanned,
            safe_apps_count=safe_count,
            risky_apps_count=risky_count,
            overall_security_score=overall_score,
            risky_apps=risky_apps_list
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        logging.error(f"Scan API Internal Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error occurred during scan process.")

@router.post("/apk")
async def deep_scan_apk(file: UploadFile = File(...)):
    if not file.filename.endswith('.apk'):
        raise HTTPException(status_code=400, detail="Only .apk files are supported for Deep Scanning.")
        
    temp_path = f"temp_{file.filename}"
    try:
        logging.info(f"Receiving physical APK upload: {file.filename}")
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        from services.analysis.apk_reverser import apk_reverser
        analysis_result = await apk_reverser.analyze_apk(temp_path, file.filename)
        
        session_id = supabase_manager.log_scan_session(
            user_id=None, 
            scan_type='apk_upload', 
            total_apps=1, 
            threats_found=1 if not analysis_result['is_safe'] else 0
        )

        if session_id and analysis_result['package_name'] != 'unknown_package':
            supabase_manager.log_app_security_report(
                scan_id=session_id,
                app_name=analysis_result['app_name'], 
                package_name=analysis_result['package_name'], 
                app_version="1.0",
                hash_sha256=analysis_result.get('file_sha256', "unknown"),
                security_score=analysis_result['risk_score'],
                is_malicious=analysis_result.get('is_malicious', False),
                risk_level=analysis_result.get('risk_level', "Safe"),
                threat_details=analysis_result.get('threat_details', {})
            )

        return {"status": "success", "data": analysis_result}
    except Exception as e:
        logging.error(f"Failed to reverse engineer APK file: {e}")
        raise HTTPException(status_code=500, detail=f"Decompilation Failed: {e}")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

from pydantic import BaseModel
class WhitelistRequest(BaseModel):
    package_name: str
    
@router.post("/whitelist")
async def whitelist_app(payload: WhitelistRequest):
    res = supabase_manager.add_to_whitelist(user_id=None, package_name=payload.package_name)
    return {"status": "success", "message": "App added to whitelist"}

import uuid
from services.pdf.pdf_scanner import PDFScanner

@router.post("/pdf")
async def deep_scan_pdf(file: UploadFile = File(...)):
    """
    Accepts raw .pdf files for scanning. Saves them securely, analyzes, and scores.
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only .pdf files are supported.")
        
    upload_dir = os.path.join(os.getcwd(), "uploads", "pdf")
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename to avoid collision
    unique_id = str(uuid.uuid4())
    safe_filename = f"{unique_id}_{file.filename.replace(' ', '_')}"
    file_path = os.path.join(upload_dir, safe_filename)
    
    try:
        logging.info(f"Receiving physical PDF upload: {file.filename}")
        
        # We read the file in chunks or directly
        content = await file.read()
        
        # Check size (max 50MB for example, though user mentioned 5-100MB is fine, let's limit 100MB = 104857600 bytes)
        if len(content) > 100 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="File too large. Over 100MB limit.")
            
        file_size_mb = len(content) / (1024 * 1024)
        
        with open(file_path, "wb") as buffer:
            buffer.write(content)
            
        # Parse the binary via our PDF Scanner Service
        report = PDFScanner.process_pdf(file_path, file.filename, file_size_mb)
        
        # Log to Supabase 
        supabase_manager.log_pdf_report(
            file_name=report["file_name"],
            file_path=report["file_path"],
            file_size=report["file_size"],
            scan_score=report["scan_score"],
            status=report["overall_status"],
            report_data=report["checks"]
        )

        return {"status": "success", "data": report, "id": safe_filename}
    except Exception as e:
        logging.error(f"Failed to analyze PDF file: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"PDF Analysis Failed: {e}")

@router.delete("/pdf/{file_id}")
async def delete_pdf(file_id: str):
    """
    Deletes the uploaded PDF file securely from the local system.
    """
    upload_dir = os.path.join(os.getcwd(), "uploads", "pdf")
    file_path = os.path.join(upload_dir, file_id)
    
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            logging.info(f"Safely purged PDF from disk: {file_id}")
            return {"status": "success", "message": "File optionally purged."}
        except Exception as e:
            logging.error(f"Failed to delete {file_path}: {e}")
            raise HTTPException(status_code=500, detail="Could not delete file.")
    
    # If the file didn't exist, we just tell the user success anyway (idempotent)
    return {"status": "success", "message": "File not found or already purged."}
