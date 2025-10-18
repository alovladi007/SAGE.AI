"""
Celery Tasks for Academic Integrity Platform
backend/celery_tasks.py

Defines background tasks for paper processing, ML analysis, and maintenance.
"""

from celery_app import celery_app
from main import (
    SessionLocal, Paper, ProcessingJob, AnomalyFlag,
    TextProcessor, EmbeddingGenerator, AnomalyDetector
)
from datetime import datetime, timedelta
import uuid
import base64
import asyncio
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name='celery_tasks.process_paper_task')
def process_paper_task(self, paper_id: str, content_base64: str) -> Dict[str, Any]:
    """
    Process uploaded paper: extract text, generate embeddings, detect anomalies

    Args:
        self: Celery task instance
        paper_id: UUID of the paper to process
        content_base64: Base64-encoded PDF/TXT content

    Returns:
        Dict with processing results
    """
    db = SessionLocal()

    try:
        # Update task progress
        self.update_state(state='PROCESSING', meta={'progress': 0})

        # Decode content
        content = base64.b64decode(content_base64)

        # Get paper from database
        paper = db.query(Paper).filter(Paper.id == paper_id).first()
        if not paper:
            return {"error": "Paper not found", "paper_id": paper_id}

        # Update status
        paper.status = "processing"
        db.commit()

        logger.info(f"Processing paper {paper_id}: {paper.title}")

        # Step 1: Extract text (30% progress)
        self.update_state(state='PROCESSING', meta={'progress': 10, 'step': 'Extracting text'})

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            text_data = loop.run_until_complete(
                TextProcessor.extract_text_from_pdf(content)
            )

            paper.content = text_data["full_text"]
            paper.sections = text_data["sections"]
            db.commit()

            logger.info(f"Extracted {text_data['word_count']} words from paper {paper_id}")

        except Exception as e:
            logger.error(f"Text extraction failed for {paper_id}: {str(e)}")
            raise

        # Step 2: Generate embeddings (60% progress)
        self.update_state(state='PROCESSING', meta={'progress': 40, 'step': 'Generating embeddings'})

        try:
            embeddings = loop.run_until_complete(
                EmbeddingGenerator.generate_section_embeddings(text_data["sections"])
            )

            paper.embeddings = embeddings
            db.commit()

            logger.info(f"Generated embeddings for paper {paper_id}")

        except Exception as e:
            logger.error(f"Embedding generation failed for {paper_id}: {str(e)}")
            # Continue processing even if embeddings fail
            embeddings = {}

        # Step 3: Detect anomalies (80% progress)
        self.update_state(state='PROCESSING', meta={'progress': 70, 'step': 'Detecting anomalies'})

        anomalies = []
        try:
            # Statistical anomalies
            stat_anomalies = AnomalyDetector.check_statistical_anomalies(text_data["full_text"])
            anomalies.extend(stat_anomalies)

            # Citation anomalies
            if text_data["sections"].get("references"):
                cite_anomalies = AnomalyDetector.check_citation_anomalies(
                    text_data["sections"]["references"]
                )
                anomalies.extend(cite_anomalies)

            # Store anomaly flags
            for anomaly in anomalies:
                flag = AnomalyFlag(
                    id=uuid.uuid4(),
                    paper_id=paper.id,
                    anomaly_type=anomaly["type"],
                    severity=anomaly["severity"],
                    confidence=0.8,
                    description=anomaly["description"],
                    evidence=anomaly
                )
                db.add(flag)

            db.commit()
            logger.info(f"Detected {len(anomalies)} anomalies in paper {paper_id}")

        except Exception as e:
            logger.error(f"Anomaly detection failed for {paper_id}: {str(e)}")
            # Continue even if anomaly detection fails

        # Step 4: Complete (100% progress)
        self.update_state(state='PROCESSING', meta={'progress': 90, 'step': 'Finalizing'})

        # Update paper status
        paper.status = "completed"
        paper.processed_at = datetime.utcnow()

        # Update job status
        job = db.query(ProcessingJob).filter(
            ProcessingJob.paper_id == paper_id,
            ProcessingJob.job_type == "full_analysis"
        ).first()

        if job:
            job.status = "completed"
            job.completed_at = datetime.utcnow()
            job.result = {
                "word_count": text_data.get("word_count", 0),
                "page_count": text_data.get("page_count", 0),
                "anomaly_count": len(anomalies),
                "has_embeddings": len(embeddings) > 0
            }

        db.commit()

        loop.close()

        logger.info(f"Successfully processed paper {paper_id}")

        return {
            "status": "completed",
            "paper_id": paper_id,
            "word_count": text_data.get("word_count", 0),
            "anomalies_detected": len(anomalies),
            "embeddings_generated": len(embeddings)
        }

    except Exception as e:
        logger.error(f"Error processing paper {paper_id}: {str(e)}")

        # Update paper status to failed
        paper = db.query(Paper).filter(Paper.id == paper_id).first()
        if paper:
            paper.status = "failed"
            paper.error_log = str(e)

            # Update job status
            job = db.query(ProcessingJob).filter(
                ProcessingJob.paper_id == paper_id
            ).first()
            if job:
                job.status = "failed"
                job.error_message = str(e)

            db.commit()

        return {"error": str(e), "paper_id": paper_id}

    finally:
        db.close()


@celery_app.task(name='celery_tasks.calculate_similarity_task')
def calculate_similarity_task(paper_id: str, threshold: float = 0.3) -> Dict[str, Any]:
    """
    Calculate similarity between a paper and all other papers

    Args:
        paper_id: UUID of the paper
        threshold: Minimum similarity threshold

    Returns:
        Dict with similarity results
    """
    db = SessionLocal()

    try:
        from main import SimilarityEngine

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        similarities = loop.run_until_complete(
            SimilarityEngine.find_similar_papers(paper_id, db, threshold=threshold)
        )

        loop.close()

        logger.info(f"Found {len(similarities)} similar papers for {paper_id}")

        return {
            "paper_id": paper_id,
            "similar_papers_count": len(similarities),
            "similarities": similarities[:10]  # Top 10
        }

    except Exception as e:
        logger.error(f"Similarity calculation failed for {paper_id}: {str(e)}")
        return {"error": str(e), "paper_id": paper_id}

    finally:
        db.close()


@celery_app.task(name='celery_tasks.cleanup_old_jobs')
def cleanup_old_jobs() -> Dict[str, int]:
    """
    Clean up old completed jobs (run periodically)

    Returns:
        Dict with cleanup statistics
    """
    db = SessionLocal()

    try:
        # Delete jobs older than 30 days
        cutoff_date = datetime.utcnow() - timedelta(days=30)

        deleted = db.query(ProcessingJob).filter(
            ProcessingJob.completed_at < cutoff_date,
            ProcessingJob.status.in_(["completed", "failed"])
        ).delete()

        db.commit()

        logger.info(f"Cleaned up {deleted} old jobs")

        return {"deleted_jobs": deleted}

    except Exception as e:
        logger.error(f"Job cleanup failed: {str(e)}")
        return {"error": str(e)}

    finally:
        db.close()


@celery_app.task(name='celery_tasks.batch_process_papers')
def batch_process_papers(paper_ids: list) -> Dict[str, Any]:
    """
    Process multiple papers in batch

    Args:
        paper_ids: List of paper UUIDs

    Returns:
        Dict with batch processing results
    """
    results = []

    for paper_id in paper_ids:
        # Get paper content from database
        db = SessionLocal()
        try:
            paper = db.query(Paper).filter(Paper.id == paper_id).first()
            if not paper or not paper.content:
                results.append({"paper_id": paper_id, "error": "Paper not found or no content"})
                continue

            # Encode content and process
            content_b64 = base64.b64encode(paper.content.encode()).decode('utf-8')
            result = process_paper_task.delay(paper_id, content_b64)

            results.append({
                "paper_id": paper_id,
                "task_id": result.id,
                "status": "queued"
            })

        finally:
            db.close()

    return {
        "total_papers": len(paper_ids),
        "queued": len([r for r in results if "task_id" in r]),
        "failed": len([r for r in results if "error" in r]),
        "results": results
    }
