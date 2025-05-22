import pyotp
import hashlib
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app

def generate_otp_secret():
    """Generate a random secret for OTP"""
    return pyotp.random_base32()

def generate_otp(secret):
    """Generate a time-based OTP"""
    totp = pyotp.TOTP(secret)
    return totp.now()

def verify_otp(secret, otp):
    """Verify the provided OTP"""
    totp = pyotp.TOTP(secret)
    return totp.verify(otp)

def hash_password(password):
    """Hash a password for storing"""
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return salt.hex() + ':' + key.hex()

def verify_password(stored_password, provided_password):
    """Verify a stored password against one provided by user"""
    salt_hex, key_hex = stored_password.split(':')
    salt = bytes.fromhex(salt_hex)
    stored_key = bytes.fromhex(key_hex)
    new_key = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt, 100000)
    return new_key == stored_key

def send_email(to_email, subject, body):
    """Send an email (for OTP or password reset)"""
    # This is a placeholder. In a real application, you would use a proper email service
    # like SendGrid, Mailgun, or SMTP
    try:
        # Get email configuration from environment variables
        smtp_server = os.environ.get('SMTP_SERVER', 'smtp.example.com')
        smtp_port = int(os.environ.get('SMTP_PORT', 587))
        smtp_username = os.environ.get('SMTP_USERNAME', 'user@example.com')
        smtp_password = os.environ.get('SMTP_PASSWORD', 'password')
        from_email = os.environ.get('FROM_EMAIL', 'noreply@example.com')
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send email: {str(e)}")
        return False