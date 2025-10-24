"""
Business rules engine for fraud detection
"""
import pandas as pd
from typing import Dict
from .config import BUSINESS_RULES


class BusinessRulesEngine:
    """Engine for applying business logic rules for fraud detection"""
    
    def evaluate_transaction(self, transaction: Dict) -> Dict:
        """Evaluate transaction against business rules"""
        fraud_indicators = []
        confidence = 0.0
        
        # Rule 1: High amount threshold
        if self.check_high_amount(transaction):
            fraud_indicators.append("High transaction amount")
            confidence += 0.2
        
        # Rule 2: Suspicious time patterns
        if self.check_suspicious_timing(transaction):
            fraud_indicators.append("Suspicious transaction timing")
            confidence += 0.25
        
        # Rule 3: Suspicious amount patterns
        if self.check_suspicious_amounts(transaction):
            fraud_indicators.append("Suspicious amount pattern")
            confidence += 0.3
        
        is_fraud = confidence >= 0.5  # Threshold for business rule fraud detection
        
        return {
            'is_fraud': is_fraud,
            'confidence': min(confidence, 1.0),
            'reasons': fraud_indicators
        }
    
    def check_high_amount(self, transaction: Dict) -> bool:
        """Check if transaction amount exceeds threshold"""
        amount = float(transaction.get('amt', 0))
        return amount > BUSINESS_RULES['max_amount_threshold']
    
    def check_suspicious_timing(self, transaction: Dict) -> bool:
        """Check if transaction occurs during high-risk hours"""
        trans_time = pd.to_datetime(transaction['trans_date_trans_time'])
        hour = trans_time.hour
        return hour in BUSINESS_RULES['high_risk_hours']
    
    def check_suspicious_amounts(self, transaction: Dict) -> bool:
        """Check for suspicious amount patterns"""
        amount = int(transaction.get('amt', 0))
        return amount in BUSINESS_RULES['suspicious_amount_patterns']
