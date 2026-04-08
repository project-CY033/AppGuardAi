from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from .database import Base


class ScanStatus(str, enum.Enum):
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ScanType(str, enum.Enum):
    FULL = "full"
    STATIC = "static"
    DYNAMIC = "dynamic"
    PERMISSION = "permission"
    CLONE = "clone"
    MALWARE = "malware"
    PHISHING = "phishing"
    NETWORK = "network"
    QUICK = "quick"


class ThreatLevel(str, enum.Enum):
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ScanJob(Base):
    """Represents a scan job in the queue."""
    __tablename__ = "scan_jobs"

    id = Column(String(36), primary_key=True)  # UUID
    app_id = Column(Integer, ForeignKey("apps.id"), nullable=False)
    scan_type = Column(Enum(ScanType), default=ScanType.FULL)
    status = Column(Enum(ScanStatus), default=ScanStatus.PENDING)
    priority = Column(Integer, default=5)  # 1=highest, 10=lowest
    
    # Progress tracking
    progress = Column(Float, default=0.0)
    current_stage = Column(String(100))
    stages_completed = Column(JSON, default=list)
    stages_total = Column(Integer, default=8)
    
    # Configuration
    config = Column(JSON, default=dict)
    enabled_analyzers = Column(JSON, default=list)
    
    # Results summary
    threat_level = Column(Enum(ThreatLevel))
    risk_score = Column(Float)
    findings_count = Column(Integer, default=0)
    critical_findings = Column(Integer, default=0)
    high_findings = Column(Integer, default=0)
    medium_findings = Column(Integer, default=0)
    low_findings = Column(Integer, default=0)
    
    # Timing
    queued_at = Column(DateTime)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    duration_seconds = Column(Float)
    
    # Worker info
    worker_id = Column(String(100))
    error_message = Column(Text)
    
    # Metadata
    created_by = Column(String(100))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    results = relationship("ScanResult", back_populates="scan_job", cascade="all, delete-orphan")


class ScanResult(Base):
    """Individual findings from a scan."""
    __tablename__ = "scan_results"

    id = Column(Integer, primary_key=True, index=True)
    scan_job_id = Column(String(36), ForeignKey("scan_jobs.id"), nullable=False)
    app_id = Column(Integer, ForeignKey("apps.id"), nullable=False)
    
    # Finding details
    category = Column(String(100), nullable=False)  # e.g., "permission", "code", "network", "behavior"
    subcategory = Column(String(100))
    title = Column(String(255), nullable=False)
    description = Column(Text)
    severity = Column(Enum(ThreatLevel), nullable=False)
    confidence = Column(Float, default=0.0)  # 0.0 - 1.0
    
    # Location
    file_path = Column(String(512))
    line_number = Column(Integer)
    code_snippet = Column(Text)
    
    # Evidence
    evidence = Column(JSON, default=dict)
    ioc_type = Column(String(50))  # Indicator of Compromise type
    ioc_value = Column(String(512))
    
    # ML/Detection details
    detection_method = Column(String(100))  # "heuristic", "ml", "signature", "behavioral"
    model_version = Column(String(50))
    feature_importance = Column(JSON, default=dict)
    
    # Remediation
    remediation = Column(Text)
    references = Column(JSON, default=list)
    cve_ids = Column(JSON, default=list)
    cwe_ids = Column(JSON, default=list)
    
    # Status
    is_false_positive = Column(Boolean, default=False)
    reviewed_by = Column(String(100))
    reviewed_at = Column(DateTime)
    review_notes = Column(Text)
    
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    scan_job = relationship("ScanJob", back_populates="results")
    app = relationship("App", back_populates="scan_results")


class PermissionAnalysis(Base):
    """Detailed permission analysis for an app."""
    __tablename__ = "permission_analyses"

    id = Column(Integer, primary_key=True, index=True)
    app_id = Column(Integer, ForeignKey("apps.id"), nullable=False)
    scan_job_id = Column(String(36), ForeignKey("scan_jobs.id"))
    
    # Permission lists
    declared_permissions = Column(JSON, default=list)
    requested_permissions = Column(JSON, default=list)
    used_permissions = Column(JSON, default=list)
    hidden_permissions = Column(JSON, default=list)
    dangerous_permissions = Column(JSON, default=list)
    protection_level_permissions = Column(JSON, default=dict)
    
    # Analysis results
    permission_risk_score = Column(Float, default=0.0)
    permission_anomalies = Column(JSON, default=list)
    permission_recommendations = Column(JSON, default=list)
    
    # Category baseline comparison
    category = Column(String(100))
    category_permission_baseline = Column(JSON, default=dict)
    permission_deviation_score = Column(Float, default=0.0)
    excess_permissions = Column(JSON, default=list)
    missing_permissions = Column(JSON, default=list)
    
    # Hidden/stealth detection
    dynamic_permissions = Column(JSON, default=list)
    reflection_accessed_permissions = Column(JSON, default=list)
    native_permissions = Column(JSON, default=list)
    
    # Z-score analysis
    permission_z_scores = Column(JSON, default=dict)
    suspicious_permission_groups = Column(JSON, default=list)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    app = relationship("App", back_populates="permissions")


class CloneDetection(Base):
    """Clone detection results and analysis."""
    __tablename__ = "clone_detections"

    id = Column(Integer, primary_key=True, index=True)
    app_id = Column(Integer, ForeignKey("apps.id"), nullable=False)
    original_app_id = Column(Integer, ForeignKey("apps.id"), nullable=False)
    
    # Similarity scores
    overall_similarity = Column(Float, nullable=False)
    code_similarity = Column(Float)
    icon_similarity = Column(Float)
    permission_similarity = Column(Float)
    api_similarity = Column(Float)
    metadata_similarity = Column(Float)
    
    # Detection methods
    detection_methods = Column(JSON, default=list)
    ast_similarity_score = Column(Float)
    pdg_similarity_score = Column(Float)
    perceptual_hash_distance = Column(Float)
    text_similarity_score = Column(Float)
    
    # Clone characteristics
    clone_type = Column(String(50))  # "exact", "reskin", "repackaged", "api_clone"
    modifications = Column(JSON, default=list)
    added_code = Column(JSON, default=list)
    removed_code = Column(JSON, default=list)
    modified_permissions = Column(JSON, default=list)
    
    # LSH/NN results
    nearest_neighbors = Column(JSON, default=list)
    lsh_bucket = Column(String(100))
    
    confidence = Column(Float, default=0.0)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    app = relationship("App", foreign_keys=[app_id])
    original_app = relationship("App", foreign_keys=[original_app_id])
