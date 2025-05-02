"""
G3r4ki Database Models

This module defines SQLAlchemy models for the G3r4ki framework database.
"""

import os
import sys
import json
import uuid
import datetime
from typing import Dict, List, Any, Optional, Union
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, LargeBinary, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Operation(Base):
    """An offensive security operation."""
    
    __tablename__ = 'operations'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    start_time = Column(DateTime, default=datetime.datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    status = Column(String(50), default='created')  # created, running, completed, failed
    operator = Column(String(255), nullable=True)
    operation_type = Column(String(100), nullable=False)  # rat, keylogger, c2, etc.
    target_scope = Column(Text, nullable=True)  # JSON-encoded scope information
    notes = Column(Text, nullable=True)
    
    # Relationships
    agents = relationship("Agent", back_populates="operation")
    activities = relationship("Activity", back_populates="operation")
    
    def __repr__(self):
        return f"<Operation {self.name} ({self.status})>"

class Agent(Base):
    """A deployed agent or implant."""
    
    __tablename__ = 'agents'
    
    id = Column(Integer, primary_key=True)
    agent_id = Column(String(255), unique=True, nullable=False)  # UUID or assigned ID
    operation_id = Column(Integer, ForeignKey('operations.id'))
    name = Column(String(255), nullable=True)
    platform = Column(String(100), nullable=False)  # windows, linux, macos, android, ios
    agent_type = Column(String(100), nullable=False)  # rat, keylogger, c2_client, etc.
    ip_address = Column(String(100), nullable=True)
    hostname = Column(String(255), nullable=True)
    username = Column(String(255), nullable=True)
    check_in_time = Column(DateTime, nullable=True)
    last_active = Column(DateTime, nullable=True)
    status = Column(String(50), default='created')  # created, deployed, active, inactive, compromised
    capabilities = Column(Text, nullable=True)  # JSON-encoded capabilities
    configuration = Column(Text, nullable=True)  # JSON-encoded configuration
    
    # Relationships
    operation = relationship("Operation", back_populates="agents")
    activities = relationship("Activity", back_populates="agent")
    files = relationship("File", back_populates="agent")
    
    def __repr__(self):
        return f"<Agent {self.agent_id} ({self.platform}/{self.agent_type})>"

class Activity(Base):
    """An activity or event from an agent."""
    
    __tablename__ = 'activities'
    
    id = Column(Integer, primary_key=True)
    operation_id = Column(Integer, ForeignKey('operations.id'))
    agent_id = Column(Integer, ForeignKey('agents.id'), nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    activity_type = Column(String(100), nullable=False)  # command, file_upload, screenshot, keylog, etc.
    command = Column(Text, nullable=True)
    output = Column(Text, nullable=True)
    status = Column(String(50), default='success')  # success, failed, error
    meta_data = Column(Text, nullable=True)  # JSON-encoded metadata
    
    # Relationships
    operation = relationship("Operation", back_populates="activities")
    agent = relationship("Agent", back_populates="activities")
    
    def __repr__(self):
        return f"<Activity {self.activity_type} ({self.timestamp})>"

class File(Base):
    """A file uploaded from or downloaded to an agent."""
    
    __tablename__ = 'files'
    
    id = Column(Integer, primary_key=True)
    agent_id = Column(Integer, ForeignKey('agents.id'), nullable=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=True)
    file_type = Column(String(100), nullable=True)  # keylog, screenshot, download, upload, etc.
    file_size = Column(Integer, nullable=True)
    content_type = Column(String(255), nullable=True)
    upload_time = Column(DateTime, default=datetime.datetime.utcnow)
    md5_hash = Column(String(32), nullable=True)
    sha256_hash = Column(String(64), nullable=True)
    stored_path = Column(String(512), nullable=True)  # Where the file is stored on disk
    meta_data = Column(Text, nullable=True)  # JSON-encoded metadata
    
    # For small files, can store directly in DB
    content_small = Column(LargeBinary, nullable=True)
    
    # Relationships
    agent = relationship("Agent", back_populates="files")
    
    def __repr__(self):
        return f"<File {self.filename} ({self.file_type})>"

class C2Server(Base):
    """A Command and Control server configuration."""
    
    __tablename__ = 'c2_servers'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    server_type = Column(String(100), nullable=False)  # internal, covenant, mythic, etc.
    host = Column(String(255), nullable=False)
    port = Column(Integer, nullable=False)
    use_ssl = Column(Boolean, default=True)
    auth_token = Column(String(512), nullable=True)
    api_key = Column(String(512), nullable=True)
    username = Column(String(255), nullable=True)
    password = Column(String(255), nullable=True)
    status = Column(String(50), default='configured')  # configured, running, stopped, error
    last_start_time = Column(DateTime, nullable=True)
    last_stop_time = Column(DateTime, nullable=True)
    configuration = Column(Text, nullable=True)  # JSON-encoded configuration
    
    def __repr__(self):
        return f"<C2Server {self.name} ({self.server_type})>"

class Credential(Base):
    """A credential harvested during operations."""
    
    __tablename__ = 'credentials'
    
    id = Column(Integer, primary_key=True)
    operation_id = Column(Integer, ForeignKey('operations.id'))
    agent_id = Column(Integer, ForeignKey('agents.id'), nullable=True)
    username = Column(String(255), nullable=True)
    password = Column(String(512), nullable=True)
    credential_type = Column(String(100), nullable=False)  # password, hash, token, cookie, etc.
    source = Column(String(255), nullable=True)  # browser, memory, keylogger, etc.
    host = Column(String(255), nullable=True)
    service = Column(String(255), nullable=True)
    collect_time = Column(DateTime, default=datetime.datetime.utcnow)
    meta_data = Column(Text, nullable=True)  # JSON-encoded metadata
    notes = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<Credential {self.credential_type} ({self.username})>"

class Configuration(Base):
    """Application and module configuration."""
    
    __tablename__ = 'configurations'
    
    id = Column(Integer, primary_key=True)
    config_name = Column(String(255), nullable=False, unique=True)
    config_section = Column(String(255), nullable=False)  # app, offensive, rat, keylogger, c2, etc.
    config_data = Column(JSON, nullable=False)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    def __repr__(self):
        return f"<Configuration {self.config_section}.{self.config_name}>"