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
    A flexible parser that uses OpenAI's GPT to transform unformatted financial documents
    into structured tables with two-level categorization.
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
    
    def transform_to_structured_table(self, content):
        """
        Use GPT to transform unformatted financial document content into a structured table
        with two-level categorization (main_category and subcategory).
        
        Args:
            content (str): Raw content from the financial document
            
        Returns:
            pandas.DataFrame: Structured table with standardized columns including main_category and subcategory
        """
        try:
            # Define the main categories and subcategories
            main_categories = {
                "Revenue": ["Sales", "Grants", "Donations", "Interest", "Royalties", "Other Income"],
                "Expenses": ["Office", "Travel", "Marketing", "Professional Services", "Technology", "Payroll", "Utilities", "Rent", "Insurance", "Supplies", "Other Expenses"],
                "Assets": ["Equipment", "Property", "Investments", "Cash", "Accounts Receivable", "Other Assets"],
                "Liabilities": ["Loans", "Credit Cards", "Accounts Payable", "Taxes Payable", "Other Liabilities"],
                "Equity": ["Owner's Equity", "Retained Earnings", "Other Equity"],
                "Transfers": ["Internal Transfers", "External Transfers"],
                "Uncategorized": ["Unknown"]
            }
            
            # Flatten the categories for the prompt
            categories_text = ""
            for main_cat, subcats in main_categories.items():
                subcats_str = ", ".join([f'"{subcat}"' for subcat in subcats])
                categories_text += f'"{main_cat}": [{subcats_str}],\n'
            
            prompt = f"""
            You are a financial data extraction expert. Transform the following unformatted financial document content into a structured table with two-level categorization.
            
            INSTRUCTIONS:
            1. Analyze the document to determine if it's a transaction list, profit and loss statement, balance sheet, or other financial document.
            2. Extract all relevant financial data and organize it into a standardized table format.
            3. For ALL document types, create a table with these columns:
               - date: Use document date if available, or today's date if not (format: YYYY-MM-DD)
               - description: Detailed description of the item
               - amount: Numeric value (positive for income/assets, negative for expenses/liabilities)
               - main_category: Assign ONE of the following main categories: "Revenue", "Expenses", "Assets", "Liabilities", "Equity", "Transfers", "Uncategorized"
               - subcategory: Assign the most appropriate subcategory based on the main category:
                 {categories_text}
            
            4. For transaction lists: Each row should represent one transaction.
            5. For profit and loss statements: Create rows for each revenue and expense item.
            6. For balance sheets: Create rows for each asset, liability, and equity item.
            
            Return ONLY a JSON object with the format:
            {{
                "table_data": [
                    {{
                        "date": "YYYY-MM-DD",
                        "description": "Detailed description",
                        "amount": 1234.56,
                        "main_category": "Main Category",
                        "subcategory": "Subcategory"
                    }},
                    ...more rows...
                ]
            }}
            
            IMPORTANT:
            - Include ALL financial data from the document
            - Ensure amounts are numeric values
            - Use ONLY the provided main categories and their corresponding subcategories
            - Use NZ English spelling conventions
            - If a field is unknown, use null or empty string
            - Make sure the JSON is valid and properly formatted
            
            Document content:
            {content[:8000]}  # Limit content to avoid token limits
            """
            
            print("Sending content to GPT for transformation with two-level categorization...")
            
            response = self.client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "You are a financial data extraction expert that transforms unformatted financial documents into structured tables with two-level categorization using NZ English spelling."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            print(f"GPT transformation complete. Extracted {len(result.get('table_data', []))} rows of data with two-level categorization.")
            
            # Convert to DataFrame
            df = pd.DataFrame(result.get("table_data", []))
            
            # Ensure correct data types
            if 'amount' in df.columns:
                df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
            
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'], errors='coerce').dt.strftime('%Y-%m-%d')
            
            # Ensure we have the required columns for the application
            required_columns = ['date', 'description', 'amount', 'main_category', 'subcategory']
            for col in required_columns:
                if col not in df.columns:
                    if col == 'description':
                        df['description'] = "Unknown"
                    elif col == 'date':
                        df['date'] = pd.Timestamp.now().strftime('%Y-%m-%d')
                    elif col == 'amount':
                        df['amount'] = 0.0
                    elif col == 'main_category':
                        df['main_category'] = "Uncategorized"
                    elif col == 'subcategory':
                        df['subcategory'] = "Unknown"
            
            # Return the structured table with two-level categorization
            return df[required_columns]
        
        except Exception as e:
            print(f"Error transforming document to structured table: {e}")
            # Return empty DataFrame with required columns
            return pd.DataFrame(columns=['date', 'description', 'amount', 'main_category', 'subcategory'])
    
    def parse_financial_document(self, file_path):
        """
        Parse a financial document using GPT to transform it into a structured table with two-level categorization.
        
        Args:
            file_path (str): Path to the financial document file
            
        Returns:
            pandas.DataFrame: DataFrame with structured financial data including main_category and subcategory
        """
        try:
            # Extract content from file
            content_data = self.extract_file_content(file_path)
            content = content_data["main_content"]
            
            # Transform content to structured table with two-level categorization
            df = self.transform_to_structured_table(content)
            
            return df
        except Exception as e:
            print(f"Error parsing financial document: {e}")
            # Return empty DataFrame with standard columns
            return pd.DataFrame(columns=['date', 'description', 'amount', 'main_category', 'subcategory'])

# Function to use in the main application
def parse_with_gpt(file_path):
    """
    Parse a financial document using GPT to transform it into a structured table with two-level categorization.
    
    Args:
        file_path (str): Path to the financial document file
        
    Returns:
        pandas.DataFrame: DataFrame with structured financial data including main_category and subcategory
    """
    try:
        parser = GPTFinancialParser()
        return parser.parse_financial_document(file_path)
    except Exception as e:
        print(f"Error parsing with GPT: {e}")
        return pd.DataFrame(columns=['date', 'description', 'amount', 'main_category', 'subcategory'])
