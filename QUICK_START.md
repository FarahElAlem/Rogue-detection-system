# 🚀 Quick Start Guide

Get your Rogue Detection System running in 5 minutes!

---

## ⚡ Installation (5 Steps)

### 1️⃣ Install Python
- Download Python 3.8+ from [python.org](https://python.org)
- ✅ Check "Add Python to PATH" during installation

### 2️⃣ Setup Project
```bash
# Navigate to project directory
cd rogue-detection-system

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux/macOS
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Configure
```bash
# Copy example config
cp config.json.example config.json

# Edit with your switch details
notepad config.json  # Windows
nano config.json     # Linux
```

**Minimum configuration:**
```json
{
  "switch_ip": "192.168.1.3",
  "switch_username": "admin",
  "switch_password": "your_password"
}
```

### 5️⃣ Run
```bash
python app.py
```

**Access:** http://localhost:5000  
**Login:** `admin` / `admin123`

---

## 🎯 First Steps After Login

### 1. Test Switch Connection
```
Settings → Test Connection → Should show "✓ Connected"
```

### 2. Authorize Your Devices
```
Devices → Find your device → Click "Authorize"
```

### 3. View Dashboard
```
Dashboard → See device counts and recent events
```

---

## 📊 Main Features

| Feature | Location | What It Does |
|---------|----------|--------------|
| **Dashboard** | `/` | View statistics and recent events |
| **Devices** | `/devices` | Authorize/manage devices |
| **Ports** | `/ports` | Enable/disable ports, change VLANs |
| **Events** | `/events` | View complete activity log |
| **Settings** | `/settings` | Configure system |

---

## 🔧 Common Tasks

### Authorize a Device
1. Go to **Devices** page
2. Find device by MAC address
3. Click **"Authorize"** button
4. Done! Device moves to VLAN 1

### Change Port VLAN
1. Go to **Ports** page
2. Find the port (e.g., Et0/0)
3. Click **"Change VLAN"** button
4. Select VLAN number
5. Click **"Change VLAN"**

### View Rogue Devices
1. Go to **Dashboard**
2. Check "Rogues" counter
3. Click to see list
4. Rogues are automatically in VLAN 999

---

## ⚠️ Important Notes

### Security
- ⚠️ **Change default password immediately!**
- Default: `admin` / `admin123`
- Go to Settings → Change Password

### VLANs
- **VLAN 1** = Authorized devices (normal network)
- **VLAN 999** = Rogue devices (quarantine)

### Scan Interval
- System scans every **30 seconds** by default
- Change in `config.json`: `scan_interval_seconds`

---

## 🐛 Quick Troubleshooting

### Can't connect to switch?
```bash
# Test connectivity
ping 192.168.1.3

# Test SSH
ssh admin@192.168.1.3

# Check config.json has correct IP and credentials
```

### Web interface won't load?
```bash
# Check if app is running
ps aux | grep app.py  # Linux
tasklist | findstr python  # Windows

# Check firewall allows port 5000
```

### No devices showing?
1. Check switch connection (Settings → Test Connection)
2. Verify devices are connected to switch
3. Wait 30 seconds for first scan

---

## 📧 Enable Email Alerts (Optional)

Edit `config.json`:
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

**For Gmail:** Use App Password, not regular password

---

## 🎓 Learning Path

### Beginner (30 minutes)
1. ✅ Install and run (10 min)
2. ✅ Authorize first device (5 min)
3. ✅ Explore web interface (15 min)

### Intermediate (1 hour)
1. ✅ Configure email alerts (15 min)
2. ✅ Manage ports and VLANs (20 min)
3. ✅ Review events and logs (25 min)

### Advanced (2 hours)
1. ✅ Production deployment (1 hour)
2. ✅ Custom configurations (30 min)
3. ✅ Integration with monitoring (30 min)

---

## 📚 More Information

- **Full Documentation:** See `DOCUMENTATION.md`
- **Detailed README:** See `README.md`
- **Troubleshooting:** See `DOCUMENTATION.md` → Troubleshooting section

---

## ✅ Success Checklist

- [ ] Python installed
- [ ] Dependencies installed
- [ ] Config file created
- [ ] Application running
- [ ] Web interface accessible
- [ ] Switch connection tested
- [ ] First device authorized
- [ ] Default password changed

---

**🎉 You're all set! Start protecting your network!**

*Last Updated: October 2025*

