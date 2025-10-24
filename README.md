# 🛡️ Rogue Detection System

**Advanced Network Security System for Cisco Switches**

A comprehensive Flask-based web application that monitors network devices, detects rogue devices, and automatically quarantines them using VLAN isolation or port shutdown.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)](https://flask.palletsprojects.com/)
[![Netmiko](https://img.shields.io/badge/Netmiko-4.3.0-orange.svg)](https://github.com/ktbyers/netmiko)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📋 Table of Contents

- [Features](#-features)
- [System Requirements](#-system-requirements)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
  - [Linux/Ubuntu](#linux-ubuntu)
  - [Windows](#windows)
  - [Google Cloud Platform](#google-cloud-platform)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Web Interface](#-web-interface)
- [API Documentation](#-api-documentation)
- [Security](#-security)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🚀 Features

### Core Features
- ✅ **Real-time Device Monitoring** - Continuous scanning of network devices
- ✅ **Rogue Device Detection** - MAC address-based authorization
- ✅ **Automatic Quarantine** - VLAN 999 isolation or port shutdown
- ✅ **Auto-Restore** - Automatic VLAN restoration when devices are authorized
- ✅ **Vendor Identification** - 229+ vendor database for device identification
- ✅ **Email Alerts** - Instant notifications for security events
- ✅ **Event Logging** - Complete audit trail of all activities
- ✅ **Port Management** - Monitor and control switch ports
- ✅ **VLAN Management** - Change port VLANs directly from web interface

### Advanced Features
- 🔐 **User Authentication** - Secure login system
- 📊 **Dashboard** - Real-time statistics and visualizations
- 📁 **CSV Import/Export** - Bulk device management
- 🔄 **Auto-Refresh** - Real-time updates without page reload
- 📧 **Email Notifications** - Configurable SMTP alerts
- 🎨 **Modern UI** - Responsive Bootstrap 5 interface
- 🔍 **Search & Filter** - Quick device and event lookup
- 📱 **Mobile Responsive** - Works on all devices

### Security Features
- 🛡️ **MAC Address Whitelisting** - Only authorized devices allowed
- 🚫 **Automatic Isolation** - Instant quarantine of rogue devices
- 📝 **Audit Logging** - Complete activity tracking
- 🔒 **Session Management** - Secure user sessions
- 🔑 **Enable Mode Support** - Cisco privileged EXEC mode
- ⚠️ **Risk Scoring** - Threat level assessment

---

## 💻 System Requirements

### Hardware Requirements
- **CPU:** 1+ cores (2+ recommended)
- **RAM:** 512 MB minimum (1 GB recommended)
- **Storage:** 100 MB minimum (500 MB recommended)
- **Network:** Ethernet connection to switch

### Software Requirements
- **Operating System:**
  - Linux (Ubuntu 20.04+, Debian 10+, CentOS 8+)
  - Windows 10/11 or Windows Server 2016+
  - macOS 10.15+
  - Google Cloud Platform (Compute Engine)
  
- **Python:** 3.8 or higher
- **Database:** SQLite 3 (included with Python)
- **Browser:** Chrome, Firefox, Safari, or Edge (latest versions)

### Network Requirements
- **Switch:** Cisco IOS device with SSH enabled
- **Connectivity:** IP reachability to switch management interface
- **Credentials:** SSH username/password and enable password
- **Ports:** TCP 22 (SSH), TCP 5000 (Web Interface)

---

## ⚡ Quick Start

### 1. Clone or Download
```bash
# If using git
git clone https://github.com/yourusername/rogue-detection-system.git
cd rogue-detection-system

# Or download and extract the ZIP file
```

### 2. Install Dependencies
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# OR
venv\Scripts\activate     # Windows

# Install packages
pip install -r requirements.txt
```

### 3. Configure
```bash
# Copy example config
cp config.json.example config.json

# Edit configuration
nano config.json  # Linux
# OR
notepad config.json  # Windows
```

### 4. Run
```bash
# Start the application
sudo venv/bin/python3 app.py  # Linux (sudo for port 80)
# OR
python app.py                  # Windows
```

### 5. Access
Open browser: **http://localhost:5000**

**Default Login:**
- Username: `admin`
- Password: `admin123`

---

## 📦 Installation

### Linux (Ubuntu/Debian)

#### Step 1: Update System
```bash
sudo apt update && sudo apt upgrade -y
```

#### Step 2: Install Python & Dependencies
```bash
# Install Python 3 and pip
sudo apt install python3 python3-pip python3-venv -y

# Install system dependencies
sudo apt install git sqlite3 -y
```

#### Step 3: Download Application
```bash
# Create directory
mkdir -p ~/rogue_detection_system
cd ~/rogue_detection_system

# Download or copy files here
```

#### Step 4: Setup Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
```

#### Step 5: Configure
```bash
# Copy example config
cp config.json.example config.json

# Edit configuration
nano config.json
```

**Edit these values:**
```json
{
  "switch_ip": "192.168.1.3",
  "switch_username": "your_username",
  "switch_password": "your_password",
  "switch_enable_password": "your_enable_password"
}
```

#### Step 6: Run Application
```bash
# Run on port 5000 (no sudo needed)
venv/bin/python3 app.py

# OR run on port 80 (requires sudo)
sudo venv/bin/python3 app.py
```

#### Step 7: Create Systemd Service (Optional)
```bash
# Create service file
sudo nano /etc/systemd/system/rogue-detection.service
```

**Add this content:**
```ini
[Unit]
Description=Rogue Detection System
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/home/your_username/rogue_detection_system
Environment="PATH=/home/your_username/rogue_detection_system/venv/bin"
ExecStart=/home/your_username/rogue_detection_system/venv/bin/python3 app.py
Restart=always
RestartSec=10

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

---

### Windows

#### Step 1: Install Python
1. Download Python 3.8+ from [python.org](https://www.python.org/downloads/)
2. Run installer
3. ✅ Check "Add Python to PATH"
4. Click "Install Now"

#### Step 2: Download Application
1. Download ZIP file
2. Extract to `C:\rogue_detection_system`
3. Open PowerShell or Command Prompt

#### Step 3: Setup Virtual Environment
```powershell
# Navigate to directory
cd C:\rogue_detection_system

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

#### Step 4: Configure
```powershell
# Copy example config
copy config.json.example config.json

# Edit configuration
notepad config.json
```

#### Step 5: Run Application
```powershell
# Run application
python app.py
```

#### Step 6: Create Windows Service (Optional)
Use **NSSM (Non-Sucking Service Manager)**:

1. Download NSSM from [nssm.cc](https://nssm.cc/download)
2. Extract to `C:\nssm`
3. Open Command Prompt as Administrator:

```cmd
cd C:\nssm\win64
nssm install RogueDetection "C:\rogue_detection_system\venv\Scripts\python.exe" "C:\rogue_detection_system\app.py"
nssm set RogueDetection AppDirectory "C:\rogue_detection_system"
nssm start RogueDetection
```

---

### Google Cloud Platform

#### Step 1: Create VM Instance
```bash
# Using gcloud CLI
gcloud compute instances create rogue-detection \
  --zone=us-central1-a \
  --machine-type=e2-micro \
  --image-family=ubuntu-2004-lts \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=10GB \
  --tags=http-server,https-server
```

#### Step 2: Configure Firewall
```bash
# Allow web traffic
gcloud compute firewall-rules create allow-rogue-detection \
  --allow=tcp:5000 \
  --source-ranges=0.0.0.0/0 \
  --target-tags=http-server
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
sudo apt install python3 python3-pip python3-venv git -y

# Clone or download application
cd ~
# Copy your files here

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure
cp config.json.example config.json
nano config.json

# Run application
python3 app.py
```

#### Step 5: Setup Startup Script (Optional)
```bash
# Create startup script
sudo nano /etc/rc.local
```

**Add:**
```bash
#!/bin/bash
cd /home/your_username/rogue_detection_system
/home/your_username/rogue_detection_system/venv/bin/python3 app.py &
exit 0
```

```bash
# Make executable
sudo chmod +x /etc/rc.local
```

---

## ⚙️ Configuration

### config.json Structure

```json
{
  "switch_ip": "192.168.1.3",
  "switch_username": "admin",
  "switch_password": "your_password",
  "switch_enable_password": "your_enable_password",
  "switch_port": 22,
  "scan_interval": 30,
  "quarantine_vlan": 999,
  "default_vlan": 1,
  "quarantine_action": "vlan",
  "email_enabled": false,
  "email_smtp_server": "smtp.gmail.com",
  "email_smtp_port": 587,
  "email_username": "your_email@gmail.com",
  "email_password": "your_app_password",
  "email_recipients": ["admin@example.com"],
  "web_port": 5000,
  "web_host": "0.0.0.0",
  "debug_mode": false,
  "log_level": "INFO"
}
```

### Configuration Options

| Option | Description | Default | Required |
|--------|-------------|---------|----------|
| `switch_ip` | Switch management IP | - | ✅ |
| `switch_username` | SSH username | - | ✅ |
| `switch_password` | SSH password | - | ✅ |
| `switch_enable_password` | Enable mode password | - | ✅ |
| `switch_port` | SSH port | 22 | ❌ |
| `scan_interval` | Scan frequency (seconds) | 30 | ❌ |
| `quarantine_vlan` | Isolation VLAN ID | 999 | ❌ |
| `default_vlan` | Default VLAN for authorized devices | 1 | ❌ |
| `quarantine_action` | Action: "vlan" or "shutdown" | vlan | ❌ |
| `email_enabled` | Enable email alerts | false | ❌ |
| `web_port` | Web interface port | 5000 | ❌ |
| `web_host` | Web interface host | 0.0.0.0 | ❌ |

---

## 🎯 Usage

### Starting the Application

**Linux:**
```bash
cd ~/rogue_detection_system
source venv/bin/activate
sudo venv/bin/python3 app.py
```

**Windows:**
```powershell
cd C:\rogue_detection_system
venv\Scripts\activate
python app.py
```

### Accessing Web Interface

1. Open browser
2. Navigate to: `http://localhost:5000`
3. Login with credentials:
   - Username: `admin`
   - Password: `admin123`

### First-Time Setup

1. **Configure Switch Settings**
   - Go to Settings page
   - Enter switch IP, credentials, enable password
   - Click "Save Settings"
   - Test connection

2. **Add Authorized Devices**
   - Go to Devices page
   - Click "Add Device"
   - Enter MAC address and description
   - Click "Authorize"

3. **Start Monitoring**
   - Detection starts automatically
   - View dashboard for real-time stats
   - Check Events page for activity logs

### Managing Devices

#### Authorize Device
```
1. Navigate to Devices page
2. Click "Add Device" button
3. Enter MAC address (format: AA:BB:CC:DD:EE:FF)
4. Enter description (e.g., "John's Laptop")
5. Click "Authorize"
```

#### Unauthorize Device
```
1. Navigate to Devices page
2. Find device in list
3. Click "Revoke" button
4. Confirm action
```

#### Import Devices (CSV)
```
1. Navigate to Import/Export page
2. Prepare CSV file:
   mac_address,description
   AA:BB:CC:DD:EE:FF,Device 1
   11:22:33:44:55:66,Device 2
3. Click "Choose File"
4. Select CSV file
5. Click "Import"
```

### Managing Ports

#### View Port Status
```
1. Navigate to Ports page
2. View all ports with status
3. Use search to filter ports
4. Click "Refresh" for latest status
```

#### Change Port VLAN
```
1. Navigate to Ports page
2. Find port in list
3. Click yellow "Change VLAN" button
4. Select new VLAN ID
5. Enter reason (optional)
6. Click "Change VLAN"
```

#### Enable/Disable Port
```
1. Navigate to Ports page
2. Find port in list
3. Toggle switch to enable/disable
4. Status updates automatically
```

---

## 🖥️ Web Interface

### Dashboard (`/`)
- **Statistics Cards:** Total devices, authorized, rogues, quarantined
- **Recent Events:** Latest 10 security events
- **Quick Actions:** Add device, view quarantine, refresh
- **Real-time Updates:** Auto-refresh every 30 seconds

### Devices (`/devices`)
- **Device List:** All detected devices with status
- **Vendor Information:** Automatic vendor lookup
- **Actions:** Authorize, revoke, view details
- **Search:** Filter by MAC, vendor, or description
- **Auto-refresh:** Toggle for real-time updates

### Ports (`/ports`)
- **Port Status:** All switch ports with VLAN info
- **Statistics:** Connected, disabled, not connected
- **Actions:** Enable, disable, change VLAN
- **Search:** Filter ports by name or status
- **Auto-refresh:** 30-second interval

### Events (`/events`)
- **Event Log:** Complete audit trail
- **Filters:** By type, severity, date range
- **Export:** Download as CSV
- **Search:** Find specific events
- **Pagination:** Navigate through history

### Quarantine (`/quarantine`)
- **Quarantined Devices:** All isolated devices
- **Reason:** Why device was quarantined
- **Actions:** Release, keep quarantined
- **Timeline:** When quarantine started

### Settings (`/settings`)
- **Switch Configuration:** IP, credentials, enable password
- **Detection Settings:** Scan interval, quarantine action
- **Email Settings:** SMTP configuration
- **System Settings:** Web port, debug mode
- **Test Connection:** Verify switch connectivity

### Import/Export (`/import_export`)
- **Import Devices:** Bulk upload from CSV
- **Export Devices:** Download authorized devices
- **Export Events:** Download event logs
- **Templates:** Download CSV templates

---

## 📡 API Documentation

### Authentication
All API endpoints require authentication via session cookies.

### Endpoints

#### Device Management

**Get All Devices**
```http
GET /api/devices
Response: {
  "devices": [
    {
      "mac_address": "AA:BB:CC:DD:EE:FF",
      "ip_address": "192.168.1.100",
      "vendor": "Cisco",
      "status": "authorized",
      "last_seen": "2025-10-23 12:00:00"
    }
  ]
}
```

**Authorize Device**
```http
POST /api/devices/authorize
Body: {
  "mac_address": "AA:BB:CC:DD:EE:FF",
  "description": "John's Laptop"
}
Response: {
  "success": true,
  "message": "Device authorized"
}
```

**Unauthorize Device**
```http
POST /api/devices/unauthorize
Body: {
  "mac_address": "AA:BB:CC:DD:EE:FF"
}
Response: {
  "success": true,
  "message": "Device unauthorized"
}
```

#### Port Management

**Get Port Status**
```http
GET /api/ports/status
Response: {
  "ports": [
    {
      "port": "Et0/0",
      "admin_status": "enabled",
      "operational_status": "up",
      "vlan": "1",
      "last_modified": "2025-10-23 12:00:00"
    }
  ]
}
```

**Change Port VLAN**
```http
POST /api/ports/change-vlan
Body: {
  "port": "Et0/0",
  "vlan_id": 10,
  "reason": "Moving to guest VLAN"
}
Response: {
  "success": true,
  "message": "Port Et0/0 moved to VLAN 10"
}
```

**Toggle Port**
```http
POST /api/ports/toggle
Body: {
  "port": "Et0/0",
  "action": "enable"
}
Response: {
  "success": true,
  "message": "Port enabled"
}
```

#### Event Management

**Get Events**
```http
GET /api/events?limit=50&offset=0
Response: {
  "events": [
    {
      "id": 1,
      "event_type": "ROGUE_DETECTED",
      "severity": "HIGH",
      "description": "Unauthorized device detected",
      "timestamp": "2025-10-23 12:00:00"
    }
  ],
  "total": 100
}
```

---

## 🔒 Security

### Best Practices

1. **Change Default Credentials**
   - Modify default admin password immediately
   - Use strong passwords (12+ characters)

2. **Secure Configuration**
   - Store `config.json` with restricted permissions
   - Never commit credentials to version control
   - Use environment variables for sensitive data

3. **Network Security**
   - Run behind firewall
   - Use HTTPS in production (reverse proxy)
   - Restrict access to management network

4. **Switch Security**
   - Use dedicated service account for SSH
   - Limit enable mode privileges
   - Enable SSH key authentication

5. **Regular Updates**
   - Keep Python packages updated
   - Monitor security advisories
   - Apply patches promptly

### File Permissions (Linux)

```bash
# Secure configuration file
chmod 600 config.json
chown your_user:your_group config.json

# Secure database
chmod 600 rogue_monitor.db
chown your_user:your_group rogue_monitor.db

# Secure application directory
chmod 750 ~/rogue_detection_system
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. Cannot Connect to Switch
**Symptoms:** "Failed to connect to switch" error

**Solutions:**
```bash
# Test connectivity
ping 192.168.1.3

# Test SSH manually
ssh admin@192.168.1.3

# Check firewall
sudo ufw status
sudo ufw allow 22/tcp

# Verify credentials in config.json
```

#### 2. Web Interface Not Loading
**Symptoms:** "Connection refused" or timeout

**Solutions:**
```bash
# Check if app is running
ps aux | grep app.py

# Check port availability
netstat -tuln | grep 5000

# Check firewall
sudo ufw allow 5000/tcp

# Run with debug mode
python app.py --debug
```

#### 3. Database Errors
**Symptoms:** "No such table" or "Database locked"

**Solutions:**
```bash
# Check database file exists
ls -l rogue_monitor.db

# Check permissions
chmod 644 rogue_monitor.db

# Recreate database (WARNING: deletes data)
rm rogue_monitor.db
python app.py  # Will recreate on startup
```

#### 4. Port Status Not Updating
**Symptoms:** Ports show old status

**Solutions:**
```bash
# Verify switch connectivity
# Check enable password in config.json
# Manually refresh ports in web interface
# Check switch SSH access
```

#### 5. Email Alerts Not Working
**Symptoms:** No emails received

**Solutions:**
```bash
# Verify email settings in config.json
# Check SMTP server and port
# For Gmail: Use App Password, not regular password
# Test email manually from Settings page
```

### Debug Mode

Enable debug mode for detailed logs:

```bash
# Edit config.json
"debug_mode": true

# Or run with debug flag
python app.py --debug
```

### Logs Location

```bash
# Application logs
tail -f /var/log/rogue-detection.log

# System logs (if using systemd)
sudo journalctl -u rogue-detection -f
```

---

## 📚 Additional Documentation

- **[START_HERE.md](START_HERE.md)** - Quick start guide
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Detailed deployment instructions
- **[VLAN_CHANGE_FEATURE.md](VLAN_CHANGE_FEATURE.md)** - VLAN management guide
- **[PROJECT_FILES_GUIDE.md](PROJECT_FILES_GUIDE.md)** - File structure overview
- **[DETECTION_LOGIC.md](DETECTION_LOGIC.md)** - How detection works
- **[SECURITY_MODEL.md](SECURITY_MODEL.md)** - Security architecture

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Authors

- **Your Name** - Initial work - [YourGitHub](https://github.com/yourusername)

---

## 🙏 Acknowledgments

- **Netmiko** - SSH connection library
- **Flask** - Web framework
- **Bootstrap** - UI framework
- **Font Awesome** - Icons

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/yourusername/rogue-detection-system/issues)
- **Email:** support@example.com
- **Documentation:** [Wiki](https://github.com/yourusername/rogue-detection-system/wiki)

---

## 🗺️ Roadmap

- [ ] Multi-switch support
- [ ] Advanced threat detection (MAC spoofing, port hopping)
- [ ] Integration with SIEM systems
- [ ] Mobile app
- [ ] API rate limiting
- [ ] Role-based access control
- [ ] LDAP/Active Directory integration
- [ ] Automated backup/restore
- [ ] Performance monitoring
- [ ] Custom alerting rules

---

## 📊 Project Statistics

- **Lines of Code:** ~15,000
- **Python Files:** 7 core modules
- **Templates:** 9 HTML pages
- **Supported Vendors:** 229+ MAC vendors
- **API Endpoints:** 20+
- **Database Tables:** 5

---

**Made with ❤️ for Network Security**

*Last Updated: October 23, 2025*
