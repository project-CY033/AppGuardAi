from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from .database import Base


class AppCategory(str, enum.Enum):
    COMMUNICATION = "communication"
    SOCIAL = "social"
    FINANCE = "finance"
    GAMING = "gaming"
    UTILITY = "utility"
    PRODUCTIVITY = "productivity"
    ENTERTAINMENT = "entertainment"
    EDUCATION = "education"
    HEALTH = "health"
    WEATHER = "weather"
    NEWS = "news"
    SHOPPING = "shopping"
    TRAVEL = "travel"
    PHOTOGRAPHY = "photography"
    MUSIC = "music"
    OTHER = "other"


class AppPlatform(str, enum.Enum):
    ANDROID = "android"
    IOS = "ios"
    WINDOWS = "windows"
    MACOS = "macos"
    LINUX = "linux"
    WEB = "web"


class AppTrustLevel(str, enum.Enum):
    VERIFIED = "verified"
    TRUSTED = "trusted"
    UNKNOWN = "unknown"
    SUSPICIOUS = "suspicious"
    MALICIOUS = "malicious"


class App(Base):
    """Represents an application being analyzed or monitored."""
    __tablename__ = "apps"

    id = Column(Integer, primary_key=True, index=True)
    package_name = Column(String(255), index=True, nullable=False)
    app_name = Column(String(255), nullable=False)
    version_name = Column(String(100))
    version_code = Column(Integer)
    platform = Column(Enum(AppPlatform), default=AppPlatform.ANDROID)
    category = Column(Enum(AppCategory), default=AppCategory.OTHER)
    
    # Developer info
    developer_name = Column(String(255))
    developer_email = Column(String(255))
    developer_website = Column(String(512))
    developer_address = Column(Text)
    
    # App metadata
    min_sdk_version = Column(Integer)
    target_sdk_version = Column(Integer)
    app_size = Column(Integer)  # bytes
    icon_hash = Column(String(64))  # perceptual hash
    icon_url = Column(String(512))
    description = Column(Text)
    
    # Store info
    store_url = Column(String(512))
    store_rating = Column(Float)
    store_downloads = Column(String(100))
    first_seen = Column(DateTime, default=func.now())
    last_updated = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Security assessment
    trust_level = Column(Enum(AppTrustLevel), default=AppTrustLevel.UNKNOWN)
    overall_risk_score = Column(Float, default=0.0)
    is_clone = Column(Boolean, default=False)
    clone_of_id = Column(Integer, ForeignKey("apps.id"), nullable=True)
    is_phishing = Column(Boolean, default=False)
    is_malware = Column(Boolean, default=False)
    malware_family = Column(String(100))
    
    # Fingerprinting
    code_signature_hash = Column(String(128))
    certificate_fingerprint = Column(String(128))
    dex_hash = Column(String(64))
    native_lib_hashes = Column(JSON, default=list)
    
    # Analysis flags
    has_hidden_permissions = Column(Boolean, default=False)
    has_dynamic_code_loading = Column(Boolean, default=False)
    has_native_code = Column(Boolean, default=False)
    uses_reflection = Column(Boolean, default=False)
    is_obfuscated = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    versions = relationship("AppVersion", back_populates="app", cascade="all, delete-orphan")
    signatures = relationship("AppSignature", back_populates="app", cascade="all, delete-orphan")
    scan_results = relationship("ScanResult", back_populates="app", cascade="all, delete-orphan")
    permissions = relationship("PermissionAnalysis", back_populates="app", cascade="all, delete-orphan")
    api_calls = relationship("APICall", back_populates="app", cascade="all, delete-orphan")
    incidents = relationship("Incident", back_populates="app", cascade="all, delete-orphan")
    
    # Clone relationship
    clone_parent = relationship("App", remote_side=[id], backref="clones")


class AppVersion(Base):
    """Tracks different versions of an app."""
    __tablename__ = "app_versions"

    id = Column(Integer, primary_key=True, index=True)
    app_id = Column(Integer, ForeignKey("apps.id"), nullable=False)
    version_name = Column(String(100), nullable=False)
    version_code = Column(Integer)
    apk_hash = Column(String(64))
    apk_size = Column(Integer)
    release_date = Column(DateTime)
    changelog = Column(Text)
    
    # Version-specific analysis
    permissions_added = Column(JSON, default=list)
    permissions_removed = Column(JSON, default=list)
    risk_score = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=func.now())
    
    app = relationship("App", back_populates="versions")


class AppSignature(Base):
    """Digital signatures and certificates for apps."""
    __tablename__ = "app_signatures"

    id = Column(Integer, primary_key=True, index=True)
    app_id = Column(Integer, ForeignKey("apps.id"), nullable=False)
    certificate_dn = Column(String(512))
    certificate_issuer = Column(String(512))
    certificate_serial = Column(String(128))
    certificate_not_before = Column(DateTime)
    certificate_not_after = Column(DateTime)
    signature_algorithm = Column(String(100))
    is_self_signed = Column(Boolean, default=False)
    is_debuggable = Column(Boolean, default=False)
    is_signed_v1 = Column(Boolean, default=False)
    is_signed_v2 = Column(Boolean, default=False)
    is_signed_v3 = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=func.now())
    
    app = relationship("App", back_populates="signatures")
