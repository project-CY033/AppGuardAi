from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Enum, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from .database import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    ANALYST = "analyst"
    VIEWER = "viewer"
    API = "api"


class User(Base):
    """Platform users."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    full_name = Column(String(200))
    role = Column(Enum(UserRole), default=UserRole.ANALYST)
    org_id = Column(Integer, ForeignKey("organizations.id"))
    
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Preferences
    preferences = Column(JSON, default=dict)
    notification_settings = Column(JSON, default=dict)
    
    # Security
    last_login = Column(DateTime)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime)
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String(100))
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization", back_populates="members")
    api_keys = relationship("APIKey", back_populates="user", cascade="all, delete-orphan")


class Organization(Base):
    """Multi-tenant organizations."""
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    
    # Plan and limits
    plan = Column(String(50), default="free")
    max_users = Column(Integer, default=5)
    max_scans_per_month = Column(Integer, default=100)
    max_apps = Column(Integer, default=50)
    
    # Settings
    settings = Column(JSON, default=dict)
    compliance_profile = Column(String(50))
    
    # Billing
    billing_email = Column(String(255))
    subscription_status = Column(String(20), default="active")
    subscription_expires = Column(DateTime)
    
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    members = relationship("User", back_populates="organization")


class APIKey(Base):
    """API keys for programmatic access."""
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    name = Column(String(100), nullable=False)
    key = Column(String(64), unique=True, nullable=False, index=True)
    prefix = Column(String(8))  # First 8 chars for identification
    
    # Permissions
    scopes = Column(JSON, default=list)
    rate_limit = Column(Integer, default=1000)  # requests per hour
    
    # Usage
    last_used = Column(DateTime)
    usage_count = Column(Integer, default=0)
    
    # Expiry
    expires_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=func.now())
    
    user = relationship("User", back_populates="api_keys")


class AuditLog(Base):
    """Audit log for compliance and security."""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    
    action = Column(String(50), nullable=False)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(String(100))
    
    details = Column(JSON, default=dict)
    
    # Request context
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    
    # Result
    success = Column(Boolean, default=True)
    error_message = Column(Text)
    
    timestamp = Column(DateTime, default=func.now(), index=True)
