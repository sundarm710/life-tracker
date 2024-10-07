import os
import sys
# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)
import streamlit as st
import pandas as pd
import plotly.graph_objs as go

from utility.expense_parsing import parse_main

st.set_page_config(layout="wide")

# Load data
@st.cache_data
def load_data():
    parse_main()
    # Load the CSV into a DataFrame
    df = pd.read_csv("files/ledger_output.csv", parse_dates=["Date"])
    df['Date'] = pd.to_datetime(df['Date'])
    df['Day of Week'] = df['Date'].dt.day_name()  # Add day of the week
    df['Amount'] = pd.to_numeric(df['Amount'].replace('₹', '', regex=True).replace(',', '', regex=True), errors='coerce')
    df['DateGroup'] = df['Date'].dt.strftime('%Y-%m-%d')
    df['Week'] = df['Date'].dt.to_period('W').astype(str)
    df['Month'] = df['Date'].dt.to_period('M').astype(str)
    return df

def fetch_only_expenses():
    df = load_data()
    df = df[df['Expense_1'] == 'Expenses']
    return df

def fetch_only_expenses_excluding_home_loan():
    df = fetch_only_expenses()
    df = df[(df['Expense_3'] != 'Loan') & (df['Expense_2'] != 'Home')]
    return df

def fetch_default_expenses():
    df = fetch_only_expenses()
    df = df[df['Expense_2'].isin(['Bike', 'Entertainment', 'Food', 'Vice', 'Subscriptions', 'Home', 'SelfCare'])]
    return df

def fetch_hover_text(df):
    # Ensure columns exist in DataFrame
    return [f"{expense_1} ({expense_2}, {expense_3})<br>{description}<br>{date.strftime('%Y-%m-%d')}, {amount:.2f} ₹" 
            for expense_1, expense_2, expense_3, description, amount, date  
                in zip(df['Expense_1'], 
                       df['Expense_2'], 
                       df['Expense_3'], 
                       df['Description'],
                       df['Amount'], 
                       df['Date'])]



# Function to create time charts (daily, weekly, or monthly)
def create_time_chart(df, view_type, group_by):
    """
    Create a stacked bar chart based on the view type.

    :param df: DataFrame containing the expense data
    :param view_type: 'daily', 'weekly', or 'monthly'
    :param group_by: The level of grouping ('Expense_1', 'Expense_2', 'Expense_3')
    :return: Plotly figure object
    """
    if view_type == 'daily':
        
        x_values = 'DateGroup'
        title = f"Daily Expense Breakdown"
        xaxis_title = "Date"
    elif view_type == 'weekly':
        
        x_values = 'Week'
        title = f"Weekly Expense Breakdown"
        xaxis_title = "Week"
    elif view_type == 'monthly':

        x_values = 'Month'
        title = f"Monthly Expense Breakdown"
        xaxis_title = "Month"
    else:
        raise ValueError("Invalid view type. Choose 'daily', 'weekly', or 'monthly'.")

    # # Group the data by the chosen expense level and date grouping
    # grouped_df = df.groupby([x_values, group_by])['Amount'].sum().reset_index()
    # # Sort the grouped data by the date column
    # grouped_df = grouped_df.sort_values(x_values)


    # grouped_df = df.groupby([col for col in df.columns if col != 'Amount'])['Amount'].sum().reset_index()

    # # Sort the grouped data by the date column
    # grouped_df = grouped_df.sort_values('Date')

    # st.dataframe(df)
    # Create the figure and add traces
    fig = go.Figure()

    # Group the data by the chosen expense level and date grouping
    grouped_df = df.groupby([x_values, group_by])['Amount'].sum().reset_index()
    
    # Sort the grouped data by the date column
    grouped_df = grouped_df.sort_values(x_values)

    # Get unique categories
    categories = grouped_df[group_by].unique()

    # Create a stacked bar chart
    for category in categories:
        category_df = grouped_df[grouped_df[group_by] == category]
        fig.add_trace(go.Bar(
            x=category_df[x_values],
            y=category_df['Amount'],
            name=category,
            hoverinfo='text',
            hovertext=[f"{category}<br>{x_val}<br>Amount: ₹{amount:.2f}" 
                       for x_val, amount in zip(category_df[x_values], category_df['Amount'])]
        ))

    fig.update_layout(
        title=title,
        xaxis_title=xaxis_title,
        yaxis_title="Amount (₹)",
        barmode='stack',
        showlegend=True,
    )

    return fig

# Streamlit UI
st.title("Expense Dashboard")

with st.form("Expense Type"):
    expense_type = st.radio("Select Expense Type", ["All", "Default Expenses"])
    home_loan_option = st.checkbox("Include Home Loan", value=True)
    submit_button = st.form_submit_button("Submit")

df = fetch_only_expenses()
# st.dataframe(df)

if submit_button:

    if expense_type == "All":
        df = fetch_only_expenses()
    elif expense_type == "Default Expenses":
        df = fetch_default_expenses()

    if not home_loan_option:
        df = df[df['Expense_3'] != 'Loan']

# Group by options (Expense_1, Expense_2, Expense_3)
group_by_option = st.selectbox("Group by", ["Expense_2", "Expense_1", "Expense_3"])

# Tabs for daily, weekly, and monthly views
tab1, tab2, tab3 = st.tabs(["Daily View", "Weekly View", "Monthly View"])

# Create charts for each tab
with tab1:
    fig_daily = create_time_chart(df, 'daily', group_by_option)
    st.plotly_chart(fig_daily, use_container_width=True)

with tab2:
    fig_weekly = create_time_chart(df, 'weekly', group_by_option)
    st.plotly_chart(fig_weekly, use_container_width=True)

with tab3:
    fig_monthly = create_time_chart(df, 'monthly', group_by_option)
    st.plotly_chart(fig_monthly, use_container_width=True)

# Filter by Expense_2 and display a breakdown by Expense_3
expense_2_filter = st.selectbox("Filter by Expense_2", df["Expense_2"].dropna().unique())

# Filter data based on the selected Expense_2
filtered_df = df[(df['Expense_2'] == expense_2_filter) & (df['Expense_1'] == 'Expenses')]

# Tabs for daily, weekly, and monthly views of filtered data by Expense_3
tab4, tab5, tab6 = st.tabs([f"Daily - {expense_2_filter}", f"Weekly - {expense_2_filter}", f"Monthly - {expense_2_filter}"])

with tab4:
    fig_daily_filtered = create_time_chart(filtered_df, 'daily', 'Expense_3')
    st.plotly_chart(fig_daily_filtered, use_container_width=True)

with tab5:
    fig_weekly_filtered = create_time_chart(filtered_df, 'weekly', 'Expense_3')
    st.plotly_chart(fig_weekly_filtered, use_container_width=True)

with tab6:
    fig_monthly_filtered = create_time_chart(filtered_df, 'monthly', 'Expense_3')
    st.plotly_chart(fig_monthly_filtered, use_container_width=True)
