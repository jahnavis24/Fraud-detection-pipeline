"""
Sidebar component for dashboard controls
"""
import streamlit as st
from datetime import datetime
from config import DASHBOARD_CONFIG


def render_sidebar():
    """Render sidebar controls and return control values"""
    st.sidebar.header("Dashboard Controls")
    
    auto_refresh = st.sidebar.checkbox("Auto Refresh", value=True)
    refresh_interval = st.sidebar.slider(
        "Refresh Interval (seconds)", 
        DASHBOARD_CONFIG['min_refresh_interval'], 
        DASHBOARD_CONFIG['max_refresh_interval'], 
        DASHBOARD_CONFIG['default_refresh_interval']
    )
    
    refresh_now = st.sidebar.button("Refresh Now")
    
    return {
        'auto_refresh': auto_refresh,
        'refresh_interval': refresh_interval,
        'refresh_now': refresh_now
    }


def handle_auto_refresh(controls):
    """Handle auto refresh logic"""
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = datetime.now()
    
    if controls['refresh_now']:
        st.rerun()
    
    if controls['auto_refresh']:
        time_since_refresh = (datetime.now() - st.session_state.last_refresh).seconds
        if time_since_refresh >= controls['refresh_interval']:
            st.session_state.last_refresh = datetime.now()
            st.rerun()
