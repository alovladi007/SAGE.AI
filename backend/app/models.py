"""
Database Models for Academic Integrity Platform
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean, JSON, Enum as SQLEnum, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from enum import Enum as PyEnum
from .database import Base
import uuid


def generate_uuid():
    return str(uuid.uuid4())


class PaperStatus(PyEnum):
    """Paper processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class UserRole(PyEnum):
    """User roles in the system"""
    ADMIN = "admin"
    REVIEWER = "reviewer"
    RESEARCHER = "researcher"
    STUDENT = "student"


class AlertSeverity(PyEnum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class User(Base):
    """User model"""
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    institution = Column(String, nullable=True)
    department = Column(String, nullable=True)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.RESEARCHER)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    papers = relationship("Paper", back_populates="submitter")
    reviews = relationship("Review", back_populates="reviewer")
    comments = relationship("Comment", back_populates="user")


class Paper(Base):
    """Academic paper model"""
    __tablename__ = "papers"

    paper_id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(Text, nullable=False)
    abstract = Column(Text, nullable=True)
    full_text = Column(Text, nullable=True)
    authors = Column(JSON, nullable=True)  # List of author names
    journal = Column(String, nullable=True)
    publication_date = Column(DateTime, nullable=True)
    doi = Column(String, unique=True, nullable=True, index=True)
    arxiv_id = Column(String, unique=True, nullable=True, index=True)
    pubmed_id = Column(String, unique=True, nullable=True, index=True)

    # File information
    file_path = Column(String, nullable=True)
    file_size = Column(Integer, nullable=True)
    file_hash = Column(String, nullable=True, index=True)

    # Processing status
    status = Column(SQLEnum(PaperStatus), default=PaperStatus.PENDING, index=True)
    risk_score = Column(Float, default=0.0, index=True)
    processing_started_at = Column(DateTime(timezone=True), nullable=True)
    processing_completed_at = Column(DateTime(timezone=True), nullable=True)
    processing_error = Column(Text, nullable=True)

    # Submission info
    submitter_id = Column(String, ForeignKey("users.id"), nullable=True)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())

    # Metadata
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    submitter = relationship("User", back_populates="papers")
    analysis_results = relationship("AnalysisResult", back_populates="paper", cascade="all, delete-orphan")
    similarity_matches = relationship("SimilarityMatch", back_populates="source_paper", cascade="all, delete-orphan")
    anomalies = relationship("Anomaly", back_populates="paper", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="paper", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="paper", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index('idx_paper_status_risk', 'status', 'risk_score'),
        Index('idx_paper_submitted', 'submitted_at'),
    )


class AnalysisResult(Base):
    """Complete analysis result for a paper"""
    __tablename__ = "analysis_results"

    id = Column(String, primary_key=True, default=generate_uuid)
    paper_id = Column(String, ForeignKey("papers.paper_id"), nullable=False)

    # Overall scores
    overall_risk_score = Column(Float, default=0.0)
    text_similarity_score = Column(Float, default=0.0)
    semantic_similarity_score = Column(Float, default=0.0)
    statistical_anomaly_score = Column(Float, default=0.0)
    image_manipulation_score = Column(Float, default=0.0)
    citation_anomaly_score = Column(Float, default=0.0)

    # Detailed results
    similarity_findings = Column(JSON, nullable=True)
    anomaly_findings = Column(JSON, nullable=True)
    recommendations = Column(JSON, nullable=True)

    # Processing info
    processing_time_seconds = Column(Float, nullable=True)
    ml_model_version = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    paper = relationship("Paper", back_populates="analysis_results")


class SimilarityMatch(Base):
    """Similarity match between papers"""
    __tablename__ = "similarity_matches"

    id = Column(String, primary_key=True, default=generate_uuid)
    source_paper_id = Column(String, ForeignKey("papers.paper_id"), nullable=False)
    target_paper_id = Column(String, nullable=False)  # Can be external paper
    target_paper_title = Column(Text, nullable=True)
    target_paper_authors = Column(JSON, nullable=True)

    # Similarity scores
    overall_similarity = Column(Float, nullable=False)
    text_similarity = Column(Float, default=0.0)
    semantic_similarity = Column(Float, default=0.0)
    structural_similarity = Column(Float, default=0.0)

    # Matching details
    matching_sections = Column(JSON, nullable=True)  # Which sections matched
    matching_excerpts = Column(JSON, nullable=True)  # Actual matching text excerpts

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    source_paper = relationship("Paper", back_populates="similarity_matches")

    # Indexes
    __table_args__ = (
        Index('idx_similarity_source', 'source_paper_id'),
        Index('idx_similarity_score', 'overall_similarity'),
    )


class Anomaly(Base):
    """Detected anomaly in a paper"""
    __tablename__ = "anomalies"

    id = Column(String, primary_key=True, default=generate_uuid)
    paper_id = Column(String, ForeignKey("papers.paper_id"), nullable=False)

    # Anomaly classification
    type = Column(String, nullable=False, index=True)  # statistical_fraud, image_manipulation, citation_anomaly, etc.
    severity = Column(SQLEnum(AlertSeverity), nullable=False, index=True)
    confidence = Column(Float, nullable=False)

    # Details
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    location = Column(String, nullable=True)  # Section or page where anomaly was found
    evidence = Column(JSON, nullable=True)  # Supporting evidence

    # Detection info
    detection_method = Column(String, nullable=True)
    detected_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    paper = relationship("Paper", back_populates="anomalies")


class Review(Base):
    """Human review of a paper"""
    __tablename__ = "reviews"

    id = Column(String, primary_key=True, default=generate_uuid)
    paper_id = Column(String, ForeignKey("papers.paper_id"), nullable=False)
    reviewer_id = Column(String, ForeignKey("users.id"), nullable=False)

    # Review content
    decision = Column(String, nullable=True)  # approved, flagged, rejected
    risk_assessment = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    recommendations = Column(Text, nullable=True)

    # Status
    status = Column(String, default="in_progress")  # in_progress, completed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    paper = relationship("Paper", back_populates="reviews")
    reviewer = relationship("User", back_populates="reviews")


class Comment(Base):
    """Comments on papers"""
    __tablename__ = "comments"

    id = Column(String, primary_key=True, default=generate_uuid)
    paper_id = Column(String, ForeignKey("papers.paper_id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)

    content = Column(Text, nullable=False)
    parent_comment_id = Column(String, ForeignKey("comments.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    paper = relationship("Paper", back_populates="comments")
    user = relationship("User", back_populates="comments")


class ProcessingJob(Base):
    """Background processing job tracker"""
    __tablename__ = "processing_jobs"

    job_id = Column(String, primary_key=True, default=generate_uuid)
    paper_id = Column(String, ForeignKey("papers.paper_id"), nullable=True)
    job_type = Column(String, nullable=False)  # analysis, batch_processing, etc.

    status = Column(String, default="queued")  # queued, processing, completed, failed
    progress = Column(Float, default=0.0)

    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)

    result = Column(JSON, nullable=True)
    metadata = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Indexes
    __table_args__ = (
        Index('idx_job_status', 'status'),
        Index('idx_job_created', 'created_at'),
    )


class Alert(Base):
    """System alerts and notifications"""
    __tablename__ = "alerts"

    id = Column(String, primary_key=True, default=generate_uuid)
    severity = Column(SQLEnum(AlertSeverity), nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)

    # Alert details
    alert_type = Column(String, nullable=False)  # high_risk_paper, system_health, anomaly_spike, etc.
    related_paper_id = Column(String, ForeignKey("papers.paper_id"), nullable=True)

    # Status
    acknowledged = Column(Boolean, default=False)
    resolved = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    # Indexes
    __table_args__ = (
        Index('idx_alert_severity', 'severity'),
        Index('idx_alert_resolved', 'resolved'),
    )
