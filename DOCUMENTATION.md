# 📚 Rogue Detection System - Documentation

## Table of Contents

1. [Installation](#installation)
2. [Configuration](#configuration)
3. [Usage Guide](#usage-guide)
4. [Features](#features)
5. [Troubleshooting](#troubleshooting)
6. [API Reference](#api-reference)

---

## Installation

### Step 1: System Requirements

**Required:**
- Python 3.8 or higher
- Cisco switch with SSH enabled
- 512 MB RAM minimum
- 100 MB disk space

**Supported Operating Systems:**
- Windows 10/11
- Linux (Ubuntu, Debian, CentOS)
- macOS 10.15+

### Step 2: Install Python Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure Application

```bash
# Copy example configuration
cp config.json.example config.json

# Edit configuration file
# Add your switch IP, username, and password
```

### Step 4: Run Application

```bash
python app.py
```

Access at: http://localhost:5000

---

## Configuration

### config.json Structure

```json
{
  "switch_ip": "192.168.1.3",
  "switch_username": "admin",
  "switch_password": "password",
  "network_range": "192.168.1.0/24",
  "web_host": "0.0.0.0",
  "web_port": 5000,
  "scan_interval_seconds": 30,
  "auto_isolate_rogues": false,
  "send_alerts": true,
  "enable_email_alerts": false,
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  "smtp_username": "",
  "smtp_password": "",
  "email_to": []
}
```

### Configuration Options

#### Network Settings

| Option | Description | Example |
|--------|-------------|---------|
| `switch_ip` | Cisco switch IP address | `192.168.1.3` |
| `switch_username` | SSH username | `admin` |
| `switch_password` | SSH password | `password123` |
| `network_range` | Network to monitor | `192.168.1.0/24` |

#### Web Interface

| Option | Description | Default |
|--------|-------------|---------|
| `web_host` | Host to bind to | `0.0.0.0` |
| `web_port` | Port number | `5000` |

#### Detection Settings

| Option | Description | Default |
|--------|-------------|---------|
| `scan_interval_seconds` | Scan frequency | `30` |
| `auto_isolate_rogues` | Auto-quarantine rogues | `false` |
| `send_alerts` | Enable alerts | `true` |

#### Email Settings

| Option | Description | Example |
|--------|-------------|---------|
| `enable_email_alerts` | Enable email notifications | `true` |
| `smtp_server` | SMTP server address | `smtp.gmail.com` |
| `smtp_port` | SMTP port | `587` |
| `smtp_username` | Email username | `user@gmail.com` |
| `smtp_password` | Email password/app password | `app_password` |
| `email_to` | Recipient emails | `["admin@example.com"]` |

---

## Usage Guide

### First Time Setup

1. **Login to Web Interface**
   - URL: http://localhost:5000
   - Username: `admin`
   - Password: `admin123`
   - ⚠️ Change password immediately!

2. **Test Switch Connection**
   - Go to Settings page
   - Click "Test Connection"
   - Verify connection is successful

3. **Authorize Known Devices**
   - Go to Devices page
   - Find your devices
   - Click "Authorize" for each known device

### Daily Operations

#### Authorizing a Device

1. Navigate to **Devices** page
2. Find the device (by MAC address or vendor)
3. Click **"Authorize"** button
4. Enter device name and owner (optional)
5. Click **"Confirm"**
6. Device is moved to VLAN 1

#### Viewing Rogue Devices

1. Go to **Dashboard**
2. Check "Rogues" counter
3. Click on counter to see list
4. Rogue devices are automatically in VLAN 999

#### Managing Ports

1. Go to **Ports** page
2. View all switch ports and their status
3. Actions available:
   - **Enable Port**: Click toggle switch
   - **Disable Port**: Click toggle switch
   - **Change VLAN**: Click "Change VLAN" button

#### Viewing Events

1. Go to **Events** page
2. See complete activity log
3. Filter by:
   - Event type
   - Date range
   - Severity
4. Export to CSV for reporting

---

## Features

### 1. Real-Time Device Detection

**How it works:**
- System connects to switch every 30 seconds
- Retrieves MAC address table
- Compares against authorized devices
- Detects new/rogue devices

**Benefits:**
- Immediate threat detection
- Continuous monitoring
- No manual intervention needed

### 2. Automatic Quarantine

**VLAN-Based Quarantine:**
- Authorized devices: VLAN 1 (normal network)
- Rogue devices: VLAN 999 (isolated network)

**Process:**
```
Device connects → Detected → Authorized?
                              ↓
                         Yes → VLAN 1
                         No  → VLAN 999
```

### 3. Device Management

**Features:**
- Authorize/unauthorize devices
- View device details
- Search and filter
- Bulk import/export (CSV)

**Device Information:**
- MAC address
- IP address
- Vendor (auto-detected)
- Switch port
- VLAN
- Last seen timestamp

### 4. Port Management

**Capabilities:**
- View all ports
- Enable/disable ports
- Change port VLANs
- View port statistics

**Port States:**
- 🟢 **Enabled** - Port is active
- 🔴 **Disabled** - Port is shut down
- ⚪ **Not Connected** - No device connected

### 5. Event Logging

**Event Types:**
- `ROGUE_DETECTED` - New unauthorized device found
- `DEVICE_AUTHORIZED` - Device added to whitelist
- `DEVICE_QUARANTINED` - Device moved to VLAN 999
- `PORT_SHUTDOWN` - Port disabled
- `VLAN_CHANGED` - Port VLAN modified

**Event Information:**
- Timestamp
- Event type
- Severity (INFO, WARNING, HIGH)
- Description
- Action taken

### 6. Email Alerts

**Triggers:**
- Rogue device detected
- Device quarantined
- Port shutdown
- System errors

**Email Content:**
- Event description
- Device details
- Timestamp
- Recommended actions

---

## Troubleshooting

### Common Issues

#### 1. Cannot Connect to Switch

**Symptoms:**
- Error: "Failed to connect to switch"
- "TCP connection failed"

**Solutions:**
```bash
# Test network connectivity
ping 192.168.1.3

# Test SSH access
ssh admin@192.168.1.3

# Verify credentials in config.json
# Check switch SSH is enabled
```

#### 2. Web Interface Not Loading

**Symptoms:**
- Browser shows "Connection refused"
- Page won't load

**Solutions:**
```bash
# Check if application is running
ps aux | grep app.py  # Linux
tasklist | findstr python  # Windows

# Check port is available
netstat -tuln | grep 5000  # Linux
netstat -an | findstr 5000  # Windows

# Check firewall
sudo ufw allow 5000/tcp  # Linux
# Windows: Add firewall rule for port 5000
```

#### 3. Devices Not Detected

**Symptoms:**
- No devices showing up
- Device count is 0

**Solutions:**
1. Verify switch connection (Settings → Test Connection)
2. Check switch has devices connected
3. Verify scan interval is running
4. Check switch credentials are correct
5. Review application logs

#### 4. VLAN Changes Not Working

**Symptoms:**
- Device stays in VLAN 999
- VLAN change fails

**Solutions:**
1. Check switch enable password is set
2. Verify user has privilege to change VLANs
3. Ensure VLAN exists on switch
4. Check port is in access mode (not trunk)

#### 5. Email Alerts Not Sending

**Symptoms:**
- No emails received
- Email errors in logs

**Solutions:**
1. Verify `enable_email_alerts` is `true`
2. Check SMTP settings are correct
3. For Gmail: Use App Password, not regular password
4. Test email from Settings page
5. Check spam folder

### Debug Mode

Enable detailed logging:

```python
# In config.json
{
  "log_level": "DEBUG"
}
```

View logs:
```bash
# Check application output
# Logs are printed to console

# On Linux with systemd:
journalctl -u rogue-detection -f
```

---

## API Reference

### Authentication

All API endpoints require authentication via session cookies.

### Devices API

#### Get All Devices
```http
GET /api/devices
```

**Response:**
```json
{
  "success": true,
  "devices": [
    {
      "mac_address": "AA:BB:CC:DD:EE:FF",
      "ip_address": "192.168.1.100",
      "vendor": "Cisco",
      "status": "authorized",
      "vlan": 1,
      "switch_port": "Et0/0"
    }
  ]
}
```

#### Authorize Device
```http
POST /api/devices/<mac_address>/authorize
```

**Request Body:**
```json
{
  "device_name": "John's Laptop",
  "device_type": "Laptop",
  "owner": "John Doe"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Device authorized successfully"
}
```

#### Unauthorize Device
```http
POST /api/devices/<mac_address>/unauthorize
```

**Response:**
```json
{
  "success": true,
  "message": "Device unauthorized successfully"
}
```

### Ports API

#### Get All Ports
```http
GET /api/ports/status
```

**Response:**
```json
{
  "success": true,
  "ports": [
    {
      "port": "Et0/0",
      "admin_status": "enabled",
      "operational_status": "up",
      "vlan": "1"
    }
  ]
}
```

#### Change Port VLAN
```http
POST /api/ports/change-vlan
```

**Request Body:**
```json
{
  "port": "Et0/0",
  "vlan_id": 10,
  "reason": "Moving to guest VLAN"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Port Et0/0 moved to VLAN 10"
}
```

#### Enable/Disable Port
```http
POST /api/ports/<port_name>/enable
POST /api/ports/<port_name>/shutdown
```

**Response:**
```json
{
  "success": true,
  "message": "Port enabled successfully"
}
```

### Events API

#### Get Events
```http
GET /api/events?limit=50&offset=0
```

**Response:**
```json
{
  "success": true,
  "events": [
    {
      "id": 1,
      "event_type": "ROGUE_DETECTED",
      "severity": "HIGH",
      "description": "Unauthorized device detected",
      "timestamp": "2025-10-24 12:00:00"
    }
  ],
  "total": 100
}
```

---

## Best Practices

### Security

1. **Change Default Password**
   - Change `admin/admin123` immediately
   - Use strong passwords (12+ characters)

2. **Secure Configuration**
   - Protect `config.json` file
   - Never commit passwords to Git
   - Use environment variables in production

3. **Network Security**
   - Run behind firewall
   - Use HTTPS in production
   - Restrict access to management network

4. **Regular Maintenance**
   - Update dependencies monthly
   - Backup database weekly
   - Review logs regularly

### Performance

1. **Scan Interval**
   - Default: 30 seconds
   - Increase for large networks
   - Decrease for faster detection

2. **Database Maintenance**
   - Archive old events periodically
   - Backup database regularly
   - Monitor database size

### Deployment

1. **Production Setup**
   - Use systemd service (Linux)
   - Use NSSM service (Windows)
   - Enable HTTPS
   - Set up monitoring

2. **High Availability**
   - Run multiple instances
   - Use load balancer
   - Database replication

---

## Support

### Getting Help

- **Documentation:** This file
- **README:** Quick start guide
- **Issues:** GitHub Issues
- **Email:** support@example.com

### Reporting Bugs

Include:
1. System information (OS, Python version)
2. Configuration (remove passwords)
3. Error messages
4. Steps to reproduce

---

**Last Updated:** October 2025
**Version:** 1.0.0

