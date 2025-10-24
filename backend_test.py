__package__ = 'backend'

import decimal
from backend.dynamo.database_operations import AnomalyTransactions
from dotenv import load_dotenv
from decimal import Decimal
import json
import boto3
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


SMTP_HOST = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USER = os.environ.get('EMAIL_USER', 'your_default_user')
SMTP_PASSWORD = os.environ.get('EMAIL_PASSWORD', 'your_default_password')
ALERT_RECIPIENT = 'uetaifitness2025@gmail.com'
ALERTS_TABLE = 'alerts'

smtp_host = SMTP_HOST
smtp_port = SMTP_PORT
smtp_user = SMTP_USER
smtp_password = SMTP_PASSWORD
recipient = ALERT_RECIPIENT

load_dotenv()

def send_email(subject, body, to_email):
    sender_email = os.environ['EMAIL_USER']
    sender_password = os.environ['EMAIL_PASS']
    print(f'Information: {sender_email}, {sender_password}, {to_email}')

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        print("✅ Email sent.")
    except Exception as e:
        print("❌ Error sending email:", e)
    finally:
        server.quit()

def send_email_notification(alert_data):
        """Send email notification"""
        try:
            subject = f"🚨 Fraud Alert - {alert_data['severity'].upper()} - Transaction {alert_data['transaction_id']}"
            
            # Create HTML email body
            html_body = create_email_html(alert_data)
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = smtp_user
            msg['To'] = recipient
            
            # Attach HTML body
            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
            print(f"✅ Email notification sent for alert: {alert_data['alertID']}")
            
            logger.info(f"Email notification sent for alert: {alert_data['alertID']}")
            
        except Exception as e:
            logger.error(f"Error sending email notification: {str(e)}")
            # Don't raise - continue processing other notifications

    
def create_email_html(alert_data):
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

def lambda_handler(event, context):
    for record in event['Records']:
        # Message from SQS
        message = json.loads(record['body'])

        subject = f"🚨 Fraud Alert: Transaction {message.get('transactionID')}"
        body = f"Alert Details:\n\n{json.dumps(message, indent=2)}"
        to_email = os.environ['ALERT_RECEIVER']  # người nhận email cảnh báo

        send_email(subject, body, to_email)

    return {
        'statusCode': 200,
        'body': json.dumps('Alerts sent.')
    }

# Testing the email sending function
if __name__ == "__main__":
    load_dotenv()
    alert_data = {
        'alertID': '12345',
        'transaction_id': '12345',
        'fraud_score': 99.9,
        'detection_method': 'machine_learning',
        'detection_details': {
            'model_version': 'v1.0',
            'threshold': 0.8
        },
        'transaction_data': {
            'amount': 100.0,
            'currency': 'USD',
            'status': 'PENDING'
        },
        'timestamp': datetime.now().isoformat(),
        'severity': 'high'
    }

    send_email_notification(alert_data)