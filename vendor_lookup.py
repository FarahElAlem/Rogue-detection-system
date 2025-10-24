"""
Enhanced Vendor Lookup Module
Identifies device manufacturers from MAC address OUI (Organizationally Unique Identifier)
"""

class VendorLookup:
    """Enhanced vendor identification from MAC addresses"""
    
    # Comprehensive OUI database (first 3 octets of MAC address)
    OUI_DATABASE = {
        # Virtual Machine Vendors
        '00:50:56': 'VMware',
        '00:0C:29': 'VMware',
        '00:05:69': 'VMware',
        '00:1C:14': 'VMware',
        '00:1C:42': 'Parallels',
        '08:00:27': 'Oracle VirtualBox',
        '00:15:5D': 'Microsoft Hyper-V',
        '00:03:FF': 'Microsoft Virtual PC',
        '52:54:00': 'QEMU/KVM',
        
        # EVE-NG / Network Simulation
        'AA:BB:CC': 'EVE-NG VPC',
        '50:00:00': 'EVE-NG',
        
        # Major Network Equipment Vendors
        '00:00:0C': 'Cisco Systems',
        '00:01:42': 'Cisco Systems',
        '00:01:43': 'Cisco Systems',
        '00:01:63': 'Cisco Systems',
        '00:01:64': 'Cisco Systems',
        '00:01:96': 'Cisco Systems',
        '00:01:97': 'Cisco Systems',
        '00:01:C7': 'Cisco Systems',
        '00:02:16': 'Cisco Systems',
        '00:02:17': 'Cisco Systems',
        '00:02:3D': 'Cisco Systems',
        '00:02:4A': 'Cisco Systems',
        '00:02:4B': 'Cisco Systems',
        '00:02:7D': 'Cisco Systems',
        '00:02:7E': 'Cisco Systems',
        '00:02:B9': 'Cisco Systems',
        '00:02:BA': 'Cisco Systems',
        '00:02:FC': 'Cisco Systems',
        '00:02:FD': 'Cisco Systems',
        '00:03:31': 'Cisco Systems',
        '00:03:32': 'Cisco Systems',
        '00:03:6B': 'Cisco Systems',
        '00:03:6C': 'Cisco Systems',
        '00:03:9F': 'Cisco Systems',
        '00:03:A0': 'Cisco Systems',
        '00:03:E3': 'Cisco Systems',
        '00:03:E4': 'Cisco Systems',
        '00:03:FD': 'Cisco Systems',
        '00:03:FE': 'Cisco Systems',
        
        # HP/Hewlett-Packard
        '00:00:0D': 'Hewlett Packard',
        '00:01:E6': 'Hewlett Packard',
        '00:01:E7': 'Hewlett Packard',
        '00:02:A5': 'Hewlett Packard',
        '00:08:02': 'Hewlett Packard',
        '00:10:83': 'Hewlett Packard',
        '00:11:0A': 'Hewlett Packard',
        '00:11:85': 'Hewlett Packard',
        '00:12:79': 'Hewlett Packard',
        '00:13:21': 'Hewlett Packard',
        '00:14:38': 'Hewlett Packard',
        '00:14:C2': 'Hewlett Packard',
        '00:15:60': 'Hewlett Packard',
        '00:16:35': 'Hewlett Packard',
        '00:17:08': 'Hewlett Packard',
        '00:17:A4': 'Hewlett Packard',
        '00:18:71': 'Hewlett Packard',
        '00:18:FE': 'Hewlett Packard',
        '00:19:BB': 'Hewlett Packard',
        '00:1A:4B': 'Hewlett Packard',
        '00:1B:3F': 'Hewlett Packard',
        '00:1B:78': 'Hewlett Packard',
        '00:1C:2E': 'Hewlett Packard',
        '00:1C:C4': 'Hewlett Packard',
        '00:1E:0B': 'Hewlett Packard',
        
        # Dell
        '00:01:02': 'Dell',
        '00:06:5B': 'Dell',
        '00:08:74': 'Dell',
        '00:0B:DB': 'Dell',
        '00:0D:56': 'Dell',
        '00:0F:1F': 'Dell',
        '00:11:43': 'Dell',
        '00:12:3F': 'Dell',
        '00:13:72': 'Dell',
        '00:14:22': 'Dell',
        '00:15:C5': 'Dell',
        '00:16:F0': 'Dell',
        '00:18:8B': 'Dell',
        '00:19:B9': 'Dell',
        '00:1A:A0': 'Dell',
        '00:1C:23': 'Dell',
        '00:1D:09': 'Dell',
        '00:1E:4F': 'Dell',
        '00:21:70': 'Dell',
        '00:21:9B': 'Dell',
        '00:22:19': 'Dell',
        '00:23:AE': 'Dell',
        '00:24:E8': 'Dell',
        '00:25:64': 'Dell',
        '00:26:B9': 'Dell',
        
        # Apple
        '00:03:93': 'Apple',
        '00:05:02': 'Apple',
        '00:0A:27': 'Apple',
        '00:0A:95': 'Apple',
        '00:0D:93': 'Apple',
        '00:10:FA': 'Apple',
        '00:11:24': 'Apple',
        '00:13:E4': 'Apple',
        '00:14:51': 'Apple',
        '00:16:CB': 'Apple',
        '00:17:F2': 'Apple',
        '00:19:E3': 'Apple',
        '00:1B:63': 'Apple',
        '00:1C:B3': 'Apple',
        '00:1D:4F': 'Apple',
        '00:1E:52': 'Apple',
        '00:1E:C2': 'Apple',
        '00:1F:5B': 'Apple',
        '00:1F:F3': 'Apple',
        '00:21:E9': 'Apple',
        '00:22:41': 'Apple',
        '00:23:12': 'Apple',
        '00:23:32': 'Apple',
        '00:23:6C': 'Apple',
        '00:23:DF': 'Apple',
        '00:24:36': 'Apple',
        '00:25:00': 'Apple',
        '00:25:4B': 'Apple',
        '00:25:BC': 'Apple',
        '00:26:08': 'Apple',
        '00:26:4A': 'Apple',
        '00:26:B0': 'Apple',
        '00:26:BB': 'Apple',
        
        # Lenovo/IBM
        '00:02:55': 'IBM',
        '00:04:AC': 'IBM',
        '00:09:6B': 'IBM',
        '00:0E:7F': 'Lenovo',
        '00:11:25': 'Lenovo',
        '00:13:CE': 'Lenovo',
        '00:16:41': 'Lenovo',
        '00:17:31': 'Lenovo',
        '00:19:D1': 'Lenovo',
        '00:1C:25': 'Lenovo',
        '00:1E:37': 'Lenovo',
        '00:21:5A': 'Lenovo',
        '00:23:7D': 'Lenovo',
        '00:26:55': 'Lenovo',
        '5C:F9:DD': 'Lenovo',
        '68:F7:28': 'Lenovo',
        '74:E5:43': 'Lenovo',
        
        # Asus
        '00:0E:A6': 'Asus',
        '00:11:2F': 'Asus',
        '00:13:D4': 'Asus',
        '00:15:F2': 'Asus',
        '00:17:31': 'Asus',
        '00:19:21': 'Asus',
        '00:1A:92': 'Asus',
        '00:1B:FC': 'Asus',
        '00:1D:60': 'Asus',
        '00:1E:8C': 'Asus',
        '00:22:15': 'Asus',
        '00:23:54': 'Asus',
        '00:24:8C': 'Asus',
        '00:25:D3': 'Asus',
        '00:26:18': 'Asus',
        
        # Samsung
        '00:00:F0': 'Samsung',
        '00:02:78': 'Samsung',
        '00:07:AB': 'Samsung',
        '00:09:18': 'Samsung',
        '00:0D:AE': 'Samsung',
        '00:12:47': 'Samsung',
        '00:12:FB': 'Samsung',
        '00:13:77': 'Samsung',
        '00:15:99': 'Samsung',
        '00:16:32': 'Samsung',
        '00:16:6B': 'Samsung',
        '00:16:6C': 'Samsung',
        '00:17:C9': 'Samsung',
        '00:17:D5': 'Samsung',
        '00:18:AF': 'Samsung',
        '00:1A:8A': 'Samsung',
        '00:1B:98': 'Samsung',
        '00:1C:43': 'Samsung',
        '00:1D:25': 'Samsung',
        '00:1E:7D': 'Samsung',
        '00:1F:CD': 'Samsung',
        '00:21:19': 'Samsung',
        '00:21:4C': 'Samsung',
        '00:23:39': 'Samsung',
        '00:23:D6': 'Samsung',
        '00:24:90': 'Samsung',
        '00:25:38': 'Samsung',
        '00:26:37': 'Samsung',
        
        # TP-Link
        '00:27:19': 'TP-Link',
        '14:CF:92': 'TP-Link',
        '1C:3B:F3': 'TP-Link',
        '30:B5:C2': 'TP-Link',
        '50:C7:BF': 'TP-Link',
        '64:70:02': 'TP-Link',
        '74:DA:38': 'TP-Link',
        '90:F6:52': 'TP-Link',
        'A0:F3:C1': 'TP-Link',
        'C0:4A:00': 'TP-Link',
        'E8:94:F6': 'TP-Link',
        'EC:08:6B': 'TP-Link',
        'F4:EC:38': 'TP-Link',
        
        # Raspberry Pi
        'B8:27:EB': 'Raspberry Pi Foundation',
        'DC:A6:32': 'Raspberry Pi Foundation',
        'E4:5F:01': 'Raspberry Pi Foundation',
        '28:CD:C1': 'Raspberry Pi Foundation',
        
        # Intel
        '00:02:B3': 'Intel',
        '00:03:47': 'Intel',
        '00:04:23': 'Intel',
        '00:07:E9': 'Intel',
        '00:0C:F1': 'Intel',
        '00:0E:0C': 'Intel',
        '00:11:11': 'Intel',
        '00:12:F0': 'Intel',
        '00:13:02': 'Intel',
        '00:13:20': 'Intel',
        '00:13:CE': 'Intel',
        '00:13:E8': 'Intel',
        '00:15:00': 'Intel',
        '00:15:17': 'Intel',
        '00:16:6F': 'Intel',
        '00:16:76': 'Intel',
        '00:16:EA': 'Intel',
        '00:16:EB': 'Intel',
        '00:18:DE': 'Intel',
        '00:19:D1': 'Intel',
        '00:19:D2': 'Intel',
        '00:1B:21': 'Intel',
        '00:1B:77': 'Intel',
        '00:1C:BF': 'Intel',
        '00:1D:E0': 'Intel',
        '00:1D:E1': 'Intel',
        '00:1E:67': 'Intel',
        '00:1F:3A': 'Intel',
        '00:1F:3B': 'Intel',
        '00:1F:3C': 'Intel',
    }
    
    @classmethod
    def get_vendor(cls, mac_address: str) -> str:
        """
        Get vendor name from MAC address
        
        Args:
            mac_address: MAC address in format AA:BB:CC:DD:EE:FF
            
        Returns:
            Vendor name or 'Unknown'
        """
        if not mac_address or len(mac_address) < 8:
            return 'Unknown'
        
        # Extract OUI (first 3 octets)
        oui = mac_address[:8].upper()
        
        # Look up in database
        vendor = cls.OUI_DATABASE.get(oui)
        
        if vendor:
            return vendor
        
        # Special cases for EVE-NG and lab environments
        if mac_address.upper().startswith('AA:BB:CC'):
            return 'EVE-NG VPC'
        elif mac_address.upper().startswith('50:00:00'):
            return 'EVE-NG Device'
        elif mac_address.upper().startswith('52:54:00'):
            return 'QEMU/KVM Virtual Machine'
        
        return 'Unknown'
    
    @classmethod
    def is_virtual_machine(cls, mac_address: str) -> bool:
        """Check if MAC address belongs to a virtual machine"""
        vm_prefixes = [
            '00:50:56',  # VMware
            '00:0C:29',  # VMware
            '00:05:69',  # VMware
            '00:1C:14',  # VMware
            '00:1C:42',  # Parallels
            '08:00:27',  # VirtualBox
            '00:15:5D',  # Hyper-V
            '00:03:FF',  # Virtual PC
            '52:54:00',  # QEMU/KVM
            'AA:BB:CC',  # EVE-NG
            '50:00:00',  # EVE-NG
        ]
        
        oui = mac_address[:8].upper()
        return any(oui.startswith(prefix) for prefix in vm_prefixes)
    
    @classmethod
    def get_device_category(cls, mac_address: str) -> str:
        """Categorize device type based on vendor"""
        vendor = cls.get_vendor(mac_address)
        
        vm_vendors = ['VMware', 'VirtualBox', 'Hyper-V', 'QEMU', 'EVE-NG', 'Virtual']
        network_vendors = ['Cisco', 'Juniper', 'Arista', 'HP', 'Dell']
        mobile_vendors = ['Apple', 'Samsung']
        iot_vendors = ['Raspberry Pi', 'TP-Link']
        
        if any(vm in vendor for vm in vm_vendors):
            return 'Virtual Machine'
        elif any(nw in vendor for nw in network_vendors):
            return 'Network Equipment'
        elif any(mb in vendor for mb in mobile_vendors):
            return 'Mobile/Workstation'
        elif any(iot in vendor for iot in iot_vendors):
            return 'IoT Device'
        else:
            return 'Unknown'


# For backward compatibility with existing code
def get_vendor_from_mac(mac_address: str) -> str:
    """Legacy function for backward compatibility"""
    return VendorLookup.get_vendor(mac_address)

