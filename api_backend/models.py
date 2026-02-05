"""
Pydantic Models for API Request/Response validation
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from enum import Enum


class AnalysisStatus(str, Enum):
    """Analysis status enum"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class InvestmentDecision(str, Enum):
    """Investment decision enum"""
    PASS = "PASS"
    MAYBE = "MAYBE"
    INVEST = "INVEST"


class SeverityLevel(str, Enum):
    """Risk severity levels"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


# ============ Document Upload Models ============

class DocumentUploadResponse(BaseModel):
    """Response after document upload"""
    startup_id: str
    message: str
    files_processed: Dict[str, int]
    chunks_created: int


# ============ Analysis Models ============

class StartAnalysisRequest(BaseModel):
    """Request to start analysis"""
    startup_id: str


class AnalysisStatusResponse(BaseModel):
    """Analysis status response"""
    startup_id: str
    status: AnalysisStatus
    progress: Optional[int] = None
    message: Optional[str] = None


class CompanyInfo(BaseModel):
    """Company information"""
    name: str
    sector: str
    stage: str
    founded_year: Optional[int]
    location: str


class Metrics(BaseModel):
    """Financial metrics"""
    mrr: Optional[float]
    arr: Optional[float]
    revenue: Optional[float]
    growth_rate_monthly: Optional[str]
    customers: Optional[int]
    burn_rate_monthly: Optional[float]
    runway_months: Optional[int]
    churn_rate: Optional[str]


class RedFlag(BaseModel):
    """Red flag model"""
    type: str
    severity: SeverityLevel
    title: str
    description: str
    evidence: List[str]
    impact: str


class RiskAnalysis(BaseModel):
    """Risk analysis results"""
    red_flags: List[RedFlag]
    risk_score: int
    overall_assessment: str


class Recommendation(BaseModel):
    """Investment recommendation"""
    decision: InvestmentDecision
    confidence: int
    investment_thesis: str
    key_strengths: List[str]
    key_concerns: List[str]
    suggested_valuation: Optional[str]
    suggested_investment: Optional[str]
    follow_up_questions: List[str]
    deal_score: int
    next_steps: str


class AnalysisResults(BaseModel):
    """Complete analysis results"""
    startup_id: str
    status: str
    extracted_data: Dict[str, Any]
    benchmark_data: Dict[str, Any]
    risk_analysis: RiskAnalysis
    market_research: Dict[str, Any]
    growth_assessment: Dict[str, Any]
    recommendation: Recommendation


# ============ Report Models ============

class GenerateReportRequest(BaseModel):
    """Request to generate PDF report"""
    startup_id: str
    


class GenerateReportResponse(BaseModel):
    """Response after generating report"""
    success: bool
    pdf_filename: str
    pdf_path: str
    message: str


class DownloadReportResponse(BaseModel):
    """Response for report download"""
    filename: str
    content_type: str = "application/pdf"


# ============ Email Models ============

class SendEmailRequest(BaseModel):
    """Request to send email with report"""
    recipient_email: str
    startup_id: str
    company_name: str
    decision: InvestmentDecision
    pdf_path: str
    
    @validator('recipient_email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Invalid email address')
        return v


class SendBulkEmailRequest(BaseModel):
    """Request to send bulk emails"""
    recipient_emails: List[str]
    startup_id: str
    company_name: str
    decision: InvestmentDecision
    pdf_path: str
    
    @validator('recipient_emails')
    def validate_emails(cls, v):
        if not v:
            raise ValueError('At least one recipient email required')
        for email in v:
            if '@' not in email:
                raise ValueError(f'Invalid email address: {email}')
        return v


class EmailResponse(BaseModel):
    """Response after sending email"""
    success: bool
    message: str
    recipient: Optional[str] = None
    recipients_sent: Optional[int] = None
    recipients_failed: Optional[int] = None
    failed_emails: Optional[List[str]] = None


# ============ Health Check Models ============

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    services: Dict[str, str]