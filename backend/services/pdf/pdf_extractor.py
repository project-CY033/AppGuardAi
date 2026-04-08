import logging
from PyPDF2 import PdfReader
from typing import Dict, Any

class PDFExtractor:
    @staticmethod
    def extract_metadata(file_path: str) -> Dict[str, Any]:
        """
        Extracts structural data and metadata from a PDF file using PyPDF2.
        """
        results = {
            "has_javascript": False,
            "has_embedded_files": False,
            "has_encryption": False,
            "metadata": {},
            "page_count": 0,
            "is_corrupt": False,
            "error": None
        }

        try:
            with open(file_path, "rb") as f:
                reader = PdfReader(f, strict=False)
                
                if reader.is_encrypted:
                    results["has_encryption"] = True
                    # Try with empty password
                    try:
                        reader.decrypt("")
                    except Exception:
                        pass
                        
                results["page_count"] = len(reader.pages)
                
                # Metadata
                if reader.metadata:
                    results["metadata"] = {k: v for k, v in reader.metadata.items()}
                
                # Check for standard JS elements in root/catalog if mapped
                trailer = reader.trailer
                if "/Root" in trailer:
                    root = trailer["/Root"].get_object()
                    if "/Names" in root:
                        names = root["/Names"].get_object()
                        if "/JavaScript" in names or "/EmbeddedFiles" in names:
                            results["has_javascript"] = "/JavaScript" in names
                            results["has_embedded_files"] = "/EmbeddedFiles" in names
                            
        except Exception as e:
            logging.error(f"PyPDF2 Extraction failed for {file_path}: {e}")
            results["is_corrupt"] = True
            results["error"] = str(e)
            
        return results
