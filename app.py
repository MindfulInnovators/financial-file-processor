import streamlit as st
import os
import pandas as pd
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Import custom modules
from parsers.gpt_parser import parse_with_gpt  # Only import the GPT parser
from visualization import display_financial_dashboard
from download import add_download_button
from history import save_upload_history, display_upload_history

# Load environment variables
load_dotenv()

# Constants
UPLOAD_DIR = "uploads"
DATA_DIR = "data"

# Ensure directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

# Initialize session state
if "processed_data" not in st.session_state:
    st.session_state.processed_data = None
if "file_uploaded" not in st.session_state:
    st.session_state.file_uploaded = False

def process_uploaded_file(uploaded_file):
    """Process the uploaded file using the GPT parser."""
    file_type = uploaded_file.name.split(".")[-1].lower()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{uploaded_file.name}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    # Save the uploaded file
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # Always use the GPT-powered parser
    processed_data = parse_with_gpt(file_path)
    
    # Save upload history
    save_upload_history(filename, file_type)
    
    return processed_data

def main():
    st.set_page_config(
        page_title="Financial File Processor",
        page_icon="💰",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("Financial File Processor")
    st.write("Upload financial files (Excel, CSV, PDF, or Image) to extract and structure data using AI")
    
    # Sidebar for file upload and options
    with st.sidebar:
        st.header("Upload Files")
        uploaded_file = st.file_uploader(
            "Choose a financial file", 
            type=["xlsx", "xls", "csv", "pdf", "jpg", "jpeg", "png"]
        )
        
        st.divider()
        
        # API Key configuration status
        st.subheader("OpenAI API Configuration")
        # Check if API key is likely configured (via env var or st.secrets)
        api_key_present = os.getenv("OPENAI_API_KEY") is not None
        if not api_key_present:
            try:
                # Check if API key exists in Streamlit secrets without reimporting
                if hasattr(st, "secrets") and "OPENAI_API_KEY" in st.secrets:
                    api_key_present = True
            except:
                pass # st.secrets might not be available locally

        if api_key_present:
            st.success("API Key configured ✅")
        else:
            st.warning("API Key not found. Please configure it in Streamlit Cloud secrets.")
        
        st.divider()
        
        # Display upload history in sidebar
        display_upload_history()
    
    # Process uploaded file
    if uploaded_file is not None and not st.session_state.file_uploaded:
        with st.spinner("Processing file with AI..."):
            processed_data = process_uploaded_file(uploaded_file)
            
            if processed_data is not None and not processed_data.empty:
                st.session_state.processed_data = processed_data
                st.session_state.file_uploaded = True
                st.success("File processed successfully!")
                st.rerun()
            elif processed_data is not None and processed_data.empty:
                 st.error("AI processing returned no data. Please check the file content or API key.")
                 st.session_state.file_uploaded = False # Allow re-upload
            else:
                 st.error("An error occurred during file processing.")
                 st.session_state.file_uploaded = False # Allow re-upload

    
    # Main content area
    if st.session_state.processed_data is not None:
        # Display the dashboard using the processed data
        display_financial_dashboard(st.session_state.processed_data)
        
        # Add download button for the processed data
        st.divider()
        add_download_button(st.session_state.processed_data)
        
        # Optionally display the raw extracted table
        with st.expander("View Raw Extracted Data Table"):
            st.dataframe(st.session_state.processed_data, use_container_width=True)
    
    # Reset button
    if st.session_state.file_uploaded:
        if st.button("Process Another File", type="primary"):
            st.session_state.processed_data = None
            st.session_state.file_uploaded = False
            st.rerun()
    
    # Footer
    st.divider()
    st.caption("Financial File Processor - Powered by Streamlit and OpenAI")

if __name__ == "__main__":
    main()

