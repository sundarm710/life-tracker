"""
Expense Dashboard

This module provides a Streamlit-based dashboard for visualizing expense data.

Key Features:
1. Data loading and preprocessing
2. Expense filtering options
3. Interactive charts for daily, weekly, and monthly views
4. Detailed breakdown of expenses by category
5. Runway calculation based on current net worth and average monthly burn rate

Functions:
- load_data(): Load and preprocess expense data
- fetch_only_expenses(): Filter for expense transactions
- fetch_only_expenses_excluding_home_loan(): Filter expenses excluding home loans
- fetch_food_expenses(): Filter for food-related expenses
- fetch_default_expenses(): Filter for predefined default expense categories
- fetch_hover_text(): Generate hover text for chart tooltips
- create_time_chart(): Create stacked bar charts for expense visualization
- format_in_indian_system(): Format numbers in the Indian numbering system

UI Components:
- Expense type selection (All vs Default Expenses)
- Home loan inclusion option
- Grouping option (Expense_1, Expense_2, Expense_3)
- Tabs for different time views (Daily, Weekly, Monthly)
- Filtered view by specific Expense_2 category
- Runway calculation based on current net worth and average monthly burn rate

Dependencies:
- streamlit
- pandas
- plotly

Usage:
Run this script with Streamlit to launch the interactive dashboard.
"""

import os
import sys
# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)
import streamlit as st
from utility.expenses_base import fetch_only_expenses, fetch_default_expenses, format_in_indian_system

# Streamlit UI
st.title("Expense Dashboard")

with st.form("Expense Type"):
    expense_type = st.radio("Select Expense Type", ["All", "Default Expenses"])
    home_loan_option = st.checkbox("Include Home Loan", value=True)
    submit_button = st.form_submit_button("Submit")

df = fetch_only_expenses()

if submit_button:
    if expense_type == "All":
        df = fetch_only_expenses()
    elif expense_type == "Default Expenses":
        df = fetch_default_expenses()

    if not home_loan_option:
        df = df[df['Expense_3'] != 'Loan']

# Runway Calculation Section
st.header("Runway Calculation")

# Calculate month-on-month expenses using a weighted moving average
df['Month'] = df['Date'].dt.to_period('M')
monthly_expenses = df.groupby('Month')['Amount'].sum().reset_index()
monthly_expenses['Weighted_Moving_Avg'] = monthly_expenses['Amount'].rolling(window=3, min_periods=1).apply(
    lambda x: (x * [0.1, 0.3, 0.6][-len(x):]).sum(), raw=True
)
st.dataframe(monthly_expenses)

# Calculate average burn per month
average_burn = monthly_expenses['Weighted_Moving_Avg'].mean()
st.metric(label="Average Burn (₹)", value=format_in_indian_system(average_burn))

# Input slider for current net worth
net_worth = st.slider("Enter your current net worth (₹)", min_value=0, max_value=10000000, value=3500000, step=10000)
formatted_net_worth = format_in_indian_system(net_worth)
st.metric(label="Net Worth (₹)", value=formatted_net_worth)

# Calculate runway
runway_months = net_worth / average_burn
# Calculate runway for different liquidation percentages
liquidation_percentages = [1, 0.5, 0.25, 0.1]
runway_metrics = {}

for percentage in liquidation_percentages:
    liquidated_amount = net_worth * percentage
    runway_metrics[percentage] = liquidated_amount / average_burn
import streamlit.components.v1 as components

# Display the runway metrics for different liquidation percentages
st.subheader("Runway Metrics for Different Liquidation Percentages")

# Create a table to display the runway metrics
runway_table = """
<table style="width:100%; border-collapse: collapse;">
    <thead>
        <tr style="background-color: #f2f2f2;">
            <th style="padding: 8px; text-align: left; border-bottom: 1px solid #ddd;">Liquidation Percentage</th>
            <th style="padding: 8px; text-align: left; border-bottom: 1px solid #ddd;">Runway (months)</th>
            <th style="padding: 8px; text-align: left; border-bottom: 1px solid #ddd;">Runway (years)</th>
        </tr>
    </thead>
    <tbody>
"""
for percentage, runway in runway_metrics.items():
    runway_table += f"""
        <tr>
            <td style="padding: 8px; text-align: left; border-bottom: 1px solid #ddd; color: #ff5733;">{int(percentage * 100)}%</td>
            <td style="padding: 8px; text-align: left; border-bottom: 1px solid #ddd; color: #ff5733;">{runway:.2f}</td>
            <td style="padding: 8px; text-align: left; border-bottom: 1px solid #ddd; color: #ff5733;">{runway / 12:.2f}</td>
        </tr>
    """

runway_table += """
    </tbody>
</table>
"""

# Render the table using Streamlit's HTML component
components.html(runway_table, height=300, scrolling=True)
