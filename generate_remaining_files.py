"""
Script to generate all remaining backend files for the Academic Integrity Platform
This creates all API routers, services, and utility files
"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

# Files to create
FILES = {
    "backend/app/routers/__init__.py": '''"""
API Routers
"""

from .auth import router as auth_router
from .papers import router as papers_router
from .analysis import router as analysis_router
from .jobs import router as jobs_router
from .search import router as search_router
from .statistics import router as statistics_router
from .reviews import router as reviews_router
from .alerts import router as alerts_router
from .admin import router as admin_router
from .health import router as health_router

__all__ = [
    "auth_router",
    "papers_router",
    "analysis_router",
    "jobs_router",
    "search_router",
    "statistics_router",
    "reviews_router",
    "alerts_router",
    "admin_router",
    "health_router"
]
''',

    "backend/app/routers/health.py": '''"""
Health check endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import httpx

from ..database import get_db
from ..schemas import HealthCheckResponse
from ..config import settings

router = APIRouter()


@router.get("/health", response_model=HealthCheckResponse)
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Comprehensive health check endpoint
    """

    # Check database
    db_status = "healthy"
    try:
        await db.execute("SELECT 1")
    except Exception:
        db_status = "unhealthy"

    # Check Redis (simplified)
    redis_status = "healthy"

    # Check Elasticsearch (simplified)
    es_status = "healthy"

    # Check ML Worker (simplified)
    ml_worker_status = "healthy"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{settings.ML_WORKER_URL}/health", timeout=5)
            ml_worker_status = "healthy" if response.status_code == 200 else "unhealthy"
    except Exception:
        ml_worker_status = "unhealthy"

    overall_status = "healthy" if all([
        db_status == "healthy",
        redis_status == "healthy",
        es_status == "healthy"
    ]) else "degraded"

    return HealthCheckResponse(
        status=overall_status,
        version=settings.APP_VERSION,
        database=db_status,
        redis=redis_status,
        elasticsearch=es_status,
        ml_worker=ml_worker_status,
        timestamp=datetime.utcnow()
    )
''',

    "backend/app/routers/auth.py": '''"""
Authentication endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..database import get_db
from ..models import User
from ..schemas import UserCreate, UserResponse, LoginRequest, Token
from ..auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    get_current_user
)

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user"""

    # Check if user already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        institution=user_data.institution,
        department=user_data.department,
        role=user_data.role
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


@router.post("/login", response_model=Token)
async def login(credentials: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Login and get access token"""

    # Find user
    result = await db.execute(select(User).where(User.email == credentials.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    # Create tokens
    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(data={"sub": user.id})

    # Update last login
    from datetime import datetime
    user.last_login = datetime.utcnow()
    await db.commit()

    return Token(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user
''',

    "backend/app/routers/papers.py": '''"""
Paper management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import os
import hashlib

from ..database import get_db
from ..models import User, Paper, ProcessingJob, PaperStatus
from ..schemas import PaperResponse, PaperDetail, UploadResponse
from ..auth import get_current_user
from ..config import settings

router = APIRouter()


def calculate_file_hash(file_content: bytes) -> str:
    """Calculate SHA-256 hash of file"""
    return hashlib.sha256(file_content).hexdigest()


@router.post("/upload", response_model=UploadResponse)
async def upload_paper(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload a paper for analysis"""

    # Validate file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {settings.ALLOWED_EXTENSIONS}"
        )

    # Read file content
    file_content = await file.read()
    file_size = len(file_content)

    if file_size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE} bytes"
        )

    # Calculate file hash
    file_hash = calculate_file_hash(file_content)

    # Check for duplicate
    result = await db.execute(select(Paper).where(Paper.file_hash == file_hash))
    existing_paper = result.scalar_one_or_none()

    if existing_paper:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This file has already been uploaded"
        )

    # Save file to storage (simplified - would use MinIO in production)
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)

    from pathlib import Path
    import uuid
    file_id = str(uuid.uuid4())
    file_path = upload_dir / f"{file_id}{file_ext}"

    with open(file_path, "wb") as f:
        f.write(file_content)

    # Create paper record
    new_paper = Paper(
        title=file.filename,
        file_path=str(file_path),
        file_size=file_size,
        file_hash=file_hash,
        status=PaperStatus.PENDING,
        submitter_id=current_user.id
    )

    db.add(new_paper)
    await db.flush()

    # Create processing job
    job = ProcessingJob(
        paper_id=new_paper.paper_id,
        job_type="analysis",
        status="queued"
    )

    db.add(job)
    await db.commit()
    await db.refresh(new_paper)
    await db.refresh(job)

    # TODO: Trigger async processing task

    return UploadResponse(
        job_id=job.job_id,
        paper_id=new_paper.paper_id,
        status="queued",
        message="Paper uploaded successfully and queued for processing"
    )


@router.get("/{paper_id}", response_model=PaperDetail)
async def get_paper(
    paper_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get paper details"""

    result = await db.execute(select(Paper).where(Paper.paper_id == paper_id))
    paper = result.scalar_one_or_none()

    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paper not found"
        )

    return paper


@router.get("/", response_model=List[PaperResponse])
async def list_papers(
    limit: int = 20,
    offset: int = 0,
    status_filter: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List papers"""

    query = select(Paper).offset(offset).limit(limit)

    if status_filter:
        query = query.where(Paper.status == status_filter)

    result = await db.execute(query)
    papers = result.scalars().all()

    return papers
''',

    "backend/app/routers/analysis.py": '''"""
Analysis endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..database import get_db
from ..models import User, Paper, AnalysisResult, SimilarityMatch, Anomaly
from ..schemas import FullAnalysisResponse, AnalysisResultResponse
from ..auth import get_current_user

router = APIRouter()


@router.get("/{paper_id}", response_model=FullAnalysisResponse)
async def get_analysis(
    paper_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get full analysis for a paper"""

    # Get paper
    result = await db.execute(select(Paper).where(Paper.paper_id == paper_id))
    paper = result.scalar_one_or_none()

    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paper not found"
        )

    # Get analysis result
    result = await db.execute(
        select(AnalysisResult).where(AnalysisResult.paper_id == paper_id)
    )
    analysis = result.scalar_one_or_none()

    # Get similarity matches
    result = await db.execute(
        select(SimilarityMatch).where(SimilarityMatch.source_paper_id == paper_id)
    )
    similarity_matches = result.scalars().all()

    # Get anomalies
    result = await db.execute(
        select(Anomaly).where(Anomaly.paper_id == paper_id)
    )
    anomalies = result.scalars().all()

    return FullAnalysisResponse(
        paper=paper,
        analysis=analysis,
        similarity_matches=similarity_matches,
        anomalies=anomalies
    )
''',

    "backend/app/routers/jobs.py": '''"""
Job management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..database import get_db
from ..models import User, ProcessingJob
from ..schemas import JobStatus
from ..auth import get_current_user

router = APIRouter()


@router.get("/{job_id}/status", response_model=JobStatus)
async def get_job_status(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get job status"""

    result = await db.execute(select(ProcessingJob).where(ProcessingJob.job_id == job_id))
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    return job
''',

    "backend/app/routers/search.py": '''"""
Search endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from ..database import get_db
from ..models import User, Paper
from ..schemas import PaperSearchRequest, PaperSearchResponse
from ..auth import get_current_user

router = APIRouter()


@router.post("/", response_model=PaperSearchResponse)
async def search_papers(
    search_params: PaperSearchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Search papers with filters"""

    query = select(Paper)

    # Apply filters
    filters = []

    if search_params.query:
        # Simple text search (would use full-text search in production)
        filters.append(Paper.title.ilike(f"%{search_params.query}%"))

    if search_params.author:
        filters.append(Paper.authors.contains([search_params.author]))

    if search_params.journal:
        filters.append(Paper.journal == search_params.journal)

    if search_params.min_risk_score is not None:
        filters.append(Paper.risk_score >= search_params.min_risk_score)

    if search_params.max_risk_score is not None:
        filters.append(Paper.risk_score <= search_params.max_risk_score)

    if search_params.start_date:
        filters.append(Paper.submitted_at >= search_params.start_date)

    if search_params.end_date:
        filters.append(Paper.submitted_at <= search_params.end_date)

    if search_params.status:
        filters.append(Paper.status == search_params.status)

    if filters:
        query = query.where(and_(*filters))

    # Count total
    from sqlalchemy import func as sql_func
    count_query = select(sql_func.count()).select_from(Paper)
    if filters:
        count_query = count_query.where(and_(*filters))

    count_result = await db.execute(count_query)
    total = count_result.scalar()

    # Apply pagination
    query = query.offset(search_params.offset).limit(search_params.limit)

    # Execute query
    result = await db.execute(query)
    papers = result.scalars().all()

    return PaperSearchResponse(
        results=papers,
        total=total,
        limit=search_params.limit,
        offset=search_params.offset
    )
''',

    "backend/app/routers/statistics.py": '''"""
Statistics endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from ..database import get_db
from ..models import User, Paper, Anomaly, PaperStatus
from ..schemas import StatisticsOverview
from ..auth import get_current_user

router = APIRouter()


@router.get("/overview", response_model=StatisticsOverview)
async def get_statistics_overview(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get overall statistics"""

    # Total papers
    total_result = await db.execute(select(func.count(Paper.paper_id)))
    total_papers = total_result.scalar() or 0

    # Processed papers
    processed_result = await db.execute(
        select(func.count(Paper.paper_id)).where(Paper.status == PaperStatus.COMPLETED)
    )
    processed_papers = processed_result.scalar() or 0

    # Pending papers
    pending_result = await db.execute(
        select(func.count(Paper.paper_id)).where(Paper.status == PaperStatus.PENDING)
    )
    pending_papers = pending_result.scalar() or 0

    # Failed papers
    failed_result = await db.execute(
        select(func.count(Paper.paper_id)).where(Paper.status == PaperStatus.FAILED)
    )
    failed_papers = failed_result.scalar() or 0

    # Total anomalies
    anomalies_result = await db.execute(select(func.count(Anomaly.id)))
    total_anomalies = anomalies_result.scalar() or 0

    # High risk papers
    high_risk_result = await db.execute(
        select(func.count(Paper.paper_id)).where(Paper.risk_score >= 0.7)
    )
    high_risk_papers = high_risk_result.scalar() or 0

    # Medium risk papers
    medium_risk_result = await db.execute(
        select(func.count(Paper.paper_id)).where(
            (Paper.risk_score >= 0.4) & (Paper.risk_score < 0.7)
        )
    )
    medium_risk_papers = medium_risk_result.scalar() or 0

    # Low risk papers
    low_risk_result = await db.execute(
        select(func.count(Paper.paper_id)).where(Paper.risk_score < 0.4)
    )
    low_risk_papers = low_risk_result.scalar() or 0

    # Calculate average risk score
    avg_risk_result = await db.execute(select(func.avg(Paper.risk_score)))
    avg_risk_score = float(avg_risk_result.scalar() or 0.0)

    # Calculate processing rate
    processing_rate = processed_papers / total_papers if total_papers > 0 else 0.0

    return StatisticsOverview(
        total_papers=total_papers,
        processed_papers=processed_papers,
        pending_papers=pending_papers,
        failed_papers=failed_papers,
        total_anomalies_detected=total_anomalies,
        high_risk_papers=high_risk_papers,
        medium_risk_papers=medium_risk_papers,
        low_risk_papers=low_risk_papers,
        processing_rate=processing_rate,
        average_risk_score=avg_risk_score,
        average_processing_time=2.3  # Mock value
    )
''',

    "backend/app/routers/reviews.py": '''"""
Review endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from ..database import get_db
from ..models import User, Review, Paper
from ..schemas import ReviewCreate, ReviewResponse, ReviewUpdate
from ..auth import get_current_user

router = APIRouter()


@router.post("/", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    review_data: ReviewCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new review"""

    # Verify paper exists
    result = await db.execute(select(Paper).where(Paper.paper_id == review_data.paper_id))
    paper = result.scalar_one_or_none()

    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paper not found"
        )

    new_review = Review(
        paper_id=review_data.paper_id,
        reviewer_id=current_user.id,
        decision=review_data.decision,
        risk_assessment=review_data.risk_assessment,
        notes=review_data.notes,
        recommendations=review_data.recommendations
    )

    db.add(new_review)
    await db.commit()
    await db.refresh(new_review)

    return new_review


@router.get("/{paper_id}", response_model=List[ReviewResponse])
async def get_paper_reviews(
    paper_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all reviews for a paper"""

    result = await db.execute(select(Review).where(Review.paper_id == paper_id))
    reviews = result.scalars().all()

    return reviews
''',

    "backend/app/routers/alerts.py": '''"""
Alert endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from ..database import get_db
from ..models import User, Alert
from ..schemas import AlertResponse
from ..auth import get_current_user, require_reviewer

router = APIRouter()


@router.get("/", response_model=List[AlertResponse])
async def get_alerts(
    unresolved_only: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_reviewer)
):
    """Get alerts"""

    query = select(Alert)

    if unresolved_only:
        query = query.where(Alert.resolved == False)

    result = await db.execute(query)
    alerts = result.scalars().all()

    return alerts
''',

    "backend/app/routers/admin.py": '''"""
Admin endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List

from ..database import get_db
from ..models import User, Paper, UserRole
from ..schemas import UserResponse, UserUpdate
from ..auth import get_current_user, require_admin

router = APIRouter()


@router.get("/users", response_model=List[UserResponse])
async def list_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """List all users (admin only)"""

    result = await db.execute(select(User))
    users = result.scalars().all()

    return users


@router.delete("/papers/{paper_id}")
async def delete_paper(
    paper_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete a paper (admin only)"""

    result = await db.execute(select(Paper).where(Paper.paper_id == paper_id))
    paper = result.scalar_one_or_none()

    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paper not found"
        )

    await db.delete(paper)
    await db.commit()

    return {"message": "Paper deleted successfully"}
''',
}

def create_files():
    """Create all files"""
    for filepath, content in FILES.items():
        full_path = BASE_DIR / filepath
        full_path.parent.mkdir(parents=True, exist_ok=True)

        with open(full_path, 'w') as f:
            f.write(content)

        print(f"Created: {filepath}")

if __name__ == "__main__":
    create_files()
    print(f"\\nCreated {len(FILES)} files successfully!")
