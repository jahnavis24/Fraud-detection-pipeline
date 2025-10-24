"""
Alert manager for sending fraud alerts
"""
import json
import boto3
import logging
from datetime import datetime
from typing import Dict
from .config import ALERT_QUEUE_URL

logger = logging.getLogger(__name__)

# AWS client
sqs = boto3.client('sqs')


class AlertManager:
    """Manages fraud alerts"""
    
    def send_alert(self, alert_data: Dict) -> None:
        """Send alert to SQS queue"""
        if not ALERT_QUEUE_URL:
            logger.warning("Alert queue URL not configured")
            return
        
        try:
            # Send message to SQS
            response = sqs.send_message(
                QueueUrl=ALERT_QUEUE_URL,
                MessageBody=json.dumps(alert_data, default=str),
                MessageAttributes={
                    'severity': {
                        'StringValue': alert_data['severity'],
                        'DataType': 'String'
                    },
                    'detection_method': {
                        'StringValue': alert_data['detection_method'],
                        'DataType': 'String'
                    }
                }
            )
            
            logger.info(f"Alert sent to SQS: {response['MessageId']}")
            
        except Exception as e:
            logger.error(f"Error sending alert to SQS: {str(e)}")
            raise
