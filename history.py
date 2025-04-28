import json
import os
from datetime import datetime
import pandas as pd
import streamlit as st

# Constants
DATA_DIR = "data"
HISTORY_FILE = os.path.join(DATA_DIR, "upload_history.json")

# Ensure directory exists
os.makedirs(DATA_DIR, exist_ok=True)

def save_upload_history(filename, file_type, timestamp=None):
    """
    Save upload history to JSON file.
    
    Args:
        filename (str): Name of the uploaded file
        file_type (str): Type of the uploaded file (e.g., xlsx, csv, pdf, jpg)
        timestamp (str, optional): Timestamp for the upload. If None, current time is used.
    """
    # Ensure data directory exists
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Generate timestamp if not provided
    if timestamp is None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Load existing history
    history = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            try:
                history = json.load(f)
            except json.JSONDecodeError:
                history = []
    
    # Add new entry
    history.append({
        'filename': filename,
        'file_type': file_type,
        'timestamp': timestamp,
        'status': 'processed'
    })
    
    # Save updated history
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=4)

def get_upload_history():
    """
    Get upload history from JSON file.
    
    Returns:
        list: List of upload history entries
    """
    if not os.path.exists(HISTORY_FILE):
        return []
    
    with open(HISTORY_FILE, 'r') as f:
        try:
            history = json.load(f)
            return history
        except json.JSONDecodeError:
            return []

def display_upload_history():
    """
    Display upload history in Streamlit app.
    """
    history = get_upload_history()
    
    if not history:
        st.info("No upload history available.")
        return
    
    # Convert to DataFrame for display
    history_df = pd.DataFrame(history)
    
    # Format timestamp column if it exists
    if 'timestamp' in history_df.columns:
        history_df['timestamp'] = pd.to_datetime(history_df['timestamp'])
        history_df = history_df.sort_values('timestamp', ascending=False)
    
    st.subheader("Upload History")
    st.dataframe(history_df)
    
    # Add option to clear history
    if st.button("Clear Upload History"):
        clear_upload_history()
        st.success("Upload history cleared.")
        st.experimental_rerun()

def clear_upload_history():
    """
    Clear upload history by removing the history file.
    """
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)
