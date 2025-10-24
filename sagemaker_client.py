"""
SageMaker client for fraud prediction
"""
import json
import boto3
import pandas as pd
import numpy as np
import logging
from typing import Dict
from .config import SAGEMAKER_ENDPOINT

logger = logging.getLogger(__name__)

# AWS client
sagemaker_runtime = boto3.client('sagemaker-runtime')


class SageMakerClient:
    """Client for SageMaker inference"""
    
    def get_fraud_prediction(self, transaction: Dict) -> Dict:
        """Get fraud prediction from SageMaker endpoint"""
        try:
            # Preprocess data
            processed_data = self.preprocess_transaction(transaction)
            
            # Invoke SageMaker endpoint
            response = sagemaker_runtime.invoke_endpoint(
                EndpointName=SAGEMAKER_ENDPOINT,
                ContentType="text/csv",
                Body=processed_data
            )
            
            # Parse response
            prediction = json.loads(response['Body'].read().decode())
            logger.info(f"SageMaker prediction: {prediction}")
            
            # Determine if fraud based on prediction
            fraud_score = float(prediction) if isinstance(prediction, (int, float)) else 0.0
            is_fraud = fraud_score > 0.2  # Adjust threshold as needed
            
            return {
                'prediction': prediction,
                'processed_data': processed_data,
                'is_fraud': is_fraud,
                'confidence': fraud_score
            }
            
        except Exception as e:
            logger.error(f"Error in SageMaker inference: {str(e)}")
            raise
    
    def preprocess_transaction(self, transaction: Dict) -> str:
        """Preprocess transaction data for SageMaker"""
        df = pd.DataFrame([transaction])
        processed_df = self.preprocess_dataframe(df)
        return ','.join(map(str, processed_df.iloc[0].values))
    
    def preprocess_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Preprocess DataFrame for SageMaker inference"""
        df = df.copy()
        
        # Convert date columns to datetime
        df['trans_date_trans_time'] = pd.to_datetime(df['trans_date_trans_time'])
        df['dob'] = pd.to_datetime(df['dob'])
        
        # Drop unnecessary columns
        columns_to_drop = [
            'transactionID', 'first', 'last', 'street', 'trans_num', 'merchant', 'job'
        ]
        df.drop(columns=[col for col in columns_to_drop if col in df.columns], inplace=True)
        
        # Feature engineering
        df = self.add_engineered_features(df)
        
        return df
    
    def add_engineered_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add engineered features to DataFrame"""
        # Target encoding (simplified - in production, use pre-computed values)
        if 'category' in df.columns:
            df['category_target_enc'] = df['category'].map(lambda x: 0.1)  # Placeholder
        
        if 'state' in df.columns:
            df['state_target_enc'] = df['state'].map(lambda x: 0.1)  # Placeholder
        
        # Gender encoding
        if 'gender' in df.columns:
            df['gender'] = df['gender'].map({'F': 0, 'M': 1})
        
        # Time-based features
        df['transaction_hour'] = df['trans_date_trans_time'].dt.hour
        df['is_night'] = ((df['transaction_hour'] >= 22) | (df['transaction_hour'] < 6)).astype(int)
        df['transaction_dayofweek'] = df['trans_date_trans_time'].dt.dayofweek
        
        # Age calculation
        current_date = df['trans_date_trans_time'].max()
        df['age'] = (current_date - df['dob']).dt.days // 365
        
        # Distance calculation
        if all(col in df.columns for col in ['lat', 'long', 'merch_lat', 'merch_long']):
            df['distance_to_merchant'] = self.haversine_vectorized(
                df['lat'], df['long'], df['merch_lat'], df['merch_long']
            )
        
        # Drop original columns
        columns_to_drop = ['category', 'state', 'city', 'trans_date_trans_time', 'dob']
        if 'is_fraud' in df.columns:
            columns_to_drop.append('is_fraud')
            
        df.drop(columns=[col for col in columns_to_drop if col in df.columns], inplace=True)
        
        return df
    
    def haversine_vectorized(self, lat1, lon1, lat2, lon2):
        """Calculate haversine distance"""
        R = 6371  # Earth radius in km
        lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = np.sin(dlat / 2.0) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2.0) ** 2
        c = 2 * np.arcsin(np.sqrt(a))
        return R * c
