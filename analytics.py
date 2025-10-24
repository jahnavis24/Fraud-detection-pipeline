"""
Analytics tab component for the dashboard
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from utils import safe_float
from config import COLOR_SCHEMES


def render_analytics_tab(df_transactions, df_alerts):
    """Render the analytics tab content"""
    st.subheader("Analytics Dashboard")
    
    if not df_transactions.empty:
        # Fraud analysis
        _render_fraud_analysis(df_transactions)
        
        # Amount analysis
        _render_amount_analysis(df_transactions)
        
        # Time series analysis
        _render_time_series_analysis(df_alerts)
    else:
        st.info("No transaction data available for analytics")


def _render_fraud_analysis(df_transactions):
    """Render fraud vs legitimate transactions analysis"""
    col1, col2 = st.columns(2)
    
    with col1:
        # Fraud vs Legitimate transactions
        fraud_counts = df_transactions['is_fraud'].value_counts()
        fraud_labels = ['Legitimate' if idx == 0 else 'Fraud' for idx in fraud_counts.index]
        fig_fraud = px.pie(
            values=fraud_counts.values,
            names=fraud_labels,
            title='Fraud vs Legitimate Transactions',
            color_discrete_map=COLOR_SCHEMES['fraud_status']
        )
        st.plotly_chart(fig_fraud, use_container_width=True)
    
    with col2:
        # Transaction categories
        category_counts = df_transactions['category'].value_counts()
        fig_categories = px.bar(
            x=category_counts.values,
            y=category_counts.index,
            title='Transactions by Category',
            orientation='h',
            labels={'x': 'Count', 'y': 'Category'}
        )
        st.plotly_chart(fig_categories, use_container_width=True)


def _render_amount_analysis(df_transactions):
    """Render amount analysis"""
    col1, col2 = st.columns(2)
    
    with col1:
        # Amount distribution by fraud status
        df_amounts = df_transactions.copy()
        df_amounts['amount_float'] = df_amounts['amt'].apply(safe_float)
        df_amounts['fraud_status'] = df_amounts['is_fraud'].map({0: 'Legitimate', 1: 'Fraud'})
        
        fig_amounts = px.box(
            df_amounts,
            x='fraud_status',
            y='amount_float',
            title='Transaction Amount Distribution by Fraud Status',
            labels={'amount_float': 'Amount ($)', 'fraud_status': 'Status'}
        )
        st.plotly_chart(fig_amounts, use_container_width=True)


def _render_time_series_analysis(df_alerts):
    """Render time series analysis if data is available"""
    if not df_alerts.empty and 'timestamp' in df_alerts.columns:
        df_alerts_time = df_alerts.copy()
        df_alerts_time['timestamp'] = pd.to_datetime(df_alerts_time['timestamp'])
        df_alerts_time['fraud_score_float'] = df_alerts_time['fraud_score'].apply(safe_float)
        
        fig_time_series = px.line(
            df_alerts_time.sort_values('timestamp'),
            x='timestamp',
            y='fraud_score_float',
            color='severity',
            title='Fraud Scores Over Time',
            labels={'fraud_score_float': 'Fraud Score', 'timestamp': 'Time'}
        )
        st.plotly_chart(fig_time_series, use_container_width=True)
