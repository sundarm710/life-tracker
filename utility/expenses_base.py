"""
Expense Dashboard

This module provides a Streamlit-based dashboard for visualizing expense data.

Key Features:
1. Data loading and preprocessing
2. Expense filtering options
3. Interactive charts for daily, weekly, and monthly views
4. Detailed breakdown of expenses by category

Functions:
- load_data(): Load and preprocess expense data
- fetch_only_expenses(): Filter for expense transactions
- fetch_only_expenses_excluding_home_loan(): Filter expenses excluding home loans
- fetch_food_expenses(): Filter for food-related expenses
- fetch_default_expenses(): Filter for predefined default expense categories
- fetch_hover_text(): Generate hover text for chart tooltips
- create_time_chart(): Create stacked bar charts for expense visualization

UI Components:
- Expense type selection (All vs Default Expenses)
- Home loan inclusion option
- Grouping option (Expense_1, Expense_2, Expense_3)
- Tabs for different time views (Daily, Weekly, Monthly)
- Filtered view by specific Expense_2 category

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
import pandas as pd
import plotly.graph_objs as go
from utility.expense_parsing import create_expense_csv

st.set_page_config(layout="wide")

# Load data
@st.cache_data
def load_data():
    create_expense_csv()
    # Load the CSV into a DataFrame
    df = pd.read_csv("files/ledger_output.csv", parse_dates=["Date"])
    df['Date'] = pd.to_datetime(df['Date'])
    df['Day of Week'] = df['Date'].dt.day_name()  # Add day of the week
    df['Amount'] = pd.to_numeric(df['Amount'].replace('₹', '', regex=True).replace(',', '', regex=True), errors='coerce')
    df['DateGroup'] = df['Date'].dt.strftime('%Y-%m-%d')
    df['Week'] = df['Date'].dt.to_period('W').astype(str)
    df['Month'] = df['Date'].dt.to_period('M').astype(str)

    # Check for 'Expense_2' and 'Expense_3' conditions and adjust 'Amount'
    df.loc[(df['Expense_2'] == 'Home') & (df['Expense_3'] == 'Loan'), 'Amount'] /= 2
    return df


def fetch_only_expenses():
    df = load_data()
    df = df[(df['Expense_1'] == 'Expenses') | (df['Expense_1'] == 'Assets')]
    df = df[df['Expense_2'] != 'Banking']
    return df

def fetch_only_expenses_excluding_home_loan():
    df = fetch_only_expenses()
    df = df[(df['Expense_3'] != 'Loan') & (df['Expense_2'] != 'Home')]
    return df

def fetch_food_expenses():
    df = fetch_only_expenses()
    df = df[df['Expense_2'] == 'Food']
    return df

def fetch_default_expenses():
    df = fetch_only_expenses()
    df = df[df['Expense_2'].isin(['Bike', 'Entertainment', 'Food', 'Vice', 'Subscriptions', 'Home', 'SelfCare'])]
    # Define a list of exclusions for combinations of 'Expense_2' and 'Expense_3'
    exclusions = [
        ('Home', 'Furniture'),
        ('Tax', 'IncomeTax'),
        ('SelfCare', 'Gym'),
        ('Entertainment', 'DelhiSpa'),
        ('Vice', 'Stuff')
    ]

    # Apply the exclusions to the DataFrame
    for expense_2, expense_3 in exclusions:
        df = df[~((df['Expense_2'] == expense_2) & (df['Expense_3'] == expense_3))]
    return df

def format_hover_text(expense_1, expense_2, expense_3, description, amount, date):
    """
    Format the hover text for a single row of data.

    :param expense_1: Primary expense category
    :param expense_2: Secondary expense category
    :param expense_3: Tertiary expense category
    :param description: Description of the expense
    :param amount: Amount of the expense
    :param date: Date of the expense
    :return: Formatted hover text string
    """
    return f"{expense_1} ({expense_2}, {expense_3})<br>{description}<br>{date.strftime('%Y-%m-%d')}, {amount:.2f} ₹"

def fetch_hover_text(df):
    """
    Generate hover text for each row in the DataFrame.

    :param df: DataFrame containing the expense data
    :return: List of formatted hover text strings
    """
    return [
        format_hover_text(expense_1, expense_2, expense_3, description, amount, date)
        for expense_1, expense_2, expense_3, description, amount, date in zip(
            df['Expense_1'], df['Expense_2'], df['Expense_3'], df['Description'], df['Amount'], df['Date']
        )
    ]

def format_in_indian_system(number):
    if number >= 1e7:
        return f"{number / 1e7:.2f} Cr"
    elif number >= 1e5:
        return f"{number / 1e5:.2f} L"
    else:
        return f"{number / 1e3:.2f} K"