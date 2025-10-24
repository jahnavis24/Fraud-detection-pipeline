"""
Main Lambda handler for Kinesis fraud detection
"""
import json
import logging
from fraud_detector import FraudDetectionProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def lambda_handler(event, context):
    """Main Lambda function handler"""
    processor = FraudDetectionProcessor()
    
    try:
        return processor.process_kinesis_records(event['Records'])
    except Exception as e:
        logger.error(f"Error in lambda_handler: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
