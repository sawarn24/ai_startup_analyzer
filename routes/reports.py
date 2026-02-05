"""
Report Generation Router
Handles PDF report generation and downloads
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os
from datetime import datetime

from models import GenerateReportRequest, GenerateReportResponse
from backend.services.report_generate import ProfessionalReportGenerator
from routes.analysis import analysis_storage

router = APIRouter()

# Initialize report generator
report_generator = ProfessionalReportGenerator()


@router.post("/generate", response_model=GenerateReportResponse)
async def generate_report(request: GenerateReportRequest):
    """
    Generate PDF report for startup analysis
    
    Takes analysis results and generates a professional PDF report
    with charts, metrics, and recommendations
    """
    try:
        startup_id = request.startup_id
        data = analysis_storage[startup_id]
        results = data["results"] 
        # Create reports directory
        os.makedirs("reports", exist_ok=True)
        
        # Get company name from results
        company_name = results.get('extracted_data', {}).get('company_info', {}).get('name', 'Unknown')
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        pdf_filename = f"investment_report_{company_name.replace(' ', '_')}_{timestamp}.pdf"
        pdf_path = os.path.join("reports", pdf_filename)
        
        # Generate report
        generated_path = report_generator.generate_report(results, pdf_path)
        
        return {
            "success": True,
            "pdf_filename": pdf_filename,
            "pdf_path": generated_path,
            "message": "Report generated successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating report: {str(e)}"
        )


@router.get("/download/{filename}")
async def download_report(filename: str):
    """
    Download generated PDF report
    
    Returns the PDF file for download
    """
    file_path = os.path.join("reports", filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404,
            detail="Report file not found"
        )
    
    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=filename
    )


@router.get("/list")
async def list_reports():
    """
    List all generated reports
    
    Returns list of available report files
    """
    reports_dir = "reports"
    
    if not os.path.exists(reports_dir):
        return {"reports": [], "total": 0}
    
    files = [f for f in os.listdir(reports_dir) if f.endswith('.pdf')]
    
    reports = []
    for file in files:
        file_path = os.path.join(reports_dir, file)
        stat = os.stat(file_path)
        reports.append({
            "filename": file,
            "size_bytes": stat.st_size,
            "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat()
        })
    
    return {
        "reports": sorted(reports, key=lambda x: x['created_at'], reverse=True),
        "total": len(reports)
    }


@router.delete("/{filename}")
async def delete_report(filename: str):
    """
    Delete a generated report
    """
    file_path = os.path.join("reports", filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404,
            detail="Report file not found"
        )
    
    try:
        os.remove(file_path)
        return {"message": f"Report {filename} deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting report: {str(e)}"
        )