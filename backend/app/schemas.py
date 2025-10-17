"""
Pydantic schemas for request/response validation
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


# ============= ENUMS =============

class PaperStatusEnum(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class UserRoleEnum(str, Enum):
    ADMIN = "admin"
    REVIEWER = "reviewer"
    RESEARCHER = "researcher"
    STUDENT = "student"


class AlertSeverityEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ============= USER SCHEMAS =============

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    institution: Optional[str] = None
    department: Optional[str] = None
    role: UserRoleEnum = UserRoleEnum.RESEARCHER


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    institution: Optional[str] = None
    department: Optional[str] = None
    role: Optional[UserRoleEnum] = None


class UserResponse(UserBase):
    id: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============= AUTHENTICATION SCHEMAS =============

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ============= PAPER SCHEMAS =============

class PaperBase(BaseModel):
    title: str
    abstract: Optional[str] = None
    authors: Optional[List[str]] = None
    journal: Optional[str] = None
    publication_date: Optional[datetime] = None
    doi: Optional[str] = None
    arxiv_id: Optional[str] = None
    pubmed_id: Optional[str] = None


class PaperCreate(PaperBase):
    pass


class PaperUpdate(BaseModel):
    title: Optional[str] = None
    abstract: Optional[str] = None
    authors: Optional[List[str]] = None
    journal: Optional[str] = None
    publication_date: Optional[datetime] = None


class PaperResponse(PaperBase):
    paper_id: str
    status: PaperStatusEnum
    risk_score: float
    file_path: Optional[str] = None
    submitted_at: datetime
    processing_completed_at: Optional[datetime] = None
    submitter_id: Optional[str] = None

    class Config:
        from_attributes = True


class PaperDetail(PaperResponse):
    full_text: Optional[str] = None
    file_size: Optional[int] = None
    processing_error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


# ============= ANALYSIS SCHEMAS =============

class SimilarityMatchResponse(BaseModel):
    id: str
    target_paper_id: str
    target_paper_title: Optional[str] = None
    target_paper_authors: Optional[List[str]] = None
    overall_similarity: float
    text_similarity: float
    semantic_similarity: float
    structural_similarity: float
    matching_sections: Optional[Dict[str, Any]] = None
    matching_excerpts: Optional[List[Dict[str, Any]]] = None

    class Config:
        from_attributes = True


class AnomalyResponse(BaseModel):
    id: str
    type: str
    severity: AlertSeverityEnum
    confidence: float
    title: str
    description: str
    location: Optional[str] = None
    evidence: Optional[Dict[str, Any]] = None
    detection_method: Optional[str] = None

    class Config:
        from_attributes = True


class AnalysisResultResponse(BaseModel):
    id: str
    paper_id: str
    overall_risk_score: float
    text_similarity_score: float
    semantic_similarity_score: float
    statistical_anomaly_score: float
    image_manipulation_score: float
    citation_anomaly_score: float
    processing_time_seconds: Optional[float] = None
    similarity_findings: Optional[List[Dict[str, Any]]] = None
    anomaly_findings: Optional[List[Dict[str, Any]]] = None
    recommendations: Optional[List[str]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class FullAnalysisResponse(BaseModel):
    paper: PaperResponse
    analysis: Optional[AnalysisResultResponse] = None
    similarity_matches: List[SimilarityMatchResponse] = []
    anomalies: List[AnomalyResponse] = []


# ============= JOB SCHEMAS =============

class JobStatus(BaseModel):
    job_id: str
    status: str
    progress: float
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class UploadResponse(BaseModel):
    job_id: str
    paper_id: str
    status: str
    message: str


# ============= SEARCH SCHEMAS =============

class PaperSearchRequest(BaseModel):
    query: Optional[str] = None
    author: Optional[str] = None
    journal: Optional[str] = None
    min_risk_score: Optional[float] = 0.0
    max_risk_score: Optional[float] = 1.0
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[PaperStatusEnum] = None
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class PaperSearchResponse(BaseModel):
    results: List[PaperResponse]
    total: int
    limit: int
    offset: int


# ============= STATISTICS SCHEMAS =============

class StatisticsOverview(BaseModel):
    total_papers: int
    processed_papers: int
    pending_papers: int
    failed_papers: int
    total_anomalies_detected: int
    high_risk_papers: int
    medium_risk_papers: int
    low_risk_papers: int
    processing_rate: float
    average_risk_score: float
    average_processing_time: float


class TrendData(BaseModel):
    date: str
    total_papers: int
    high_risk_papers: int
    average_risk_score: float


class StatisticsTrends(BaseModel):
    daily_trends: List[TrendData]
    weekly_trends: List[TrendData]
    monthly_trends: List[TrendData]


# ============= REVIEW SCHEMAS =============

class ReviewBase(BaseModel):
    decision: Optional[str] = None
    risk_assessment: Optional[float] = None
    notes: Optional[str] = None
    recommendations: Optional[str] = None


class ReviewCreate(ReviewBase):
    paper_id: str


class ReviewUpdate(ReviewBase):
    status: Optional[str] = None


class ReviewResponse(ReviewBase):
    id: str
    paper_id: str
    reviewer_id: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============= COMMENT SCHEMAS =============

class CommentBase(BaseModel):
    content: str


class CommentCreate(CommentBase):
    paper_id: str
    parent_comment_id: Optional[str] = None


class CommentResponse(CommentBase):
    id: str
    paper_id: str
    user_id: str
    parent_comment_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============= ALERT SCHEMAS =============

class AlertResponse(BaseModel):
    id: str
    severity: AlertSeverityEnum
    title: str
    description: str
    alert_type: str
    related_paper_id: Optional[str] = None
    acknowledged: bool
    resolved: bool
    created_at: datetime
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AlertUpdate(BaseModel):
    acknowledged: Optional[bool] = None
    resolved: Optional[bool] = None


# ============= BATCH PROCESSING SCHEMAS =============

class BatchProcessingRequest(BaseModel):
    paper_ids: List[str]
    priority: int = Field(default=5, ge=1, le=10)
    options: Optional[Dict[str, Any]] = None


class BatchProcessingResponse(BaseModel):
    batch_id: str
    total_papers: int
    status: str
    created_at: datetime


# ============= EXPORT SCHEMAS =============

class ExportFormat(str, Enum):
    PDF = "pdf"
    JSON = "json"
    CSV = "csv"
    EXCEL = "excel"


class ExportRequest(BaseModel):
    paper_ids: Optional[List[str]] = None
    format: ExportFormat = ExportFormat.PDF
    include_analysis: bool = True
    include_similarity_matches: bool = True
    include_anomalies: bool = True


class ExportResponse(BaseModel):
    export_id: str
    format: ExportFormat
    status: str
    download_url: Optional[str] = None
    created_at: datetime


# ============= REPORT SCHEMAS =============

class ReportType(str, Enum):
    INSTITUTIONAL = "institutional"
    DEPARTMENTAL = "departmental"
    TREND_ANALYSIS = "trend_analysis"
    RISK_SUMMARY = "risk_summary"


class ReportRequest(BaseModel):
    report_type: ReportType
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    filters: Optional[Dict[str, Any]] = None


class ReportResponse(BaseModel):
    report_id: str
    report_type: ReportType
    status: str
    download_url: Optional[str] = None
    created_at: datetime


# ============= HEALTH CHECK SCHEMAS =============

class HealthCheckResponse(BaseModel):
    status: str
    version: str
    database: str
    redis: str
    elasticsearch: str
    ml_worker: str
    timestamp: datetime
