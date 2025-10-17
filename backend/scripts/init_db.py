#!/usr/bin/env python3
"""Initialize database schema and create initial data"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """Initialize database with schema and initial data"""
    
    # Import models to register them
    try:
        from main import Base, engine
        
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("✓ Database tables created successfully")
        
        # Create session
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Add any initial data here
        logger.info("✓ Database initialization complete")
        
        db.close()
        
    except Exception as e:
        logger.error(f"✗ Database initialization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    init_database()
