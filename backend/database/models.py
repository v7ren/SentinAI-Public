"""
Sentinel AI - SQLAlchemy Models
Database schema for the SAST tool
"""
from datetime import datetime
from typing import List, Optional
from sqlalchemy import (
    create_engine, Column, Integer, String, Float, Boolean, 
    DateTime, Text, ForeignKey, JSON, Index, Table
)
from sqlalchemy.orm import declarative_base, relationship, Session
from sqlalchemy.pool import StaticPool

Base = declarative_base()


class User(Base):
    """User entity - top level organization unit (scan ownership; auth users live in 'users' table in same DB)."""
    __tablename__ = 'scan_users'
    
    id = Column(String(100), primary_key=True)  # user_id from JSON (e.g., user_369G0KT...)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id})>"


class Project(Base):
    """Project entity - belongs to a user"""
    __tablename__ = 'projects'
    
    id = Column(String(50), primary_key=True)  # proj_{timestamp}
    user_id = Column(String(100), ForeignKey('scan_users.id'), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="projects")
    scans = relationship("Scan", back_populates="project", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_project_user_name', 'user_id', 'name'),
    )
    
    def __repr__(self):
        return f"<Project(id={self.id}, name={self.name})>"


class Scan(Base):
    """Scan entity - represents a single security scan of a project"""
    __tablename__ = 'scans'
    
    id = Column(String(100), primary_key=True)  # scan_{user_id}_{timestamp}
    project_id = Column(String(50), ForeignKey('projects.id'), nullable=False, index=True)
    scan_type = Column(String(10), nullable=False)  # "1", "2", "3"
    timestamp = Column(DateTime, nullable=False)
    project_name = Column(String(255))  # Denormalized for convenience
    
    # Full scan result as JSON (preferred); when set, no need to use normalized tables
    result_json = Column(Text, nullable=True)
    # Final DeepWiki doc (markdown) stored in DB so we don't rely on worker files
    deepwiki_doc = Column(Text, nullable=True)
    
    # Statistics (denormalized for listing; also inside result_json)
    files_scanned = Column(Integer, default=0)
    vulnerabilities_count = Column(Integer, default=0)
    elapsed_seconds = Column(Float, default=0.0)
    
    # Relationships (legacy; used only when result_json is null for old rows)
    project = relationship("Project", back_populates="scans")
    vulnerabilities = relationship("Vulnerability", back_populates="scan", cascade="all, delete-orphan")
    project_analysis = relationship("ProjectAnalysis", back_populates="scan", uselist=False, cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_scan_project_timestamp', 'project_id', 'timestamp'),
        Index('idx_scan_type', 'scan_type'),
    )
    
    def __repr__(self):
        return f"<Scan(id={self.id}, type={self.scan_type})>"


class ProjectAnalysis(Base):
    """Project analysis data associated with a scan"""
    __tablename__ = 'project_analyses'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    scan_id = Column(String(100), ForeignKey('scans.id'), nullable=False, unique=True)
    
    # Project info
    project_name = Column(String(255))
    framework = Column(String(100))
    description = Column(Text)
    
    # Security context
    has_authentication = Column(Boolean, default=False)
    has_database = Column(Boolean, default=False)
    
    # Relationships
    scan = relationship("Scan", back_populates="project_analysis")
    external_apis = relationship("ExternalApi", back_populates="project_analysis", cascade="all, delete-orphan")
    top_concerns = relationship("TopConcern", back_populates="project_analysis", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ProjectAnalysis(scan_id={self.scan_id})>"


class ExternalApi(Base):
    """External APIs detected in project analysis"""
    __tablename__ = 'external_apis'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_analysis_id = Column(Integer, ForeignKey('project_analyses.id'), nullable=False, index=True)
    api_name = Column(String(255), nullable=False)
    
    # Relationships
    project_analysis = relationship("ProjectAnalysis", back_populates="external_apis")


class TopConcern(Base):
    """Top security concerns from project analysis"""
    __tablename__ = 'top_concerns'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_analysis_id = Column(Integer, ForeignKey('project_analyses.id'), nullable=False, index=True)
    concern = Column(Text, nullable=False)
    
    # Relationships
    project_analysis = relationship("ProjectAnalysis", back_populates="top_concerns")


class Vulnerability(Base):
    """Vulnerability entity - represents a file with security issues"""
    __tablename__ = 'vulnerabilities'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    scan_id = Column(String(100), ForeignKey('scans.id'), nullable=False, index=True)
    filename = Column(String(500), nullable=False)
    status = Column(String(20), nullable=False, default='VULNERABLE')  # VULNERABLE, SAFE
    source_code = Column(Text)  # Full source code of the file
    
    # Relationships
    scan = relationship("Scan", back_populates="vulnerabilities")
    issues = relationship("Issue", back_populates="vulnerability", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_vuln_scan_filename', 'scan_id', 'filename'),
    )
    
    def __repr__(self):
        return f"<Vulnerability(filename={self.filename}, issues={len(self.issues) if self.issues else 0})>"


class Issue(Base):
    """Security issue/finding entity"""
    __tablename__ = 'issues'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    vulnerability_id = Column(Integer, ForeignKey('vulnerabilities.id'), nullable=False, index=True)
    
    # Core fields
    severity = Column(String(20), nullable=False, index=True)  # HIGH, MEDIUM, LOW, CRITICAL
    type = Column(String(100), nullable=False)  # Code Injection, Path Traversal, etc.
    subtype = Column(String(100))  # More specific classification
    trigger = Column(String(100))  # Function name that triggered
    line = Column(Integer, nullable=False)
    description = Column(Text, nullable=False)
    vulnerable_code = Column(Text)
    
    # Tier 2+ fields
    impact_summary = Column(Text)
    confidence_score = Column(Integer)  # 0-10
    cwe_id = Column(String(20))  # e.g., "CWE-94"
    
    # Tier 3 fields
    remediation = Column(JSON)  # List of remediation steps
    consequences = Column(Text)
    references = Column(JSON)  # List of reference URLs
    fingerprint = Column(String(50), index=True)  # Unique identifier for the issue
    cvss_score = Column(Float)
    fix_complexity = Column(String(20))  # LOW, MEDIUM, HIGH, CRITICAL
    
    # Code context stored as JSON
    code_context_before = Column(JSON)  # Lines before
    code_context_target = Column(Text)  # The vulnerable line
    code_context_after = Column(JSON)  # Lines after
    
    # PoC verbal data stored as JSON
    poc_verbal_vectors = Column(JSON)
    poc_verbal_steps = Column(JSON)
    
    # Relationships
    vulnerability = relationship("Vulnerability", back_populates="issues")
    keywords_detected = relationship("KeywordDetected", back_populates="issue", cascade="all, delete-orphan")
    poc_scripts = relationship("PoCScript", back_populates="issue", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_issue_severity_type', 'severity', 'type'),
        Index('idx_issue_fingerprint', 'fingerprint'),
        Index('idx_issue_vulnerability', 'vulnerability_id'),
    )
    
    def __repr__(self):
        return f"<Issue(type={self.type}, severity={self.severity}, line={self.line})>"


class KeywordDetected(Base):
    """Keywords detected for an issue"""
    __tablename__ = 'keywords_detected'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    issue_id = Column(Integer, ForeignKey('issues.id'), nullable=False, index=True)
    keyword = Column(String(100), nullable=False)
    line = Column(Integer, nullable=False)
    context = Column(Text)
    
    # Relationships
    issue = relationship("Issue", back_populates="keywords_detected")
    
    def __repr__(self):
        return f"<KeywordDetected(keyword={self.keyword}, line={self.line})>"


class PoCScript(Base):
    """Proof of Concept scripts for issues"""
    __tablename__ = 'poc_scripts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    issue_id = Column(Integer, ForeignKey('issues.id'), nullable=False, index=True, unique=True)
    language = Column(String(50))  # python, javascript, etc.
    script = Column(Text, nullable=False)
    exploit_type = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    issue = relationship("Issue", back_populates="poc_scripts")
    
    def __repr__(self):
        return f"<PoCScript(language={self.language})>"


# Database initialization
def init_db(database_url: str = "sqlite:///sentinel.db"):
    """Initialize the database and create all tables"""
    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False} if database_url.startswith("sqlite") else {},
        poolclass=StaticPool if database_url.startswith("sqlite") else None,
        echo=False
    )
    Base.metadata.create_all(engine)
    return engine


def get_session(engine):
    """Get a new database session"""
    return Session(engine)
