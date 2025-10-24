"""
Data storage handler for alerting system
"""
import boto3
import logging
from decimal import Decimal
from typing import Dict
from .config import AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, ALERTS_TABLE

logger = logging.getLogger(__name__)

# Initialize DynamoDB resource
dynamodb = boto3.resource(
    'dynamodb',
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

# DynamoDB table for storing alerts
alerts_table = dynamodb.Table(ALERTS_TABLE)


class AlertDataHandler:
    """Handles alert data storage operations"""
    
    def store_alert(self, alert_data: Dict) -> None:
        """Store alert in DynamoDB"""
        try:
            # Convert floats to Decimal for DynamoDB compatibility
            alert_data_for_dynamodb = self.convert_floats(alert_data)
            alerts_table.put_item(Item=alert_data_for_dynamodb)
            logger.info(f"Alert stored in DynamoDB: {alert_data['alertID']}")
        except Exception as e:
            logger.error(f"Error storing alert in DynamoDB: {str(e)}")
            raise
    
    def convert_floats(self, obj):
        """
        Recursively convert float values to Decimal for DynamoDB compatibility.
        
        :param obj: Object to convert (can be dict, list, or primitive)
        :return: Object with floats converted to Decimal
        """
        if isinstance(obj, float):
            return Decimal(str(obj))
        elif isinstance(obj, dict):
            return {k: self.convert_floats(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self.convert_floats(i) for i in obj]
        return obj
