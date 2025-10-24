# ⚡ Quick Reference Card

**Essential Commands & Information**

---

## 🚀 Deployment Commands

### Linux
```bash
sudo ./deploy_linux.sh
```

### Windows
```powershell
.\deploy_windows.ps1
```

### Google Cloud
```bash
./deploy_gcloud.sh
```

---

## ⚙️ Service Management

### Linux
```bash
# Start
sudo systemctl start rogue-detection

# Stop
sudo systemctl stop rogue-detection

# Restart
sudo systemctl restart rogue-detection

# Status
sudo systemctl status rogue-detection

# Logs
sudo journalctl -u rogue-detection -f
```

### Windows
```powershell
# Start
Start-Service -Name RogueDetection

# Stop
Stop-Service -Name RogueDetection

# Restart
Restart-Service -Name RogueDetection

# Status
Get-Service -Name RogueDetection

# Logs
Get-Content C:\RogueDetection\logs\stderr.log -Tail 50 -Wait
```

---

## 📁 Important Files

| File | Location (Linux) | Location (Windows) |
|------|------------------|-------------------|
| **Config** | `/home/roguedetect/rogue_detection_system/config.json` | `C:\RogueDetection\config.json` |
| **Database** | `/home/roguedetect/rogue_detection_system/rogue_monitor.db` | `C:\RogueDetection\rogue_monitor.db` |
| **Logs** | `/var/log/rogue-detection/` | `C:\RogueDetection\logs\` |
| **Backups** | `/home/roguedetect/rogue_detection_system/backups/` | `C:\RogueDetection\backups\` |

---

## 🌐 Web Interface

| Item | Value |
|------|-------|
| **URL** | `http://localhost:5000` |
| **Default Username** | `admin` |
| **Default Password** | `admin123` |

### Pages
- `/` - Dashboard
- `/devices` - Device Management
- `/ports` - Port Management
- `/events` - Event Logs
- `/quarantine` - Quarantined Devices
- `/settings` - System Settings
- `/import_export` - Import/Export

---

## 🔧 Configuration (config.json)

```json
{
  "switch_ip": "192.168.1.3",
  "switch_username": "admin",
  "switch_password": "your_password",
  "switch_enable_password": "enable_password",
  "scan_interval": 30,
  "quarantine_vlan": 999,
  "default_vlan": 1,
  "email_enabled": false,
  "web_port": 5000
}
```

---

## 🐛 Troubleshooting

### Service Won't Start
```bash
# Linux
sudo journalctl -u rogue-detection -n 50

# Windows
Get-Content C:\RogueDetection\logs\stderr.log -Tail 50
```

### Can't Connect to Switch
```bash
# Test connectivity
ping 192.168.1.3

# Test SSH
ssh admin@192.168.1.3
```

### Web Interface Not Loading
```bash
# Check if port is listening
netstat -tuln | grep 5000  # Linux
Get-NetTCPConnection -LocalPort 5000  # Windows

# Check firewall
sudo ufw status  # Linux
Get-NetFirewallRule | Where-Object {$_.LocalPort -eq 5000}  # Windows
```

---

## 📊 Common Tasks

### Add Device
```
1. Go to Devices page
2. Click "Add Device"
3. Enter MAC: AA:BB:CC:DD:EE:FF
4. Enter description
5. Click "Authorize"
```

### Change Port VLAN
```
1. Go to Ports page
2. Find port
3. Click yellow "Change VLAN" button
4. Select VLAN ID
5. Click "Change VLAN"
```

### Import Devices (CSV)
```
1. Create CSV: mac_address,description
2. Go to Import/Export page
3. Choose file
4. Click "Import"
```

---

## 🔒 Security

### Change Admin Password
```
1. Login to web interface
2. Go to Settings
3. Change password
4. Save
```

### Secure Files (Linux)
```bash
chmod 600 config.json
chmod 600 rogue_monitor.db
chmod 750 /home/roguedetect/rogue_detection_system
```

---

## 💾 Backup & Restore

### Manual Backup (Linux)
```bash
cd /home/roguedetect/rogue_detection_system
sqlite3 rogue_monitor.db ".backup backup_$(date +%Y%m%d).db"
cp config.json config_$(date +%Y%m%d).json
```

### Manual Backup (Windows)
```powershell
cd C:\RogueDetection
Copy-Item rogue_monitor.db "backup_$(Get-Date -Format 'yyyyMMdd').db"
Copy-Item config.json "config_$(Get-Date -Format 'yyyyMMdd').json"
```

### Restore
```bash
# Stop service
sudo systemctl stop rogue-detection  # Linux
Stop-Service -Name RogueDetection    # Windows

# Restore database
cp backup_20251023.db rogue_monitor.db

# Start service
sudo systemctl start rogue-detection  # Linux
Start-Service -Name RogueDetection    # Windows
```

---

## 📖 Documentation Files

| File | Purpose |
|------|---------|
| **START_HERE.md** | Quick start (5 min) |
| **README.md** | Complete docs |
| **DEPLOYMENT_COMPLETE.md** | Production deployment |
| **DOCUMENTATION_INDEX.md** | All documentation |
| **QUICK_REFERENCE.md** | This file |

---

## 🔍 Useful Commands

### Check Python Version
```bash
python3 --version  # Linux
python --version   # Windows
```

### Check Installed Packages
```bash
pip list
```

### Test Switch Connection
```bash
python3 -c "from switch_connector import SwitchConnector; from config import Config; s = SwitchConnector(Config.SWITCH_IP, Config.SWITCH_USERNAME, Config.SWITCH_PASSWORD); print('OK' if s.connect() else 'FAIL')"
```

### View Database
```bash
sqlite3 rogue_monitor.db
> .tables
> SELECT * FROM authorized_devices;
> .quit
```

---

## 📞 Support

### Documentation
- `DOCUMENTATION_INDEX.md` - All docs
- `README.md` - Troubleshooting
- `START_HERE.md` - Common issues

### Logs
- Linux: `/var/log/rogue-detection/`
- Windows: `C:\RogueDetection\logs\`
- GCP: Cloud Logging

---

## ⚡ Quick Fixes

### Reset Admin Password
```bash
# Edit database directly
sqlite3 rogue_monitor.db
> UPDATE users SET password='admin123' WHERE username='admin';
> .quit
```

### Clear Database
```bash
# Backup first!
sqlite3 rogue_monitor.db
> DELETE FROM detected_devices;
> DELETE FROM events;
> .quit
```

### Restart Everything
```bash
# Linux
sudo systemctl restart rogue-detection
sudo systemctl restart nginx

# Windows
Restart-Service -Name RogueDetection
```

---

**Keep this file handy for quick reference!**

*Last Updated: October 23, 2025*

