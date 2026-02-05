"""
Email Service Router
Handles sending reports via email
"""
from fastapi import APIRouter, HTTPException

from models import SendEmailRequest, SendBulkEmailRequest, EmailResponse
from backend.services.email_service import GmailSender


router = APIRouter()


@router.post("/send", response_model=EmailResponse)
async def send_email(request: SendEmailRequest):
    """
    Send investment report via email
    
    Sends a professionally formatted email with the PDF report attached
    """
    try:
        # Initialize Gmail sender
        gmail_sender = GmailSender()
        
        # Prepare subject
        subject = f"Investment Analysis Report - {request.company_name}"
        
        # Send email
        success = gmail_sender.send_report(
            recipient_email=request.recipient_email,
            subject=subject,
            company_name=request.company_name,
            decision=request.decision,
            pdf_path=request.pdf_path
        )
        
        if success:
            return {
                "success": True,
                "message": "Email sent successfully",
                "recipient": request.recipient_email
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to send email"
            )
            
    except ValueError as ve:
        # Gmail credentials not configured
        raise HTTPException(
            status_code=503,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error sending email: {str(e)}"
        )


@router.post("/send-bulk", response_model=EmailResponse)
async def send_bulk_email(request: SendBulkEmailRequest):
    """
    Send investment report to multiple recipients
    
    Sends the same report to multiple email addresses
    """
    try:
        # Initialize Gmail sender
        gmail_sender = GmailSender()
        
        # Prepare subject
        subject = f"Investment Analysis Report - {request.company_name}"
        
        # Send bulk emails
        results = gmail_sender.send_bulk_reports(
            recipient_list=request.recipient_emails,
            subject=subject,
            company_name=request.company_name,
            decision=request.decision,
            pdf_path=request.pdf_path
        )
        
        return {
            "success": results['failed'] == 0,
            "message": f"Sent to {results['success']} recipients, {results['failed']} failed",
            "recipients_sent": results['success'],
            "recipients_failed": results['failed'],
            "failed_emails": results.get('failed_emails', [])
        }
            
    except ValueError as ve:
        # Gmail credentials not configured
        raise HTTPException(
            status_code=503,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error sending bulk emails: {str(e)}"
        )


@router.post("/test")
async def test_email_config():
    """
    Test email configuration
    
    Verifies that Gmail API credentials are properly configured
    """
    try:
        gmail_sender = GmailSender()
        return {
            "status": "configured",
            "message": "Gmail API is properly configured"
        }
    except ValueError as ve:
        raise HTTPException(
            status_code=503,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error testing email config: {str(e)}"
        )