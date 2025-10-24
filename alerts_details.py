"""
Alerts details tab component for the dashboard
"""
import streamlit as st
import plotly.express as px
from utils import parse_transaction_data, safe_float
from config import COLOR_SCHEMES


def render_alerts_details_tab(df_alerts):
    """Render the alerts details tab content"""
    st.subheader("Alerts Details")
    
    if not df_alerts.empty:
        # Display detailed alerts
        _render_detailed_alerts(df_alerts)
        
        # Visualizations
        _render_alerts_visualizations(df_alerts)
    else:
        st.info("No alerts available")


def _render_detailed_alerts(df_alerts):
    """Render detailed alert expandable sections"""
    for _, alert in df_alerts.iterrows():
        with st.expander(f"Alert {alert['alertID']} - {alert['severity']}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Transaction ID:** {alert.get('transaction_id', 'N/A')}")
                st.write(f"**Fraud Score:** {safe_float(alert.get('fraud_score', 0)):.6f}")
                st.write(f"**Detection Method:** {alert.get('detection_method', 'N/A')}")
                st.write(f"**Timestamp:** {alert.get('timestamp', 'N/A')}")
            
            with col2:
                st.write("**Detection Details:**")
                detection_details = alert.get('detection_details', {})
                if detection_details:
                    st.json(detection_details)
                else:
                    st.write("No detection details available")
            
            st.write("**Transaction Data:**")
            transaction_data = parse_transaction_data(alert.get('transaction_data', {}))
            if transaction_data:
                st.json(transaction_data)
            else:
                st.write("No transaction data available")


def _render_alerts_visualizations(df_alerts):
    """Render visualizations for alerts"""
    col1, col2 = st.columns(2)
    
    with col1:
        # Alert severity distribution
        severity_counts = df_alerts['severity'].value_counts()
        fig_severity = px.pie(
            values=severity_counts.values,
            names=severity_counts.index,
            title="Alert Severity Distribution",
            color_discrete_map=COLOR_SCHEMES['severity']
        )
        st.plotly_chart(fig_severity, use_container_width=True)
    
    with col2:
        # Fraud scores distribution
        fraud_scores = df_alerts['fraud_score'].apply(safe_float).tolist()
        fig_scores = px.histogram(
            x=fraud_scores,
            title='Alert Fraud Scores Distribution',
            nbins=20,
            labels={'x': 'Fraud Score', 'y': 'Count'}
        )
        st.plotly_chart(fig_scores, use_container_width=True)
