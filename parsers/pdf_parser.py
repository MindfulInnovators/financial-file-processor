import pandas as pd
import pdfplumber
import os
import re
from datetime import datetime

def parse_pdf(file_path):
    """
    Parse PDF files to extract financial data.
    
    Args:
        file_path (str): Path to the PDF file
        
    Returns:
        pandas.DataFrame: DataFrame with extracted financial data
    """
    try:
        # Extract text from PDF
        extracted_text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                extracted_text += page.extract_text() + "\n"
        
        # Look for table-like structures in the text
        lines = extracted_text.split('\n')
        
        # Initialize lists to store extracted data
        dates = []
        descriptions = []
        amounts = []
        
        # Regular expressions for pattern matching
        date_pattern = r'\d{1,4}[-/\.]\d{1,2}[-/\.]\d{1,4}'
        amount_pattern = r'[$£€]?\s*\d+[.,]\d+'
        
        # Process each line
        for line in lines:
            # Skip empty lines
            if not line.strip():
                continue
            
            # Try to extract date
            date_match = re.search(date_pattern, line)
            date = date_match.group(0) if date_match else None
            
            # Try to extract amount
            amount_match = re.search(amount_pattern, line)
            amount = amount_match.group(0) if amount_match else None
            
            # If we found both date and amount, extract description
            if date and amount:
                # Remove date and amount from line to get description
                description = line
                description = re.sub(date_pattern, '', description)
                description = re.sub(amount_pattern, '', description)
                description = description.strip()
                
                # Clean up amount (remove currency symbols)
                amount = re.sub(r'[$£€\s]', '', amount)
                
                # Add to lists
                dates.append(date)
                descriptions.append(description)
                amounts.append(amount)
        
        # If we found structured data, create DataFrame
        if dates and amounts:
            result_df = pd.DataFrame({
                'date': dates,
                'description': descriptions,
                'amount': amounts
            })
            
            # Convert date to datetime
            result_df['date'] = pd.to_datetime(result_df['date'], errors='coerce')
            
            # Convert amount to numeric
            result_df['amount'] = pd.to_numeric(result_df['amount'].str.replace(',', '.'), errors='coerce')
            
            # Drop rows with missing values
            result_df = result_df.dropna(subset=['amount'])
            
            # Format date as string for display
            result_df['date'] = result_df['date'].dt.strftime('%Y-%m-%d')
            
            return result_df
        
        # If no structured data found, try to extract tables using pdfplumber
        tables_data = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    if table:
                        tables_data.append(table)
        
        # If tables found, process them
        if tables_data:
            # Assume first row is header
            headers = tables_data[0][0]
            data = []
            
            # Process all tables
            for table in tables_data:
                for row in table[1:]:  # Skip header row
                    data.append(row)
            
            # Create DataFrame
            df = pd.DataFrame(data, columns=headers)
            
            # Clean column names
            df.columns = [str(col).lower().strip().replace(' ', '_') for col in df.columns]
            
            # Try to identify key columns
            date_cols = [col for col in df.columns if 'date' in str(col).lower() or 'period' in str(col).lower() or 'time' in str(col).lower()]
            amount_cols = [col for col in df.columns if 'amount' in str(col).lower() or 'sum' in str(col).lower() or 'value' in str(col).lower() or 'price' in str(col).lower()]
            desc_cols = [col for col in df.columns if 'desc' in str(col).lower() or 'narration' in str(col).lower() or 'detail' in str(col).lower() or 'transaction' in str(col).lower()]
            
            # Create standardized DataFrame
            result_df = pd.DataFrame()
            
            # Extract date
            if date_cols:
                date_col = date_cols[0]
                result_df['date'] = df[date_col]
                # Convert to datetime if not already
                result_df['date'] = pd.to_datetime(result_df['date'], errors='coerce')
            else:
                # Use current date if no date column found
                result_df['date'] = datetime.now()
            
            # Extract amount
            if amount_cols:
                amount_col = amount_cols[0]
                result_df['amount'] = df[amount_col]
                # Convert to numeric if not already
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
        
        # If no structured data found, create a simple entry
        filename = os.path.basename(file_path)
        result_df = pd.DataFrame({
            'date': [datetime.now().strftime('%Y-%m-%d')],
            'description': [f"Data from {filename} - manual review required"],
            'amount': [0.0]
        })
        
        return result_df
    
    except Exception as e:
        print(f"Error parsing PDF file: {e}")
        # Return empty DataFrame with correct columns
        return pd.DataFrame(columns=['date', 'description', 'amount'])
