#!/usr/bin/env python3
"""
Check current email configuration
"""

from config import Config

def check_email_config():
    """Check current email configuration"""
    print("Current Email Configuration:")
    print("=" * 40)
    print(f"Enable Email Alerts: {Config.ENABLE_EMAIL_ALERTS}")
    print(f"SMTP Server: {Config.SMTP_SERVER}")
    print(f"SMTP Port: {Config.SMTP_PORT}")
    print(f"SMTP Username: {Config.SMTP_USERNAME}")
    print(f"SMTP Password: {'*' * len(Config.SMTP_PASSWORD) if Config.SMTP_PASSWORD else 'Not set'}")
    print(f"Email From: {Config.EMAIL_FROM}")
    print(f"Email To: {Config.EMAIL_TO}")
    print(f"Subject Prefix: {Config.EMAIL_SUBJECT_PREFIX}")
    
    print("\n" + "=" * 40)
    if Config.ENABLE_EMAIL_ALERTS:
        print("✅ Email alerts are ENABLED")
    else:
        print("❌ Email alerts are DISABLED")
        print("   Go to Settings → Email Notification Settings")
        print("   Check 'Enable Email Alerts' and save")
    
    if not Config.EMAIL_TO:
        print("❌ No recipient emails configured")
        print("   Add email addresses in 'Recipient Emails' field")
    
    if not Config.SMTP_USERNAME:
        print("❌ SMTP username not configured")
        print("   Fill in SMTP Username field")

if __name__ == "__main__":
    check_email_config()
