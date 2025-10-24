"""
Alerts section component for the dashboard
"""
import streamlit as st
import pandas as pd
from utils import (
    parse_transaction_data, 
    extract_transaction_amount, 
    extract_merchant_name,
    format_currency,
    format_timestamp_display,
    safe_float
)
from config import COLOR_SCHEMES, DASHBOARD_CONFIG


def render_alerts_section(df_alerts):
    """Render the recent alerts section"""
    st.subheader("🚨 Recent Alerts")
    
    # Create scrollable container
    st.markdown('<div class="alerts-container">', unsafe_allow_html=True)
    
    if not df_alerts.empty:
        # Show only the most recent alerts for better scrolling
        recent_alerts = df_alerts.head(DASHBOARD_CONFIG['recent_alerts_display'])
        
        for _, alert in recent_alerts.iterrows():
            _render_alert_card(alert)
        
        # Show link to view all alerts if there are more
        if len(df_alerts) > DASHBOARD_CONFIG['max_alerts_display']:
            st.markdown(
                f"<small style='text-align: center; display: block; margin-top: 10px;'>"
                f"📄 Showing {DASHBOARD_CONFIG['max_alerts_display']} most recent alerts. "
                f"View all {len(df_alerts)} alerts in the Alerts Details tab.</small>", 
                unsafe_allow_html=True
            )
    else:
        st.info("🔇 No alerts at this time")
    
    st.markdown('</div>', unsafe_allow_html=True)


def _render_alert_card(alert):
    """Render individual alert card"""
    severity = alert['severity'].lower()
    
    # Parse transaction data to get key info
    transaction_data = parse_transaction_data(alert.get('transaction_data', {}))
    
    # Extract key transaction details
    amount = extract_transaction_amount(transaction_data)
    merchant = extract_merchant_name(transaction_data)
    
    # Get basic info
    fraud_score = safe_float(alert.get('fraud_score', 0))
    timestamp = alert.get('timestamp', 'N/A')
    time_display = format_timestamp_display(timestamp)
    
    # Get severity icon
    icon = COLOR_SCHEMES['severity_icons'].get(
        severity, 
        COLOR_SCHEMES['severity_icons']['default']
    )
    
    st.markdown(f"""
    <div class="alert-{severity}">
        {icon} <strong>{alert['severity']}</strong> 
        <span style="float: right; font-size: 0.8em; opacity: 0.8;">{time_display}</span>
        <br>
        <strong>Score:</strong> {fraud_score:.2f} | <strong>Amount:</strong> {format_currency(amount)}
        <br>
        <strong>Merchant:</strong> {merchant[:35]}{'...' if len(merchant) > 35 else ''}
        <br>
        <small><strong>ID:</strong> {alert.get('transaction_id', 'N/A')}</small>
    </div>
    """, unsafe_allow_html=True)
