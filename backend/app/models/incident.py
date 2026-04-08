from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from .database import Base


class IncidentStatus(str, enum.Enum):
    NEW = "new"
    INVESTIGATING = "investigating"
    CONFIRMED = "confirmed"
    CONTAINMENT = "containment"
    ERADICATION = "eradication"
    RECOVERY = "recovery"
    CLOSED = "closed"
    FALSE_POSITIVE = "false_positive"


class IncidentSeverity(str, enum.Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IncidentCategory(str, enum.Enum):
    MALWARE_DETECTED = "malware_detected"
    CLONE_APP = "clone_app"
    PHISHING = "phishing"
    DATA_EXFILTRATION = "data_exfiltration"
    PRIVACY_VIOLATION = "privacy_violation"
    SUSPICIOUS_PERMISSION = "suspicious_permission"
    UNUSUAL_NETWORK_ACTIVITY = "unusual_network_activity"
    CERTIFICATE_ISSUE = "certificate_issue"
    CODE_INJECTION = "code_injection"
    ROOT_DETECTION_BYPASS = "root_detection_bypass"
    ANTI_ANALYSIS = "anti_analysis"
    CRYPTOJACKING = "cryptojacking"
    RANSOMWARE = "ransomware"
    BACKDOOR = "backdoor"
    OTHER = "other"


class Incident(Base):
    """Security incidents detected by the platform."""
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(String(36), unique=True, nullable=False)  # UUID
    title = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Classification
    category = Column(Enum(IncidentCategory), nullable=False)
    severity = Column(Enum(IncidentSeverity), nullable=False)
    status = Column(Enum(IncidentStatus), default=IncidentStatus.NEW)
    
    # Related entities
    app_id = Column(Integer, ForeignKey("apps.id"), nullable=True)
    scan_job_id = Column(String(36), nullable=True)
    user_id = Column(Integer, nullable=True)
    
    # Threat intelligence
    threat_type = Column(String(50))
    malware_family = Column(String(100))
    iocs = Column(JSON, default=list)
    mitre_techniques = Column(JSON, default=list)
    
    # Risk assessment
    risk_score = Column(Float, default=0.0)
    impact_score = Column(Float, default=0.0)
    likelihood_score = Column(Float, default=0.0)
    
    # Evidence
    evidence = Column(JSON, default=dict)
    artifacts = Column(JSON, default=list)
    affected_systems = Column(JSON, default=list)
    
    # Response
    assigned_to = Column(String(100))
    playbook_id = Column(Integer, ForeignKey("playbooks.id"), nullable=True)
    automated_actions = Column(JSON, default=list)
    manual_actions = Column(JSON, default=list)
    
    # SLA tracking
    sla_deadline = Column(DateTime)
    sla_breached = Column(Boolean, default=False)
    response_time_minutes = Column(Integer)
    resolution_time_minutes = Column(Integer)
    
    # Resolution
    resolution_summary = Column(Text)
    lessons_learned = Column(Text)
    root_cause = Column(Text)
    
    # Metadata
    source = Column(String(100), default="system")
    tags = Column(JSON, default=list)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    closed_at = Column(DateTime)
    
    # Relationships
    app = relationship("App", back_populates="incidents")
    timeline = relationship("IncidentTimeline", back_populates="incident", cascade="all, delete-orphan")
    playbook = relationship("Playbook")


class IncidentTimeline(Base):
    """Timeline of events for an incident."""
    __tablename__ = "incident_timeline"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    
    event_type = Column(String(50), nullable=False)  # "status_change", "action", "finding", "comment"
    title = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Actor
    actor_type = Column(String(20))  # "system", "user", "automation"
    actor_id = Column(String(100))
    actor_name = Column(String(100))
    
    # Data
    event_data = Column(JSON, default=dict)
    previous_value = Column(String(100))
    new_value = Column(String(100))
    
    created_at = Column(DateTime, default=func.now())
    
    incident = relationship("Incident", back_populates="timeline")


class Playbook(Base):
    """Incident response playbooks."""
    __tablename__ = "playbooks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Trigger conditions
    trigger_category = Column(Enum(IncidentCategory))
    trigger_severity = Column(Enum(IncidentSeverity))
    trigger_conditions = Column(JSON, default=dict)
    
    # Actions
    automated_steps = Column(JSON, default=list)
    manual_steps = Column(JSON, default=list)
    notification_rules = Column(JSON, default=list)
    
    # SLA
    response_sla_hours = Column(Integer)
    resolution_sla_hours = Column(Integer)
    
    # Status
    is_active = Column(Boolean, default=True)
    execution_count = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class SLAPolicy(Base):
    """SLA policies for incident management."""
    __tablename__ = "sla_policies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    
    # Conditions
    severity = Column(Enum(IncidentSeverity), nullable=False)
    category = Column(Enum(IncidentCategory))
    
    # SLA times (in hours)
    response_time = Column(Integer, nullable=False)
    resolution_time = Column(Integer, nullable=False)
    
    # Escalation
    escalation_levels = Column(JSON, default=list)
    notification_recipients = Column(JSON, default=list)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
