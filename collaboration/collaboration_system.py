# Collaboration Features - Multi-Reviewer Workflows, Comments, and History Tracking
# collaboration_system.py

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import uuid
from collections import defaultdict
import redis
import websockets
from sqlalchemy import create_engine, Column, String, DateTime, Float, Integer, Boolean, ForeignKey, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import hashlib
import difflib
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============= DATABASE MODELS =============

Base = declarative_base()

class ReviewStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DISPUTED = "disputed"
    CONSENSUS_REACHED = "consensus_reached"

class ReviewerRole(Enum):
    LEAD_REVIEWER = "lead_reviewer"
    REVIEWER = "reviewer"
    EXPERT_REVIEWER = "expert_reviewer"
    OBSERVER = "observer"
    MODERATOR = "moderator"

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    role = Column(String, default=ReviewerRole.REVIEWER.value)
    institution = Column(String)
    expertise_areas = Column(JSON)

    # Relationships
    reviews = relationship("Review", back_populates="reviewer")
    comments = relationship("Comment", back_populates="author")
    annotations = relationship("Annotation", back_populates="author")
    activities = relationship("ActivityLog", back_populates="user")

class Paper(Base):
    __tablename__ = "papers"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    authors = Column(JSON)
    content = Column(Text)
    risk_score = Column(Float)
    version = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    reviews = relationship("Review", back_populates="paper")
    comments = relationship("Comment", back_populates="paper")
    annotations = relationship("Annotation", back_populates="paper")
    workflows = relationship("ReviewWorkflow", back_populates="paper")
    versions = relationship("PaperVersion", back_populates="paper")

class ReviewWorkflow(Base):
    __tablename__ = "review_workflows"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    paper_id = Column(String, ForeignKey("papers.id"))
    status = Column(String, default=ReviewStatus.PENDING.value)
    created_at = Column(DateTime, default=datetime.utcnow)
    deadline = Column(DateTime)
    consensus_threshold = Column(Float, default=0.7)

    # Workflow settings
    require_consensus = Column(Boolean, default=True)
    min_reviewers = Column(Integer, default=3)
    allow_discussion = Column(Boolean, default=True)
    blind_review = Column(Boolean, default=False)

    # Relationships
    paper = relationship("Paper", back_populates="workflows")
    assignments = relationship("ReviewAssignment", back_populates="workflow")
    decisions = relationship("ReviewDecision", back_populates="workflow")

class ReviewAssignment(Base):
    __tablename__ = "review_assignments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id = Column(String, ForeignKey("review_workflows.id"))
    reviewer_id = Column(String, ForeignKey("users.id"))
    role = Column(String, default=ReviewerRole.REVIEWER.value)
    assigned_at = Column(DateTime, default=datetime.utcnow)
    accepted = Column(Boolean, default=None)
    completed = Column(Boolean, default=False)

    # Relationships
    workflow = relationship("ReviewWorkflow", back_populates="assignments")
    reviewer = relationship("User")
    review = relationship("Review", uselist=False)

class Review(Base):
    __tablename__ = "reviews"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    paper_id = Column(String, ForeignKey("papers.id"))
    reviewer_id = Column(String, ForeignKey("users.id"))
    assignment_id = Column(String, ForeignKey("review_assignments.id"))

    # Review content
    risk_assessment = Column(Float)
    confidence_score = Column(Float)
    findings = Column(JSON)
    recommendation = Column(String)
    detailed_feedback = Column(Text)

    # Timestamps
    started_at = Column(DateTime)
    submitted_at = Column(DateTime)
    time_spent_minutes = Column(Integer, default=0)

    # Relationships
    paper = relationship("Paper", back_populates="reviews")
    reviewer = relationship("User", back_populates="reviews")
    assignment = relationship("ReviewAssignment", back_populates="review")
    votes = relationship("ReviewVote", back_populates="review")

class Comment(Base):
    __tablename__ = "comments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    paper_id = Column(String, ForeignKey("papers.id"))
    author_id = Column(String, ForeignKey("users.id"))
    parent_id = Column(String, ForeignKey("comments.id"), nullable=True)

    content = Column(Text, nullable=False)
    comment_type = Column(String)  # general, question, concern, suggestion
    section = Column(String)  # abstract, methodology, results, etc.

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    is_resolved = Column(Boolean, default=False)

    # Relationships
    paper = relationship("Paper", back_populates="comments")
    author = relationship("User", back_populates="comments")
    replies = relationship("Comment", backref="parent", remote_side=[id])
    reactions = relationship("CommentReaction", back_populates="comment")

class Annotation(Base):
    __tablename__ = "annotations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    paper_id = Column(String, ForeignKey("papers.id"))
    author_id = Column(String, ForeignKey("users.id"))

    # Location in document
    page_number = Column(Integer)
    start_position = Column(Integer)
    end_position = Column(Integer)
    selected_text = Column(Text)

    # Annotation content
    content = Column(Text, nullable=False)
    annotation_type = Column(String)  # highlight, note, question, issue
    severity = Column(String)  # info, warning, critical
    color = Column(String, default="#FFFF00")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    # Relationships
    paper = relationship("Paper", back_populates="annotations")
    author = relationship("User", back_populates="annotations")

class ReviewDecision(Base):
    __tablename__ = "review_decisions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id = Column(String, ForeignKey("review_workflows.id"))

    decision = Column(String)  # approve, reject, request_revision
    consensus_score = Column(Float)
    justification = Column(Text)
    conditions = Column(JSON)

    decided_at = Column(DateTime, default=datetime.utcnow)
    decided_by = Column(String, ForeignKey("users.id"))

    # Relationships
    workflow = relationship("ReviewWorkflow", back_populates="decisions")
    decider = relationship("User")

class ReviewVote(Base):
    __tablename__ = "review_votes"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    review_id = Column(String, ForeignKey("reviews.id"))
    voter_id = Column(String, ForeignKey("users.id"))

    vote = Column(String)  # agree, disagree, abstain
    confidence = Column(Float)
    comment = Column(Text)

    voted_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    review = relationship("Review", back_populates="votes")
    voter = relationship("User")

class CommentReaction(Base):
    __tablename__ = "comment_reactions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    comment_id = Column(String, ForeignKey("comments.id"))
    user_id = Column(String, ForeignKey("users.id"))

    reaction = Column(String)  # like, helpful, agree, disagree, question
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    comment = relationship("Comment", back_populates="reactions")
    user = relationship("User")

class PaperVersion(Base):
    __tablename__ = "paper_versions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    paper_id = Column(String, ForeignKey("papers.id"))
    version_number = Column(Integer)

    content_hash = Column(String)
    changes = Column(JSON)
    changed_by = Column(String, ForeignKey("users.id"))
    changed_at = Column(DateTime, default=datetime.utcnow)
    change_reason = Column(Text)

    # Store full content snapshot
    content_snapshot = Column(Text)
    metadata_snapshot = Column(JSON)

    # Relationships
    paper = relationship("Paper", back_populates="versions")
    editor = relationship("User")

class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    paper_id = Column(String, ForeignKey("papers.id"), nullable=True)

    action_type = Column(String)  # view, edit, comment, review, etc.
    action_details = Column(JSON)
    ip_address = Column(String)
    user_agent = Column(String)

    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="activities")
    paper = relationship("Paper")

# ============= WORKFLOW MANAGER =============

class WorkflowManager:
    """Manages multi-reviewer workflows"""

    def __init__(self, db_session):
        self.db = db_session
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)

    async def create_workflow(self, paper_id: str, settings: Dict[str, Any]) -> str:
        """Create a new review workflow"""

        workflow = ReviewWorkflow(
            paper_id=paper_id,
            status=ReviewStatus.PENDING.value,
            deadline=settings.get('deadline'),
            consensus_threshold=settings.get('consensus_threshold', 0.7),
            require_consensus=settings.get('require_consensus', True),
            min_reviewers=settings.get('min_reviewers', 3),
            allow_discussion=settings.get('allow_discussion', True),
            blind_review=settings.get('blind_review', False)
        )

        self.db.add(workflow)
        self.db.commit()

        # Auto-assign reviewers if specified
        if 'auto_assign' in settings and settings['auto_assign']:
            await self._auto_assign_reviewers(workflow.id, settings.get('expertise_required', []))

        # Send notifications
        await self._notify_workflow_created(workflow.id)

        return workflow.id

    async def assign_reviewer(self, workflow_id: str, reviewer_id: str,
                            role: ReviewerRole = ReviewerRole.REVIEWER) -> str:
        """Assign a reviewer to a workflow"""

        # Check if already assigned
        existing = self.db.query(ReviewAssignment).filter_by(
            workflow_id=workflow_id,
            reviewer_id=reviewer_id
        ).first()

        if existing:
            raise ValueError("Reviewer already assigned to this workflow")

        assignment = ReviewAssignment(
            workflow_id=workflow_id,
            reviewer_id=reviewer_id,
            role=role.value
        )

        self.db.add(assignment)
        self.db.commit()

        # Send invitation
        await self._send_review_invitation(assignment.id)

        return assignment.id

    async def _auto_assign_reviewers(self, workflow_id: str, expertise_required: List[str]):
        """Automatically assign reviewers based on expertise"""

        workflow = self.db.query(ReviewWorkflow).get(workflow_id)

        # Find eligible reviewers
        eligible_reviewers = self.db.query(User).filter(
            User.expertise_areas.contains(expertise_required)
        ).all()

        # Score and rank reviewers
        scored_reviewers = []
        for reviewer in eligible_reviewers:
            score = self._calculate_reviewer_score(reviewer, expertise_required)
            scored_reviewers.append((reviewer, score))

        # Sort by score and assign top reviewers
        scored_reviewers.sort(key=lambda x: x[1], reverse=True)

        for i, (reviewer, score) in enumerate(scored_reviewers[:workflow.min_reviewers]):
            role = ReviewerRole.LEAD_REVIEWER if i == 0 else ReviewerRole.REVIEWER
            await self.assign_reviewer(workflow_id, reviewer.id, role)

    def _calculate_reviewer_score(self, reviewer: User, expertise_required: List[str]) -> float:
        """Calculate reviewer suitability score"""

        score = 0.0

        # Expertise match
        reviewer_expertise = set(reviewer.expertise_areas or [])
        required_expertise = set(expertise_required)
        overlap = reviewer_expertise.intersection(required_expertise)
        score += len(overlap) * 10

        # Past review quality (from historical data)
        past_reviews = self.db.query(Review).filter_by(reviewer_id=reviewer.id).all()
        if past_reviews:
            avg_confidence = sum(r.confidence_score or 0 for r in past_reviews) / len(past_reviews)
            score += avg_confidence * 5

        # Availability (check current assignments)
        active_assignments = self.db.query(ReviewAssignment).filter_by(
            reviewer_id=reviewer.id,
            completed=False
        ).count()
        score -= active_assignments * 2

        return score

    async def submit_review(self, assignment_id: str, review_data: Dict[str, Any]) -> str:
        """Submit a review for an assignment"""

        assignment = self.db.query(ReviewAssignment).get(assignment_id)
        if not assignment:
            raise ValueError("Assignment not found")

        if assignment.completed:
            raise ValueError("Review already submitted")

        # Create review
        review = Review(
            paper_id=assignment.workflow.paper_id,
            reviewer_id=assignment.reviewer_id,
            assignment_id=assignment_id,
            risk_assessment=review_data.get('risk_assessment'),
            confidence_score=review_data.get('confidence_score'),
            findings=review_data.get('findings'),
            recommendation=review_data.get('recommendation'),
            detailed_feedback=review_data.get('detailed_feedback'),
            started_at=review_data.get('started_at'),
            submitted_at=datetime.utcnow(),
            time_spent_minutes=review_data.get('time_spent_minutes', 0)
        )

        self.db.add(review)

        # Mark assignment as completed
        assignment.completed = True

        self.db.commit()

        # Check if workflow is complete
        await self._check_workflow_completion(assignment.workflow_id)

        # Notify other reviewers
        await self._notify_review_submitted(review.id)

        return review.id

    async def _check_workflow_completion(self, workflow_id: str):
        """Check if all reviews are complete and calculate consensus"""

        workflow = self.db.query(ReviewWorkflow).get(workflow_id)
        assignments = self.db.query(ReviewAssignment).filter_by(workflow_id=workflow_id).all()

        # Check if minimum reviews completed
        completed_count = sum(1 for a in assignments if a.completed)

        if completed_count >= workflow.min_reviewers:
            # Calculate consensus
            reviews = self.db.query(Review).join(ReviewAssignment).filter(
                ReviewAssignment.workflow_id == workflow_id
            ).all()

            if workflow.require_consensus:
                consensus_score = self._calculate_consensus(reviews)

                if consensus_score >= workflow.consensus_threshold:
                    workflow.status = ReviewStatus.CONSENSUS_REACHED.value
                    await self._finalize_workflow(workflow_id, consensus_score)
                else:
                    workflow.status = ReviewStatus.DISPUTED.value
                    await self._initiate_discussion(workflow_id)
            else:
                workflow.status = ReviewStatus.COMPLETED.value
                await self._finalize_workflow(workflow_id)

            self.db.commit()

    def _calculate_consensus(self, reviews: List[Review]) -> float:
        """Calculate consensus score among reviews"""

        if not reviews:
            return 0.0

        # Extract risk assessments
        risk_scores = [r.risk_assessment for r in reviews if r.risk_assessment is not None]

        if len(risk_scores) < 2:
            return 1.0  # Single review = full consensus

        # Calculate variance
        mean_risk = sum(risk_scores) / len(risk_scores)
        variance = sum((score - mean_risk) ** 2 for score in risk_scores) / len(risk_scores)

        # Convert to consensus score (lower variance = higher consensus)
        max_variance = 0.25  # Maximum expected variance (0-1 scale)
        consensus = max(0, 1 - (variance / max_variance))

        # Also consider recommendations
        recommendations = [r.recommendation for r in reviews if r.recommendation]
        if recommendations:
            unique_recommendations = set(recommendations)
            recommendation_consensus = 1.0 / len(unique_recommendations)
            consensus = (consensus + recommendation_consensus) / 2

        return consensus

    async def _initiate_discussion(self, workflow_id: str):
        """Initiate discussion phase for disputed reviews"""

        # Create discussion thread
        discussion_id = str(uuid.uuid4())

        # Store in Redis for real-time collaboration
        self.redis_client.hset(
            f"discussion:{workflow_id}",
            mapping={
                "id": discussion_id,
                "status": "active",
                "started_at": datetime.utcnow().isoformat()
            }
        )

        # Notify reviewers
        await self._notify_discussion_started(workflow_id)

    async def _finalize_workflow(self, workflow_id: str, consensus_score: float = None):
        """Finalize workflow and generate decision"""

        workflow = self.db.query(ReviewWorkflow).get(workflow_id)
        reviews = self.db.query(Review).join(ReviewAssignment).filter(
            ReviewAssignment.workflow_id == workflow_id
        ).all()

        # Aggregate findings
        aggregated_findings = self._aggregate_review_findings(reviews)

        # Determine final decision
        avg_risk = sum(r.risk_assessment for r in reviews if r.risk_assessment) / len(reviews)

        if avg_risk >= 0.7:
            decision = "reject"
        elif avg_risk >= 0.4:
            decision = "request_revision"
        else:
            decision = "approve"

        # Create decision record
        review_decision = ReviewDecision(
            workflow_id=workflow_id,
            decision=decision,
            consensus_score=consensus_score,
            justification=self._generate_decision_justification(reviews, aggregated_findings),
            conditions=aggregated_findings.get('conditions', [])
        )

        self.db.add(review_decision)
        self.db.commit()

        # Notify stakeholders
        await self._notify_decision_made(review_decision.id)

    def _aggregate_review_findings(self, reviews: List[Review]) -> Dict[str, Any]:
        """Aggregate findings from multiple reviews"""

        aggregated = {
            "common_issues": [],
            "unique_issues": [],
            "conditions": [],
            "strengths": []
        }

        all_findings = []
        for review in reviews:
            if review.findings:
                all_findings.extend(review.findings)

        # Count occurrences
        finding_counts = defaultdict(int)
        for finding in all_findings:
            finding_key = json.dumps(finding, sort_keys=True)
            finding_counts[finding_key] += 1

        # Classify as common or unique
        for finding_key, count in finding_counts.items():
            finding = json.loads(finding_key)
            if count >= len(reviews) / 2:
                aggregated["common_issues"].append(finding)
            else:
                aggregated["unique_issues"].append(finding)

        return aggregated

    def _generate_decision_justification(self, reviews: List[Review],
                                        aggregated_findings: Dict) -> str:
        """Generate justification for the decision"""

        justification = "Based on the review panel's assessment:\n\n"

        # Summarize risk assessments
        risk_scores = [r.risk_assessment for r in reviews if r.risk_assessment]
        if risk_scores:
            avg_risk = sum(risk_scores) / len(risk_scores)
            justification += f"- Average risk score: {avg_risk:.2%}\n"
            justification += f"- Risk range: {min(risk_scores):.2%} - {max(risk_scores):.2%}\n\n"

        # Common issues
        if aggregated_findings["common_issues"]:
            justification += "Common concerns identified by multiple reviewers:\n"
            for issue in aggregated_findings["common_issues"][:5]:
                justification += f"- {issue.get('description', 'Issue')}\n"
            justification += "\n"

        # Reviewer recommendations
        recommendations = [r.recommendation for r in reviews if r.recommendation]
        if recommendations:
            rec_counts = defaultdict(int)
            for rec in recommendations:
                rec_counts[rec] += 1

            justification += "Reviewer recommendations:\n"
            for rec, count in rec_counts.items():
                justification += f"- {rec}: {count}/{len(reviews)} reviewers\n"

        return justification

    async def _notify_workflow_created(self, workflow_id: str):
        """Send notification about new workflow"""
        logger.info(f"Workflow created: {workflow_id}")
        # Implementation for actual notification system

    async def _send_review_invitation(self, assignment_id: str):
        """Send review invitation to assigned reviewer"""
        logger.info(f"Review invitation sent: {assignment_id}")
        # Implementation for actual notification system

    async def _notify_review_submitted(self, review_id: str):
        """Notify about submitted review"""
        logger.info(f"Review submitted: {review_id}")
        # Implementation for actual notification system

    async def _notify_discussion_started(self, workflow_id: str):
        """Notify about discussion phase"""
        logger.info(f"Discussion started for workflow: {workflow_id}")
        # Implementation for actual notification system

    async def _notify_decision_made(self, decision_id: str):
        """Notify about final decision"""
        logger.info(f"Decision made: {decision_id}")
        # Implementation for actual notification system

# ============= COLLABORATION MANAGER =============

class CollaborationManager:
    """Manages real-time collaboration features"""

    def __init__(self, db_session):
        self.db = db_session
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        self.active_sessions = {}
        self.websocket_connections = defaultdict(set)

    async def add_comment(self, paper_id: str, user_id: str,
                         comment_data: Dict[str, Any]) -> str:
        """Add a comment to a paper"""

        comment = Comment(
            paper_id=paper_id,
            author_id=user_id,
            parent_id=comment_data.get('parent_id'),
            content=comment_data.get('content'),
            comment_type=comment_data.get('type', 'general'),
            section=comment_data.get('section')
        )

        self.db.add(comment)
        self.db.commit()

        # Broadcast to active users
        await self._broadcast_new_comment(paper_id, comment)

        # Track activity
        self._log_activity(user_id, paper_id, 'comment', {'comment_id': comment.id})

        return comment.id

    async def add_annotation(self, paper_id: str, user_id: str,
                           annotation_data: Dict[str, Any]) -> str:
        """Add an annotation to a paper"""

        annotation = Annotation(
            paper_id=paper_id,
            author_id=user_id,
            page_number=annotation_data.get('page_number'),
            start_position=annotation_data.get('start_position'),
            end_position=annotation_data.get('end_position'),
            selected_text=annotation_data.get('selected_text'),
            content=annotation_data.get('content'),
            annotation_type=annotation_data.get('type', 'note'),
            severity=annotation_data.get('severity', 'info'),
            color=annotation_data.get('color', '#FFFF00')
        )

        self.db.add(annotation)
        self.db.commit()

        # Broadcast to active users
        await self._broadcast_new_annotation(paper_id, annotation)

        # Track activity
        self._log_activity(user_id, paper_id, 'annotate', {'annotation_id': annotation.id})

        return annotation.id

    def get_comments_thread(self, paper_id: str) -> List[Dict[str, Any]]:
        """Get comment thread for a paper"""

        comments = self.db.query(Comment).filter_by(
            paper_id=paper_id,
            parent_id=None
        ).order_by(Comment.created_at.desc()).all()

        return [self._serialize_comment_thread(comment) for comment in comments]

    def _serialize_comment_thread(self, comment: Comment) -> Dict[str, Any]:
        """Serialize comment with replies"""

        return {
            "id": comment.id,
            "author": {
                "id": comment.author.id,
                "name": comment.author.name,
                "role": comment.author.role
            },
            "content": comment.content,
            "type": comment.comment_type,
            "section": comment.section,
            "created_at": comment.created_at.isoformat(),
            "is_resolved": comment.is_resolved,
            "reactions": [
                {
                    "user_id": r.user_id,
                    "reaction": r.reaction
                }
                for r in comment.reactions
            ],
            "replies": [
                self._serialize_comment_thread(reply)
                for reply in comment.replies
            ]
        }

    def get_annotations(self, paper_id: str, page_number: int = None) -> List[Dict[str, Any]]:
        """Get annotations for a paper or specific page"""

        query = self.db.query(Annotation).filter_by(paper_id=paper_id)

        if page_number is not None:
            query = query.filter_by(page_number=page_number)

        annotations = query.order_by(Annotation.start_position).all()

        return [
            {
                "id": a.id,
                "author": {
                    "id": a.author.id,
                    "name": a.author.name
                },
                "page": a.page_number,
                "start": a.start_position,
                "end": a.end_position,
                "text": a.selected_text,
                "content": a.content,
                "type": a.annotation_type,
                "severity": a.severity,
                "color": a.color,
                "created_at": a.created_at.isoformat()
            }
            for a in annotations
        ]

    def add_reaction(self, comment_id: str, user_id: str, reaction: str) -> bool:
        """Add reaction to a comment"""

        # Check if reaction already exists
        existing = self.db.query(CommentReaction).filter_by(
            comment_id=comment_id,
            user_id=user_id
        ).first()

        if existing:
            existing.reaction = reaction
        else:
            new_reaction = CommentReaction(
                comment_id=comment_id,
                user_id=user_id,
                reaction=reaction
            )
            self.db.add(new_reaction)

        self.db.commit()
        return True

    def resolve_comment(self, comment_id: str, resolved_by: str) -> bool:
        """Mark comment as resolved"""

        comment = self.db.query(Comment).get(comment_id)
        if comment:
            comment.is_resolved = True
            self.db.commit()

            # Log activity
            self._log_activity(resolved_by, comment.paper_id, 'resolve_comment',
                             {'comment_id': comment_id})
            return True
        return False

    async def start_collaboration_session(self, paper_id: str, user_id: str) -> str:
        """Start a collaboration session"""

        session_id = str(uuid.uuid4())

        # Store session in Redis
        session_data = {
            "session_id": session_id,
            "paper_id": paper_id,
            "user_id": user_id,
            "started_at": datetime.utcnow().isoformat(),
            "active": True
        }

        self.redis_client.hset(f"session:{session_id}", mapping=session_data)

        # Add to active sessions
        self.redis_client.sadd(f"paper_sessions:{paper_id}", session_id)

        # Track active user
        self.redis_client.sadd(f"paper_users:{paper_id}", user_id)

        return session_id

    async def end_collaboration_session(self, session_id: str):
        """End a collaboration session"""

        session_data = self.redis_client.hgetall(f"session:{session_id}")

        if session_data:
            # Remove from active sessions
            self.redis_client.srem(f"paper_sessions:{session_data['paper_id']}", session_id)
            self.redis_client.srem(f"paper_users:{session_data['paper_id']}", session_data['user_id'])

            # Mark as inactive
            self.redis_client.hset(f"session:{session_id}", "active", False)

    def get_active_collaborators(self, paper_id: str) -> List[Dict[str, Any]]:
        """Get list of active collaborators on a paper"""

        user_ids = self.redis_client.smembers(f"paper_users:{paper_id}")

        users = []
        for user_id in user_ids:
            user = self.db.query(User).get(user_id)
            if user:
                users.append({
                    "id": user.id,
                    "name": user.name,
                    "role": user.role
                })

        return users

    async def _broadcast_new_comment(self, paper_id: str, comment: Comment):
        """Broadcast new comment to active users"""

        message = {
            "type": "new_comment",
            "paper_id": paper_id,
            "comment": self._serialize_comment_thread(comment)
        }

        await self._broadcast_to_paper_users(paper_id, message)

    async def _broadcast_new_annotation(self, paper_id: str, annotation: Annotation):
        """Broadcast new annotation to active users"""

        message = {
            "type": "new_annotation",
            "paper_id": paper_id,
            "annotation": {
                "id": annotation.id,
                "author_id": annotation.author_id,
                "page": annotation.page_number,
                "content": annotation.content,
                "type": annotation.annotation_type
            }
        }

        await self._broadcast_to_paper_users(paper_id, message)

    async def _broadcast_to_paper_users(self, paper_id: str, message: Dict):
        """Broadcast message to all users viewing a paper"""

        # Get WebSocket connections for paper
        connections = self.websocket_connections.get(paper_id, set())

        for websocket in connections.copy():
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Failed to send WebSocket message: {e}")
                connections.remove(websocket)

    def _log_activity(self, user_id: str, paper_id: str, action: str, details: Dict = None):
        """Log user activity"""

        activity = ActivityLog(
            user_id=user_id,
            paper_id=paper_id,
            action_type=action,
            action_details=details or {}
        )

        self.db.add(activity)
        self.db.commit()

# ============= VERSION CONTROL MANAGER =============

class VersionControlManager:
    """Manages paper versions and change tracking"""

    def __init__(self, db_session):
        self.db = db_session

    def create_version(self, paper_id: str, user_id: str,
                      reason: str = None) -> str:
        """Create a new version of a paper"""

        paper = self.db.query(Paper).get(paper_id)
        if not paper:
            raise ValueError("Paper not found")

        # Calculate content hash
        content_hash = hashlib.sha256(paper.content.encode()).hexdigest()

        # Check if content actually changed
        last_version = self.db.query(PaperVersion).filter_by(
            paper_id=paper_id
        ).order_by(PaperVersion.version_number.desc()).first()

        if last_version and last_version.content_hash == content_hash:
            return last_version.id  # No changes

        # Create new version
        new_version_number = (last_version.version_number + 1) if last_version else 1

        # Calculate changes
        changes = self._calculate_changes(
            last_version.content_snapshot if last_version else "",
            paper.content
        )

        version = PaperVersion(
            paper_id=paper_id,
            version_number=new_version_number,
            content_hash=content_hash,
            changes=changes,
            changed_by=user_id,
            change_reason=reason,
            content_snapshot=paper.content,
            metadata_snapshot={
                "title": paper.title,
                "authors": paper.authors,
                "risk_score": paper.risk_score
            }
        )

        self.db.add(version)

        # Update paper version number
        paper.version = new_version_number

        self.db.commit()

        return version.id

    def _calculate_changes(self, old_content: str, new_content: str) -> Dict[str, Any]:
        """Calculate diff between versions"""

        if not old_content:
            return {"type": "initial", "lines_added": len(new_content.splitlines())}

        old_lines = old_content.splitlines()
        new_lines = new_content.splitlines()

        differ = difflib.unified_diff(old_lines, new_lines, lineterm='')

        changes = {
            "additions": 0,
            "deletions": 0,
            "modifications": [],
            "hunks": []
        }

        current_hunk = None
        for line in differ:
            if line.startswith('+++') or line.startswith('---'):
                continue
            elif line.startswith('@@'):
                if current_hunk:
                    changes["hunks"].append(current_hunk)
                current_hunk = {"header": line, "lines": []}
            elif line.startswith('+'):
                changes["additions"] += 1
                if current_hunk:
                    current_hunk["lines"].append(line)
            elif line.startswith('-'):
                changes["deletions"] += 1
                if current_hunk:
                    current_hunk["lines"].append(line)
            elif current_hunk:
                current_hunk["lines"].append(line)

        if current_hunk:
            changes["hunks"].append(current_hunk)

        return changes

    def get_version_history(self, paper_id: str) -> List[Dict[str, Any]]:
        """Get version history for a paper"""

        versions = self.db.query(PaperVersion).filter_by(
            paper_id=paper_id
        ).order_by(PaperVersion.version_number.desc()).all()

        return [
            {
                "id": v.id,
                "version": v.version_number,
                "changed_by": {
                    "id": v.editor.id,
                    "name": v.editor.name
                } if v.editor else None,
                "changed_at": v.changed_at.isoformat(),
                "reason": v.change_reason,
                "changes": v.changes
            }
            for v in versions
        ]

    def compare_versions(self, version1_id: str, version2_id: str) -> Dict[str, Any]:
        """Compare two versions"""

        v1 = self.db.query(PaperVersion).get(version1_id)
        v2 = self.db.query(PaperVersion).get(version2_id)

        if not v1 or not v2:
            raise ValueError("Version not found")

        changes = self._calculate_changes(v1.content_snapshot, v2.content_snapshot)

        return {
            "version1": {
                "id": v1.id,
                "number": v1.version_number,
                "date": v1.changed_at.isoformat()
            },
            "version2": {
                "id": v2.id,
                "number": v2.version_number,
                "date": v2.changed_at.isoformat()
            },
            "changes": changes
        }

    def restore_version(self, paper_id: str, version_id: str,
                       restored_by: str) -> bool:
        """Restore a previous version"""

        version = self.db.query(PaperVersion).get(version_id)
        paper = self.db.query(Paper).get(paper_id)

        if not version or not paper:
            return False

        # Create new version for the restore action
        self.create_version(paper_id, restored_by, f"Restored to version {version.version_number}")

        # Restore content
        paper.content = version.content_snapshot
        paper.title = version.metadata_snapshot.get("title", paper.title)
        paper.authors = version.metadata_snapshot.get("authors", paper.authors)

        self.db.commit()

        return True

# ============= CONSENSUS MANAGER =============

class ConsensusManager:
    """Manages reviewer consensus mechanisms"""

    def __init__(self, db_session):
        self.db = db_session

    def calculate_weighted_consensus(self, reviews: List[Review]) -> Dict[str, Any]:
        """Calculate weighted consensus based on reviewer confidence"""

        if not reviews:
            return {"consensus": 0, "confidence": 0}

        # Weight by confidence scores
        weighted_risks = []
        total_weight = 0

        for review in reviews:
            weight = review.confidence_score or 0.5
            weighted_risks.append(review.risk_assessment * weight)
            total_weight += weight

        if total_weight == 0:
            return {"consensus": 0, "confidence": 0}

        # Calculate weighted average
        weighted_avg = sum(weighted_risks) / total_weight

        # Calculate agreement level
        deviations = [
            abs(review.risk_assessment - weighted_avg) * (review.confidence_score or 0.5)
            for review in reviews
        ]

        max_deviation = 1.0  # Maximum possible deviation
        avg_deviation = sum(deviations) / len(deviations)
        agreement = 1 - (avg_deviation / max_deviation)

        return {
            "consensus_risk": weighted_avg,
            "agreement_level": agreement,
            "confidence": total_weight / len(reviews),
            "num_reviews": len(reviews)
        }

    def identify_outliers(self, reviews: List[Review]) -> List[Dict[str, Any]]:
        """Identify outlier reviews"""

        if len(reviews) < 3:
            return []

        risk_scores = [r.risk_assessment for r in reviews if r.risk_assessment is not None]

        if not risk_scores:
            return []

        mean = sum(risk_scores) / len(risk_scores)
        std_dev = (sum((x - mean) ** 2 for x in risk_scores) / len(risk_scores)) ** 0.5

        outliers = []
        for review in reviews:
            if review.risk_assessment is None:
                continue

            z_score = (review.risk_assessment - mean) / (std_dev or 1)

            if abs(z_score) > 2:  # More than 2 standard deviations
                outliers.append({
                    "review_id": review.id,
                    "reviewer": review.reviewer.name,
                    "risk_assessment": review.risk_assessment,
                    "z_score": z_score,
                    "deviation": review.risk_assessment - mean
                })

        return outliers

    def vote_on_review(self, review_id: str, voter_id: str,
                      vote: str, confidence: float = None,
                      comment: str = None) -> str:
        """Cast a vote on another reviewer's assessment"""

        # Check if vote already exists
        existing = self.db.query(ReviewVote).filter_by(
            review_id=review_id,
            voter_id=voter_id
        ).first()

        if existing:
            existing.vote = vote
            existing.confidence = confidence
            existing.comment = comment
            existing.voted_at = datetime.utcnow()
        else:
            new_vote = ReviewVote(
                review_id=review_id,
                voter_id=voter_id,
                vote=vote,
                confidence=confidence,
                comment=comment
            )
            self.db.add(new_vote)

        self.db.commit()

        return existing.id if existing else new_vote.id

    def get_review_votes(self, review_id: str) -> Dict[str, Any]:
        """Get voting results for a review"""

        votes = self.db.query(ReviewVote).filter_by(review_id=review_id).all()

        vote_counts = defaultdict(int)
        for vote in votes:
            vote_counts[vote.vote] += 1

        return {
            "total_votes": len(votes),
            "vote_distribution": dict(vote_counts),
            "agreement_rate": vote_counts.get("agree", 0) / len(votes) if votes else 0,
            "votes": [
                {
                    "voter": vote.voter.name,
                    "vote": vote.vote,
                    "confidence": vote.confidence,
                    "comment": vote.comment
                }
                for vote in votes
            ]
        }

# ============= FASTAPI APPLICATION =============

app = FastAPI(title="Collaboration API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
engine = create_engine("postgresql://user:password@localhost/collaboration_db")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize managers
workflow_manager = None
collaboration_manager = None
version_manager = None
consensus_manager = None

@app.on_event("startup")
async def startup():
    global workflow_manager, collaboration_manager, version_manager, consensus_manager
    db = SessionLocal()
    workflow_manager = WorkflowManager(db)
    collaboration_manager = CollaborationManager(db)
    version_manager = VersionControlManager(db)
    consensus_manager = ConsensusManager(db)

# ============= API ENDPOINTS =============

@app.post("/api/workflows")
async def create_workflow(paper_id: str, settings: Dict[str, Any]):
    """Create a new review workflow"""
    workflow_id = await workflow_manager.create_workflow(paper_id, settings)
    return {"workflow_id": workflow_id}

@app.post("/api/workflows/{workflow_id}/assign")
async def assign_reviewer(workflow_id: str, reviewer_id: str, role: str = "reviewer"):
    """Assign a reviewer to a workflow"""
    assignment_id = await workflow_manager.assign_reviewer(
        workflow_id, reviewer_id, ReviewerRole(role)
    )
    return {"assignment_id": assignment_id}

@app.post("/api/reviews/submit")
async def submit_review(assignment_id: str, review_data: Dict[str, Any]):
    """Submit a review"""
    review_id = await workflow_manager.submit_review(assignment_id, review_data)
    return {"review_id": review_id}

@app.post("/api/comments")
async def add_comment(paper_id: str, user_id: str, comment_data: Dict[str, Any]):
    """Add a comment"""
    comment_id = await collaboration_manager.add_comment(paper_id, user_id, comment_data)
    return {"comment_id": comment_id}

@app.get("/api/papers/{paper_id}/comments")
async def get_comments(paper_id: str):
    """Get comments for a paper"""
    comments = collaboration_manager.get_comments_thread(paper_id)
    return {"comments": comments}

@app.post("/api/annotations")
async def add_annotation(paper_id: str, user_id: str, annotation_data: Dict[str, Any]):
    """Add an annotation"""
    annotation_id = await collaboration_manager.add_annotation(paper_id, user_id, annotation_data)
    return {"annotation_id": annotation_id}

@app.get("/api/papers/{paper_id}/annotations")
async def get_annotations(paper_id: str, page: int = None):
    """Get annotations for a paper"""
    annotations = collaboration_manager.get_annotations(paper_id, page)
    return {"annotations": annotations}

@app.post("/api/papers/{paper_id}/versions")
async def create_version(paper_id: str, user_id: str, reason: str = None):
    """Create a new version"""
    version_id = version_manager.create_version(paper_id, user_id, reason)
    return {"version_id": version_id}

@app.get("/api/papers/{paper_id}/history")
async def get_version_history(paper_id: str):
    """Get version history"""
    history = version_manager.get_version_history(paper_id)
    return {"history": history}

@app.websocket("/ws/{paper_id}")
async def websocket_endpoint(websocket: WebSocket, paper_id: str):
    """WebSocket endpoint for real-time collaboration"""
    await websocket.accept()

    # Add to active connections
    collaboration_manager.websocket_connections[paper_id].add(websocket)

    try:
        while True:
            data = await websocket.receive_json()

            # Handle different message types
            if data["type"] == "cursor_position":
                # Broadcast cursor position to other users
                await collaboration_manager._broadcast_to_paper_users(paper_id, data)
            elif data["type"] == "selection":
                # Broadcast text selection
                await collaboration_manager._broadcast_to_paper_users(paper_id, data)
            elif data["type"] == "typing":
                # Broadcast typing indicator
                await collaboration_manager._broadcast_to_paper_users(paper_id, data)

    except WebSocketDisconnect:
        collaboration_manager.websocket_connections[paper_id].remove(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
