"""
Configuration for Rogue Device Detection System
"""
import json
import os

class Config:
    """Application configuration"""
    
    # Network Configuration
    SWITCH_IP = "192.168.200.3"  # After reconfiguring switch to match your network
    SWITCH_USERNAME = "farah"
    SWITCH_PASSWORD = "farah"
    SWITCH_ENABLE_PASSWORD = "farah"  # Enable password for privileged mode
    SWITCH_DEVICE_TYPE = "cisco_ios"
    NETWORK_RANGE = "192.168.200.0/24"
    
    # Web Interface
    WEB_HOST = "0.0.0.0"
    WEB_PORT = 5000
    SECRET_KEY = os.urandom(24)
    
    # Monitoring
    SCAN_INTERVAL_SECONDS = 30  # How often to scan for rogue devices
    
    # Database
    DATABASE_PATH = "rogue_monitor.db"
    
    # Actions
    AUTO_ISOLATE_ROGUES = False  # Automatically shutdown ports with rogue devices (Enable after authorizing legitimate devices!)
    SEND_ALERTS = True
    
    # VLAN Configuration
    QUARANTINE_VLAN = 999        # VLAN for quarantined/rogue devices (isolated network)
    DEFAULT_AUTHORIZED_VLAN = 1  # Default VLAN for authorized devices
    ENABLE_VLAN_QUARANTINE = True  # Use VLAN-based quarantine instead of port shutdown
    AUTO_QUARANTINE_ROGUES = True  # Automatically move all rogue devices to quarantine VLAN
    
    # Email Notifications
    ENABLE_EMAIL_ALERTS = False   # Enable email notifications for rogue device detection
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    SMTP_USE_TLS = True
    SMTP_USERNAME = ""            # Your email address
    SMTP_PASSWORD = ""            # Your email password or app-specific password
    EMAIL_FROM = ""               # Sender email address (usually same as SMTP_USERNAME)
    EMAIL_TO = []                 # List of recipient email addresses
    EMAIL_SUBJECT_PREFIX = "[ROGUE ALERT]"
    
    # Logging
    LOG_FILE = "rogue_detection.log"
    LOG_LEVEL = "INFO"
    
    @classmethod
    def load_from_file(cls, config_file="config.json"):
        """Load configuration from JSON file if it exists"""
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config_data = json.load(f)
                
            # Update class attributes from config file
            for key, value in config_data.items():
                if hasattr(cls, key.upper()):
                    setattr(cls, key.upper(), value)
    
    @classmethod
    def save_to_file(cls, config_file="config.json"):
        """Save current configuration to JSON file"""
        config_data = {
            "switch_ip": cls.SWITCH_IP,
            "switch_username": cls.SWITCH_USERNAME,
            "switch_password": cls.SWITCH_PASSWORD,
            "network_range": cls.NETWORK_RANGE,
            "web_host": cls.WEB_HOST,
            "web_port": cls.WEB_PORT,
            "scan_interval_seconds": cls.SCAN_INTERVAL_SECONDS,
            "auto_isolate_rogues": cls.AUTO_ISOLATE_ROGUES,
            "send_alerts": cls.SEND_ALERTS,
            "enable_email_alerts": cls.ENABLE_EMAIL_ALERTS,
            "smtp_server": cls.SMTP_SERVER,
            "smtp_port": cls.SMTP_PORT,
            "smtp_use_tls": cls.SMTP_USE_TLS,
            "smtp_username": cls.SMTP_USERNAME,
            "smtp_password": cls.SMTP_PASSWORD,
            "email_from": cls.EMAIL_FROM,
            "email_to": cls.EMAIL_TO,
            "email_subject_prefix": cls.EMAIL_SUBJECT_PREFIX
        }
        
        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=2)

