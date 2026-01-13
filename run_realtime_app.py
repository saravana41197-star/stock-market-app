"""Main entry point for the real-time intraday stock prediction app."""
import streamlit as st
import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import and run the UI app directly
if __name__ == "__main__":
    # Configure Streamlit page
    st.set_page_config(
        page_title="Live Intraday Stock Predictor",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Import and run the UI app
    import ui_app
