"""
Switch connection and management for Cisco switches
"""
from netmiko import ConnectHandler
from typing import List, Dict, Optional
import re


class SwitchConnector:
    """Manages connection to Cisco switch and retrieves device information"""
    
    def __init__(self, host, username, password, device_type="cisco_ios", port=22, secret=""):
        self.host = host
        self.username = username
        self.password = password
        self.device_type = device_type
        self.port = port
        self.secret = secret
        self.connection = None
    
    def connect(self) -> bool:
        """Establish SSH connection to switch"""
        try:
            self.connection = ConnectHandler(
                device_type=self.device_type,
                host=self.host,
                username=self.username,
                password=self.password,
                port=self.port,
                secret=self.secret if self.secret else "",
                timeout=10,
                session_timeout=30
            )
            
            # Enter enable mode if we have a secret
            if self.secret:
                try:
                    self.connection.enable()
                    print(f"Entered enable mode on {self.host}")
                except:
                    print(f"Warning: Could not enter enable mode on {self.host}")
            
            return True
        except Exception as e:
            print(f"Failed to connect to switch: {e}")
            return False
    
    def disconnect(self):
        """Close SSH connection"""
        if self.connection:
            self.connection.disconnect()
            self.connection = None
    
    def get_mac_address_table(self) -> List[Dict]:
        """Get MAC address table from switch"""
        if not self.connection:
            if not self.connect():
                return []
        
        try:
            output = self.connection.send_command("show mac address-table")
            return self._parse_mac_table(output)
        except Exception as e:
            print(f"Error getting MAC table: {e}")
            return []
    
    def _parse_mac_table(self, output: str) -> List[Dict]:
        """Parse MAC address table output"""
        devices = []
        
        # Pattern for Cisco MAC address table
        # Example: 1    aabb.cc00.1000    DYNAMIC     Et0/1
        pattern = r'(\d+)\s+([0-9a-f.]+)\s+(\w+)\s+([\w/]+)'
        
        for line in output.split('\n'):
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                vlan, mac, entry_type, port = match.groups()
                
                # Normalize MAC address format
                mac = mac.replace('.', '').upper()
                mac = ':'.join([mac[i:i+2] for i in range(0, 12, 2)])
                
                devices.append({
                    'vlan': int(vlan),
                    'mac_address': mac,
                    'type': entry_type,
                    'port': port
                })
        
        return devices
    
    def get_arp_table(self) -> List[Dict]:
        """Get ARP table from switch"""
        if not self.connection:
            if not self.connect():
                return []
        
        try:
            output = self.connection.send_command("show arp")
            return self._parse_arp_table(output)
        except Exception as e:
            print(f"Error getting ARP table: {e}")
            return []
    
    def _parse_arp_table(self, output: str) -> List[Dict]:
        """Parse ARP table output"""
        entries = []
        
        # Pattern for Cisco ARP table
        # Example: Internet  192.168.1.10         0   aabb.cc00.1000  ARPA   Vlan1
        pattern = r'Internet\s+(\d+\.\d+\.\d+\.\d+)\s+\d+\s+([0-9a-f.]+)\s+\w+\s+([\w/]+)'
        
        for line in output.split('\n'):
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                ip, mac, interface = match.groups()
                
                # Normalize MAC address format
                mac = mac.replace('.', '').upper()
                mac = ':'.join([mac[i:i+2] for i in range(0, 12, 2)])
                
                entries.append({
                    'ip_address': ip,
                    'mac_address': mac,
                    'interface': interface
                })
        
        return entries
    
    def shutdown_port(self, port_name: str) -> bool:
        """Shutdown a specific switch port"""
        if not self.connection:
            if not self.connect():
                return False
        
        try:
            commands = [
                f'interface {port_name}',
                'shutdown',
                'exit'
            ]
            
            output = self.connection.send_config_set(commands)
            self.connection.save_config()
            
            print(f"Port {port_name} has been shutdown")
            return True
        except Exception as e:
            print(f"Error shutting down port {port_name}: {e}")
            return False
    
    def change_port_vlan(self, port_name: str, vlan_id: int) -> bool:
        """Change port to a different VLAN"""
        if not self.connection:
            if not self.connect():
                return False
        
        try:
            commands = [
                f'interface {port_name}',
                'switchport mode access',
                f'switchport access vlan {vlan_id}',
                'exit'
            ]
            
            output = self.connection.send_config_set(commands)
            self.connection.save_config()
            
            print(f"Port {port_name} moved to VLAN {vlan_id}")
            return True
        except Exception as e:
            print(f"Error changing port {port_name} to VLAN {vlan_id}: {e}")
            return False
    
    def get_port_vlan(self, port_name: str) -> Optional[int]:
        """Get the current VLAN of a port"""
        if not self.connection:
            if not self.connect():
                return None
        
        try:
            output = self.connection.send_command(f"show interface {port_name} switchport")
            
            # Parse VLAN from output
            for line in output.split('\n'):
                if 'Access Mode VLAN' in line or 'Operational Mode VLAN' in line:
                    parts = line.split(':')
                    if len(parts) > 1:
                        vlan_info = parts[1].strip().split()[0]
                        try:
                            return int(vlan_info)
                        except:
                            continue
            
            return None
        except Exception as e:
            print(f"Error getting VLAN for port {port_name}: {e}")
            return None
    
    def quarantine_port_vlan(self, port_name: str, quarantine_vlan: int) -> bool:
        """Move port to quarantine VLAN (keeps port enabled, just isolates to different VLAN)"""
        if not self.connection:
            if not self.connect():
                return False
        
        try:
            commands = [
                f'interface {port_name}',
                'switchport mode access',
                f'switchport access vlan {quarantine_vlan}',
                'no shutdown',  # Ensure port stays up
                'exit'
            ]
            
            output = self.connection.send_config_set(commands)
            self.connection.save_config()
            
            print(f"Port {port_name} quarantined to VLAN {quarantine_vlan}")
            return True
        except Exception as e:
            print(f"Error quarantining port {port_name} to VLAN {quarantine_vlan}: {e}")
            return False
    
    def enable_port(self, port_name: str) -> bool:
        """Enable a specific switch port"""
        if not self.connection:
            if not self.connect():
                return False
        
        try:
            commands = [
                f'interface {port_name}',
                'no shutdown',
                'exit'
            ]
            
            output = self.connection.send_config_set(commands)
            self.connection.save_config()
            
            print(f"Port {port_name} has been enabled")
            return True
        except Exception as e:
            print(f"Error enabling port {port_name}: {e}")
            return False
    
    def get_interface_status(self, port_name: str = None) -> List[Dict]:
        """Get status of interfaces"""
        if not self.connection:
            if not self.connect():
                return []
        
        try:
            if port_name:
                # Get specific port status
                output = self.connection.send_command(f"show interface {port_name}")
                return self._parse_single_interface_status(output, port_name)
            else:
                # Get all ports status
                output = self.connection.send_command("show interfaces status")
                return self._parse_interface_status(output)
        except Exception as e:
            print(f"Error getting interface status: {e}")
            return []
    
    def _parse_interface_status(self, output: str) -> List[Dict]:
        """Parse interface status output from 'show interfaces status'"""
        interfaces = []
        
        # Typical format:
        # Port      Name               Status       Vlan       Duplex  Speed Type
        # Gi0/0     to-router          connected    1          a-full  a-1000 RJ45
        # Gi0/1                        notconnect   1            auto    auto RJ45
        # Gi0/2                        disabled     1            auto    auto RJ45
        
        lines = output.split('\n')
        
        for line in lines:
            # Look for interface lines (Ethernet, GigabitEthernet, FastEthernet)
            # Enhanced pattern to catch all interface types
            interface_patterns = [
                'Et0/', 'Et1/', 'Et2/', 'Et3/', 'Et4/', 'Et5/', 'Et6/', 'Et7/',
                'Gi0/', 'Gi1/', 'Gi2/', 'Gi3/', 'Gi4/', 'Gi5/', 'Gi6/', 'Gi7/',
                'Fa0/', 'Fa1/', 'Fa2/', 'Fa3/', 'Fa4/', 'Fa5/', 'Fa6/', 'Fa7/',
                'Te0/', 'Te1/', 'Te2/', 'Te3/', 'Te4/', 'Te5/', 'Te6/', 'Te7/',
                'Po0', 'Po1', 'Po2', 'Po3', 'Po4', 'Po5', 'Po6', 'Po7'
            ]
            
            if any(pattern in line for pattern in interface_patterns):
                parts = line.split()
                
                if len(parts) >= 3:
                    # Extract port name
                    port = parts[0]
                    
                    # Find status and VLAN (status is typically connected/notconnect/disabled)
                    status = 'unknown'
                    vlan = 'unknown'
                    
                    for i, part in enumerate(parts):
                        if part.lower() in ['connected', 'notconnect', 'disabled', 'notconnected']:
                            status = part.lower()
                            # VLAN is usually the next field after status
                            if i + 1 < len(parts):
                                vlan = parts[i + 1]
                            break
                    
                    interfaces.append({
                        'port': port,
                        'status': status,
                        'vlan': vlan
                    })
        
        return interfaces
    
    def _parse_single_interface_status(self, output: str, port_name: str) -> List[Dict]:
        """Parse single interface detailed status"""
        status_info = {
            'port': port_name,
            'admin_status': 'unknown',
            'operational_status': 'unknown',
            'description': ''
        }
        
        for line in output.split('\n'):
            if 'administratively down' in line.lower():
                status_info['admin_status'] = 'disabled'
                status_info['operational_status'] = 'down'
            elif 'line protocol is up' in line.lower():
                status_info['admin_status'] = 'enabled'
                status_info['operational_status'] = 'up'
            elif 'line protocol is down' in line.lower():
                status_info['admin_status'] = 'enabled'
                status_info['operational_status'] = 'down'
        
        return [status_info]
    
    def get_port_details(self, port_name: str) -> Optional[Dict]:
        """Get detailed information about a specific port"""
        if not self.connection:
            if not self.connect():
                return None
        
        try:
            # Get interface details
            output = self.connection.send_command(f"show interface {port_name}")
            
            details = {
                'port': port_name,
                'admin_status': 'unknown',
                'operational_status': 'unknown',
                'speed': 'unknown',
                'duplex': 'unknown',
                'description': ''
            }
            
            for line in output.split('\n'):
                if 'administratively down' in line.lower():
                    details['admin_status'] = 'shutdown'
                elif 'is up' in line.lower() and 'line protocol' in line.lower():
                    details['admin_status'] = 'enabled'
                    details['operational_status'] = 'up'
                elif 'is down' in line.lower() and 'line protocol' in line.lower():
                    details['operational_status'] = 'down'
            
            return details
        except Exception as e:
            print(f"Error getting port details: {e}")
            return None
    
    def get_device_info(self) -> Optional[Dict]:
        """Get switch device information"""
        if not self.connection:
            if not self.connect():
                return None
        
        try:
            version_output = self.connection.send_command("show version")
            hostname_output = self.connection.send_command("show running-config | include hostname")
            
            # Basic parsing - can be enhanced
            info = {
                'hostname': self._extract_hostname(hostname_output),
                'version': 'Cisco IOS',
                'model': self._extract_model(version_output)
            }
            
            return info
        except Exception as e:
            print(f"Error getting device info: {e}")
            return None
    
    def _extract_hostname(self, output: str) -> str:
        """Extract hostname from config"""
        match = re.search(r'hostname\s+(\S+)', output)
        return match.group(1) if match else 'Unknown'
    
    def _extract_model(self, output: str) -> str:
        """Extract model from version output"""
        # Basic extraction - can be enhanced
        if 'IOSv' in output:
            return 'Cisco IOSv'
        elif 'vIOS' in output:
            return 'Cisco vIOS'
        return 'Cisco Switch'
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()

