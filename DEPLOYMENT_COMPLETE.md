# 🚀 Complete Deployment Guide

**Production-Ready Deployment for Linux, Windows, and Google Cloud**

---

## 📋 Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Linux Deployment](#linux-deployment)
3. [Windows Deployment](#windows-deployment)
4. [Google Cloud Deployment](#google-cloud-deployment)
5. [Docker Deployment](#docker-deployment)
6. [Production Configuration](#production-configuration)
7. [Security Hardening](#security-hardening)
8. [Monitoring & Maintenance](#monitoring--maintenance)
9. [Backup & Recovery](#backup--recovery)
10. [Troubleshooting](#troubleshooting)

---

## Pre-Deployment Checklist

### Requirements Verification

- [ ] **Python 3.8+** installed
- [ ] **Network access** to Cisco switch
- [ ] **SSH enabled** on switch
- [ ] **Switch credentials** (username, password, enable password)
- [ ] **Static IP** for server (recommended)
- [ ] **Firewall rules** configured
- [ ] **SSL certificate** (for HTTPS)
- [ ] **Backup strategy** planned

### Network Requirements

| Requirement | Details |
|-------------|---------|
| **Switch Access** | SSH (TCP 22) |
| **Web Interface** | HTTP (TCP 5000) or HTTPS (TCP 443) |
| **Email** | SMTP (TCP 587/465) |
| **Management** | SSH to server |

### Hardware Recommendations

| Deployment | CPU | RAM | Storage | Network |
|------------|-----|-----|---------|---------|
| **Small** (1 switch, <50 devices) | 1 core | 512 MB | 10 GB | 100 Mbps |
| **Medium** (2-5 switches, <200 devices) | 2 cores | 1 GB | 20 GB | 1 Gbps |
| **Large** (5+ switches, 200+ devices) | 4 cores | 2 GB | 50 GB | 1 Gbps |

---

## Linux Deployment

### Ubuntu 20.04/22.04 LTS (Recommended)

#### Step 1: System Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    sqlite3 \
    nginx \
    supervisor \
    ufw

# Create application user
sudo useradd -m -s /bin/bash roguedetect
sudo usermod -aG sudo roguedetect
```

#### Step 2: Application Setup

```bash
# Switch to application user
sudo su - roguedetect

# Create application directory
mkdir -p /home/roguedetect/rogue_detection_system
cd /home/roguedetect/rogue_detection_system

# Copy application files here
# (upload via SCP, rsync, or git clone)

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

#### Step 3: Configuration

```bash
# Copy example configuration
cp config.json.example config.json

# Edit configuration
nano config.json
```

**Production config.json:**
```json
{
  "switch_ip": "192.168.1.3",
  "switch_username": "roguedetect",
  "switch_password": "STRONG_PASSWORD_HERE",
  "switch_enable_password": "ENABLE_PASSWORD_HERE",
  "switch_port": 22,
  "scan_interval": 30,
  "quarantine_vlan": 999,
  "default_vlan": 1,
  "quarantine_action": "vlan",
  "email_enabled": true,
  "email_smtp_server": "smtp.gmail.com",
  "email_smtp_port": 587,
  "email_username": "alerts@yourdomain.com",
  "email_password": "APP_PASSWORD_HERE",
  "email_recipients": ["admin@yourdomain.com", "security@yourdomain.com"],
  "web_port": 5000,
  "web_host": "127.0.0.1",
  "debug_mode": false,
  "log_level": "INFO"
}
```

**Set secure permissions:**
```bash
chmod 600 config.json
chmod 600 rogue_monitor.db
chmod 750 /home/roguedetect/rogue_detection_system
```

#### Step 4: Systemd Service

```bash
# Create service file
sudo nano /etc/systemd/system/rogue-detection.service
```

**Service configuration:**
```ini
[Unit]
Description=Rogue Detection System
After=network.target

[Service]
Type=simple
User=roguedetect
Group=roguedetect
WorkingDirectory=/home/roguedetect/rogue_detection_system
Environment="PATH=/home/roguedetect/rogue_detection_system/venv/bin"
ExecStart=/home/roguedetect/rogue_detection_system/venv/bin/python3 app.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=rogue-detection

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/home/roguedetect/rogue_detection_system

[Install]
WantedBy=multi-user.target
```

**Enable and start service:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable rogue-detection
sudo systemctl start rogue-detection
sudo systemctl status rogue-detection
```

#### Step 5: Nginx Reverse Proxy (HTTPS)

```bash
# Install Certbot for Let's Encrypt
sudo apt install certbot python3-certbot-nginx -y

# Create Nginx configuration
sudo nano /etc/nginx/sites-available/rogue-detection
```

**Nginx configuration:**
```nginx
# HTTP - Redirect to HTTPS
server {
    listen 80;
    server_name rogue.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS
server {
    listen 443 ssl http2;
    server_name rogue.yourdomain.com;

    # SSL Configuration (will be added by Certbot)
    ssl_certificate /etc/letsencrypt/live/rogue.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/rogue.yourdomain.com/privkey.pem;
    
    # SSL Security
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Logging
    access_log /var/log/nginx/rogue-detection-access.log;
    error_log /var/log/nginx/rogue-detection-error.log;
    
    # Proxy to Flask
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Static files
    location /static {
        alias /home/roguedetect/rogue_detection_system/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

**Enable site and get SSL certificate:**
```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/rogue-detection /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Get SSL certificate
sudo certbot --nginx -d rogue.yourdomain.com

# Auto-renewal (already configured by Certbot)
sudo certbot renew --dry-run
```

#### Step 6: Firewall Configuration

```bash
# Enable UFW
sudo ufw enable

# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow from management network only (optional)
sudo ufw allow from 192.168.1.0/24 to any port 5000

# Check status
sudo ufw status verbose
```

#### Step 7: Logging Setup

```bash
# Create log directory
sudo mkdir -p /var/log/rogue-detection
sudo chown roguedetect:roguedetect /var/log/rogue-detection

# Configure logrotate
sudo nano /etc/logrotate.d/rogue-detection
```

**Logrotate configuration:**
```
/var/log/rogue-detection/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 roguedetect roguedetect
    sharedscripts
    postrotate
        systemctl reload rogue-detection > /dev/null 2>&1 || true
    endscript
}
```

#### Step 8: Verification

```bash
# Check service status
sudo systemctl status rogue-detection

# Check logs
sudo journalctl -u rogue-detection -f

# Check Nginx
sudo systemctl status nginx
sudo nginx -t

# Test application
curl -k https://rogue.yourdomain.com

# Check firewall
sudo ufw status

# Check ports
sudo netstat -tuln | grep -E ':(80|443|5000)'
```

---

## Windows Deployment

### Windows Server 2016/2019/2022

#### Step 1: Install Python

1. Download Python 3.8+ from [python.org](https://www.python.org/downloads/windows/)
2. Run installer:
   - ✅ Check "Add Python to PATH"
   - ✅ Check "Install for all users"
   - Choose "Customize installation"
   - ✅ Check "pip"
   - ✅ Check "py launcher"
   - Install location: `C:\Python3`

3. Verify installation:
```powershell
python --version
pip --version
```

#### Step 2: Application Setup

```powershell
# Create application directory
New-Item -ItemType Directory -Path "C:\RogueDetection"
cd C:\RogueDetection

# Copy application files here

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

#### Step 3: Configuration

```powershell
# Copy example configuration
Copy-Item config.json.example config.json

# Edit configuration
notepad config.json
```

**Set file permissions:**
```powershell
# Right-click config.json → Properties → Security
# Remove "Users" group, keep only Administrators and SYSTEM
```

#### Step 4: Windows Service (using NSSM)

**Download and install NSSM:**
1. Download from [nssm.cc](https://nssm.cc/download)
2. Extract to `C:\nssm`

**Create service:**
```powershell
# Open PowerShell as Administrator
cd C:\nssm\win64

# Install service
.\nssm install RogueDetection "C:\RogueDetection\venv\Scripts\python.exe" "C:\RogueDetection\app.py"

# Configure service
.\nssm set RogueDetection AppDirectory "C:\RogueDetection"
.\nssm set RogueDetection DisplayName "Rogue Detection System"
.\nssm set RogueDetection Description "Network security monitoring and rogue device detection"
.\nssm set RogueDetection Start SERVICE_AUTO_START
.\nssm set RogueDetection AppStdout "C:\RogueDetection\logs\stdout.log"
.\nssm set RogueDetection AppStderr "C:\RogueDetection\logs\stderr.log"
.\nssm set RogueDetection AppRotateFiles 1
.\nssm set RogueDetection AppRotateBytes 1048576

# Start service
.\nssm start RogueDetection

# Check status
.\nssm status RogueDetection
```

#### Step 5: IIS Reverse Proxy (Optional)

**Install IIS and URL Rewrite:**
```powershell
# Install IIS
Install-WindowsFeature -name Web-Server -IncludeManagementTools

# Install URL Rewrite Module
# Download from: https://www.iis.net/downloads/microsoft/url-rewrite

# Install Application Request Routing
# Download from: https://www.iis.net/downloads/microsoft/application-request-routing
```

**Configure reverse proxy:**
1. Open IIS Manager
2. Select server → Application Request Routing Cache → Server Proxy Settings
3. Enable proxy
4. Create new website
5. Add URL Rewrite rule:

```xml
<rewrite>
    <rules>
        <rule name="ReverseProxyInboundRule" stopProcessing="true">
            <match url="(.*)" />
            <action type="Rewrite" url="http://localhost:5000/{R:1}" />
        </rule>
    </rules>
</rewrite>
```

#### Step 6: Windows Firewall

```powershell
# Allow port 5000
New-NetFirewallRule -DisplayName "Rogue Detection" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow

# Allow port 80 (if using IIS)
New-NetFirewallRule -DisplayName "HTTP" -Direction Inbound -LocalPort 80 -Protocol TCP -Action Allow

# Allow port 443 (if using IIS with SSL)
New-NetFirewallRule -DisplayName "HTTPS" -Direction Inbound -LocalPort 443 -Protocol TCP -Action Allow
```

#### Step 7: Scheduled Backup

```powershell
# Create backup script
$BackupScript = @'
$Date = Get-Date -Format "yyyy-MM-dd"
$BackupDir = "C:\RogueDetection\backups\$Date"
New-Item -ItemType Directory -Path $BackupDir -Force
Copy-Item "C:\RogueDetection\rogue_monitor.db" "$BackupDir\rogue_monitor.db"
Copy-Item "C:\RogueDetection\config.json" "$BackupDir\config.json"
# Delete backups older than 30 days
Get-ChildItem "C:\RogueDetection\backups" | Where-Object {$_.CreationTime -lt (Get-Date).AddDays(-30)} | Remove-Item -Recurse
'@

$BackupScript | Out-File "C:\RogueDetection\backup.ps1"

# Create scheduled task
$Action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-File C:\RogueDetection\backup.ps1"
$Trigger = New-ScheduledTaskTrigger -Daily -At 2am
$Principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount
Register-ScheduledTask -TaskName "RogueDetection-Backup" -Action $Action -Trigger $Trigger -Principal $Principal
```

---

## Google Cloud Deployment

### Google Compute Engine

#### Step 1: Create VM Instance

**Using gcloud CLI:**
```bash
# Set project
gcloud config set project YOUR_PROJECT_ID

# Create VM
gcloud compute instances create rogue-detection \
    --zone=us-central1-a \
    --machine-type=e2-small \
    --image-family=ubuntu-2004-lts \
    --image-project=ubuntu-os-cloud \
    --boot-disk-size=20GB \
    --boot-disk-type=pd-standard \
    --tags=http-server,https-server \
    --metadata=startup-script='#!/bin/bash
apt update
apt install -y python3 python3-pip python3-venv git'
```

**Using Console:**
1. Go to Compute Engine → VM instances
2. Click "Create Instance"
3. Configure:
   - Name: `rogue-detection`
   - Region: `us-central1`
   - Zone: `us-central1-a`
   - Machine type: `e2-small` (2 vCPU, 2 GB RAM)
   - Boot disk: Ubuntu 20.04 LTS, 20 GB
   - Firewall: Allow HTTP and HTTPS traffic
4. Click "Create"

#### Step 2: Configure Firewall Rules

```bash
# Allow web traffic
gcloud compute firewall-rules create allow-rogue-detection-web \
    --allow=tcp:5000,tcp:80,tcp:443 \
    --source-ranges=0.0.0.0/0 \
    --target-tags=http-server,https-server \
    --description="Allow web traffic to Rogue Detection System"

# Allow SSH (if not already allowed)
gcloud compute firewall-rules create allow-ssh \
    --allow=tcp:22 \
    --source-ranges=0.0.0.0/0 \
    --description="Allow SSH"
```

#### Step 3: SSH to Instance

```bash
gcloud compute ssh rogue-detection --zone=us-central1-a
```

#### Step 4: Install Application

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3 python3-pip python3-venv git nginx certbot python3-certbot-nginx

# Create application directory
sudo mkdir -p /opt/rogue_detection_system
sudo chown $USER:$USER /opt/rogue_detection_system
cd /opt/rogue_detection_system

# Upload files (from local machine)
# gcloud compute scp --recurse ./rogue_detection_system/* rogue-detection:/opt/rogue_detection_system/ --zone=us-central1-a

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Configure
cp config.json.example config.json
nano config.json
```

#### Step 5: Setup Systemd Service

Follow the same systemd setup as Linux deployment (Step 4 in Linux section).

#### Step 6: Configure Nginx with SSL

```bash
# Get external IP
EXTERNAL_IP=$(gcloud compute instances describe rogue-detection --zone=us-central1-a --format='get(networkInterfaces[0].accessConfigs[0].natIP)')
echo "External IP: $EXTERNAL_IP"

# Point your domain to this IP
# Add A record: rogue.yourdomain.com → $EXTERNAL_IP

# Configure Nginx (same as Linux deployment)
# Get SSL certificate
sudo certbot --nginx -d rogue.yourdomain.com
```

#### Step 7: Setup Cloud Monitoring (Optional)

```bash
# Install monitoring agent
curl -sSO https://dl.google.com/cloudagents/add-google-cloud-ops-agent-repo.sh
sudo bash add-google-cloud-ops-agent-repo.sh --also-install

# Configure monitoring
sudo nano /etc/google-cloud-ops-agent/config.yaml
```

**Monitoring configuration:**
```yaml
logging:
  receivers:
    syslog:
      type: files
      include_paths:
        - /var/log/rogue-detection/*.log
  service:
    pipelines:
      default_pipeline:
        receivers: [syslog]

metrics:
  receivers:
    hostmetrics:
      type: hostmetrics
      collection_interval: 60s
  service:
    pipelines:
      default_pipeline:
        receivers: [hostmetrics]
```

```bash
sudo systemctl restart google-cloud-ops-agent
```

#### Step 8: Setup Cloud SQL (Optional)

For larger deployments, consider using Cloud SQL instead of SQLite:

```bash
# Create Cloud SQL instance
gcloud sql instances create rogue-detection-db \
    --database-version=POSTGRES_13 \
    --tier=db-f1-micro \
    --region=us-central1

# Create database
gcloud sql databases create roguedetect --instance=rogue-detection-db

# Create user
gcloud sql users create roguedetect \
    --instance=rogue-detection-db \
    --password=STRONG_PASSWORD
```

---

## Docker Deployment

### Dockerfile

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create directories
RUN mkdir -p /app/logs /app/backups

# Set permissions
RUN chmod 600 config.json

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/api/monitoring/status')"

# Run application
CMD ["python", "app.py"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  rogue-detection:
    build: .
    container_name: rogue-detection
    restart: unless-stopped
    ports:
      - "5000:5000"
    volumes:
      - ./config.json:/app/config.json:ro
      - ./rogue_monitor.db:/app/rogue_monitor.db
      - ./logs:/app/logs
      - ./backups:/app/backups
    environment:
      - TZ=America/New_York
    networks:
      - rogue-net
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  nginx:
    image: nginx:alpine
    container_name: rogue-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - rogue-detection
    networks:
      - rogue-net

networks:
  rogue-net:
    driver: bridge
```

### Deploy with Docker

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down

# Update
docker-compose pull
docker-compose up -d
```

---

## Production Configuration

### Environment Variables

Create `.env` file:
```bash
# Switch Configuration
SWITCH_IP=192.168.1.3
SWITCH_USERNAME=admin
SWITCH_PASSWORD=your_password
SWITCH_ENABLE_PASSWORD=your_enable_password

# Email Configuration
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_USERNAME=alerts@yourdomain.com
EMAIL_PASSWORD=your_app_password
EMAIL_RECIPIENTS=admin@yourdomain.com,security@yourdomain.com

# Application Configuration
WEB_PORT=5000
WEB_HOST=127.0.0.1
DEBUG_MODE=false
LOG_LEVEL=INFO

# Database
DATABASE_PATH=/app/rogue_monitor.db

# Security
SECRET_KEY=your_random_secret_key_here
SESSION_TIMEOUT=3600
```

### Load from Environment

Modify `config.py`:
```python
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SWITCH_IP = os.getenv('SWITCH_IP', '192.168.1.3')
    SWITCH_USERNAME = os.getenv('SWITCH_USERNAME', 'admin')
    SWITCH_PASSWORD = os.getenv('SWITCH_PASSWORD')
    SWITCH_ENABLE_PASSWORD = os.getenv('SWITCH_ENABLE_PASSWORD')
    # ... rest of config
```

---

## Security Hardening

### 1. File Permissions (Linux)

```bash
# Application directory
chmod 750 /home/roguedetect/rogue_detection_system

# Configuration
chmod 600 config.json
chmod 600 .env

# Database
chmod 600 rogue_monitor.db

# Logs
chmod 640 /var/log/rogue-detection/*.log
```

### 2. Strong Passwords

```bash
# Generate strong password
openssl rand -base64 32

# Use in config.json and .env
```

### 3. SSH Hardening

```bash
# Edit SSH config
sudo nano /etc/ssh/sshd_config
```

**Recommended settings:**
```
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
X11Forwarding no
MaxAuthTries 3
ClientAliveInterval 300
ClientAliveCountMax 2
```

```bash
sudo systemctl restart sshd
```

### 4. Fail2Ban

```bash
# Install Fail2Ban
sudo apt install fail2ban -y

# Create jail for application
sudo nano /etc/fail2ban/jail.local
```

**Configuration:**
```ini
[rogue-detection]
enabled = true
port = 5000
filter = rogue-detection
logpath = /var/log/rogue-detection/*.log
maxretry = 5
bantime = 3600
```

### 5. Rate Limiting

Add to Nginx configuration:
```nginx
limit_req_zone $binary_remote_addr zone=rogue_limit:10m rate=10r/s;

server {
    location / {
        limit_req zone=rogue_limit burst=20 nodelay;
        # ... rest of config
    }
}
```

### 6. Database Encryption

```bash
# Install SQLCipher
sudo apt install sqlcipher -y

# Encrypt database
sqlcipher rogue_monitor.db
> PRAGMA key = 'your_encryption_key';
> ATTACH DATABASE 'encrypted.db' AS encrypted KEY 'your_encryption_key';
> SELECT sqlcipher_export('encrypted');
> DETACH DATABASE encrypted;
```

---

## Monitoring & Maintenance

### System Monitoring

**Install monitoring tools:**
```bash
# Install Netdata
bash <(curl -Ss https://my-netdata.io/kickstart.sh)

# Access at http://your-server:19999
```

**Monitor application:**
```bash
# Check service status
sudo systemctl status rogue-detection

# View logs
sudo journalctl -u rogue-detection -f

# Check resource usage
htop

# Check disk space
df -h

# Check memory
free -h
```

### Application Health Check

Create `healthcheck.sh`:
```bash
#!/bin/bash

# Check if service is running
if ! systemctl is-active --quiet rogue-detection; then
    echo "Service is not running!"
    sudo systemctl start rogue-detection
    exit 1
fi

# Check if web interface responds
if ! curl -f http://localhost:5000/api/monitoring/status > /dev/null 2>&1; then
    echo "Web interface not responding!"
    sudo systemctl restart rogue-detection
    exit 1
fi

# Check database
if ! sqlite3 /home/roguedetect/rogue_detection_system/rogue_monitor.db "SELECT 1;" > /dev/null 2>&1; then
    echo "Database error!"
    exit 1
fi

echo "All checks passed"
exit 0
```

**Schedule health check:**
```bash
# Add to crontab
crontab -e

# Run every 5 minutes
*/5 * * * * /home/roguedetect/healthcheck.sh >> /var/log/healthcheck.log 2>&1
```

### Log Management

**Centralized logging with rsyslog:**
```bash
# Configure rsyslog
sudo nano /etc/rsyslog.d/30-rogue-detection.conf
```

```
if $programname == 'rogue-detection' then /var/log/rogue-detection/app.log
& stop
```

```bash
sudo systemctl restart rsyslog
```

### Performance Tuning

**Optimize SQLite:**
```python
# Add to database.py
def optimize_database(self):
    conn = self.get_connection()
    cursor = conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.execute("PRAGMA synchronous=NORMAL;")
    cursor.execute("PRAGMA cache_size=10000;")
    cursor.execute("PRAGMA temp_store=MEMORY;")
    cursor.execute("VACUUM;")
    cursor.execute("ANALYZE;")
    conn.commit()
    conn.close()
```

---

## Backup & Recovery

### Automated Backup Script

Create `backup.sh`:
```bash
#!/bin/bash

# Configuration
BACKUP_DIR="/home/roguedetect/backups"
APP_DIR="/home/roguedetect/rogue_detection_system"
DATE=$(date +%Y-%m-%d_%H-%M-%S)
RETENTION_DAYS=30

# Create backup directory
mkdir -p "$BACKUP_DIR/$DATE"

# Backup database
sqlite3 "$APP_DIR/rogue_monitor.db" ".backup '$BACKUP_DIR/$DATE/rogue_monitor.db'"

# Backup configuration
cp "$APP_DIR/config.json" "$BACKUP_DIR/$DATE/config.json"

# Backup authorized devices
cp "$APP_DIR/authorized_devices.json" "$BACKUP_DIR/$DATE/authorized_devices.json" 2>/dev/null || true

# Create tarball
cd "$BACKUP_DIR"
tar -czf "$DATE.tar.gz" "$DATE"
rm -rf "$DATE"

# Delete old backups
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete

# Upload to cloud (optional)
# aws s3 cp "$BACKUP_DIR/$DATE.tar.gz" s3://your-bucket/backups/

echo "Backup completed: $DATE.tar.gz"
```

**Schedule backup:**
```bash
# Add to crontab
crontab -e

# Daily at 2 AM
0 2 * * * /home/roguedetect/backup.sh >> /var/log/backup.log 2>&1
```

### Recovery Procedure

```bash
# Stop service
sudo systemctl stop rogue-detection

# Extract backup
cd /home/roguedetect/backups
tar -xzf 2025-10-23_02-00-00.tar.gz

# Restore database
cp 2025-10-23_02-00-00/rogue_monitor.db /home/roguedetect/rogue_detection_system/

# Restore configuration
cp 2025-10-23_02-00-00/config.json /home/roguedetect/rogue_detection_system/

# Set permissions
chmod 600 /home/roguedetect/rogue_detection_system/rogue_monitor.db
chmod 600 /home/roguedetect/rogue_detection_system/config.json

# Start service
sudo systemctl start rogue-detection
sudo systemctl status rogue-detection
```

---

## Troubleshooting

### Service Won't Start

```bash
# Check service status
sudo systemctl status rogue-detection

# Check logs
sudo journalctl -u rogue-detection -n 50

# Check Python errors
cd /home/roguedetect/rogue_detection_system
source venv/bin/activate
python app.py

# Check permissions
ls -la config.json rogue_monitor.db

# Check port availability
sudo netstat -tuln | grep 5000
```

### Database Locked

```bash
# Check for processes using database
lsof /home/roguedetect/rogue_detection_system/rogue_monitor.db

# Kill processes if needed
sudo kill -9 <PID>

# Restart service
sudo systemctl restart rogue-detection
```

### High Memory Usage

```bash
# Check memory
free -h

# Check process memory
ps aux | grep python

# Restart service
sudo systemctl restart rogue-detection

# Optimize database
sqlite3 rogue_monitor.db "VACUUM;"
```

### SSL Certificate Issues

```bash
# Renew certificate
sudo certbot renew

# Test renewal
sudo certbot renew --dry-run

# Check certificate
sudo certbot certificates

# Force renewal
sudo certbot renew --force-renewal
```

---

## Post-Deployment Checklist

- [ ] Application running and accessible
- [ ] SSL certificate installed and valid
- [ ] Firewall rules configured
- [ ] Service auto-starts on boot
- [ ] Backups scheduled and tested
- [ ] Monitoring configured
- [ ] Logs rotating properly
- [ ] Email alerts working
- [ ] Switch connection tested
- [ ] Default passwords changed
- [ ] File permissions secured
- [ ] Health checks configured
- [ ] Documentation updated
- [ ] Team trained on system

---

**Deployment Complete! 🎉**

*For support, see [README.md](README.md) or contact your system administrator.*

*Last Updated: October 23, 2025*

