"""
Data processor for DynamoDB operations
"""
import boto3
import logging
from decimal import Decimal
from datetime import datetime
from typing import Dict
from .config import TRANSACTIONS_TABLE, DETECTION_RESULTS_TABLE, DETECTION_TABLE

logger = logging.getLogger(__name__)

# AWS client
dynamodb = boto3.resource('dynamodb')

# DynamoDB tables
transactions_table = dynamodb.Table(TRANSACTIONS_TABLE)
detection_results_table = dynamodb.Table(DETECTION_RESULTS_TABLE)
detection_table = dynamodb.Table(DETECTION_TABLE)


class DataProcessor:
    """Handles data storage operations"""
    
    def store_transaction(self, transaction: Dict) -> None:
        """Store transaction in DynamoDB"""
        try:
            transaction_to_store = self.convert_floats_to_decimal(transaction)
            transactions_table.put_item(Item=transaction_to_store)
            logger.info(f"Stored transaction: {transaction['transactionID']}")
        except Exception as e:
            logger.error(f"Error storing transaction: {str(e)}")
            raise
    
    def store_detection_result(self, transaction_id: str, prediction: Dict, 
                             processed_data: str) -> None:
        """Store detection result in DynamoDB"""
        try:
            item = {
                'transactionID': transaction_id,
                'prediction': self.convert_floats_to_decimal(prediction),
                'csv_data': processed_data,
                'timestamp': datetime.now().isoformat()
            }
            detection_results_table.put_item(Item=item)
            logger.info(f"Stored detection result for: {transaction_id}")
        except Exception as e:
            logger.error(f"Error storing detection result: {str(e)}")
            raise

    def store_detection(self, transaction_id: str, method: str, is_fraud: bool,
                        confidence: float, details: Dict) -> None:
        """
        Store detection result in DynamoDB
        Args:
            transaction_id (str): Unique identifier for the transaction
            method (str): Detection method used ('business_rules', 'AI_model')
            is_fraud (bool): Whether the transaction is flagged as fraud (0 or 1)
            confidence (float): Confidence score of the detection
            details (Dict): Additional details about the detection
        """
        try:
            item = {
                'transactionID': transaction_id,
                'is_fraud': is_fraud,
                'confidence': Decimal(str(confidence)),
                'details': self.convert_floats_to_decimal(details),
                'timestamp': datetime.now().isoformat()
            }
            detection_table.put_item(Item=item)
            logger.info(f"Stored detection for: {transaction_id}")
        except Exception as e:
            logger.error(f"Error storing detection: {str(e)}")
            raise
    
    def convert_floats_to_decimal(self, obj):
        """Convert floats to Decimal for DynamoDB storage"""
        if isinstance(obj, float):
            return Decimal(str(obj))
        elif isinstance(obj, dict):
            return {k: self.convert_floats_to_decimal(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self.convert_floats_to_decimal(i) for i in obj]
        return obj
