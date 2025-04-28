import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import numpy as np
from io import BytesIO

def create_summary_charts(df):
    """
    Create summary charts for financial data visualization.
    
    Args:
        df (pandas.DataFrame): DataFrame with categorized transaction data
            Must contain 'amount' and 'category' columns
            
    Returns:
        dict: Dictionary containing various chart figures
    """
    charts = {}
    
    # Ensure we have data to visualize
    if df is None or df.empty:
        return charts
    
    # Group by category and calculate sum
    category_summary = df.groupby('category')['amount'].agg(['sum', 'count']).reset_index()
    category_summary = category_summary.sort_values('sum', ascending=False)
    
    # Create color palette - green for revenue, red for expenses, blue for others
    colors = []
    for category in category_summary['category']:
        if 'Revenue' in category:
            colors.append('#28a745')  # Green
        elif 'Expenses' in category:
            colors.append('#dc3545')  # Red
        else:
            colors.append('#007bff')  # Blue
    
    # 1. Bar chart for category totals
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    bars = ax1.bar(category_summary['category'], category_summary['sum'], color=colors)
    
    # Add data labels
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'${height:.2f}',
                ha='center', va='bottom', rotation=0)
    
    ax1.set_xlabel('Category')
    ax1.set_ylabel('Amount ($)')
    ax1.set_title('Financial Summary by Category')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    charts['category_totals'] = fig1
    
    # 2. Pie chart for category distribution
    fig2, ax2 = plt.subplots(figsize=(10, 8))
    wedges, texts, autotexts = ax2.pie(
        category_summary['sum'], 
        labels=category_summary['category'],
        autopct='%1.1f%%',
        startangle=90,
        colors=colors
    )
    
    # Make text more readable
    for text in texts:
        text.set_fontsize(9)
    for autotext in autotexts:
        autotext.set_fontsize(9)
        autotext.set_color('white')
    
    ax2.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
    ax2.set_title('Proportion of Spending by Category')
    plt.tight_layout()
    charts['category_pie'] = fig2
    
    # 3. Revenue vs Expenses bar chart
    revenue = df[df['category'].str.contains('Revenue')]['amount'].sum()
    expenses = df[df['category'].str.contains('Expenses')]['amount'].sum()
    other = df[~(df['category'].str.contains('Revenue') | df['category'].str.contains('Expenses'))]['amount'].sum()
    
    summary_data = pd.DataFrame({
        'Category': ['Revenue', 'Expenses', 'Other'],
        'Amount': [revenue, expenses, other]
    })
    
    fig3, ax3 = plt.subplots(figsize=(8, 6))
    summary_bars = ax3.bar(
        summary_data['Category'], 
        summary_data['Amount'],
        color=['#28a745', '#dc3545', '#007bff']
    )
    
    # Add data labels
    for bar in summary_bars:
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height,
                f'${height:.2f}',
                ha='center', va='bottom', rotation=0)
    
    ax3.set_xlabel('Category')
    ax3.set_ylabel('Amount ($)')
    ax3.set_title('Revenue vs Expenses Summary')
    plt.tight_layout()
    charts['revenue_expenses'] = fig3
    
    # 4. Transaction count by category
    fig4, ax4 = plt.subplots(figsize=(10, 6))
    count_bars = ax4.bar(category_summary['category'], category_summary['count'], color='#17a2b8')
    
    # Add data labels
    for bar in count_bars:
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom', rotation=0)
    
    ax4.set_xlabel('Category')
    ax4.set_ylabel('Number of Transactions')
    ax4.set_title('Transaction Count by Category')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    charts['transaction_count'] = fig4
    
    return charts

def display_financial_dashboard(df):
    """
    Display financial dashboard with charts and tables in Streamlit.
    
    Args:
        df (pandas.DataFrame): DataFrame with categorized transaction data
    """
    if df is None or df.empty:
        st.warning("No data available to display.")
        return
    
    # Display summary statistics
    st.subheader("Financial Summary")
    
    # Calculate key metrics
    total_transactions = len(df)
    total_amount = df['amount'].sum()
    avg_transaction = df['amount'].mean()
    
    # Create columns for metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Transactions", f"{total_transactions}")
    with col2:
        st.metric("Total Amount", f"${total_amount:.2f}")
    with col3:
        st.metric("Average Transaction", f"${avg_transaction:.2f}")
    
    # Create and display charts
    charts = create_summary_charts(df)
    
    # Display Revenue vs Expenses chart
    if 'revenue_expenses' in charts:
        st.subheader("Revenue vs Expenses")
        st.pyplot(charts['revenue_expenses'])
    
    # Display Category Totals chart
    if 'category_totals' in charts:
        st.subheader("Amount by Category")
        st.pyplot(charts['category_totals'])
    
    # Display Category Pie chart
    if 'category_pie' in charts:
        st.subheader("Spending Distribution")
        st.pyplot(charts['category_pie'])
    
    # Display Transaction Count chart
    if 'transaction_count' in charts:
        st.subheader("Transaction Count by Category")
        st.pyplot(charts['transaction_count'])
    
    # Display detailed transaction table
    st.subheader("Transaction Details")
    st.dataframe(df)

def generate_excel_report(df):
    """
    Generate an Excel report with categorized data and charts.
    
    Args:
        df (pandas.DataFrame): DataFrame with categorized transaction data
            
    Returns:
        bytes: Excel file as bytes
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
                df['amount'].sum(),
                df['amount'].mean()
            ]
        })
        summary.to_excel(writer, sheet_name='Summary', index=False)
        
        # Create category summary
        category_summary = df.groupby('category')['amount'].agg(['sum', 'count']).reset_index()
        category_summary.columns = ['Category', 'Total Amount', 'Transaction Count']
        category_summary = category_summary.sort_values('Total Amount', ascending=False)
        category_summary.to_excel(writer, sheet_name='Category Summary', index=False)
    
    # Get the value of the BytesIO buffer
    output.seek(0)
    return output.getvalue()
