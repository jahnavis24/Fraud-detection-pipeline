"""
Key metrics component for the dashboard
"""
import streamlit as st
from utils import format_large_currency, format_currency


def render_key_metrics(metrics):
    """Render key metrics section"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Transactions", metrics['total_transactions'])
    
    with col2:
        st.metric("High Risk Alerts", metrics['high_risk_alerts'])
    
    with col3:
        total_amount = metrics['total_amount']
        st.metric(
            "Total Amount", 
            format_large_currency(total_amount), 
            help=f"Full amount: {format_currency(total_amount)}"
        )
    
    with col4:
        st.metric("Active Alerts", metrics['total_alerts'])
