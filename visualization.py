#!/usr/bin/env python3
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

def display_financial_dashboard(df):
    """
    Display an enhanced, modern financial dashboard with filtering and two-level categorization.

    Args:
        df (pd.DataFrame): DataFrame containing financial data with columns 
                           ["date", "description", "amount", "main_category", "subcategory"].
    """
    st.header("📊 Financial Dashboard")

    if df is None or df.empty:
        st.warning("No data available to display. Please upload a file first.")
        return

    # --- Data Preparation & Cleaning ---
    try:
        df_processed = df.copy()
        # Ensure correct data types
        df_processed["date"] = pd.to_datetime(df_processed["date"], errors="coerce")
        df_processed["amount"] = pd.to_numeric(df_processed["amount"], errors="coerce")
        df_processed["main_category"] = df_processed["main_category"].astype(str).fillna("Uncategorized")
        df_processed["subcategory"] = df_processed["subcategory"].astype(str).fillna("Unknown")
        
        # Drop rows where essential data couldn't be parsed
        df_processed.dropna(subset=["date", "amount"], inplace=True)
        
        if df_processed.empty:
            st.warning("No valid financial data found after cleaning. Please check the input file format and content.")
            return
            
        df_processed["year_month"] = df_processed["date"].dt.to_period("M").astype(str) # For grouping
        df_processed["year"] = df_processed["date"].dt.year.astype(str)
        
    except Exception as e:
        st.error(f"Error preparing data for visualization: {e}")
        st.dataframe(df) # Show raw data for debugging
        return

    # --- Sidebar Filters ---
    st.sidebar.header("Dashboard Filters")
    
    # Date Range Filter
    min_date = df_processed["date"].min().date()
    max_date = df_processed["date"].max().date()
    
    # Check if min_date and max_date are the same
    if min_date == max_date:
        # Set a default range, e.g., the single day
        date_range = st.sidebar.date_input(
            "Select Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            key="date_filter"
        )
    else:
         date_range = st.sidebar.date_input(
            "Select Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            key="date_filter"
        )

    # Handle case where user might select end_date before start_date
    if len(date_range) == 2:
        start_date, end_date = date_range
        if start_date > end_date:
            st.sidebar.warning("End date cannot be before start date. Adjusting...")
            start_date, end_date = end_date, start_date # Swap them
    else: # Handle case where only one date might be selected initially
        start_date = min_date
        end_date = max_date
        st.sidebar.info("Select both a start and end date for filtering.")

    # Main Category Filter
    all_main_categories = sorted(df_processed["main_category"].unique())
    selected_main_categories = st.sidebar.multiselect(
        "Filter by Main Category",
        options=all_main_categories,
        default=all_main_categories,
        key="main_cat_filter"
    )
    
    # Subcategory Filter (dynamic based on main category selection)
    if not selected_main_categories:
         selected_main_categories = all_main_categories # Avoid error if nothing selected
         
    available_subcategories = sorted(df_processed[df_processed["main_category"].isin(selected_main_categories)]["subcategory"].unique())
    selected_subcategories = st.sidebar.multiselect(
        "Filter by Subcategory",
        options=available_subcategories,
        default=available_subcategories,
        key="sub_cat_filter"
    )
    if not selected_subcategories:
        selected_subcategories = available_subcategories # Avoid error if nothing selected

    # --- Apply Filters ---
    filtered_df = df_processed[
        (df_processed["date"].dt.date >= start_date) &
        (df_processed["date"].dt.date <= end_date) &
        (df_processed["main_category"].isin(selected_main_categories)) &
        (df_processed["subcategory"].isin(selected_subcategories))
    ].copy()

    if filtered_df.empty:
        st.warning("No data matches the selected filters.")
        return

    # --- Key Metrics ---
    st.subheader("Key Metrics (Filtered Period)")
    total_revenue = filtered_df[filtered_df["main_category"] == "Revenue"]["amount"].sum()
    total_expenses = filtered_df[filtered_df["main_category"] == "Expenses"]["amount"].sum() # Expenses are negative
    net_income = total_revenue + total_expenses # Since expenses are negative
    total_assets_value = filtered_df[filtered_df["main_category"] == "Assets"]["amount"].sum()
    total_liabilities_value = filtered_df[filtered_df["main_category"] == "Liabilities"]["amount"].sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("Revenue", f"${total_revenue:,.2f}")
    col2.metric("Expenses", f"${abs(total_expenses):,.2f}")
    col3.metric("Net Income", f"${net_income:,.2f}", delta=f"{net_income:,.2f}")
    
    # Optional: Show Assets/Liabilities if present
    if total_assets_value != 0 or total_liabilities_value != 0:
        col4, col5 = st.columns(2)
        if total_assets_value != 0:
             col4.metric("Assets Value Change", f"${total_assets_value:,.2f}")
        if total_liabilities_value != 0:
             col5.metric("Liabilities Value Change", f"${total_liabilities_value:,.2f}")

    st.divider()

    # --- Charts --- 
    st.subheader("Visualizations (Filtered Period)")
    
    # Layout columns for charts
    chart_col1, chart_col2 = st.columns(2)

    # 1. Income vs Expenses Over Time (Monthly Bar Chart)
    with chart_col1:
        try:
            monthly_summary = filtered_df.groupby("year_month").agg(
                Revenue=("amount", lambda x: x[x > 0].sum()),
                Expenses=("amount", lambda x: abs(x[x < 0].sum())) # Use absolute for plotting
            ).reset_index()
            
            fig_monthly = px.bar(monthly_summary, x="year_month", y=["Revenue", "Expenses"], 
                                 title="Monthly Revenue vs Expenses", barmode="group",
                                 labels={"year_month": "Month", "value": "Amount ($)", "variable": "Type"},
                                 color_discrete_map={"Revenue": "#2ca02c", "Expenses": "#d62728"})
            fig_monthly.update_layout(legend_title_text="Category", yaxis_tickprefix="$", yaxis_tickformat=",.2f")
            fig_monthly.update_traces(hovertemplate="<b>%{x}</b><br>%{data.name}: $%{y:,.2f}<extra></extra>")
            st.plotly_chart(fig_monthly, use_container_width=True)
        except Exception as e:
            st.warning(f"Could not generate Monthly Revenue vs Expenses chart: {e}")

    # 2. Expense Breakdown by Main Category (Treemap)
    with chart_col2:
        try:
            expense_df = filtered_df[filtered_df["main_category"] == "Expenses"].copy()
            if not expense_df.empty:
                expense_df["amount_abs"] = expense_df["amount"].abs()
                # Aggregate by main_category first, then subcategory for treemap path
                expense_summary = expense_df.groupby(["main_category", "subcategory"])["amount_abs"].sum().reset_index()
                
                fig_expense_treemap = px.treemap(expense_summary, path=[px.Constant("Expenses"), "main_category", "subcategory"], values="amount_abs",
                                               title="Expense Breakdown (Main & Subcategories)",
                                               color="main_category", # Color by main category
                                               color_discrete_sequence=px.colors.qualitative.Pastel)
                fig_expense_treemap.update_traces(
                    texttemplate="<b>%{label}</b><br>$%{value:,.2f}<br>%{percentParent:.1%}",
                    hovertemplate="<b>%{label}</b><br>Amount: $%{value:,.2f}<br>Percentage of Parent: %{percentParent:.1%}<extra></extra>"
                )
                st.plotly_chart(fig_expense_treemap, use_container_width=True)
            else:
                st.info("No expense data in the selected period/filters.")
        except Exception as e:
            st.warning(f"Could not generate Expense Breakdown Treemap: {e}")

    # 3. Revenue Breakdown by Subcategory (Pie Chart)
    try:
        revenue_df = filtered_df[filtered_df["main_category"] == "Revenue"].copy()
        if not revenue_df.empty:
            revenue_summary = revenue_df.groupby("subcategory")["amount"].sum().reset_index()
            revenue_summary = revenue_summary[revenue_summary["amount"] > 0] # Ensure positive amounts for pie
            
            if not revenue_summary.empty:
                fig_revenue_pie = px.pie(revenue_summary, values="amount", names="subcategory",
                                       title="Revenue Sources by Subcategory",
                                       hole=0.3)
                fig_revenue_pie.update_traces(
                    texttemplate="%{label}:<br>$%{value:,.2f}<br>(%{percent:.1%})",
                    hovertemplate="<b>%{label}</b><br>Amount: $%{value:,.2f}<br>Percentage: %{percent:.1%}<extra></extra>",
                    textposition="outside"
                )
                st.plotly_chart(fig_revenue_pie, use_container_width=True)
            else:
                st.info("No revenue data in the selected period/filters.")
        else:
            st.info("No revenue data in the selected period/filters.")
    except Exception as e:
        st.warning(f"Could not generate Revenue Breakdown Pie Chart: {e}")

    st.divider()

    # --- Data Table ---
    st.subheader("Filtered Data Table")
    # Select and order columns for display
    display_columns = ["date", "description", "main_category", "subcategory", "amount"]
    # Ensure columns exist before selecting
    display_columns = [col for col in display_columns if col in filtered_df.columns]
    
    # Apply formatting to the amount column for display in the table
    st.dataframe(
        filtered_df[display_columns].sort_values(by="date"), 
        use_container_width=True,
        column_config={
            "amount": st.column_config.NumberColumn(
                "Amount",
                format="$ {:,.2f}" # Apply comma formatting
            ),
            "date": st.column_config.DateColumn(
                "Date",
                format="YYYY-MM-DD"
            )
        }
    )
