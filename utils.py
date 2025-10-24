"""
Utility functions for the Fraud Detection Dashboard
"""
import json
import pandas as pd
from decimal import Decimal


def safe_float(value):
    """Safely convert various numeric types to float"""
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, Decimal):
        return float(value)
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0


def format_currency(value):
    """Format currency values"""
    return f"${safe_float(value):,.2f}"


def format_large_currency(value):
    """Format large currency values with K, M, B suffixes"""
    amount = safe_float(value)
    if amount >= 1_000_000_000:
        return f"${amount/1_000_000_000:.1f}B"
    elif amount >= 1_000_000:
        return f"${amount/1_000_000:.1f}M"
    elif amount >= 1_000:
        return f"${amount/1_000:.1f}K"
    else:
        return f"${amount:.2f}"


def format_fraud_indicator(is_fraud):
    """Format fraud indicator with styling"""
    if is_fraud == 1:
        return 'FRAUD'
    else:
        return 'LEGITIMATE'


def parse_transaction_data(transaction_data_str):
    """Parse transaction_data string from alerts table"""
    try:
        # This is a simplified parser - you might need to adjust based on actual format
        if isinstance(transaction_data_str, dict):
            return transaction_data_str
        return json.loads(transaction_data_str)
    except:
        return {}


def format_timestamp_display(timestamp):
    """Format timestamp for better display"""
    try:
        if timestamp != 'N/A' and pd.notna(timestamp):
            time_obj = pd.to_datetime(timestamp)
            return time_obj.strftime('%m/%d %H:%M')
        else:
            return str(timestamp)
    except:
        return str(timestamp)


def extract_transaction_amount(transaction_data):
    """Extract amount from transaction data"""
    amount = 0
    if transaction_data:
        if 'amt' in transaction_data:
            amt_val = transaction_data['amt']
            if isinstance(amt_val, dict) and 'N' in amt_val:
                amount = safe_float(amt_val['N'])
            else:
                amount = safe_float(amt_val)
    return amount


def extract_merchant_name(transaction_data):
    """Extract merchant name from transaction data"""
    merchant = "Unknown Merchant"
    if transaction_data:
        if 'merchant' in transaction_data:
            merch_val = transaction_data['merchant']
            if isinstance(merch_val, dict) and 'S' in merch_val:
                merchant = merch_val['S']
            else:
                merchant = str(merch_val)
    return merchant


def prepare_transaction_display(df_transactions):
    """Prepare transaction dataframe for display"""
    if df_transactions.empty:
        return df_transactions
    
    display_df = df_transactions.copy()
    display_df['Amount'] = display_df['amt'].apply(format_currency)
    display_df['Customer'] = display_df['first'].astype(str) + ' ' + display_df['last'].astype(str)
    display_df['Location'] = display_df['city'].astype(str) + ', ' + display_df['state'].astype(str)
    display_df['CC Number'] = display_df['cc_num'].astype(str).apply(
        lambda x: f"****{x[-4:]}" if len(str(x)) >= 4 else x
    )
    return display_df


def prepare_results_display(df_results):
    """Prepare detection results dataframe for display"""
    if df_results.empty:
        return df_results
    
    processed_results = []
    for _, result in df_results.iterrows():
        # Handle details field which could be either a string, list or JSON
        details = result.get('details', '')
        if isinstance(details, str) and len(details) > 100:
            details_display = details[:100] + '...'
        else:
            details_display = str(details)
        
        # Convert is_fraud to boolean display
        is_fraud = result.get('is_fraud', '')
        if isinstance(is_fraud, str):
            is_fraud_display = is_fraud.lower() == 'true'
        else:
            is_fraud_display = bool(is_fraud)
            
        processed_results.append({
            'Transaction ID': result['transactionID'],
            'Confidence': safe_float(result.get('confidence', 0)),
            'Details': details_display,
            'Fraud': is_fraud_display,
            'Timestamp': result.get('timestamp', 'N/A')
        })
    
    return processed_results
