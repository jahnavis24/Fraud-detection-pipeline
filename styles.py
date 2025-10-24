"""
CSS Styles for the Fraud Detection Dashboard
"""

DASHBOARD_STYLES = """
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .alerts-container {
        max-height: 400px;
        overflow-y: scroll;
        padding-right: 10px;
        margin-bottom: 1rem;
    }
    .alerts-container::-webkit-scrollbar {
        width: 6px;
    }
    .alerts-container::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 3px;
    }
    .alerts-container::-webkit-scrollbar-thumb {
        background: #888;
        border-radius: 3px;
    }
    .alerts-container::-webkit-scrollbar-thumb:hover {
        background: #555;
    }
    .alert-critical {
        background: linear-gradient(135deg, #fee 0%, #fdd 100%);
        border-left: 4px solid #dc3545;
        color: #721c24;
        padding: 0.8rem;
        border-radius: 0.5rem;
        margin: 0.3rem 0;
        box-shadow: 0 2px 4px rgba(220,53,69,0.1);
        font-size: 0.9em;
    }
    .alert-high {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        border-left: 4px solid #fd7e14;
        color: #856404;
        padding: 0.8rem;
        border-radius: 0.5rem;
        margin: 0.3rem 0;
        box-shadow: 0 2px 4px rgba(253,126,20,0.1);
        font-size: 0.9em;
    }
    .alert-medium {
        background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%);
        border-left: 4px solid #17a2b8;
        color: #0c5460;
        padding: 0.8rem;
        border-radius: 0.5rem;
        margin: 0.3rem 0;
        box-shadow: 0 2px 4px rgba(23,162,184,0.1);
        font-size: 0.9em;
    }
    .alert-low {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border-left: 4px solid #28a745;
        color: #155724;
        padding: 0.8rem;
        border-radius: 0.5rem;
        margin: 0.3rem 0;
        box-shadow: 0 2px 4px rgba(40,167,69,0.1);
        font-size: 0.9em;
    }
    .fraud-indicator {
        padding: 0.2rem 0.5rem;
        border-radius: 0.25rem;
        font-weight: bold;
        color: white;
    }
    .fraud-yes {
        background-color: #dc3545;
    }
    .fraud-no {
        background-color: #28a745;
    }
    .compact-metric {
        text-align: center;
        padding: 0.5rem;
    }
    .compact-metric .metric-label {
        font-size: 0.8em;
        color: #666;
        margin-bottom: 0.2rem;
    }
    .compact-metric .metric-value {
        font-size: 1.2em;
        font-weight: bold;
        color: #333;
    }
</style>
"""

def apply_styles():
    """Apply dashboard styles"""
    import streamlit as st
    st.markdown(DASHBOARD_STYLES, unsafe_allow_html=True)
