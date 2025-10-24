"""
Detection results tab component for the dashboard
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from utils import prepare_results_display


def render_detection_results_tab(df_results):
    """Render the detection results tab content"""
    st.subheader("Detection Results")
    
    if not df_results.empty:
        # Process results for display
        processed_results = prepare_results_display(df_results)
        df_processed = pd.DataFrame(processed_results)
        
        # Display results
        st.dataframe(
            df_processed,
            use_container_width=True,
            column_config={
                "Transaction ID": st.column_config.NumberColumn("Transaction ID"),
                "Confidence": st.column_config.ProgressColumn(
                    "Confidence",
                    min_value=0,
                    max_value=1,
                    format="%.6f"
                ),
                "Details": st.column_config.TextColumn(
                    "Details",
                    help="Detection details"
                ),
                "Fraud": st.column_config.CheckboxColumn(
                    "Fraud Status",
                    help="Whether the transaction is fraudulent"
                ),
                "Timestamp": st.column_config.DatetimeColumn("Timestamp")
            }
        )
        
        # Visualizations
        _render_detection_visualizations(df_processed)
    else:
        st.info("No detection results available")


def _render_detection_visualizations(df_processed):
    """Render visualizations for detection results"""
    col1, col2 = st.columns(2)
    
    with col1:
        # Confidence score distribution
        confidence_scores = df_processed['Confidence'].tolist()
        fig_conf = px.histogram(
            x=confidence_scores,
            title='Confidence Score Distribution',
            nbins=20,
            labels={'x': 'Confidence Score', 'y': 'Count'}
        )
        st.plotly_chart(fig_conf, use_container_width=True)
    
    with col2:
        # Timeline of predictions
        df_time = df_processed.copy()
        df_time['Timestamp'] = pd.to_datetime(df_time['Timestamp'])
        
        fig_time = px.scatter(
            df_time,
            x='Timestamp',
            y='Confidence',
            color='Fraud',
            title='Confidence Scores Over Time',
            labels={'Confidence': 'Confidence Score', 'Timestamp': 'Time'},
            color_discrete_map={True: '#dc3545', False: '#28a745'}
        )
        st.plotly_chart(fig_time, use_container_width=True)
