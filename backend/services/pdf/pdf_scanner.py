import os
import logging
from typing import Dict, Any
from .pdf_extractor import PDFExtractor
from .pdf_analyzer import PDFAnalyzer
from .pdf_scoring import PDFScoring

class PDFScanner:
    @staticmethod
    def process_pdf(file_path: str, file_name: str, file_size_mb: float) -> Dict[str, Any]:
        """
        Orchestrates structural extraction, deep analysis, and scoring.
        """
        logging.info(f"Starting End-to-End PDF Document Analysis: {file_name}")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} not found for analysis.")

        # 1. Extraction (PyPDF2)
        extraction_results = PDFExtractor.extract_metadata(file_path)

        # 2. Deep Analysis (peepdf sandbox via subprocess)
        analysis_results = PDFAnalyzer.analyze_heuristics(file_path)

        # 3. Scoring Engine
        scoring_results = PDFScoring.calculate_score(extraction_results, analysis_results)

        # Build final report
        report = {
            "file_name": file_name,
            "file_path": file_path,
            "file_size": f"{file_size_mb:.2f} MB",
            "scan_score": scoring_results["scan_score"],
            "overall_status": scoring_results["overall_status"],
            "checks": scoring_results["checks"],
            "metadata_extracted": bool(extraction_results.get("metadata"))
        }

        logging.info(f"PDF Analysis complete for {file_name}: Status={report['overall_status']}, Score={report['scan_score']}")
        return report
