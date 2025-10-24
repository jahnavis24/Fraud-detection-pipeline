"""
Main fraud detection processor
"""
import json
import base64
import logging
from datetime import datetime
from typing import Dict, List

from .business_rules import BusinessRulesEngine
from .sagemaker_client import SageMakerClient
from .data_processor import DataProcessor
from .alert_manager import AlertManager

logger = logging.getLogger(__name__)


class FraudDetectionProcessor:
    """Main processor for fraud detection pipeline"""
    
    def __init__(self):
        self.business_rules = BusinessRulesEngine()
        self.sagemaker_client = SageMakerClient()
        self.data_processor = DataProcessor()
        self.alert_manager = AlertManager()
    
    def process_kinesis_records(self, records: List[Dict]) -> Dict:
        """Process Kinesis records and detect fraud"""
        processed_count = 0
        
        for record in records:
            try:
                # Decode Kinesis data
                payload = base64.b64decode(record['kinesis']['data'])
                transaction = json.loads(payload)
                
                # Process single transaction
                self.process_transaction(transaction)
                processed_count += 1
                
            except Exception as e:
                logger.error(f"Error processing record: {str(e)}")
                continue
        
        return {
            "statusCode": 200,
            "body": f"Processed {processed_count} transactions"
        }
    
    def process_transaction(self, transaction: Dict) -> None:
        """
        Process a single transaction through the fraud detection pipeline
        Steps:
        1. Store transaction in DynamoDB
        2. Apply business rules (fast pre-filtering)
        3. If business rules detect fraud, skip SageMaker and send alert
        4. If business rules pass, proceed with SageMaker inference
        5. Store SageMaker result
        6. If SageMaker detects fraud, send alert
        """
        transaction_id = transaction['transactionID']
        logger.info(f"Processing transaction: {transaction_id}")
        
        try:
            # 1. Store transaction in DynamoDB
            self.data_processor.store_transaction(transaction)
            
            # 2. Apply business rules (fast pre-filtering)
            business_rule_result = self.business_rules.evaluate_transaction(transaction)
            
            # 3. If business rules detect fraud, skip SageMaker and send alert
            if business_rule_result['is_fraud']:
                logger.info(f"Business rules detected fraud for transaction: {transaction_id}")
                self.handle_fraud_detection(
                    transaction_id=transaction_id,
                    fraud_score=business_rule_result['confidence'],
                    detection_method='business_rules',
                    details=business_rule_result['reasons'],
                    transaction_data=transaction
                )

                # Store detection result
                self.data_processor.store_detection(
                    transaction_id=transaction_id,
                    method='business_rules',
                    is_fraud=True,
                    confidence=business_rule_result['confidence'],
                    details=business_rule_result['reasons']
                )
                return
            
            # 4. If business rules pass, proceed with SageMaker inference
            logger.info(f"Business rules passed, proceeding with SageMaker for: {transaction_id}")
            sagemaker_result = self.sagemaker_client.get_fraud_prediction(transaction)
            
            # 5. Store SageMaker result
            self.data_processor.store_detection_result(
                transaction_id, sagemaker_result['prediction'], 
                sagemaker_result['processed_data']
            )
            self.data_processor.store_detection(
                transaction_id=transaction_id,
                method='AI_model',
                is_fraud=sagemaker_result['is_fraud'],
                confidence=sagemaker_result['prediction'],
                details=sagemaker_result['processed_data']
            )
            
            # 6. Check if SageMaker detected fraud
            if sagemaker_result['is_fraud']:
                logger.info(f"SageMaker detected fraud for transaction: {transaction_id}")
                self.handle_fraud_detection(
                    transaction_id=transaction_id,
                    fraud_score=sagemaker_result['confidence'],
                    detection_method='AI_model',
                    details=sagemaker_result['prediction'],
                    transaction_data=transaction
                )
            
        except Exception as e:
            logger.error(f"Error processing transaction {transaction_id}: {str(e)}")
            raise
    
    def handle_fraud_detection(self, transaction_id: str, fraud_score: float, 
                             detection_method: str, details: Dict, 
                             transaction_data: Dict) -> None:
        """Handle fraud detection by sending alert to SQS"""
        alert_data = {
            'transaction_id': transaction_id,
            'fraud_score': fraud_score,
            'detection_method': detection_method,
            'detection_details': details,
            'transaction_data': transaction_data,
            'timestamp': datetime.now().isoformat(),
            'severity': self.determine_severity(fraud_score)
        }
        
        self.alert_manager.send_alert(alert_data)
    
    def determine_severity(self, fraud_score: float) -> str:
        """Determine alert severity based on fraud score"""
        if fraud_score >= 0.7:
            return 'CRITICAL'
        elif fraud_score >= 0.5:
            return 'HIGH'
        elif fraud_score >= 0.2:
            return 'MEDIUM'
        else:
            return 'LOW'
