import pandas as pd
import os
import re
from datetime import datetime

def parse_excel(file_path):
    """
    Parse Excel files to extract financial data.
    
    Args:
        file_path (str): Path to the Excel file
        
    Returns:
        pandas.DataFrame: DataFrame with extracted financial data
    """
    try:
        # Read Excel file
        df = pd.read_excel(file_path)
        
        # Clean column names (lowercase, remove spaces)
        df.columns = [col.lower().strip().replace(' ', '_') for col in df.columns]
        
        # Try to identify key columns
        date_cols = [col for col in df.columns if 'date' in col or 'period' in col or 'time' in col]
        amount_cols = [col for col in df.columns if 'amount' in col or 'sum' in col or 'value' in col or 'price' in col]
        desc_cols = [col for col in df.columns if 'desc' in col or 'narration' in col or 'detail' in col or 'transaction' in col]
        
        # If columns not found, try to infer based on data types and patterns
        if not date_cols:
            for col in df.columns:
                # Check if column contains date-like values
                if df[col].dtype == 'datetime64[ns]' or (
                    df[col].dtype == 'object' and 
                    df[col].astype(str).str.match(r'\d{1,4}[-/\.]\d{1,2}[-/\.]\d{1,4}').any()
                ):
                    date_cols.append(col)
                    break
        
        if not amount_cols:
            for col in df.columns:
                # Check if column contains numeric values
                if pd.api.types.is_numeric_dtype(df[col]):
                    amount_cols.append(col)
                    break
        
        if not desc_cols:
            for col in df.columns:
                # Check if column contains text descriptions
                if df[col].dtype == 'object' and df[col].astype(str).str.len().mean() > 10:
                    desc_cols.append(col)
                    break
        
        # Create standardized DataFrame
        result_df = pd.DataFrame()
        
        # Extract date
        if date_cols:
            date_col = date_cols[0]
            result_df['date'] = df[date_col]
            # Convert to datetime if not already
            if result_df['date'].dtype != 'datetime64[ns]':
                result_df['date'] = pd.to_datetime(result_df['date'], errors='coerce')
        else:
            # Use current date if no date column found
            result_df['date'] = datetime.now()
        
        # Extract amount
        if amount_cols:
            amount_col = amount_cols[0]
            result_df['amount'] = df[amount_col]
            # Convert to numeric if not already
            if not pd.api.types.is_numeric_dtype(result_df['amount']):
                result_df['amount'] = pd.to_numeric(result_df['amount'].astype(str).str.replace('[^0-9.-]', '', regex=True), errors='coerce')
        else:
            result_df['amount'] = 0.0
        
        # Extract description
        if desc_cols:
            desc_col = desc_cols[0]
            result_df['description'] = df[desc_col]
        else:
            # Use filename as description if no description column found
            filename = os.path.basename(file_path)
            result_df['description'] = f"Transaction from {filename}"
        
        # Drop rows with missing values
        result_df = result_df.dropna(subset=['amount'])
        
        # Format date as string for display
        result_df['date'] = result_df['date'].dt.strftime('%Y-%m-%d')
        
        return result_df
    
    except Exception as e:
        print(f"Error parsing Excel file: {e}")
        # Return empty DataFrame with correct columns
        return pd.DataFrame(columns=['date', 'description', 'amount'])
