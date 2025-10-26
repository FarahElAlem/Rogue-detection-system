# 🛡️ Rogue Detection System

A Flask-based web application for detecting and managing rogue devices on Cisco network switches.

## 📋 Overview

This system monitors your network switch, detects unauthorized devices, and automatically quarantines them by moving them to VLAN 999. Authorized devices are kept on VLAN 1.

## ✨ Features

- 🔍 **Real-time Device Detection** - Scans network every 30 seconds
- 🚫 **Automatic Quarantine** - Moves rogue devices to VLAN 999
- ✅ **Device Authorization** - Easy web interface to authorize devices
- 📊 **Dashboard** - View all devices, events, and statistics
- 🔧 **Port Management** - Enable/disable ports and change VLANs
- 📧 **Email Alerts** - Get notified when rogue devices are detected
- 📝 **Event Logging** - Complete audit trail of all activities

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Cisco switch with SSH enabled
- Windows, Linux, or macOS

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/rogue-detection-system.git
cd rogue-detection-system
```

2. **Create virtual environment**
```bash
python -m venv venv
```

3. **Activate virtual environment**
```bash
# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

4. **Install dependencies**
```bash
pip install -r requirements.txt
```

5. **Configure the system**
```bash
# Copy example config
cp config.json.example config.json
cp config.py.example config.py

# Edit with your switch details
notepad config.json  # Windows
nano config.json     # Linux
notepad config.py  # Windows
nano config.py     # Linux
```

6. **Run the application**
```bash
python app.py
```

7. **Access web interface**
- Open browser: http://localhost:5000
- Login: `admin` / `admin123`

## ⚙️ Configuration

Edit `config.json` with your switch details:

```json
{
  "switch_ip": "192.168.1.3",
  "switch_username": "admin",
  "switch_password": "your_password",
  "network_range": "192.168.1.0/24",
  "web_port": 5000,
  "scan_interval_seconds": 30
}
```

### Important Settings

| Setting | Description | Default |
|---------|-------------|---------|
| `switch_ip` | IP address of your Cisco switch | Required |
| `switch_username` | SSH username | Required |
| `switch_password` | SSH password | Required |
| `scan_interval_seconds` | How often to scan (seconds) | 30 |
| `web_port` | Web interface port | 5000 |

## 📖 Usage

### 1. Authorize a Device

1. Go to **Devices** page
2. Find the device you want to authorize
3. Click **"Authorize"** button
4. Device will be moved to VLAN 1

### 2. View Rogue Devices

1. Go to **Dashboard**
2. See "Rogues" count
3. Click to view details
4. Rogue devices are automatically in VLAN 999

### 3. Manage Ports

1. Go to **Ports** page
2. View all switch ports
3. Enable/disable ports
4. Change port VLANs

### 4. View Events

1. Go to **Events** page
2. See complete audit log
3. Filter by event type
4. Export to CSV

## 🗂️ Project Structure

```
rogue-detection-system/
├── app.py                    # Main Flask application
├── detector.py               # Detection engine
├── database.py               # Database operations
├── switch_connector.py       # Cisco switch connection
├── config.py                 # Configuration management
├── vendor_lookup.py          # MAC vendor identification
├── email_notifier.py         # Email alerts
├── requirements.txt          # Python dependencies
├── config.json.example       # Example configuration
├── templates/                # HTML templates
│   ├── index.html           # Dashboard
│   ├── devices.html         # Device management
│   ├── ports.html           # Port management
│   ├── events.html          # Event logs
│   └── settings.html        # System settings
└── static/                   # CSS and JavaScript
    ├── css/style.css
    └── js/main.js
```

## 🔧 How It Works

```
1. System scans switch every 30 seconds
         ↓
2. Gets MAC address table from switch
         ↓
3. Checks if each device is authorized
         ↓
4. Authorized? → Keep in VLAN 1 ✅
   Not Authorized? → Move to VLAN 999 ❌
         ↓
5. Log event and send email alert
```

## 📊 Web Interface Pages

### Dashboard (`/`)
- Total devices count
- Authorized devices count
- Rogue devices count
- Recent events
- Quick actions

### Devices (`/devices`)
- List all detected devices
- Authorize/unauthorize devices
- View device details
- Search and filter

### Ports (`/ports`)
- View all switch ports
- Enable/disable ports
- Change port VLANs
- Port statistics

### Events (`/events`)
- Complete event log
- Filter by type and date
- Export to CSV
- Search events

### Settings (`/settings`)
- Configure switch connection
- Email settings
- Scan interval
- System preferences

## 🔒 Security

### Default Credentials
**⚠️ Change immediately after first login!**
- Username: `admin`
- Password: `admin123`

### Best Practices
1. Change default password
2. Use strong switch passwords
3. Restrict web interface access
4. Enable HTTPS in production
5. Regular backups of database

## 🐛 Troubleshooting

### Cannot connect to switch
```bash
# Test connectivity
ping 192.168.1.3

# Test SSH
ssh admin@192.168.1.3

# Check credentials in config.json
```

### Web interface not loading
```bash
# Check if app is running
ps aux | grep app.py  # Linux
tasklist | findstr python  # Windows

# Check firewall
# Allow port 5000
```

### Devices not detected
1. Verify switch connection (Settings → Test Connection)
2. Check switch credentials
3. Ensure switch has devices connected
4. Check scan interval setting

## 📧 Email Alerts

To enable email notifications:

1. Edit `config.json`:
```json
{
  "enable_email_alerts": true,
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  "smtp_username": "your_email@gmail.com",
  "smtp_password": "your_app_password",
  "email_to": ["admin@example.com"]
}
```

2. For Gmail: Use App Password (not regular password)
3. Restart application

## 🔄 Updates

To update the system:

```bash
# Pull latest changes
git pull

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart application
python app.py
```

## 📝 API Endpoints

### Get All Devices
```http
GET /api/devices
```

### Authorize Device
```http
POST /api/devices/<mac_address>/authorize
```

### Get Port Status
```http
GET /api/ports/status
```

### Change Port VLAN
```http
POST /api/ports/change-vlan
Body: {"port": "Et0/0", "vlan_id": 10}
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Netmiko - Network device automation
- Flask - Web framework
- Bootstrap - UI framework

## 🗺️ Roadmap

- [ ] Multi-switch support
- [ ] Advanced threat detection
- [ ] Mobile app
- [ ] LDAP/Active Directory integration
- [ ] Custom alerting rules

---

**Made with ❤️ for Network Security**

*Last Updated: October 2025*
