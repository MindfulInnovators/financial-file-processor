import os
import json
import pandas as pd
from datetime import datetime
import base64
from openai import OpenAI

class GPTFinancialParser:
    """
    A streamlined parser that uses OpenAI's GPT-4 Vision model to directly process financial documents
    of any format and extract structured financial data according to NZ accounting standards.
    """
    
    # System prompt for financial extraction and consolidation
    FINANCIAL_EXTRACTION_PROMPT = """
    You are an expert financial data extraction and consolidation assistant specialising in New Zealand accounting standards.

    Your task is to read the uploaded financial file — which may contain Profit and Loss Statements, Balance Sheets, Cashflow Statements, or financial transactions — and consolidate all available financial data into a single structured JSON table with these fields:
    - HighLevelCategory (Revenue, Cost of Goods Sold, Operating Expenses, Assets, Liabilities, Equity, Cashflow, GST, Other)
    - Subcategory (Specific subcategory name like Sales Revenue, Donations, Accounts Payable)
    - Amount (numeric, no dollar signs, no commas)
    - Entity (Department or Team Name if available; otherwise null)
    - Period (e.g., 'March 2025', 'FY2024 Q1') if available; otherwise null
    - Date (specific transaction date if available, otherwise null)
    - GST_Treatment (Standard, Zero-Rated, Exempt, or Unknown)
    - Currency (NZD)

    Instructions:
    - Consolidate multiple departments, time periods, and sheets if available.
    - Categorise all line items according to New Zealand accounting practices.
    - Always use New Zealand English spelling (e.g., categorise, organisation).
    - If values are missing, set fields to null.
    - Assume all amounts are in NZD unless stated otherwise.
    - Only return strict JSON. No explanations, no commentary.
    
    Return ONLY a JSON object with the format:
    {
        "table_data": [
            {
                "HighLevelCategory": "Category name",
                "Subcategory": "Subcategory name",
                "Amount": 1234.56,
                "Entity": "Department name or null",
                "Period": "Period description or null",
                "Date": "YYYY-MM-DD or null",
                "GST_Treatment": "Standard/Zero-Rated/Exempt/Unknown",
                "Currency": "NZD"
            },
            ...more rows...
        ]
    }
    """
    
    def __init__(self):
        """Initialize the parser with OpenAI API key from environment or secrets."""
        # Get API key from environment variable or Streamlit secrets
        api_key = os.getenv("OPENAI_API_KEY")
        
        # For Streamlit Cloud, try to get from st.secrets
        if not api_key:
            try:
                import streamlit as st
                if hasattr(st, 'secrets') and "OPENAI_API_KEY" in st.secrets:
                    api_key = st.secrets["OPENAI_API_KEY"]
            except:
                pass
        
        if not api_key:
            raise ValueError("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=api_key)
    
    def parse_financial_document(self, file_path):
        """
        Parse a financial document using GPT-4 Vision to transform it into a structured table.
        
        Args:
            file_path (str): Path to the financial document file
            
        Returns:
            pandas.DataFrame: DataFrame with structured financial data
        """
        try:
            print(f"Processing file: {file_path}")
            
            # Read file as binary
            with open(file_path, "rb") as file:
                file_content = file.read()
            
            # Encode file content in base64
            encoded_file = base64.b64encode(file_content).decode('utf-8')
            
            # Get file mime type based on extension
            _, ext = os.path.splitext(file_path)
            ext = ext.lower()
            
            if ext in ['.xlsx', '.xls']:
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            elif ext == '.csv':
                mime_type = "text/csv"
            elif ext == '.pdf':
                mime_type = "application/pdf"
            elif ext in ['.jpg', '.jpeg']:
                mime_type = "image/jpeg"
            elif ext == '.png':
                mime_type = "image/png"
            else:
                mime_type = "application/octet-stream"
            
            print(f"Sending file to OpenAI for processing (mime type: {mime_type})...")
            
            # Call OpenAI API with the file
            response = self.client.chat.completions.create(
                model="gpt-4-vision-preview",  # Using Vision model to process any file type
                messages=[
                    {"role": "system", "content": self.FINANCIAL_EXTRACTION_PROMPT},
                    {"role": "user", "content": [
                        {"type": "text", "text": "Please extract and structure the financial data from the attached file."},
                        {"type": "image_url", 
                         "image_url": {
                             "url": f"data:{mime_type};base64,{encoded_file}",
                             "detail": "high"
                         }}
                    ]}
                ],
                temperature=0,
                max_tokens=4096
            )
            
            # Extract JSON structured financial data
            result_text = response.choices[0].message.content
            
            # Clean up the response to ensure it's valid JSON
            # Remove any markdown code block markers if present
            result_text = result_text.replace("```json", "").replace("```", "").strip()
            
            print("Received response from OpenAI, parsing JSON...")
            
            # Parse the JSON response
            result = json.loads(result_text)
            
            # Convert to DataFrame
            df = pd.DataFrame(result.get("table_data", []))
            
            print(f"Successfully extracted {len(df)} rows of financial data.")
            
            # Ensure correct data types
            if 'Amount' in df.columns:
                df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
            
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.strftime('%Y-%m-%d')
            
            # Map the new columns to the expected columns in the application
            column_mapping = {
                'HighLevelCategory': 'main_category',
                'Subcategory': 'subcategory',
                'Amount': 'amount',
                'Date': 'date'
            }
            
            # Create a new DataFrame with the expected columns
            app_df = pd.DataFrame()
            
            # Map columns and fill with defaults if missing
            for new_col, app_col in column_mapping.items():
                if new_col in df.columns:
                    app_df[app_col] = df[new_col]
                else:
                    if app_col == 'date':
                        app_df[app_col] = pd.Timestamp.now().strftime('%Y-%m-%d')
                    elif app_col == 'amount':
                        app_df[app_col] = 0.0
                    elif app_col == 'main_category':
                        app_df[app_col] = "Uncategorized"
                    elif app_col == 'subcategory':
                        app_df[app_col] = "Unknown"
            
            # Create description field from available information
            if 'Entity' in df.columns and 'Period' in df.columns:
                # Combine Entity and Period for description if available
                app_df['description'] = df.apply(
                    lambda row: f"{row['Entity'] if pd.notna(row['Entity']) else ''} - "
                                f"{row['Subcategory']} "
                                f"({row['Period']})" if pd.notna(row['Period']) else f"{row['Subcategory']}",
                    axis=1
                )
            elif 'Subcategory' in df.columns:
                app_df['description'] = df['Subcategory']
            else:
                app_df['description'] = "Unknown"
            
            # Store the original data with all fields for potential future use
            app_df['original_data'] = df.apply(lambda x: x.to_dict(), axis=1)
            
            # Ensure we have all required columns for the application
            required_columns = ['date', 'description', 'amount', 'main_category', 'subcategory']
            for col in required_columns:
                if col not in app_df.columns:
                    if col == 'description':
                        app_df['description'] = "Unknown"
                    elif col == 'date':
                        app_df['date'] = pd.Timestamp.now().strftime('%Y-%m-%d')
                    elif col == 'amount':
                        app_df['amount'] = 0.0
                    elif col == 'main_category':
                        app_df['main_category'] = "Uncategorized"
                    elif col == 'subcategory':
                        app_df['subcategory'] = "Unknown"
            
            # Return the structured table with the required columns first, then any additional columns
            return app_df[required_columns + [col for col in app_df.columns if col not in required_columns]]
        
        except Exception as e:
            print(f"Error parsing financial document: {e}")
            # Return empty DataFrame with standard columns
            return pd.DataFrame(columns=['date', 'description', 'amount', 'main_category', 'subcategory'])

# Function to use in the main application
def parse_with_gpt(file_path):
    """
    Parse a financial document using GPT to transform it into a structured table.
    
    Args:
        file_path (str): Path to the financial document file
        
    Returns:
        pandas.DataFrame: DataFrame with structured financial data
    """
    try:
        parser = GPTFinancialParser()
        return parser.parse_financial_document(file_path)
    except Exception as e:
        print(f"Error parsing with GPT: {e}")
        return pd.DataFrame(columns=['date', 'description', 'amount', 'main_category', 'subcategory'])
