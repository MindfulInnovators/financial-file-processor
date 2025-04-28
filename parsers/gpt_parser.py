import pandas as pd
import os
from openai import OpenAI
from dotenv import load_dotenv
import json
import io
import openpyxl
import csv

# Load environment variables
load_dotenv()

class GPTFinancialParser:
    """
    A flexible parser that uses OpenAI's GPT to extract structured financial data
    from various document types (profit and loss, balance sheet, transaction list).
    """
    
    def __init__(self):
        """Initialize the parser with OpenAI API key from environment or secrets."""
        # Get API key from environment variable or Streamlit secrets
        api_key = os.getenv("OPENAI_API_KEY")
        
        # For Streamlit Cloud, try to get from st.secrets
        if not api_key:
            try:
                import streamlit as st
                api_key = st.secrets["OPENAI_API_KEY"]
            except:
                pass
        
        if not api_key:
            raise ValueError("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=api_key)
    
    def extract_file_content(self, file_path):
        """Extract content from file based on its extension."""
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        if ext in ['.xlsx', '.xls']:
            return self._extract_excel_content(file_path)
        elif ext == '.csv':
            return self._extract_csv_content(file_path)
        elif ext == '.pdf':
            return self._extract_pdf_content(file_path)
        elif ext in ['.jpg', '.jpeg', '.png']:
            return self._extract_image_content(file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")
    
    def _extract_excel_content(self, file_path):
        """Extract content from Excel file."""
        try:
            # Read Excel file
            df = pd.read_excel(file_path)
            
            # Convert to string representation
            buffer = io.StringIO()
            df.to_csv(buffer, index=False)
            content = buffer.getvalue()
            
            # Also get sheet names and first few rows of each sheet for context
            workbook = openpyxl.load_workbook(file_path, read_only=True)
            sheet_info = []
            
            for sheet_name in workbook.sheetnames:
                sheet = workbook[sheet_name]
                rows = []
                for i, row in enumerate(sheet.iter_rows(values_only=True)):
                    if i >= 10:  # Get first 10 rows
                        break
                    rows.append(row)
                sheet_info.append({
                    "name": sheet_name,
                    "sample_rows": rows
                })
            
            return {
                "main_content": content,
                "sheet_info": sheet_info
            }
        except Exception as e:
            raise ValueError(f"Error extracting Excel content: {e}")
    
    def _extract_csv_content(self, file_path):
        """Extract content from CSV file."""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            return {"main_content": content}
        except Exception as e:
            raise ValueError(f"Error extracting CSV content: {e}")
    
    def _extract_pdf_content(self, file_path):
        """Extract content from PDF file."""
        try:
            import pdfplumber
            
            content = ""
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    content += page.extract_text() + "\n\n"
                    
                    # Extract tables if any
                    tables = page.extract_tables()
                    if tables:
                        content += "TABLES:\n"
                        for table in tables:
                            for row in table:
                                content += ",".join([str(cell) if cell else "" for cell in row]) + "\n"
                            content += "\n"
            
            return {"main_content": content}
        except Exception as e:
            raise ValueError(f"Error extracting PDF content: {e}")
    
    def _extract_image_content(self, file_path):
        """Extract content from image file using OCR."""
        try:
            import pytesseract
            from PIL import Image
            
            img = Image.open(file_path)
            content = pytesseract.image_to_string(img)
            
            return {"main_content": content}
        except Exception as e:
            raise ValueError(f"Error extracting image content: {e}")
    
    def detect_document_type(self, content):
        """Use GPT to detect the type of financial document."""
        try:
            prompt = f"""
            Analyze the following financial document content and determine its type.
            Possible types include:
            1. Transaction List - Contains individual financial transactions with dates, descriptions, and amounts
            2. Profit and Loss Statement - Shows revenue, expenses, and profit/loss over a period
            3. Balance Sheet - Shows assets, liabilities, and equity at a specific point in time
            4. Cash Flow Statement - Shows cash inflows and outflows
            5. Other - Any other type of financial document
            
            Return ONLY a JSON object with the format: {{"document_type": "type_name"}}
            
            Document content:
            {content[:4000]}  # Limit content to avoid token limits
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "You are a financial document analysis assistant that identifies document types."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result["document_type"]
        except Exception as e:
            print(f"Error detecting document type: {e}")
            return "Unknown"
    
    def parse_financial_document(self, file_path):
        """
        Parse a financial document using GPT to extract structured data.
        
        Args:
            file_path (str): Path to the financial document file
            
        Returns:
            pandas.DataFrame: DataFrame with structured financial data
        """
        try:
            # Extract content from file
            content_data = self.extract_file_content(file_path)
            content = content_data["main_content"]
            
            # Detect document type
            document_type = self.detect_document_type(content)
            print(f"Detected document type: {document_type}")
            
            # Create appropriate prompt based on document type
            if document_type.lower() in ["transaction list", "transactions"]:
                return self._parse_transaction_list(content)
            elif document_type.lower() in ["profit and loss statement", "profit and loss", "income statement"]:
                return self._parse_profit_and_loss(content)
            elif document_type.lower() in ["balance sheet"]:
                return self._parse_balance_sheet(content)
            else:
                # Default to generic financial data extraction
                return self._parse_generic_financial_data(content)
        except Exception as e:
            print(f"Error parsing financial document: {e}")
            # Return empty DataFrame with standard columns
            return pd.DataFrame(columns=['date', 'description', 'amount'])
    
    def _parse_transaction_list(self, content):
        """Parse a transaction list document."""
        try:
            prompt = f"""
            Extract transaction data from the following financial document.
            The document appears to be a transaction list.
            
            For each transaction, extract:
            1. Date - in YYYY-MM-DD format if available, otherwise use the document date or today's date
            2. Description - the transaction description or payee
            3. Amount - the transaction amount as a numeric value (positive for income, negative for expenses)
            
            Return ONLY a JSON object with the format:
            {{
                "transactions": [
                    {{"date": "YYYY-MM-DD", "description": "Description 1", "amount": 123.45}},
                    {{"date": "YYYY-MM-DD", "description": "Description 2", "amount": -67.89}}
                ]
            }}
            
            Document content:
            {content[:8000]}  # Limit content to avoid token limits
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "You are a financial data extraction assistant that extracts transaction data from documents."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Convert to DataFrame
            df = pd.DataFrame(result["transactions"])
            
            # Ensure correct data types
            if 'amount' in df.columns:
                df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
            
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'], errors='coerce').dt.strftime('%Y-%m-%d')
            
            return df
        except Exception as e:
            print(f"Error parsing transaction list: {e}")
            return pd.DataFrame(columns=['date', 'description', 'amount'])
    
    def _parse_profit_and_loss(self, content):
        """Parse a profit and loss statement."""
        try:
            prompt = f"""
            Extract financial data from the following profit and loss statement.
            
            For each line item, extract:
            1. Date - use the statement period end date if available, otherwise today's date
            2. Description - the line item description (e.g., "Revenue", "Expenses: Rent", "Net Income")
            3. Amount - the line item amount as a numeric value
            
            Group the items into these categories:
            - Revenue items (positive amounts)
            - Expense items (negative amounts)
            - Profit/Loss calculations
            
            Return ONLY a JSON object with the format:
            {{
                "transactions": [
                    {{"date": "YYYY-MM-DD", "description": "Revenue: Sales", "amount": 10000.00}},
                    {{"date": "YYYY-MM-DD", "description": "Expenses: Rent", "amount": -2000.00}},
                    {{"date": "YYYY-MM-DD", "description": "Net Income", "amount": 8000.00}}
                ]
            }}
            
            Document content:
            {content[:8000]}  # Limit content to avoid token limits
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "You are a financial data extraction assistant that extracts profit and loss data from statements."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Convert to DataFrame
            df = pd.DataFrame(result["transactions"])
            
            # Ensure correct data types
            if 'amount' in df.columns:
                df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
            
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'], errors='coerce').dt.strftime('%Y-%m-%d')
            
            return df
        except Exception as e:
            print(f"Error parsing profit and loss statement: {e}")
            return pd.DataFrame(columns=['date', 'description', 'amount'])
    
    def _parse_balance_sheet(self, content):
        """Parse a balance sheet."""
        try:
            prompt = f"""
            Extract financial data from the following balance sheet.
            
            For each line item, extract:
            1. Date - use the balance sheet date if available, otherwise today's date
            2. Description - the line item description (e.g., "Assets: Cash", "Liabilities: Loans", "Equity: Retained Earnings")
            3. Amount - the line item amount as a numeric value
            
            Group the items into these categories:
            - Assets (positive amounts)
            - Liabilities (negative amounts)
            - Equity items
            
            Return ONLY a JSON object with the format:
            {{
                "transactions": [
                    {{"date": "YYYY-MM-DD", "description": "Assets: Cash", "amount": 5000.00}},
                    {{"date": "YYYY-MM-DD", "description": "Liabilities: Loans", "amount": -3000.00}},
                    {{"date": "YYYY-MM-DD", "description": "Equity: Retained Earnings", "amount": 2000.00}}
                ]
            }}
            
            Document content:
            {content[:8000]}  # Limit content to avoid token limits
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "You are a financial data extraction assistant that extracts balance sheet data."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Convert to DataFrame
            df = pd.DataFrame(result["transactions"])
            
            # Ensure correct data types
            if 'amount' in df.columns:
                df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
            
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'], errors='coerce').dt.strftime('%Y-%m-%d')
            
            return df
        except Exception as e:
            print(f"Error parsing balance sheet: {e}")
            return pd.DataFrame(columns=['date', 'description', 'amount'])
    
    def _parse_generic_financial_data(self, content):
        """Parse generic financial data when document type is unclear."""
        try:
            prompt = f"""
            Extract financial data from the following document.
            The document type is unclear, so extract any financial information you can find.
            
            For each financial item, extract:
            1. Date - any date associated with the item, or the document date, or today's date
            2. Description - a description of the financial item
            3. Amount - the monetary amount as a numeric value
            
            Return ONLY a JSON object with the format:
            {{
                "transactions": [
                    {{"date": "YYYY-MM-DD", "description": "Item 1", "amount": 123.45}},
                    {{"date": "YYYY-MM-DD", "description": "Item 2", "amount": 67.89}}
                ]
            }}
            
            Document content:
            {content[:8000]}  # Limit content to avoid token limits
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "You are a financial data extraction assistant that extracts financial data from documents."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Convert to DataFrame
            df = pd.DataFrame(result["transactions"])
            
            # Ensure correct data types
            if 'amount' in df.columns:
                df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
            
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'], errors='coerce').dt.strftime('%Y-%m-%d')
            
            return df
        except Exception as e:
            print(f"Error parsing generic financial data: {e}")
            return pd.DataFrame(columns=['date', 'description', 'amount'])

# Function to use in the main application
def parse_with_gpt(file_path):
    """
    Parse a financial document using GPT.
    
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
        return pd.DataFrame(columns=['date', 'description', 'amount'])
