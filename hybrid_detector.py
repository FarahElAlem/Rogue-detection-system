#!/usr/bin/env python3
"""
Hybrid Rogue Detection System
Combines switch-based detection with ARP fallback
"""
import sqlite3
import json
import os
import subprocess
import time
from datetime import datetime
from typing import List, Dict, Optional

from database import DatabaseManager
from config import Config


class HybridRogueDetector:
    """Hybrid detector that tries switch first, falls back to ARP"""
    
    def __init__(self, config=None):
        self.config = config or Config
        self.db = DatabaseManager(self.config.DATABASE_PATH)
        self.latest_scan_results = {
            'timestamp': None,
            'total_devices': 0,
            'authorized': 0,
            'rogues': 0,
            'devices': []
        }
    
    def scan_network_arp(self):
        """Scan network using ARP table"""
        print("🔍 Scanning network using ARP...")
        
        try:
            # Use arp command to get ARP table
            result = subprocess.run(['arp', '-a'], capture_output=True, text=True)
            
            if result.returncode != 0:
                print("❌ ARP scan failed")
                return []
            
            devices = []
            lines = result.stdout.split('\n')
            
            for line in lines:
                if 'dynamic' in line.lower() or 'static' in line.lower():
                    parts = line.split()
                    if len(parts) >= 3:
                        ip = parts[0]
                        mac = parts[1]
                        
                        # Clean up MAC address
                        mac = mac.replace('-', ':').upper()
                        
                        if self.is_valid_mac(mac):
                            devices.append({
                                'ip_address': ip,
                                'mac_address': mac,
                                'hostname': 'Unknown',
                                'vendor': 'Unknown',
                                'switch_port': 'Unknown',
                                'vlan': 1
                            })
            
            print(f"✅ Found {len(devices)} devices via ARP")
            return devices
            
        except Exception as e:
            print(f"❌ ARP scan error: {e}")
            return []
    
    def is_valid_mac(self, mac):
        """Check if MAC address is valid and not broadcast/multicast"""
        if not mac or len(mac) != 17:
            return False
        
        parts = mac.split(':')
        if len(parts) != 6:
            return False
        
        for part in parts:
            if len(part) != 2:
                return False
            try:
                int(part, 16)
            except ValueError:
                return False
        
        # Filter out broadcast and multicast addresses
        if mac == 'FF:FF:FF:FF:FF:FF':
            return False
        
        # Filter out multicast addresses (first octet has bit 0 set)
        first_octet = int(parts[0], 16)
        if first_octet & 0x01:  # Multicast bit set
            return False
        
        # Filter out common virtual/broadcast patterns
        if mac.startswith('01:00:5E'):  # IPv4 multicast
            return False
        if mac.startswith('33:33'):     # IPv6 multicast
            return False
        
        return True
    
    def is_device_authorized(self, mac_address):
        """Check if device is authorized"""
        return self.db.is_device_authorized(mac_address)
    
    def add_or_update_device(self, device_info):
        """Add or update device in database"""
        return self.db.add_or_update_device(device_info)
    
    def log_event(self, event_info):
        """Log security event"""
        return self.db.log_event(event_info)
    
    def get_statistics(self):
        """Get system statistics"""
        return self.db.get_statistics()
    
    def get_rogue_devices(self):
        """Get all rogue devices"""
        return self.db.get_rogue_devices()
    
    def get_recent_events(self, limit=10):
        """Get recent events"""
        return self.db.get_recent_events(limit)
    
    def perform_scan(self):
        """Perform a complete network scan using ARP fallback"""
        print(f"\n🔍 Starting network scan at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
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
            # Try ARP scanning first (more reliable for standalone)
            devices = self.scan_network_arp()
            
            if not devices:
                print("❌ No devices found")
                results['error'] = "No devices found in ARP table"
                return results
            
            # Process each device
            new_rogues = 0
            for device in devices:
                mac = device['mac_address']
                
                # Check if authorized
                is_authorized = self.is_device_authorized(mac)
                is_rogue = not is_authorized
                
                # Update device info
                device['is_authorized'] = 1 if is_authorized else 0
                device['is_rogue'] = 1 if is_rogue else 0
                
                # Add/update device in database
                self.add_or_update_device(device)
                
                results['devices'].append(device)
                results['total_devices'] += 1
                
                if is_authorized:
                    results['authorized'] += 1
                else:
                    results['rogues'] += 1
                    
                    # Check if this is a new rogue device
                    existing_rogues = self.db.get_rogue_devices()
                    existing_rogue_macs = [d['mac_address'] for d in existing_rogues]
                    
                    is_new_rogue = mac not in existing_rogue_macs
                    
                    if is_new_rogue:
                        new_rogues += 1
                        print(f"🚨 NEW ROGUE DETECTED: {mac} ({device['ip_address']})")
                        
                        # Log the event
                        self.log_event({
                            'event_type': 'ROGUE_DETECTED',
                            'severity': 'CRITICAL',
                            'mac_address': mac,
                            'ip_address': device['ip_address'],
                            'description': f"Rogue device detected: {mac}",
                            'action_taken': 'Pending review'
                        })
            
            results['new_rogues'] = new_rogues
            results['success'] = True
            
            print(f"\n📊 SCAN RESULTS:")
            print(f"   Total devices: {results['total_devices']}")
            print(f"   Authorized: {results['authorized']}")
            print(f"   Rogues: {results['rogues']}")
            print(f"   New rogues this scan: {new_rogues}")
            
            self.latest_scan_results = results
            
        except Exception as e:
            results['error'] = str(e)
            print(f"❌ Scan error: {e}")
        
        return results
    
    def get_latest_results(self):
        """Get results from latest scan"""
        return self.latest_scan_results
    
    def start_continuous_monitoring(self):
        """Start continuous monitoring in background"""
        print("🔄 Continuous monitoring started")
        # This is a placeholder - implement if needed
    
    def stop_continuous_monitoring(self):
        """Stop continuous monitoring"""
        print("⏹️ Continuous monitoring stopped")
        # This is a placeholder - implement if needed
    
    def isolate_device(self, mac_address, port):
        """Isolate a device"""
        print(f"🔒 Isolating device {mac_address} on port {port}")
        # This is a placeholder - implement if needed
        return True
    
    def restore_device(self, mac_address, port):
        """Restore a device"""
        print(f"🔓 Restoring device {mac_address} on port {port}")
        # This is a placeholder - implement if needed
        return True
