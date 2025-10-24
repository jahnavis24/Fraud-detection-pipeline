"""
Footer component for the dashboard
"""
import streamlit as st
from datetime import datetime


def render_footer(dataframes, controls):
    """Render the dashboard footer"""
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if 'last_refresh' in st.session_state:
            last_update = st.session_state.last_refresh.strftime('%Y-%m-%d %H:%M:%S')
        else:
            last_update = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        st.markdown(f"**Last updated:** {last_update}")
    
    with col2:
        total_transactions = len(dataframes['df_transactions'])
        total_results = len(dataframes['df_results'])
        total_alerts = len(dataframes['df_alerts'])
        st.markdown(
            f"**Total Records:** {total_transactions} transactions, "
            f"{total_results} results, {total_alerts} alerts"
        )
    
    with col3:
        if controls['auto_refresh']:
            st.markdown(f"**Next refresh:** {controls['refresh_interval']}s")
