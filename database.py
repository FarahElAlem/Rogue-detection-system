"""
Database management for Rogue Device Detection System
"""
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional


class DatabaseManager:
    """Manages all database operations"""
    
    def __init__(self, db_path="rogue_monitor.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _convert_datetime_to_string(self, devices):
        """Convert datetime objects to strings for JSON serialization"""
        for device in devices:
            if 'first_seen' in device and device['first_seen']:
                if hasattr(device['first_seen'], 'isoformat'):
                    device['first_seen'] = device['first_seen'].isoformat()
            if 'last_seen' in device and device['last_seen']:
                if hasattr(device['last_seen'], 'isoformat'):
                    device['last_seen'] = device['last_seen'].isoformat()
        return devices
    
    def init_database(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Devices table - all detected devices
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS devices (
                mac_address TEXT PRIMARY KEY,
                ip_address TEXT,
                hostname TEXT,
                vendor TEXT,
                switch_port TEXT,
                vlan INTEGER,
                original_vlan INTEGER,
                is_authorized INTEGER DEFAULT 0,
                is_rogue INTEGER DEFAULT 0,
                first_seen TIMESTAMP,
                last_seen TIMESTAMP,
                status TEXT DEFAULT 'active'
            )
        ''')
        
        # Authorized devices table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS authorized_devices (
                mac_address TEXT PRIMARY KEY,
                device_name TEXT,
                device_type TEXT,
                owner TEXT,
                department TEXT,
                notes TEXT,
                authorized_date TIMESTAMP,
                authorized_by TEXT
            )
        ''')
        
        # Events/Incidents table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP,
                event_type TEXT,
                severity TEXT,
                mac_address TEXT,
                ip_address TEXT,
                switch_port TEXT,
                description TEXT,
                action_taken TEXT,
                FOREIGN KEY (mac_address) REFERENCES devices(mac_address)
            )
        ''')
        
        # Port status table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS port_status (
                port_name TEXT PRIMARY KEY,
                admin_status TEXT DEFAULT 'enabled',
                operational_status TEXT DEFAULT 'up',
                last_modified TIMESTAMP,
                modified_by TEXT,
                reason TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_or_update_device(self, device_info: Dict) -> bool:
        """Add new device or update existing one"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            mac = device_info['mac_address']
            now = datetime.now()
            
            # Check if device exists
            cursor.execute('SELECT mac_address, first_seen FROM devices WHERE mac_address = ?', (mac,))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing device
                cursor.execute('''
                    UPDATE devices SET
                        ip_address = ?,
                        hostname = ?,
                        vendor = ?,
                        switch_port = ?,
                        vlan = ?,
                        is_rogue = ?,
                        last_seen = ?,
                        status = 'active'
                    WHERE mac_address = ?
                ''', (
                    device_info.get('ip_address'),
                    device_info.get('hostname'),
                    device_info.get('vendor'),
                    device_info.get('switch_port'),
                    device_info.get('vlan'),
                    device_info.get('is_rogue', 0),
                    now,
                    mac
                ))
            else:
                # Insert new device
                cursor.execute('''
                    INSERT INTO devices (
                        mac_address, ip_address, hostname, vendor, switch_port, vlan,
                        is_authorized, is_rogue, first_seen, last_seen, status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'active')
                ''', (
                    mac,
                    device_info.get('ip_address'),
                    device_info.get('hostname'),
                    device_info.get('vendor'),
                    device_info.get('switch_port'),
                    device_info.get('vlan'),
                    device_info.get('is_authorized', 0),
                    device_info.get('is_rogue', 0),
                    now,
                    now
                ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding/updating device: {e}")
            return False
    
    def get_device_by_mac(self, mac_address: str) -> Dict:
        """Get a single device by MAC address"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM devices WHERE mac_address = ?', (mac_address,))
        device = cursor.fetchone()
        conn.close()
        
        if device:
            return dict(device)
        return None
    
    def get_all_devices(self) -> List[Dict]:
        """Get all devices"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM devices ORDER BY last_seen DESC')
        devices = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return self._convert_datetime_to_string(devices)
    
    def get_rogue_devices(self) -> List[Dict]:
        """Get all rogue devices (excludes multicast/broadcast)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM devices 
            WHERE is_rogue = 1 
            AND status = "active"
            AND mac_address NOT LIKE '01:00:5E:%'
            AND mac_address NOT LIKE '33:33:%'
            AND mac_address != 'FF:FF:FF:FF:FF:FF'
            ORDER BY last_seen DESC
        ''')
        devices = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return self._convert_datetime_to_string(devices)
    
    def get_authorized_devices(self) -> List[Dict]:
        """Get all authorized devices"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM authorized_devices ORDER BY device_name')
        devices = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return devices
    
    def is_device_authorized(self, mac_address: str) -> bool:
        """Check if a MAC address is authorized"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT mac_address FROM authorized_devices WHERE mac_address = ?', (mac_address,))
        result = cursor.fetchone()
        conn.close()
        return result is not None
    
    def authorize_device(self, mac_address: str, device_info: Dict) -> bool:
        """Authorize a device"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            now = datetime.now()
            
            cursor.execute('''
                INSERT OR REPLACE INTO authorized_devices (
                    mac_address, device_name, device_type, owner, department, notes,
                    authorized_date, authorized_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                mac_address,
                device_info.get('device_name', 'Unknown'),
                device_info.get('device_type', 'Unknown'),
                device_info.get('owner', 'Unknown'),
                device_info.get('department', 'Unknown'),
                device_info.get('notes', ''),
                now,
                device_info.get('authorized_by', 'admin')
            ))
            
            # Update device table
            cursor.execute('''
                UPDATE devices SET is_authorized = 1, is_rogue = 0
                WHERE mac_address = ?
            ''', (mac_address,))
            
            conn.commit()
            conn.close()
            
            # Log event
            self.log_event({
                'event_type': 'DEVICE_AUTHORIZED',
                'severity': 'INFO',
                'mac_address': mac_address,
                'description': f"Device {device_info.get('device_name')} was authorized",
                'action_taken': 'Added to authorized devices list'
            })
            
            return True
        except Exception as e:
            print(f"Error authorizing device: {e}")
            return False
    
    def unauthorize_device(self, mac_address: str) -> bool:
        """Remove device from authorized list"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM authorized_devices WHERE mac_address = ?', (mac_address,))
            cursor.execute('UPDATE devices SET is_authorized = 0 WHERE mac_address = ?', (mac_address,))
            
            conn.commit()
            conn.close()
            
            return True
        except Exception as e:
            print(f"Error unauthorizing device: {e}")
            return False
    
    def log_event(self, event_info: Dict) -> bool:
        """Log a security event"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO events (
                    timestamp, event_type, severity, mac_address, ip_address,
                    switch_port, description, action_taken
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now(),
                event_info.get('event_type'),
                event_info.get('severity'),
                event_info.get('mac_address'),
                event_info.get('ip_address'),
                event_info.get('switch_port'),
                event_info.get('description'),
                event_info.get('action_taken')
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error logging event: {e}")
            return False
    
    def get_recent_events(self, limit=100) -> List[Dict]:
        """Get recent events"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM events ORDER BY timestamp DESC LIMIT ?', (limit,))
        events = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return events
    
    def get_statistics(self) -> Dict:
        """Get system statistics (excludes multicast/broadcast addresses)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        # Filter condition to exclude multicast and broadcast addresses
        # Multicast: 01:00:5E:... (IPv4), 33:33:... (IPv6)
        # Broadcast: FF:FF:FF:FF:FF:FF
        filter_condition = '''AND mac_address NOT LIKE '01:00:5E:%' 
                              AND mac_address NOT LIKE '33:33:%' 
                              AND mac_address != 'FF:FF:FF:FF:FF:FF' '''
        
        # Active devices on production network (real devices only)
        cursor.execute(f'SELECT COUNT(*) as count FROM devices WHERE status = "active" {filter_condition}')
        stats['active_devices'] = cursor.fetchone()['count']
        
        # Authorized devices (active on network)
        cursor.execute(f'SELECT COUNT(*) as count FROM devices WHERE is_authorized = 1 AND status = "active" {filter_condition}')
        stats['authorized_devices'] = cursor.fetchone()['count']
        
        # Active rogue devices (on network, not yet quarantined - immediate threat)
        cursor.execute(f'SELECT COUNT(*) as count FROM devices WHERE is_rogue = 1 AND status = "active" {filter_condition}')
        stats['active_rogues'] = cursor.fetchone()['count']
        
        # Quarantined devices (isolated from network)
        cursor.execute('SELECT COUNT(*) as count FROM devices WHERE status = "quarantined"')
        stats['quarantined_devices'] = cursor.fetchone()['count']
        
        # Total devices in database (for reference)
        cursor.execute('SELECT COUNT(*) as count FROM devices WHERE status IN ("active", "quarantined")')
        stats['total_devices'] = cursor.fetchone()['count']
        
        # Today's events
        cursor.execute('''
            SELECT COUNT(*) as count FROM events 
            WHERE DATE(timestamp) = DATE('now')
        ''')
        stats['today_events'] = cursor.fetchone()['count']
        
        # Critical events today
        cursor.execute('''
            SELECT COUNT(*) as count FROM events 
            WHERE DATE(timestamp) = DATE('now') AND severity = 'CRITICAL'
        ''')
        stats['today_critical_events'] = cursor.fetchone()['count']
        
        conn.close()
        return stats
    
    def load_authorized_devices_from_json(self, json_file: str) -> int:
        """Load authorized devices from JSON file (for initial import only)"""
        try:
            with open(json_file, 'r') as f:
                devices = json.load(f)
            
            count = 0
            for device in devices:
                if self.authorize_device(device['mac_address'], device):
                    count += 1
            
            return count
        except Exception as e:
            print(f"Error loading authorized devices: {e}")
            return 0
    
    def export_authorized_devices_to_json(self, json_file: str) -> bool:
        """Export authorized devices to JSON file (for backup only)"""
        try:
            devices = self.get_authorized_devices()
            with open(json_file, 'w') as f:
                json.dump(devices, f, indent=2, default=str)
            return True
        except Exception as e:
            print(f"Error exporting authorized devices: {e}")
            return False
    
    def bulk_authorize_devices(self, devices_list: List[Dict]) -> int:
        """Bulk authorize multiple devices - for initial setup"""
        count = 0
        for device in devices_list:
            try:
                mac = device.get('mac_address')
                if mac and self.authorize_device(mac, device):
                    count += 1
            except Exception as e:
                print(f"Error authorizing {device.get('mac_address')}: {e}")
                continue
        return count
    
    def initialize_default_devices(self) -> int:
        """Initialize with common default authorized devices"""
        default_devices = [
            {
                'mac_address': 'AA:BB:CC:00:10:00',
                'device_name': 'VPC1',
                'device_type': 'Computer',
                'owner': 'Admin',
                'department': 'IT',
                'notes': 'Pre-authorized lab device 1'
            },
            {
                'mac_address': 'AA:BB:CC:00:20:00',
                'device_name': 'VPC2',
                'device_type': 'Computer',
                'owner': 'Admin',
                'department': 'IT',
                'notes': 'Pre-authorized lab device 2'
            }
        ]
        
        return self.bulk_authorize_devices(default_devices)
    
    def update_port_status(self, port_name: str, admin_status: str, reason: str = '', modified_by: str = 'system') -> bool:
        """Update port status in database"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO port_status 
                (port_name, admin_status, last_modified, modified_by, reason)
                VALUES (?, ?, ?, ?, ?)
            ''', (port_name, admin_status, datetime.now(), modified_by, reason))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating port status: {e}")
            return False
    
    def get_port_status(self, port_name: str) -> Optional[Dict]:
        """Get status of a specific port"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM port_status WHERE port_name = ?', (port_name,))
        result = cursor.fetchone()
        conn.close()
        return dict(result) if result else None
    
    def get_all_port_statuses(self) -> List[Dict]:
        """Get status of all ports"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM port_status ORDER BY port_name')
        ports = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return ports
    
    def quarantine_device(self, mac_address: str, quarantine_vlan: int, reason: str = 'Security violation') -> bool:
        """Quarantine a device (move to quarantine VLAN)"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Get current VLAN to save it
            cursor.execute('SELECT vlan, original_vlan FROM devices WHERE mac_address = ?', (mac_address,))
            result = cursor.fetchone()
            
            if result:
                current_vlan = result['vlan']
                original_vlan = result['original_vlan']
                
                # Save original VLAN if not already saved
                if not original_vlan:
                    original_vlan = current_vlan
            else:
                original_vlan = None
            
            # Update device to quarantined status and new VLAN
            cursor.execute('''
                UPDATE devices 
                SET status = 'quarantined', 
                    vlan = ?, 
                    original_vlan = ?
                WHERE mac_address = ?
            ''', (quarantine_vlan, original_vlan, mac_address))
            
            conn.commit()
            conn.close()
            
            # Log quarantine event
            self.log_event({
                'event_type': 'DEVICE_QUARANTINED',
                'severity': 'HIGH',
                'mac_address': mac_address,
                'description': f'Device quarantined to VLAN {quarantine_vlan}: {reason}',
                'action_taken': f'Moved to quarantine VLAN {quarantine_vlan}'
            })
            
            return True
        except Exception as e:
            print(f"Error quarantining device: {e}")
            return False
    
    def restore_device_vlan(self, mac_address: str, target_vlan: int) -> bool:
        """Restore device to proper VLAN (after authorization or release from quarantine)"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE devices 
                SET vlan = ?, 
                    status = 'active'
                WHERE mac_address = ?
            ''', (target_vlan, mac_address))
            
            conn.commit()
            conn.close()
            
            return True
        except Exception as e:
            print(f"Error restoring device VLAN: {e}")
            return False
    
    def get_device_original_vlan(self, mac_address: str) -> Optional[int]:
        """Get the original VLAN of a device (before quarantine)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT original_vlan FROM devices WHERE mac_address = ?', (mac_address,))
        result = cursor.fetchone()
        conn.close()
        
        if result and result['original_vlan']:
            return result['original_vlan']
        return None
    
    def get_quarantined_devices(self) -> List[Dict]:
        """Get all quarantined devices"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM devices WHERE status = "quarantined" ORDER BY last_seen DESC')
        devices = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return devices
    
    def reset_database(self, keep_authorized: bool = True) -> bool:
        """Reset database by clearing all data
        
        Args:
            keep_authorized: If True, keeps authorized devices list. If False, clears everything.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Clear devices table
            cursor.execute('DELETE FROM devices')
            
            # Clear events table
            cursor.execute('DELETE FROM events')
            
            # Clear port status table
            cursor.execute('DELETE FROM port_status')
            
            # Optionally clear authorized devices
            if not keep_authorized:
                cursor.execute('DELETE FROM authorized_devices')
            
            conn.commit()
            conn.close()
            
            print(f"✅ Database reset complete (authorized devices {'kept' if keep_authorized else 'cleared'})")
            return True
        except Exception as e:
            print(f"❌ Error resetting database: {e}")
            return False

