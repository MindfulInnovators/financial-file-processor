import streamlit as st
import os
import json
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Import custom modules
from parsers.excel_parser import parse_excel
from parsers.csv_parser import parse_csv
from parsers.pdf_parser import parse_pdf
from parsers.image_parser import parse_image
from parsers.openai_integration import categorize_transactions
from parsers.gpt_parser import parse_with_gpt  # Import the new GPT parser
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
if 'transactions' not in st.session_state:
    st.session_state.transactions = None
if 'categorized_data' not in st.session_state:
    st.session_state.categorized_data = None
if 'file_uploaded' not in st.session_state:
    st.session_state.file_uploaded = False
if 'use_gpt_parser' not in st.session_state:
    st.session_state.use_gpt_parser = True  # Default to using GPT parser

def process_uploaded_file(uploaded_file):
    """Process the uploaded file based on its type"""
    file_type = uploaded_file.name.split('.')[-1].lower()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{uploaded_file.name}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    # Save the uploaded file
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # Parse the file based on user preference
    if st.session_state.use_gpt_parser:
        # Use the GPT-powered parser for intelligent extraction
        transactions = parse_with_gpt(file_path)
    else:
        # Use the traditional parsers
        if file_type in ['xlsx', 'xls']:
            transactions = parse_excel(file_path)
        elif file_type == 'csv':
            transactions = parse_csv(file_path)
        elif file_type == 'pdf':
            transactions = parse_pdf(file_path)
        elif file_type in ['jpg', 'jpeg', 'png']:
            transactions = parse_image(file_path)
        else:
            st.error(f"Unsupported file type: {file_type}")
            return None
    
    # Save upload history
    save_upload_history(filename, file_type)
    
    return transactions

def main():
    st.set_page_config(
        page_title="Financial File Processor",
        page_icon="💰",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("Financial File Processor")
    st.write("Upload financial files to extract and categorize transactions using AI")
    
    # Sidebar for file upload and options
    with st.sidebar:
        st.header("Upload Files")
        uploaded_file = st.file_uploader(
            "Choose a financial file (Excel, CSV, PDF, or Image)", 
            type=["xlsx", "xls", "csv", "pdf", "jpg", "jpeg", "png"]
        )
        
        st.divider()
        
        # Parser selection
        st.subheader("Parser Options")
        st.session_state.use_gpt_parser = st.checkbox(
            "Use GPT-powered intelligent parser", 
            value=st.session_state.use_gpt_parser,
            help="Enable to use GPT for intelligent extraction from complex financial documents like profit and loss statements and balance sheets"
        )
        
        st.divider()
        
        # API Key configuration status
        st.subheader("OpenAI API Configuration")
        # Check if API key is likely configured (via env var or st.secrets)
        api_key_present = os.getenv("OPENAI_API_KEY") is not None
        if not api_key_present:
            try:
                import streamlit as st
                if "OPENAI_API_KEY" in st.secrets:
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
        with st.spinner("Processing file..."):
            transactions = process_uploaded_file(uploaded_file)
            
            if transactions is not None:
                st.session_state.transactions = transactions
                
                # Categorize transactions using OpenAI
                with st.spinner("Categorizing transactions with AI..."):
                    categorized_data = categorize_transactions(transactions)
                    st.session_state.categorized_data = categorized_data
                
                st.session_state.file_uploaded = True
                st.success("File processed successfully!")
                st.rerun()
    
    # Main content area
    if st.session_state.transactions is not None:
        # Create tabs for different views
        tab1, tab2 = st.tabs(["Extracted Data", "Categorized Data"])
        
        with tab1:
            st.subheader("Extracted Transactions")
            st.dataframe(st.session_state.transactions, use_container_width=True)
        
        with tab2:
            if st.session_state.categorized_data is not None:
                # Display financial dashboard
                display_financial_dashboard(st.session_state.categorized_data)
                
                # Add download button
                st.divider()
                add_download_button(st.session_state.categorized_data)
    
    # Reset button
    if st.session_state.file_uploaded:
        if st.button("Process Another File", type="primary"):
            st.session_state.transactions = None
            st.session_state.categorized_data = None
            st.session_state.file_uploaded = False
            st.rerun()
    
    # Footer
    st.divider()
    st.caption("Financial File Processor - Powered by Streamlit and OpenAI")

if __name__ == "__main__":
    main()
