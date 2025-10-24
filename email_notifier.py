"""
Email notification system for rogue device alerts
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, List
import traceback


class EmailNotifier:
    """Handles email notifications for security events"""
    
    def __init__(self, config):
        """Initialize email notifier with configuration"""
        self.config = config
        self.enabled = config.ENABLE_EMAIL_ALERTS
        self.smtp_server = config.SMTP_SERVER
        self.smtp_port = config.SMTP_PORT
        self.smtp_use_tls = config.SMTP_USE_TLS
        self.smtp_username = config.SMTP_USERNAME
        self.smtp_password = config.SMTP_PASSWORD
        self.email_from = config.EMAIL_FROM or config.SMTP_USERNAME
        self.email_to = config.EMAIL_TO if isinstance(config.EMAIL_TO, list) else [config.EMAIL_TO]
        self.subject_prefix = config.EMAIL_SUBJECT_PREFIX
    
    def send_rogue_device_alert(self, device_info: Dict, action_taken: str = "Pending") -> bool:
        """
        Send email alert for rogue device detection
        
        Args:
            device_info: Dictionary containing device details (mac, ip, port, etc.)
            action_taken: Action taken against the device
        
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        if not self.enabled:
            print("Email alerts disabled - skipping notification")
            return False
        
        if not self.email_to or not self.email_from:
            print("Email configuration incomplete - cannot send alert")
            return False
        
        try:
            # Prepare email content
            subject = f"{self.subject_prefix} Rogue Device Detected"
            
            # Create HTML email body
            html_body = self._create_rogue_alert_html(device_info, action_taken)
            
            # Create plain text version
            text_body = self._create_rogue_alert_text(device_info, action_taken)
            
            # Send email
            return self._send_email(subject, text_body, html_body)
            
        except Exception as e:
            print(f"Failed to send rogue device alert: {e}")
            traceback.print_exc()
            return False
    
    def send_quarantine_alert(self, device_info: Dict, vlan_id: int) -> bool:
        """
        Send email alert when device is quarantined
        
        Args:
            device_info: Dictionary containing device details
            vlan_id: Quarantine VLAN ID
        
        Returns:
            bool: True if email sent successfully
        """
        if not self.enabled:
            return False
        
        try:
            subject = f"{self.subject_prefix} Device Quarantined"
            
            html_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif;">
                <div style="background-color: #ff9800; padding: 20px; border-radius: 5px;">
                    <h2 style="color: white; margin: 0;">⚠️ Device Quarantined</h2>
                </div>
                <div style="padding: 20px;">
                    <p>An unauthorized device has been automatically quarantined.</p>
                    
                    <h3>Device Information:</h3>
                    <table style="border-collapse: collapse; width: 100%;">
                        <tr>
                            <td style="padding: 8px; border: 1px solid #ddd; background-color: #f2f2f2;"><strong>MAC Address:</strong></td>
                            <td style="padding: 8px; border: 1px solid #ddd;">{device_info.get('mac_address', 'Unknown')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border: 1px solid #ddd; background-color: #f2f2f2;"><strong>IP Address:</strong></td>
                            <td style="padding: 8px; border: 1px solid #ddd;">{device_info.get('ip_address', 'Unknown')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border: 1px solid #ddd; background-color: #f2f2f2;"><strong>Switch Port:</strong></td>
                            <td style="padding: 8px; border: 1px solid #ddd;">{device_info.get('switch_port', 'Unknown')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border: 1px solid #ddd; background-color: #f2f2f2;"><strong>Quarantine VLAN:</strong></td>
                            <td style="padding: 8px; border: 1px solid #ddd;">{vlan_id}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border: 1px solid #ddd; background-color: #f2f2f2;"><strong>Vendor:</strong></td>
                            <td style="padding: 8px; border: 1px solid #ddd;">{device_info.get('vendor', 'Unknown')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border: 1px solid #ddd; background-color: #f2f2f2;"><strong>Detected:</strong></td>
                            <td style="padding: 8px; border: 1px solid #ddd;">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</td>
                        </tr>
                    </table>
                    
                    <h3 style="color: #ff9800;">Action Taken:</h3>
                    <p>The device has been automatically moved to quarantine VLAN {vlan_id} to isolate it from the production network.</p>
                    
                    <h3>Next Steps:</h3>
                    <ol>
                        <li>Investigate the device to determine if it's legitimate</li>
                        <li>If authorized, add it to the authorized devices list</li>
                        <li>If malicious, keep quarantined and investigate further</li>
                    </ol>
                </div>
            </body>
            </html>
            """
            
            text_body = f"""
DEVICE QUARANTINED

An unauthorized device has been automatically quarantined.

Device Information:
-------------------
MAC Address: {device_info.get('mac_address', 'Unknown')}
IP Address: {device_info.get('ip_address', 'Unknown')}
Switch Port: {device_info.get('switch_port', 'Unknown')}
Quarantine VLAN: {vlan_id}
Vendor: {device_info.get('vendor', 'Unknown')}
Detected: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Action Taken:
The device has been automatically moved to quarantine VLAN {vlan_id}.

Next Steps:
1. Investigate the device to determine if it's legitimate
2. If authorized, add it to the authorized devices list
3. If malicious, keep quarantined and investigate further
            """
            
            return self._send_email(subject, text_body, html_body)
            
        except Exception as e:
            print(f"Failed to send quarantine alert: {e}")
            return False
    
    def _create_rogue_alert_html(self, device_info: Dict, action_taken: str) -> str:
        """Create HTML formatted email body for rogue device alert"""
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <div style="background-color: #dc3545; padding: 20px; border-radius: 5px;">
                <h2 style="color: white; margin: 0;">🚨 ROGUE DEVICE DETECTED</h2>
            </div>
            <div style="padding: 20px;">
                <p><strong>A new unauthorized device has been detected on your network!</strong></p>
                
                <h3>Device Information:</h3>
                <table style="border-collapse: collapse; width: 100%;">
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd; background-color: #f2f2f2;"><strong>MAC Address:</strong></td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{device_info.get('mac_address', 'Unknown')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd; background-color: #f2f2f2;"><strong>IP Address:</strong></td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{device_info.get('ip_address', 'Unknown')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd; background-color: #f2f2f2;"><strong>Hostname:</strong></td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{device_info.get('hostname', 'Unknown')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd; background-color: #f2f2f2;"><strong>Switch Port:</strong></td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{device_info.get('switch_port', 'Unknown')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd; background-color: #f2f2f2;"><strong>VLAN:</strong></td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{device_info.get('vlan', 'Unknown')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd; background-color: #f2f2f2;"><strong>Vendor:</strong></td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{device_info.get('vendor', 'Unknown')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd; background-color: #f2f2f2;"><strong>Detected:</strong></td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</td>
                    </tr>
                </table>
                
                <h3 style="color: #dc3545;">Action Taken:</h3>
                <p style="padding: 10px; background-color: #fff3cd; border-left: 4px solid #ffc107;">
                    {action_taken}
                </p>
                
                <h3>Recommended Actions:</h3>
                <ol>
                    <li>Verify if this is a legitimate device</li>
                    <li>Check physical location of switch port</li>
                    <li>Investigate network activity from this device</li>
                    <li>If legitimate, authorize the device in the system</li>
                    <li>If malicious, keep isolated and investigate further</li>
                </ol>
                
                <hr>
                <p style="color: #6c757d; font-size: 12px;">
                    This is an automated alert from the Rogue Device Detection System.<br>
                    Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                </p>
            </div>
        </body>
        </html>
        """
    
    def _create_rogue_alert_text(self, device_info: Dict, action_taken: str) -> str:
        """Create plain text email body for rogue device alert"""
        return f"""
ROGUE DEVICE DETECTED!
=====================

A new unauthorized device has been detected on your network!

Device Information:
-------------------
MAC Address: {device_info.get('mac_address', 'Unknown')}
IP Address: {device_info.get('ip_address', 'Unknown')}
Hostname: {device_info.get('hostname', 'Unknown')}
Switch Port: {device_info.get('switch_port', 'Unknown')}
VLAN: {device_info.get('vlan', 'Unknown')}
Vendor: {device_info.get('vendor', 'Unknown')}
Detected: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Action Taken:
{action_taken}

Recommended Actions:
1. Verify if this is a legitimate device
2. Check physical location of switch port
3. Investigate network activity from this device
4. If legitimate, authorize the device in the system
5. If malicious, keep isolated and investigate further

---
This is an automated alert from the Rogue Device Detection System.
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
    
    def _send_email(self, subject: str, text_body: str, html_body: str = None) -> bool:
        """
        Send email via SMTP
        
        Args:
            subject: Email subject
            text_body: Plain text email body
            html_body: HTML email body (optional)
        
        Returns:
            bool: True if sent successfully
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email_from
            msg['To'] = ', '.join(self.email_to)
            msg['Subject'] = subject
            
            # Attach plain text version
            msg.attach(MIMEText(text_body, 'plain'))
            
            # Attach HTML version if provided
            if html_body:
                msg.attach(MIMEText(html_body, 'html'))
            
            # Connect to SMTP server and send
            if self.smtp_use_tls:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            
            # Login if credentials provided
            if self.smtp_username and self.smtp_password:
                server.login(self.smtp_username, self.smtp_password)
            
            # Send email
            server.send_message(msg)
            server.quit()
            
            print(f"✅ Email alert sent successfully to {', '.join(self.email_to)}")
            return True
            
        except smtplib.SMTPAuthenticationError:
            print("❌ Email authentication failed - check SMTP username/password")
            return False
        except smtplib.SMTPException as e:
            print(f"❌ SMTP error: {e}")
            return False
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            traceback.print_exc()
            return False
    
    def test_connection(self) -> bool:
        """
        Test email configuration by sending a test email
        
        Returns:
            bool: True if test successful
        """
        if not self.enabled:
            print("Email alerts are disabled")
            return False
        
        subject = f"{self.subject_prefix} Test Email"
        text_body = f"""
This is a test email from the Rogue Device Detection System.

If you received this email, your email configuration is working correctly.

Configuration:
- SMTP Server: {self.smtp_server}:{self.smtp_port}
- TLS: {self.smtp_use_tls}
- From: {self.email_from}
- To: {', '.join(self.email_to)}

Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <div style="background-color: #28a745; padding: 20px; border-radius: 5px;">
                <h2 style="color: white; margin: 0;">✅ Test Email</h2>
            </div>
            <div style="padding: 20px;">
                <p>This is a test email from the Rogue Device Detection System.</p>
                <p>If you received this email, your email configuration is working correctly.</p>
                
                <h3>Configuration:</h3>
                <ul>
                    <li><strong>SMTP Server:</strong> {self.smtp_server}:{self.smtp_port}</li>
                    <li><strong>TLS:</strong> {self.smtp_use_tls}</li>
                    <li><strong>From:</strong> {self.email_from}</li>
                    <li><strong>To:</strong> {', '.join(self.email_to)}</li>
                </ul>
                
                <hr>
                <p style="color: #6c757d; font-size: 12px;">
                    Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                </p>
            </div>
        </body>
        </html>
        """
        
        return self._send_email(subject, text_body, html_body)

