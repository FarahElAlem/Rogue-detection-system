# 🚀 START HERE - Rogue Detection System

**Quick Start Guide - Get Running in 5 Minutes!**

---

## 📋 What You Need

✅ Python 3.8 or higher  
✅ Cisco switch with SSH enabled  
✅ Switch IP address and credentials  
✅ Network connectivity to switch  

---

## ⚡ Quick Installation

### Option 1: Linux (Ubuntu/Debian)

```bash
# 1. Install Python (if not installed)
sudo apt update
sudo apt install python3 python3-pip python3-venv -y

# 2. Navigate to project directory
cd ~/rogue_detection_system

# 3. Create virtual environment
python3 -m venv venv

# 4. Activate virtual environment
source venv/bin/activate

# 5. Install dependencies
pip install -r requirements.txt

# 6. Copy and edit configuration
cp config.json.example config.json
nano config.json

# 7. Run the application
sudo venv/bin/python3 app.py
```

### Option 2: Windows

```powershell
# 1. Install Python from python.org (if not installed)

# 2. Navigate to project directory
cd C:\rogue_detection_system

# 3. Create virtual environment
python -m venv venv

# 4. Activate virtual environment
venv\Scripts\activate

# 5. Install dependencies
pip install -r requirements.txt

# 6. Copy and edit configuration
copy config.json.example config.json
notepad config.json

# 7. Run the application
python app.py
```

---

## ⚙️ Configuration (config.json)

**Minimum required settings:**

```json
{
  "switch_ip": "192.168.1.3",
  "switch_username": "admin",
  "switch_password": "your_password",
  "switch_enable_password": "your_enable_password",
  "scan_interval": 30,
  "quarantine_vlan": 999,
  "default_vlan": 1
}
```

**Edit these 4 values:**
1. `switch_ip` - Your switch management IP
2. `switch_username` - SSH username
3. `switch_password` - SSH password
4. `switch_enable_password` - Enable mode password

---

## 🌐 Access Web Interface

1. **Open browser**
2. **Navigate to:** `http://localhost:5000`
3. **Login:**
   - Username: `admin`
   - Password: `admin123`

---

## 🎯 First Steps After Login

### Step 1: Test Switch Connection
```
1. Click "Settings" in navigation
2. Verify switch settings
3. Click "Test Connection"
4. Should see "✓ Connection successful"
```

### Step 2: Add Your First Device
```
1. Click "Devices" in navigation
2. Click "Add Device" button
3. Enter MAC address: AA:BB:CC:DD:EE:FF
4. Enter description: "My Laptop"
5. Click "Authorize"
```

### Step 3: View Dashboard
```
1. Click "Dashboard" in navigation
2. See real-time statistics
3. View recent events
4. Monitor device count
```

### Step 4: Check Ports
```
1. Click "Ports" in navigation
2. View all switch ports
3. See which ports are connected
4. Try changing a port VLAN
```

---

## 📊 Understanding the Interface

### Dashboard (`/`)
- **Total Devices:** All detected devices
- **Authorized:** Whitelisted devices
- **Rogues:** Unauthorized devices
- **Quarantined:** Isolated devices

### Devices (`/devices`)
- **Green badge:** Authorized device
- **Red badge:** Rogue device
- **Actions:** Authorize, Revoke, View

### Ports (`/ports`)
- **Green badge:** Port enabled
- **Red badge:** Port disabled
- **Yellow button:** Change VLAN
- **Toggle:** Enable/Disable port

### Events (`/events`)
- **Complete audit log**
- **Filter by type/severity**
- **Export to CSV**

---

## 🔧 Common Tasks

### Add Multiple Devices (CSV Import)

**1. Create CSV file (devices.csv):**
```csv
mac_address,description
AA:BB:CC:DD:EE:FF,John's Laptop
11:22:33:44:55:66,Server 1
22:33:44:55:66:77,Printer
```

**2. Import:**
```
1. Go to "Import/Export" page
2. Click "Choose File"
3. Select devices.csv
4. Click "Import"
```

### Change Port VLAN

```
1. Go to "Ports" page
2. Find port (e.g., Et0/0)
3. Click yellow "Change VLAN" button
4. Select VLAN ID (e.g., 10)
5. Enter reason (optional)
6. Click "Change VLAN"
```

### Enable Email Alerts

**1. Edit config.json:**
```json
{
  "email_enabled": true,
  "email_smtp_server": "smtp.gmail.com",
  "email_smtp_port": 587,
  "email_username": "your_email@gmail.com",
  "email_password": "your_app_password",
  "email_recipients": ["admin@example.com"]
}
```

**2. For Gmail:**
- Enable 2-factor authentication
- Generate App Password
- Use App Password in config

**3. Restart application**

### View Quarantined Devices

```
1. Go to "Quarantine" page
2. See all isolated devices
3. Click "Release" to restore
4. Device moves back to default VLAN
```

---

## 🐛 Troubleshooting

### Problem: Can't connect to switch

**Solution:**
```bash
# Test connectivity
ping 192.168.1.3

# Test SSH manually
ssh admin@192.168.1.3

# Check config.json has correct IP and credentials
```

### Problem: Web interface won't load

**Solution:**
```bash
# Check if app is running
ps aux | grep app.py  # Linux
tasklist | findstr python  # Windows

# Try different port
python app.py --port 8080

# Check firewall
sudo ufw allow 5000/tcp  # Linux
```

### Problem: Ports not showing

**Solution:**
```
1. Make sure you're logged in
2. Check switch connection in Settings
3. Click "Refresh Port Status" button
4. Verify enable password is correct
```

### Problem: Database errors

**Solution:**
```bash
# Check database exists
ls -l rogue_monitor.db

# If corrupted, delete and restart
rm rogue_monitor.db
python app.py  # Will recreate
```

---

## 🔒 Security Checklist

- [ ] Change default admin password
- [ ] Use strong switch passwords
- [ ] Restrict web interface to management network
- [ ] Enable firewall rules
- [ ] Set proper file permissions (Linux)
- [ ] Use HTTPS in production
- [ ] Regular backups of database
- [ ] Monitor logs regularly

---

## 📚 Next Steps

### Learn More:
- **[README.md](README.md)** - Complete documentation
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Production deployment
- **[VLAN_CHANGE_FEATURE.md](VLAN_CHANGE_FEATURE.md)** - VLAN management
- **[DETECTION_LOGIC.md](DETECTION_LOGIC.md)** - How detection works

### Advanced Features:
- Multi-switch support (coming soon)
- Advanced threat detection
- Custom alerting rules
- API integration
- Mobile app

---

## 🆘 Getting Help

### Check Logs:
```bash
# Enable debug mode
python app.py --debug

# View logs
tail -f /var/log/rogue-detection.log
```

### Test Components:
```bash
# Test switch connection
python -c "from switch_connector import SwitchConnector; from config import Config; s = SwitchConnector(Config.SWITCH_IP, Config.SWITCH_USERNAME, Config.SWITCH_PASSWORD); print('OK' if s.connect() else 'FAIL')"

# Test database
python -c "from database import DatabaseManager; db = DatabaseManager(); print('OK' if db else 'FAIL')"
```

### Common Commands:
```bash
# Start application
python app.py

# Start with debug
python app.py --debug

# Start on different port
python app.py --port 8080

# Check Python version
python --version

# List installed packages
pip list

# Update packages
pip install --upgrade -r requirements.txt
```

---

## 💡 Tips & Tricks

### 1. Auto-Refresh
- Enable "Auto-refresh" toggle on Devices and Ports pages
- Updates every 30 seconds automatically

### 2. Search & Filter
- Use search box to quickly find devices or ports
- Filter events by type and severity

### 3. Keyboard Shortcuts
- `Ctrl + R` - Refresh current page
- `Ctrl + F` - Search on page
- `Esc` - Close modals

### 4. CSV Export
- Export devices and events to CSV
- Use for reporting and analysis
- Import back to restore devices

### 5. Port Statistics
- View connected/disabled port counts
- Quick overview of network status
- Color-coded for easy identification

---

## 🎓 Understanding Detection

### How It Works:

1. **Scanning:** System connects to switch every 30 seconds
2. **MAC Lookup:** Gets MAC address table from switch
3. **Authorization Check:** Compares against authorized devices
4. **Action:** If unauthorized, moves to VLAN 999 or shuts down port
5. **Logging:** Records all events in database
6. **Alerting:** Sends email if configured

### Detection Flow:

```
Device Connects
    ↓
MAC Address Detected
    ↓
Is Authorized? → YES → Allow (VLAN 1)
    ↓
   NO
    ↓
ROGUE DETECTED!
    ↓
Quarantine (VLAN 999)
    ↓
Log Event + Send Email
```

---

## 📊 System Status

### Check System Health:

```bash
# CPU usage
top

# Memory usage
free -h

# Disk space
df -h

# Network connectivity
ping 192.168.1.3

# Application status
systemctl status rogue-detection  # If using systemd
```

---

## 🚀 Production Deployment

### For Production Use:

1. **Use systemd service** (Linux)
2. **Run behind reverse proxy** (Nginx/Apache)
3. **Enable HTTPS** (SSL certificate)
4. **Set up monitoring** (Nagios/Zabbix)
5. **Configure backups** (Database + Config)
6. **Restrict network access** (Firewall rules)
7. **Use strong passwords** (12+ characters)
8. **Enable audit logging** (All actions)

See **[DEPLOYMENT.md](DEPLOYMENT.md)** for detailed instructions.

---

## ✅ Success Checklist

- [ ] Python 3.8+ installed
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] config.json configured
- [ ] Switch connection tested
- [ ] Web interface accessible
- [ ] Default password changed
- [ ] First device authorized
- [ ] Dashboard showing stats
- [ ] Ports visible and manageable

**If all checked, you're ready to go! 🎉**

---

## 🎯 Quick Reference Card

| Task | Command |
|------|---------|
| Start app | `python app.py` |
| Stop app | `Ctrl + C` |
| Access web | `http://localhost:5000` |
| Default login | admin / admin123 |
| Config file | `config.json` |
| Database | `rogue_monitor.db` |
| Logs | `/var/log/rogue-detection.log` |
| Test switch | Settings → Test Connection |
| Add device | Devices → Add Device |
| Change VLAN | Ports → Change VLAN |

---

**Need more help? Check [README.md](README.md) for complete documentation!**

**Happy Monitoring! 🛡️**

*Last Updated: October 23, 2025*
