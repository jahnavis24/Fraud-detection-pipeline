"""
Email notification service
"""
import json
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict
from .config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, ALERT_RECIPIENT

logger = logging.getLogger(__name__)


class EmailNotificationService:
    """Handles email notifications for fraud alerts"""
    
    def __init__(self):
        self.smtp_host = SMTP_HOST
        self.smtp_port = SMTP_PORT
        self.smtp_user = SMTP_USER
        self.smtp_password = SMTP_PASSWORD
        self.recipient = ALERT_RECIPIENT
    
    def send_email_notification(self, alert_data: Dict) -> None:
        """Send email notification"""
        try:
            subject = f"🚨 Fraud Alert - {alert_data['severity'].upper()} - Transaction {alert_data['transaction_id']}"
            
            # Create HTML email body
            html_body = self.create_email_html(alert_data)
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.smtp_user
            msg['To'] = self.recipient
            
            # Attach HTML body
            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email notification sent for alert: {alert_data['alertID']}")
            
        except Exception as e:
            logger.error(f"Error sending email notification: {str(e)}")
            # Don't raise - continue processing other notifications
    
    def create_email_html(self, alert_data: Dict) -> str:
        """Create HTML email body"""
        severity_colors = {
            'high': '#dc3545',
            'medium': '#ffc107',
            'low': '#28a745'
        }
        
        severity_color = severity_colors.get(alert_data['severity'], '#6c757d')
        
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background-color: {severity_color}; color: white; padding: 20px; text-align: center;">
                <h1>🚨 Fraud Alert Detected</h1>
                <h2>Severity: {alert_data['severity'].upper()}</h2>
            </div>
            
            <div style="padding: 20px; background-color: #f8f9fa;">
                <h3>Transaction Details</h3>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Transaction ID:</strong></td>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd;">{alert_data['transaction_id']}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Amount:</strong></td>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd;">${alert_data.get('transaction_data', {}).get('amt', 'N/A')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Fraud Score:</strong></td>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd;">{alert_data['fraud_score']:.2f}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Detection Method:</strong></td>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd;">{alert_data['detection_method']}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Timestamp:</strong></td>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd;">{alert_data['timestamp']}</td>
                    </tr>
                </table>
                
                <h3>Detection Details</h3>
                <div style="background-color: white; padding: 15px; border-radius: 5px; margin: 10px 0;">
                    <pre style="white-space: pre-wrap; font-family: monospace; font-size: 12px;">{json.dumps(alert_data['detection_details'], indent=2)}</pre>
                </div>
                
                <div style="margin-top: 20px; padding: 15px; background-color: #fff3cd; border-radius: 5px;">
                    <strong>⚠️ Action Required:</strong> Please review this transaction immediately and take appropriate action.
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
