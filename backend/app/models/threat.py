from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from .database import Base


class IndicatorType(str, enum.Enum):
    HASH = "hash"
    DOMAIN = "domain"
    IP = "ip"
    URL = "url"
    EMAIL = "email"
    CERTIFICATE = "certificate"
    PACKAGE_NAME = "package_name"
    API_KEY = "api_key"
    CRYPTO_ADDRESS = "crypto_address"
    FILE_PATH = "file_path"
    REGISTRY_KEY = "registry_key"
    BEHAVIORAL = "behavioral"


class ThreatType(str, enum.Enum):
    MALWARE = "malware"
    PHISHING = "phishing"
    SPYWARE = "spyware"
    ADWARE = "adware"
    TROJAN = "trojan"
    RANSOMWARE = "ransomware"
    BACKDOOR = "backdoor"
    ROOTKIT = "rootkit"
    WORM = "worm"
    BOTNET = "botnet"
    CRYPTOMINER = "cryptominer"
    CLONE_APP = "clone_app"
    FAKE_APP = "fake_app"
    DATA_THEFT = "data_theft"
    PRIVACY_VIOLATION = "privacy_violation"


class ThreatSource(str, enum.Enum):
    VIRUSTOTAL = "virustotal"
    ABUSEIPDB = "abuseipdb"
    SHODAN = "shodan"
    MISP = "misp"
    ALIENVAULT = "alienvault"
    EMERGING_THREATS = "emerging_threats"
    INTERNAL = "internal"
    COMMUNITY = "community"
    CUSTOM = "custom"


class ThreatIndicator(Base):
    """Threat indicators (IOCs) from various sources."""
    __tablename__ = "threat_indicators"

    id = Column(Integer, primary_key=True, index=True)
    indicator_type = Column(Enum(IndicatorType), nullable=False, index=True)
    indicator_value = Column(String(1024), nullable=False, index=True)
    threat_type = Column(Enum(ThreatType), nullable=False)
    source = Column(Enum(ThreatSource), nullable=False)
    
    # Threat details
    malware_family = Column(String(100))
    campaign_name = Column(String(200))
    description = Column(Text)
    tags = Column(JSON, default=list)
    
    # Severity
    severity = Column(String(20), default="medium")
    confidence = Column(Float, default=0.5)
    
    # First/last seen
    first_seen = Column(DateTime)
    last_seen = Column(DateTime)
    expiry_date = Column(DateTime)  # Auto-expire old indicators
    
    # Source references
    source_url = Column(String(512))
    source_id = Column(String(255))
    source_references = Column(JSON, default=list)
    
    # Statistics
    hit_count = Column(Integer, default=0)
    false_positive_count = Column(Integer, default=0)
    
    # Additional context
    context = Column(JSON, default=dict)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        {"sqlite_autoincrement": True},
    )


class MalwareFamily(Base):
    """Known malware families and their characteristics."""
    __tablename__ = "malware_families"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    aliases = Column(JSON, default=list)
    category = Column(String(50))
    description = Column(Text)
    
    # Characteristics
    tactics = Column(JSON, default=list)  # MITRE ATT&CK tactics
    techniques = Column(JSON, default=list)  # MITRE ATT&CK techniques
    indicators = Column(JSON, default=dict)
    
    # Detection signatures
    yara_rules = Column(JSON, default=list)
    signature_patterns = Column(JSON, default=list)
    behavioral_signatures = Column(JSON, default=list)
    
    # Metadata
    first_seen = Column(DateTime)
    last_seen = Column(DateTime)
    is_active = Column(Boolean, default=True)
    
    # Statistics
    sample_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class PhishingSignature(Base):
    """Phishing detection signatures and patterns."""
    __tablename__ = "phishing_signatures"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    target_brand = Column(String(100))
    
    # Detection patterns
    url_patterns = Column(JSON, default=list)
    domain_patterns = Column(JSON, default=list)
    text_patterns = Column(JSON, default=list)
    visual_similarity_threshold = Column(Float, default=0.85)
    
    # Brand detection
    brand_keywords = Column(JSON, default=list)
    brand_colors = Column(JSON, default=list)
    brand_logos = Column(JSON, default=list)  # perceptual hashes
    
    # NLP patterns
    phishing_keywords = Column(JSON, default=list)
    urgency_phrases = Column(JSON, default=list)
    credential_phrases = Column(JSON, default=list)
    
    # Regex patterns
    credential_form_patterns = Column(JSON, default=list)
    suspicious_url_patterns = Column(JSON, default=list)
    
    # Confidence and metadata
    confidence = Column(Float, default=0.7)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class ThreatIntelligenceFeed(Base):
    """Configuration for threat intelligence feeds."""
    __tablename__ = "threat_intel_feeds"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    source = Column(Enum(ThreatSource), nullable=False)
    feed_type = Column(String(50))  # "ioc", "blacklist", "whitelist", "yara"
    
    # Configuration
    url = Column(String(512))
    api_key = Column(String(255))
    format = Column(String(20))  # "json", "csv", "stix", "misp"
    
    # Schedule
    update_interval = Column(Integer, default=3600)  # seconds
    last_updated = Column(DateTime)
    next_update = Column(DateTime)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_healthy = Column(Boolean, default=True)
    error_count = Column(Integer, default=0)
    last_error = Column(Text)
    
    # Statistics
    indicators_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
