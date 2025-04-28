import pandas as pd
import os
from io import BytesIO
import streamlit as st

def create_download_excel(df):
    """
    Create a downloadable Excel file with categorized financial data.
    
    Args:
        df (pandas.DataFrame): DataFrame with categorized transaction data
            
    Returns:
        bytes: Excel file as bytes for download
    """
    if df is None or df.empty:
        return None
    
    # Create a BytesIO object to store the Excel file
    output = BytesIO()
    
    # Create Excel writer
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Write transaction data to sheet
        df.to_excel(writer, sheet_name='Transactions', index=False)
        
        # Create summary sheet
        summary = pd.DataFrame({
            'Metric': ['Total Transactions', 'Total Amount', 'Average Transaction'],
            'Value': [
                len(df),
                f"${df['amount'].sum():.2f}",
                f"${df['amount'].mean():.2f}"
            ]
        })
        summary.to_excel(writer, sheet_name='Summary', index=False)
        
        # Create category summary
        category_summary = df.groupby('category')['amount'].agg(['sum', 'count']).reset_index()
        category_summary.columns = ['Category', 'Total Amount', 'Transaction Count']
        category_summary = category_summary.sort_values('Total Amount', ascending=False)
        
        # Format the Total Amount column
        category_summary['Total Amount'] = category_summary['Total Amount'].apply(lambda x: f"${x:.2f}")
        
        category_summary.to_excel(writer, sheet_name='Category Summary', index=False)
    
    # Get the value of the BytesIO buffer
    output.seek(0)
    return output.getvalue()

def add_download_button(df, filename="categorized_transactions.xlsx"):
    """
    Add a download button to the Streamlit app for downloading categorized data.
    
    Args:
        df (pandas.DataFrame): DataFrame with categorized transaction data
        filename (str): Name of the file to be downloaded
    """
    if df is None or df.empty:
        st.warning("No data available to download.")
        return
    
    # Create Excel file
    excel_data = create_download_excel(df)
    
    if excel_data is not None:
        st.download_button(
            label="Download Categorized Data (Excel)",
            data=excel_data,
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="download_button"
        )
        
        st.info("Click the button above to download the categorized financial data as an Excel file.")
    else:
        st.error("Failed to create downloadable file.")
