"""
Alert processor for handling SQS messages
"""
import json
import logging
from datetime import datetime
from typing import Dict, List

from .data_handler import AlertDataHandler
from .email_service import EmailNotificationService

logger = logging.getLogger(__name__)


class AlertProcessor:
    """Processes fraud alerts from SQS queue"""
    
    def __init__(self):
        self.data_handler = AlertDataHandler()
        self.email_service = EmailNotificationService()
    
    def process_sqs_messages(self, records: List[Dict]) -> int:
        """Process SQS messages containing fraud alerts"""
        processed_count = 0
        
        for record in records:
            try:
                # Parse SQS message
                message_body = json.loads(record['body'])
                
                # Extract message attributes
                attributes = record.get('messageAttributes', {})
                severity = attributes.get('severity', {}).get('stringValue', 'medium')
                detection_method = attributes.get('detection_method', {}).get('stringValue', 'unknown')
                
                # Process the alert
                alert_data = {
                    'alertID': record['messageId'],
                    'transaction_id': message_body.get('transaction_id'),
                    'fraud_score': message_body.get('fraud_score'),
                    'detection_method': detection_method,
                    'detection_details': message_body.get('detection_details', {}),
                    'transaction_data': message_body.get('transaction_data', {}),
                    'timestamp': datetime.now().isoformat(),
                    'severity': severity
                }
                
                # Store alert in DynamoDB
                self.data_handler.store_alert(alert_data)

                # Send notifications
                self.email_service.send_email_notification(alert_data)
                
                processed_count += 1
                logger.info(f"Processed alert: {alert_data['alertID']}")

            except Exception as e:
                logger.error(f"Error processing SQS message: {str(e)}")
                continue
        
        return processed_count
