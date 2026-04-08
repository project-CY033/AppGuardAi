from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from .database import Base


class APICategory(str, enum.Enum):
    NETWORK = "network"
    FILE = "file"
    DATABASE = "database"
    DEVICE = "device"
    ACCOUNT = "account"
    LOCATION = "location"
    CAMERA = "camera"
    MICROPHONE = "microphone"
    BLUETOOTH = "bluetooth"
    TELEPHONY = "telephony"
    SMS = "sms"
    CONTACTS = "contacts"
    CALENDAR = "calendar"
    SENSORS = "sensors"
    CRYPTO = "crypto"
    REFLECTION = "reflection"
    DYNAMIC_CODE = "dynamic_code"
    SYSTEM = "system"
    OTHER = "other"


class TrafficProtocol(str, enum.Enum):
    HTTP = "http"
    HTTPS = "https"
    FTP = "ftp"
    SMTP = "smtp"
    DNS = "dns"
    TCP = "tcp"
    UDP = "udp"
    WEBSOCKET = "websocket"
    SSL_TLS = "ssl_tls"
    OTHER = "other"


class APICall(Base):
    """API calls made by applications."""
    __tablename__ = "api_calls"

    id = Column(Integer, primary_key=True, index=True)
    app_id = Column(Integer, ForeignKey("apps.id"), nullable=False)
    device_id = Column(String(100))
    
    # API details
    api_name = Column(String(255), nullable=False)
    api_class = Column(String(255))
    api_method = Column(String(255))
    category = Column(Enum(APICategory), nullable=False)
    
    # Call context
    call_stack = Column(JSON, default=list)
    thread_id = Column(String(50))
    process_id = Column(Integer)
    timestamp = Column(DateTime, nullable=False)
    
    # Parameters and return
    parameters = Column(JSON, default=dict)
    return_value = Column(Text)
    return_type = Column(String(100))
    
    # Permission check
    required_permission = Column(String(255))
    has_permission = Column(Boolean, default=True)
    permission_bypass_method = Column(String(100))
    
    # Risk assessment
    is_suspicious = Column(Boolean, default=False)
    suspicion_reason = Column(Text)
    risk_score = Column(Float, default=0.0)
    
    # Patterns
    call_frequency = Column(Integer, default=1)
    calls_per_minute = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=func.now())
    
    app = relationship("App", back_populates="api_calls")


class NetworkTraffic(Base):
    """Network traffic captured from applications."""
    __tablename__ = "network_traffic"

    id = Column(Integer, primary_key=True, index=True)
    app_id = Column(Integer, ForeignKey("apps.id"), nullable=False)
    session_id = Column(String(100))
    
    # Connection details
    protocol = Column(Enum(TrafficProtocol), nullable=False)
    source_ip = Column(String(45))
    source_port = Column(Integer)
    destination_ip = Column(String(45))
    destination_port = Column(Integer)
    destination_host = Column(String(255))
    
    # Request
    method = Column(String(10))  # GET, POST, etc.
    url = Column(Text)
    path = Column(String(1024))
    query_params = Column(JSON, default=dict)
    request_headers = Column(JSON, default=dict)
    request_body = Column(Text)
    request_size = Column(Integer, default=0)
    
    # Response
    response_status = Column(Integer)
    response_headers = Column(JSON, default=dict)
    response_body = Column(Text)
    response_size = Column(Integer, default=0)
    
    # Timing
    timestamp = Column(DateTime, nullable=False)
    duration_ms = Column(Float)
    ttfb_ms = Column(Float)  # Time to first byte
    
    # Analysis
    is_encrypted = Column(Boolean, default=True)
    certificate_info = Column(JSON, default=dict)
    
    # Threat detection
    is_suspicious = Column(Boolean, default=False)
    suspicion_reason = Column(Text)
    risk_score = Column(Float, default=0.0)
    
    # PII detection
    contains_pii = Column(Boolean, default=False)
    pii_types = Column(JSON, default=list)
    pii_redacted_body = Column(Text)
    
    # Geo info
    destination_country = Column(String(10))
    destination_city = Column(String(100))
    destination_asn = Column(String(100))
    destination_org = Column(String(200))
    
    # DNS
    dns_queries = Column(JSON, default=list)
    resolved_ips = Column(JSON, default=list)
    
    created_at = Column(DateTime, default=func.now())
    
    app = relationship("App")


class DeviceHealth(Base):
    """Device health metrics for monitoring."""
    __tablename__ = "device_health"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(100), nullable=False, index=True)
    
    # Device info
    device_model = Column(String(100))
    device_manufacturer = Column(String(100))
    android_version = Column(String(20))
    security_patch_level = Column(String(20))
    os_version = Column(String(50))
    
    # Root/Jailbreak
    is_rooted = Column(Boolean, default=False)
    root_detection_bypass = Column(Boolean, default=False)
    root_management_apps = Column(JSON, default=list)
    
    # Security state
    is_locked = Column(Boolean, default=True)
    encryption_enabled = Column(Boolean, default=False)
    screen_lock_type = Column(String(20))
    security_software_installed = Column(JSON, default=list)
    
    # System integrity
    system_files_modified = Column(JSON, default=list)
    suspicious_processes = Column(JSON, default=list)
    loaded_modules = Column(JSON, default=list)
    
    # Permissions state
    accessibility_services = Column(JSON, default=list)
    device_admin_apps = Column(JSON, default=list)
    overlay_apps = Column(JSON, default=list)
    vpn_apps = Column(JSON, default=list)
    
    # Network state
    active_connections = Column(JSON, default=list)
    vpn_active = Column(Boolean, default=False)
    proxy_configured = Column(Boolean, default=False)
    
    # Battery and performance
    battery_level = Column(Float)
    battery_health = Column(String(20))
    cpu_usage = Column(Float)
    memory_usage = Column(Float)
    storage_usage = Column(Float)
    
    # Risk assessment
    risk_score = Column(Float, default=0.0)
    risk_factors = Column(JSON, default=list)
    
    timestamp = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=func.now())


class MonitoringAlert(Base):
    """Real-time monitoring alerts."""
    __tablename__ = "monitoring_alerts"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(100), index=True)
    app_id = Column(Integer, ForeignKey("apps.id"), nullable=True)
    
    alert_type = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Severity
    severity = Column(String(20), default="medium")
    risk_score = Column(Float, default=0.0)
    
    # Context
    source = Column(String(50))  # "api_monitor", "network_monitor", "permission_monitor", "device_monitor"
    trigger_data = Column(JSON, default=dict)
    
    # Response
    acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(String(100))
    acknowledged_at = Column(DateTime)
    
    action_taken = Column(String(100))
    action_result = Column(Text)
    
    timestamp = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=func.now())
