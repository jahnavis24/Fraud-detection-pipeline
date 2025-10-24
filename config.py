"""
Configuration file for the Fraud Detection Dashboard
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# AWS Configuration
AWS_CONFIG = {
    'region_name': 'ap-southeast-2',
    'aws_access_key_id': os.environ.get('AWS_ACCESS_KEY_ID'),
    'aws_secret_access_key': os.environ.get('AWS_SECRET_ACCESS_KEY')
}

# Page Configuration
PAGE_CONFIG = {
    'page_title': "Fraud Detection Dashboard",
    'layout': "wide",
    'initial_sidebar_state': "expanded"
}

# Dashboard Settings
DASHBOARD_CONFIG = {
    'default_refresh_interval': 30,
    'max_refresh_interval': 60,
    'min_refresh_interval': 5,
    'default_transaction_limit': 100,
    'default_results_limit': 100,
    'default_alerts_limit': 100,
    'recent_alerts_display': 4,
    'max_alerts_display': 8
}

# Color Schemes
COLOR_SCHEMES = {
    'fraud_status': {
        'Legitimate': '#28a745',
        'Fraud': '#dc3545'
    },
    'severity': {
        'LOW': '#28a745',
        'MEDIUM': '#ffc107',
        'HIGH': '#fd7e14',
        'CRITICAL': '#dc3545'
    },
    'severity_icons': {
        'critical': '🔴',
        'high': '🟠',
        'medium': '🟡',
        'low': '🟢',
        'default': '⚪'
    }
}

# Column Configurations
TRANSACTION_COLUMNS = [
    'transactionID', 'Amount', 'Customer', 'merchant', 'category',
    'Location', 'CC Number', 'trans_date_trans_time'
]

TRANSACTION_COLUMN_CONFIG = {
    "transactionID": "Transaction ID",
    "merchant": "Merchant",
    "category": "Category",
    "trans_date_trans_time": "Date & Time",
    "CC Number": "Credit Card"
}

# Tabs Configuration
TAB_CONFIG = [
    {"id": "tab1", "icon": "📊", "title": "Transactions"},
    {"id": "tab2", "icon": "🔍", "title": "Detection Results"},
    {"id": "tab3", "icon": "🚨", "title": "Alerts Details"},
    {"id": "tab4", "icon": "📈", "title": "Analytics"}
]
