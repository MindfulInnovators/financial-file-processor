import pandas as pd
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def categorize_transactions(transactions_df):
    """
    Categorize financial transactions using OpenAI's GPT-4.1 API.
    
    Args:
        transactions_df (pandas.DataFrame): DataFrame with transaction data
            Must contain 'date', 'description', and 'amount' columns
            
    Returns:
        pandas.DataFrame: Original DataFrame with added 'category' column
    """
    try:
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
            print("Warning: OpenAI API key not found. Using placeholder categories.")
            # Add placeholder category if API key is missing
            transactions_df['category'] = "Uncategorized"
            return transactions_df
        
        # Initialize OpenAI client
        client = OpenAI(api_key=api_key)
        
        # Create a copy of the DataFrame to avoid modifying the original
        result_df = transactions_df.copy()
        
        # Add a new column for categories
        result_df['category'] = ""
        
        # Prepare transactions for batch processing
        transactions_list = []
        for _, row in result_df.iterrows():
            transaction = {
                'date': row['date'],
                'description': row['description'],
                'amount': float(row['amount'])
            }
            transactions_list.append(transaction)
        
        # Create prompt for OpenAI
        prompt = f"""
        I have a list of financial transactions that I need categorized into standard accounting categories.
        Please use New Zealand English spelling conventions.
        
        For each transaction, assign ONE of the following categories:
        - Revenue (income, sales, etc.)
        - Expenses: Office (rent, utilities, supplies, etc.)
        - Expenses: Travel (airfare, accommodation, meals while traveling, etc.)
        - Expenses: Marketing (advertising, promotions, etc.)
        - Expenses: Professional Services (legal, accounting, consulting, etc.)
        - Expenses: Technology (software, hardware, IT services, etc.)
        - Expenses: Payroll (salaries, wages, benefits, etc.)
        - Expenses: Other (miscellaneous expenses)
        - Asset Purchase (equipment, property, investments, etc.)
        - Liability Payment (loan repayments, credit card payments, etc.)
        - Transfer (moving money between accounts)
        - Uncategorized (if unable to determine)
        
        Here are the transactions:
        {transactions_list}
        
        Return ONLY a JSON array with the categories in the same order as the transactions, like this:
        ["Category1", "Category2", "Category3", ...]
        """
        
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4-turbo",  # Using the latest available model as a fallback for GPT-4.1
            messages=[
                {"role": "system", "content": "You are a financial categorization assistant that follows New Zealand English spelling conventions."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,  # Low temperature for more consistent results
            response_format={"type": "json_object"}
        )
        
        # Extract categories from response
        try:
            import json
            response_content = response.choices[0].message.content
            print(f"API Response: {response_content}")  # Debug output
            
            # Parse the JSON response
            response_json = json.loads(response_content)
            
            # Check if 'categories' key exists
            if 'categories' in response_json:
                categories = response_json["categories"]
            else:
                # If not, try to use the first array found in the response
                for key, value in response_json.items():
                    if isinstance(value, list):
                        categories = value
                        break
                else:
                    # If no array found, raise an error
                    raise KeyError("No categories array found in response")
            
            # Ensure we have the right number of categories
            if len(categories) == len(result_df):
                result_df['category'] = categories
            else:
                print(f"Warning: Received {len(categories)} categories for {len(result_df)} transactions. Using placeholder categories.")
                result_df['category'] = "Uncategorized"
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error parsing API response: {e}")
            print(f"Response content: {response.choices[0].message.content}")
            result_df['category'] = "Uncategorized"
        
        return result_df
    
    except Exception as e:
        print(f"Error categorizing transactions: {e}")
        # Add placeholder category if there's an error
        transactions_df['category'] = "Uncategorized"
        return transactions_df
