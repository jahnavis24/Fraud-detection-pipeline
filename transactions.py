"""
Transactions tab component for the dashboard
"""
import streamlit as st
from utils import prepare_transaction_display
from config import TRANSACTION_COLUMNS, TRANSACTION_COLUMN_CONFIG


def render_transactions_tab(df_transactions):
    """Render the transactions tab content"""
    st.subheader("Transaction List")
    
    if not df_transactions.empty:
        # Prepare display data
        display_df = prepare_transaction_display(df_transactions)
        
        # Display transactions table
        st.dataframe(
            display_df[TRANSACTION_COLUMNS],
            use_container_width=True,
            column_config=TRANSACTION_COLUMN_CONFIG
        )
    else:
        st.info("No transactions available")
