"""
G3r4ki Database Module

This module provides database connectivity for the G3r4ki framework.
"""

import os
import logging
from typing import Optional
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

# Configure logging
logger = logging.getLogger("g3r4ki.database")

# Database connection
engine = None
Session = None

def init_db(database_url: Optional[str] = None):
    """
    Initialize the database connection.
    
    Args:
        database_url: Optional database URL override (default: use DATABASE_URL environment variable)
    """
    global engine, Session
    
    try:
        # Get database URL from environment or parameter
        db_url = database_url or os.environ.get("DATABASE_URL")
        
        if not db_url:
            logger.error("No DATABASE_URL environment variable found and no database_url provided")
            return False
        
        # Create engine
        engine = create_engine(
            db_url,
            pool_pre_ping=True,
            pool_recycle=300
        )
        
        # Create session factory
        session_factory = sessionmaker(bind=engine)
        Session = scoped_session(session_factory)
        
        logger.info("Database connection initialized")
        return True
    
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        return False

def get_session():
    """
    Get a database session.
    
    Returns:
        SQLAlchemy session object or None if database not initialized
    """
    global Session
    
    if Session is None:
        init_db()
        
        if Session is None:
            logger.error("Database not initialized")
            return None
    
    return Session()

def create_tables():
    """
    Create database tables if they don't exist.
    
    Returns:
        True if successful, False otherwise
    """
    global engine
    
    try:
        if engine is None:
            if not init_db():
                return False
        
        # Import models and create tables
        from .models import Base
        Base.metadata.create_all(engine)
        
        logger.info("Database tables created")
        return True
    
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        return False