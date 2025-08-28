#!/usr/bin/env python3
"""
Email Integration for AI Customer Support
Supports SMTP sending and IMAP monitoring for incoming emails
"""

import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
import os
import time
import threading
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailIntegration:
    """Email integration for sending and receiving customer support emails"""
    
    def __init__(self, 
                 smtp_server: str,
                 smtp_port: int,
                 imap_server: str,
                 imap_port: int,
                 email_address: str,
                 password: str,
                 use_tls: bool = True):
        """
        Initialize email integration
        
        Args:
            smtp_server: SMTP server (e.g., smtp.gmail.com)
            smtp_port: SMTP port (587 for TLS, 465 for SSL)
            imap_server: IMAP server (e.g., imap.gmail.com)
            imap_port: IMAP port (993 for SSL)
            email_address: Your support email address
            password: Email password or app password
            use_tls: Whether to use TLS encryption
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.imap_server = imap_server
        self.imap_port = imap_port
        self.email_address = email_address
        self.password = password
        self.use_tls = use_tls
        
        # Test connections
        self.verify_smtp_connection()
        self.verify_imap_connection()
        
        # Email monitoring
        self.monitoring = False
        self.monitor_thread = None
    
    def verify_smtp_connection(self) -> bool:
        """Verify SMTP connection for sending emails"""
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            if self.use_tls:
                server.starttls()
            server.login(self.email_address, self.password)
            server.quit()
            logger.info("✅ SMTP connection verified")
            return True
        except Exception as e:
            logger.error(f"❌ SMTP connection failed: {e}")
            return False
    
    def verify_imap_connection(self) -> bool:
        """Verify IMAP connection for reading emails"""
        try:
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(self.email_address, self.password)
            mail.select('inbox')
            mail.logout()
            logger.info("✅ IMAP connection verified")
            return True
        except Exception as e:
            logger.error(f"❌ IMAP connection failed: {e}")
            return False
    
    def send_email(self, 
                   to_email: str, 
                   subject: str, 
                   message: str, 
                   reply_to: Optional[str] = None,
                   html_content: Optional[str] = None) -> Dict[str, Any]:
        """
        Send email response
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            message: Plain text message
            reply_to: Optional reply-to email
            html_content: Optional HTML version of message
            
        Returns:
            Dict with success status and details
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email_address
            msg['To'] = to_email
            msg['Subject'] = subject
            
            if reply_to:
                msg['Reply-To'] = reply_to
            
            # Add plain text part
            text_part = MIMEText(message, 'plain')
            msg.attach(text_part)
            
            # Add HTML part if provided
            if html_content:
                html_part = MIMEText(html_content, 'html')
                msg.attach(html_part)
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            if self.use_tls:
                server.starttls()
            server.login(self.email_address, self.password)
            
            text = msg.as_string()
            server.sendmail(self.email_address, to_email, text)
            server.quit()
            
            logger.info(f"✅ Email sent to {to_email}")
            return {
                'success': True,
                'to': to_email,
                'subject': subject,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to send email: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_unread_emails(self) -> List[Dict[str, Any]]:
        """Get unread emails from inbox"""
        try:
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(self.email_address, self.password)
            mail.select('inbox')
            
            # Search for unread emails
            status, messages = mail.search(None, 'UNSEEN')
            
            emails = []
            if status == 'OK':
                for num in messages[0].split():
                    status, msg_data = mail.fetch(num, '(RFC822)')
                    
                    if status == 'OK':
                        email_body = msg_data[0][1]
                        email_message = email.message_from_bytes(email_body)
                        
                        # Extract email details
                        subject = decode_header(email_message["Subject"])[0][0]
                        if isinstance(subject, bytes):
                            subject = subject.decode()
                        
                        from_email = email_message.get("From")
                        date = email_message.get("Date")
                        
                        # Extract email content
                        content = self.extract_email_content(email_message)
                        
                        emails.append({
                            'id': num.decode(),
                            'from': from_email,
                            'subject': subject,
                            'date': date,
                            'content': content,
                            'timestamp': datetime.now().isoformat()
                        })
            
            mail.logout()
            return emails
            
        except Exception as e:
            logger.error(f"❌ Failed to get emails: {e}")
            return []
    
    def extract_email_content(self, email_message) -> str:
        """Extract text content from email message"""
        content = ""
        
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    body = part.get_payload(decode=True).decode()
                    content += body
        else:
            body = email_message.get_payload(decode=True).decode()
            content = body
        
        return content.strip()
    
    def mark_as_read(self, email_id: str) -> bool:
        """Mark email as read"""
        try:
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(self.email_address, self.password)
            mail.select('inbox')
            
            mail.store(email_id, '+FLAGS', '\\Seen')
            mail.logout()
            
            return True
        except Exception as e:
            logger.error(f"❌ Failed to mark email as read: {e}")
            return False
    
    def start_email_monitoring(self, callback_function: Callable, check_interval: int = 30):
        """
        Start monitoring for new emails
        
        Args:
            callback_function: Function to call when new email arrives
            check_interval: How often to check for emails (seconds)
        """
        def monitor_emails():
            logger.info("📧 Starting email monitoring...")
            self.monitoring = True
            
            while self.monitoring:
                try:
                    unread_emails = self.get_unread_emails()
                    
                    for email_data in unread_emails:
                        logger.info(f"📧 New email from {email_data['from']}: {email_data['subject']}")
                        
                        # Call the callback function with email data
                        callback_function(email_data)
                        
                        # Mark as read
                        self.mark_as_read(email_data['id'])
                    
                    time.sleep(check_interval)
                    
                except Exception as e:
                    logger.error(f"❌ Email monitoring error: {e}")
                    time.sleep(check_interval)
        
        self.monitor_thread = threading.Thread(target=monitor_emails)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def stop_email_monitoring(self):
        """Stop email monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
        logger.info("📧 Email monitoring stopped")
    
    def create_html_response(self, message: str, company_name: str = "AI Support") -> str:
        """Create HTML formatted email response"""
        html_template = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                    <h2 style="color: #2c3e50; margin: 0;">{company_name} Customer Support</h2>
                </div>
                
                <div style="background-color: white; padding: 20px; border-radius: 8px; border: 1px solid #e9ecef;">
                    <p style="margin-bottom: 20px;">Thank you for contacting us! Here's our response:</p>
                    
                    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; border-left: 4px solid #007bff;">
                        {message.replace(chr(10), '<br>')}
                    </div>
                    
                    <p style="margin-top: 20px; font-size: 14px; color: #6c757d;">
                        This response was generated by our AI customer support system. 
                        If you need further assistance, please reply to this email.
                    </p>
                </div>
                
                <div style="text-align: center; margin-top: 20px; font-size: 12px; color: #6c757d;">
                    <p>Powered by AI Customer Support System</p>
                </div>
            </div>
        </body>
        </html>
        """
        return html_template


def create_email_integration(provider: str = "gmail", **kwargs) -> Optional[EmailIntegration]:
    """
    Factory function to create email integration
    
    Args:
        provider: 'gmail', 'outlook', or 'custom'
        **kwargs: Provider-specific configuration
    """
    try:
        if provider == "gmail":
            return EmailIntegration(
                smtp_server="smtp.gmail.com",
                smtp_port=587,
                imap_server="imap.gmail.com",
                imap_port=993,
                email_address=kwargs.get('email_address'),
                password=kwargs.get('password'),
                use_tls=True
            )
        elif provider == "outlook":
            return EmailIntegration(
                smtp_server="smtp-mail.outlook.com",
                smtp_port=587,
                imap_server="outlook.office365.com",
                imap_port=993,
                email_address=kwargs.get('email_address'),
                password=kwargs.get('password'),
                use_tls=True
            )
        elif provider == "custom":
            return EmailIntegration(**kwargs)
        else:
            logger.error(f"❌ Unknown email provider: {provider}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Failed to create email integration: {e}")
        return None


# Example usage and testing
if __name__ == "__main__":
    # Example configuration (use environment variables in production)
    config = {
        'email_address': os.getenv('SUPPORT_EMAIL', 'your-support@gmail.com'),
        'password': os.getenv('EMAIL_PASSWORD', 'your-app-password')
    }
    
    # Create email integration
    email_integration = create_email_integration('gmail', **config)
    
    if email_integration:
        # Test sending email (uncomment to test)
        # result = email_integration.send_email(
        #     to_email='test@example.com',
        #     subject='Test AI Support Response',
        #     message='This is a test response from your AI customer support system.',
        #     html_content=email_integration.create_html_response(
        #         'This is a test response from your AI customer support system.',
        #         'Test Company'
        #     )
        # )
        # print(f"Send result: {result}")
        
        print("✅ Email integration ready!")
    else:
        print("❌ Failed to initialize email integration")