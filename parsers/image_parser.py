import pandas as pd
import os
import re
from datetime import datetime
import pytesseract
from PIL import Image

def parse_image(file_path):
    """
    Parse image files to extract financial data using OCR.
    
    Args:
        file_path (str): Path to the image file
        
    Returns:
        pandas.DataFrame: DataFrame with extracted financial data
    """
    try:
        # Open the image
        img = Image.open(file_path)
        
        # Extract text using OCR
        extracted_text = pytesseract.image_to_string(img)
        
        # Look for structured data in the text
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
        
        # If no structured data found, try to identify table-like structures
        # This is a simplified approach - in a real application, more sophisticated
        # table detection algorithms would be used
        
        # Look for lines with multiple numeric values
        table_lines = []
        for line in lines:
            # Count numbers in the line
            num_count = len(re.findall(r'\d+[.,]?\d*', line))
            if num_count >= 2:
                table_lines.append(line)
        
        # If we found potential table lines
        if table_lines:
            # Try to extract data from these lines
            for line in table_lines:
                # Try to extract date
                date_match = re.search(date_pattern, line)
                date = date_match.group(0) if date_match else datetime.now().strftime('%Y-%m-%d')
                
                # Try to extract amount
                amount_match = re.search(amount_pattern, line)
                amount = amount_match.group(0) if amount_match else "0.0"
                amount = re.sub(r'[$£€\s]', '', amount)
                
                # Extract description (everything else)
                description = line
                if date_match:
                    description = re.sub(date_pattern, '', description)
                if amount_match:
                    description = re.sub(amount_pattern, '', description)
                description = description.strip()
                
                # Add to lists
                dates.append(date)
                descriptions.append(description)
                amounts.append(amount)
            
            # Create DataFrame
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
        
        # If no structured data found, create a simple entry
        filename = os.path.basename(file_path)
        result_df = pd.DataFrame({
            'date': [datetime.now().strftime('%Y-%m-%d')],
            'description': [f"Data from {filename} - manual review required"],
            'amount': [0.0]
        })
        
        return result_df
    
    except Exception as e:
        print(f"Error parsing image file: {e}")
        # Return empty DataFrame with correct columns
        return pd.DataFrame(columns=['date', 'description', 'amount'])
