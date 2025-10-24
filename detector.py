"""
Core rogue device detection engine
"""
import time
import threading
from datetime import datetime
from typing import List, Dict
from database import DatabaseManager
from switch_connector import SwitchConnector
from email_notifier import EmailNotifier
from config import Config
from vendor_lookup import VendorLookup


class RogueDeviceDetector:
    """Main detection engine"""
    
    def __init__(self, config=None):
        self.config = config or Config
        self.db = DatabaseManager(self.config.DATABASE_PATH)
        self.email_notifier = EmailNotifier(self.config)
        self.is_running = False
        self.monitor_thread = None
        self.latest_scan_results = {
            'timestamp': None,
            'total_devices': 0,
            'authorized': 0,
            'rogues': 0,
            'devices': []
        }
    
    def perform_scan(self) -> Dict:
        """Perform a single network scan"""
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting network scan...")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'total_devices': 0,
            'authorized': 0,
            'rogues': 0,
            'new_rogues': 0,
            'devices': [],
            'success': False,
            'error': None
        }
        
        try:
            # Connect to switch
            with SwitchConnector(
                host=self.config.SWITCH_IP,
                username=self.config.SWITCH_USERNAME,
                password=self.config.SWITCH_PASSWORD,
                device_type=self.config.SWITCH_DEVICE_TYPE
            ) as switch:
                
                # Get MAC address table
                mac_table = switch.get_mac_address_table()
                
                # Get ARP table for IP addresses
                arp_table = switch.get_arp_table()
                
                # Create IP lookup dictionary
                ip_lookup = {entry['mac_address']: entry['ip_address'] 
                            for entry in arp_table}
                
                # Process each device
                for entry in mac_table:
                    mac = entry['mac_address']
                    
                    # Skip switch's own MAC and broadcast
                    if mac == 'FF:FF:FF:FF:FF:FF' or not mac:
                        continue
                    
                    # Check if authorized
                    is_authorized = self.db.is_device_authorized(mac)
                    is_rogue = not is_authorized
                    
                    # Get IP from ARP table
                    ip_address = ip_lookup.get(mac, 'Unknown')
                    
                    # CRITICAL: Check if device exists BEFORE adding to database
                    # This must be done BEFORE add_or_update_device() call
                    existing_device_check = self.db.get_device_by_mac(mac)
                    device_existed_before = existing_device_check is not None
                    
                    # Prepare device info
                    device_info = {
                        'mac_address': mac,
                        'ip_address': ip_address,
                        'hostname': self._resolve_hostname(ip_address),
                        'vendor': self._get_vendor_from_mac(mac),
                        'switch_port': entry['port'],
                        'vlan': entry.get('vlan', 1),
                        'is_authorized': 1 if is_authorized else 0,
                        'is_rogue': 1 if is_rogue else 0
                    }
                    
                    # Add/update in database
                    self.db.add_or_update_device(device_info)
                    
                    results['devices'].append(device_info)
                    results['total_devices'] += 1
                    
                    if is_authorized:
                        results['authorized'] += 1
                    else:
                        results['rogues'] += 1
                        
                        # Device is NEW rogue if it didn't exist before AND is not authorized
                        # We checked device_existed_before BEFORE adding to database
                        is_new_rogue = not device_existed_before and is_rogue
                        
                        if is_new_rogue:
                            results['new_rogues'] += 1
                            
                            # Determine action taken
                            action_taken = 'Pending'
                            
                            # Log rogue detection event
                            self.db.log_event({
                                'event_type': 'ROGUE_DETECTED',
                                'severity': 'CRITICAL',
                                'mac_address': mac,
                                'ip_address': ip_address,
                                'switch_port': entry['port'],
                                'description': f"Rogue device detected: {mac} on port {entry['port']}",
                                'action_taken': action_taken
                            })
                            
                            # Auto-quarantine rogue devices to separate VLAN
                            if self.config.ENABLE_VLAN_QUARANTINE and self.config.AUTO_QUARANTINE_ROGUES:
                                try:
                                    # Move to quarantine VLAN
                                    success = switch.quarantine_port_vlan(entry['port'], self.config.QUARANTINE_VLAN)
                                    
                                    if success:
                                        action_taken = f'Auto-quarantined to VLAN {self.config.QUARANTINE_VLAN}'
                                        
                                        # Update database
                                        self.db.quarantine_device(mac, self.config.QUARANTINE_VLAN, 'Auto-quarantine: Unauthorized device')
                                        self.db.update_port_status(
                                            entry['port'], 
                                            'auto-quarantine', 
                                            f'Rogue device auto-moved to VLAN {self.config.QUARANTINE_VLAN}',
                                            'system'
                                        )
                                        
                                        self.db.log_event({
                                            'event_type': 'AUTO_QUARANTINE',
                                            'severity': 'HIGH',
                                            'mac_address': mac,
                                            'ip_address': ip_address,
                                            'switch_port': entry['port'],
                                            'description': f'Rogue device auto-quarantined to VLAN {self.config.QUARANTINE_VLAN}',
                                            'action_taken': action_taken
                                        })
                                        
                                        print(f"✅ Auto-quarantined rogue device {mac} to VLAN {self.config.QUARANTINE_VLAN}")
                                        
                                        # Send quarantine email notification
                                        self.email_notifier.send_quarantine_alert(device_info, self.config.QUARANTINE_VLAN)
                                        
                                except Exception as e:
                                    print(f"⚠️ Failed to auto-quarantine {mac}: {e}")
                            
                            # Fallback: Auto-isolate via port shutdown if configured
                            elif self.config.AUTO_ISOLATE_ROGUES and not self.config.ENABLE_VLAN_QUARANTINE:
                                action_taken = 'Port shutdown initiated'
                                self.isolate_device(mac, entry['port'], switch)
                            
                            # Send email notification for new rogue device
                            self.email_notifier.send_rogue_device_alert(device_info, action_taken)
                        
                        else:
                            # Existing rogue device - already notified, no need to spam
                            # Only log if status changed (e.g., moved ports or came back from quarantine)
                            if existing_device_check and existing_device_check.get('switch_port') != entry['port']:
                                self.db.log_event({
                                    'event_type': 'ROGUE_PORT_CHANGED',
                                    'severity': 'HIGH',
                                    'mac_address': mac,
                                    'ip_address': ip_address,
                                    'switch_port': entry['port'],
                                    'description': f"Rogue device {mac} moved from port {existing_device_check.get('switch_port')} to {entry['port']}",
                                    'action_taken': 'Port change detected'
                                })
                                # Send notification about port change
                                self.email_notifier.send_rogue_device_alert(device_info, 'Port changed - requires attention')
                            
                            # Just update last_seen timestamp, don't spam notifications
                            print(f"ℹ️ Existing rogue device {mac} still present on port {entry['port']} - awaiting admin action")
                
                results['success'] = True
                
                # Always use DB statistics for accurate counts (scan may miss devices)
                db_stats = self.db.get_statistics()
                results['statistics'] = db_stats
                # Map database field names to scan result field names
                results['total_devices'] = db_stats.get('active_devices', 0)  # Active devices on network
                results['authorized'] = db_stats.get('authorized_devices', 0)
                results['rogues'] = db_stats.get('active_rogues', 0)  # Active rogues (not quarantined)

                self.latest_scan_results = results
                
                print(f"Scan complete: {results['total_devices']} devices found, "
                      f"{results['authorized']} authorized, {results['rogues']} rogues")
                
        except Exception as e:
            results['error'] = str(e)
            print(f"Scan error: {e}")
        
        return results
    
    def isolate_device(self, mac_address: str, port: str, switch: SwitchConnector = None) -> bool:
        """Isolate a rogue device by shutting down its port"""
        try:
            print(f"Isolating rogue device {mac_address} on port {port}")
            
            # Use provided switch connection or create new one
            should_disconnect = False
            if not switch:
                switch = SwitchConnector(
                    host=self.config.SWITCH_IP,
                    username=self.config.SWITCH_USERNAME,
                    password=self.config.SWITCH_PASSWORD
                )
                switch.connect()
                should_disconnect = True
            
            # Shutdown the port
            success = switch.shutdown_port(port)
            
            if success:
                # Log the action
                self.db.log_event({
                    'event_type': 'PORT_SHUTDOWN',
                    'severity': 'HIGH',
                    'mac_address': mac_address,
                    'switch_port': port,
                    'description': f"Automatically shut down port {port} due to rogue device",
                    'action_taken': 'Port shutdown successful'
                })
                
                # Update device status
                conn = self.db.get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    'UPDATE devices SET status = "isolated" WHERE mac_address = ?',
                    (mac_address,)
                )
                conn.commit()
                conn.close()
                
                print(f"Successfully isolated device {mac_address}")
            
            if should_disconnect:
                switch.disconnect()
            
            return success
            
        except Exception as e:
            print(f"Error isolating device: {e}")
            return False
    
    def restore_device(self, mac_address: str, port: str) -> bool:
        """Restore a previously isolated device"""
        try:
            with SwitchConnector(
                host=self.config.SWITCH_IP,
                username=self.config.SWITCH_USERNAME,
                password=self.config.SWITCH_PASSWORD
            ) as switch:
                
                success = switch.enable_port(port)
                
                if success:
                    self.db.log_event({
                        'event_type': 'PORT_ENABLED',
                        'severity': 'INFO',
                        'mac_address': mac_address,
                        'switch_port': port,
                        'description': f"Port {port} enabled for device {mac_address}",
                        'action_taken': 'Port enabled'
                    })
                    
                    # Update device status
                    conn = self.db.get_connection()
                    cursor = conn.cursor()
                    cursor.execute(
                        'UPDATE devices SET status = "active" WHERE mac_address = ?',
                        (mac_address,)
                    )
                    conn.commit()
                    conn.close()
                
                return success
        except Exception as e:
            print(f"Error restoring device: {e}")
            return False
    
    def _resolve_hostname(self, ip_address: str) -> str:
        """Attempt to resolve hostname from IP"""
        if ip_address == 'Unknown':
            return 'Unknown'
        
        try:
            import socket
            hostname = socket.gethostbyaddr(ip_address)[0]
            return hostname
        except:
            return 'Unknown'
    
    def _get_vendor_from_mac(self, mac_address: str) -> str:
        """Get vendor from MAC address OUI (first 3 octets)"""
        # Use enhanced vendor lookup module
        return VendorLookup.get_vendor(mac_address)
    
    def start_continuous_monitoring(self):
        """Start continuous monitoring in background"""
        if self.is_running:
            print("Monitoring is already running")
            return
        
        self.is_running = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        print("Continuous monitoring started")
    
    def stop_continuous_monitoring(self):
        """Stop continuous monitoring"""
        self.is_running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        print("Continuous monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.is_running:
            try:
                self.perform_scan()
            except Exception as e:
                print(f"Monitoring error: {e}")
            
            # Wait for next scan
            time.sleep(self.config.SCAN_INTERVAL_SECONDS)
    
    def get_latest_results(self) -> Dict:
        """Get results from latest scan"""
        return self.latest_scan_results
    
    def get_statistics(self) -> Dict:
        """Get system statistics"""
        return self.db.get_statistics()

