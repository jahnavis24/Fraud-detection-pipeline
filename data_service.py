"""
Data service for loading and processing dashboard data
"""
import streamlit as st
import pandas as pd
import sys
import os

# Add backend path
sys.path.insert(0, 'C:\\Users\\ADMIN\\Desktop\\AWS_architecture\\src\\')

from backend.dynamo.database_operations import AnomalyTransactions
from config import AWS_CONFIG, DASHBOARD_CONFIG


@st.cache_resource
def init_dynamodb():
    """Initialize DynamoDB connection"""
    return AnomalyTransactions(
        region_name=AWS_CONFIG['region_name'],
        aws_access_key_id=AWS_CONFIG['aws_access_key_id'],
        aws_secret_access_key=AWS_CONFIG['aws_secret_access_key']
    )


class DataService:
    """Service for managing dashboard data"""
    
    def __init__(self):
        self.db = None
        self._initialize_db()
    
    def _initialize_db(self):
        """Initialize database connection"""
        try:
            self.db = init_dynamodb()
            self.db.initialize_tables()
        except Exception as e:
            st.error(f"Error initializing database: {str(e)}")
            raise e
    
    def load_all_data(self):
        """Load all data from DynamoDB tables"""
        try:
            transactions = self.db.list_transactions(
                limit=DASHBOARD_CONFIG['default_transaction_limit']
            )
            results = self.db.list_results(
                limit=DASHBOARD_CONFIG['default_results_limit']
            )
            alerts = self.db.list_alerts(
                limit=DASHBOARD_CONFIG['default_alerts_limit']
            )
            
            return {
                'transactions': transactions,
                'results': results,
                'alerts': alerts
            }
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            return {
                'transactions': [],
                'results': [],
                'alerts': []
            }
    
    def get_dataframes(self):
        """Get data as pandas DataFrames"""
        data = self.load_all_data()
        
        return {
            'df_transactions': pd.DataFrame(data['transactions']) if data['transactions'] else pd.DataFrame(),
            'df_results': pd.DataFrame(data['results']) if data['results'] else pd.DataFrame(),
            'df_alerts': pd.DataFrame(data['alerts']) if data['alerts'] else pd.DataFrame()
        }
    
    def get_key_metrics(self, dataframes):
        """Calculate key metrics from dataframes"""
        df_transactions = dataframes['df_transactions']
        df_alerts = dataframes['df_alerts']
        
        metrics = {
            'total_transactions': len(df_transactions),
            'total_alerts': len(df_alerts),
            'high_risk_alerts': 0,
            'total_amount': 0.0
        }
        
        if not df_alerts.empty:
            metrics['high_risk_alerts'] = len(
                df_alerts[df_alerts['severity'].isin(['HIGH', 'CRITICAL'])]
            )
        
        if not df_transactions.empty:
            from utils import safe_float
            metrics['total_amount'] = df_transactions['amt'].apply(safe_float).sum()
        
        return metrics
