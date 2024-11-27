import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utility.expenses_base import fetch_only_expenses, fetch_default_expenses, fetch_hover_text


# Function to create time charts (daily, weekly, or monthly)
def create_time_chart(df, view_type, group_by):
    """
    Create a stacked bar chart based on the view type.

    :param df: DataFrame containing the expense data
    :param view_type: 'daily', 'weekly', or 'monthly'
    :param group_by: The level of grouping ('Expense_1', 'Expense_2', 'Expense_3')
    :return: Plotly figure object
    """
    view_type_mapping = {
        'daily': ('DateGroup', 'Daily Expense Breakdown', 'Date'),
        'weekly': ('Week', 'Weekly Expense Breakdown', 'Week'),
        'monthly': ('Month', 'Monthly Expense Breakdown', 'Month')
    }

    if view_type not in view_type_mapping:
        raise ValueError("Invalid view type. Choose 'daily', 'weekly', or 'monthly'.")

    x_values, title, xaxis_title = view_type_mapping[view_type]

    # Group the data by the chosen expense level and date grouping
    grouped_df = df.groupby([x_values, 'Expense_1', 'Expense_2', 'Expense_3', 'Description', 'Date'])['Amount'].sum().reset_index()
    grouped_df = grouped_df.sort_values(x_values)

    # Create the figure and add traces
    fig = go.Figure()

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
            customdata=category_df[['Expense_1', 'Expense_2', 'Expense_3', 'Description', 'Date']],
            hovertemplate=fetch_hover_text(category_df), 
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
tab3, tab1, tab2 = st.tabs(["Monthly View", "Daily View", "Weekly View"])

# Create charts for each tab
with tab3:
    fig_monthly = create_time_chart(df, 'monthly', group_by_option)
    st.plotly_chart(fig_monthly, use_container_width=True)
with tab2:
    fig_weekly = create_time_chart(df, 'weekly', group_by_option)
    st.plotly_chart(fig_weekly, use_container_width=True)
with tab1:
    fig_daily = create_time_chart(df, 'daily', group_by_option)
    st.plotly_chart(fig_daily, use_container_width=True)

# Filter by Expense_2 and display a breakdown by Expense_3
expense_2_filter = st.selectbox("Filter by Expense_2", df["Expense_2"].dropna().unique())

# Filter data based on the selected Expense_2
filtered_df = df[(df['Expense_2'] == expense_2_filter) & (df['Expense_1'] == 'Expenses')]

# Tabs for daily, weekly, and monthly views of filtered data by Expense_3
tab4, tab5, tab6 = st.tabs([f"Monthly - {expense_2_filter}", f"Daily - {expense_2_filter}", f"Weekly - {expense_2_filter}"])

with tab6:
    fig_daily_filtered = create_time_chart(filtered_df, 'daily', 'Expense_3')
    st.plotly_chart(fig_daily_filtered, use_container_width=True)

with tab5:
    fig_weekly_filtered = create_time_chart(filtered_df, 'weekly', 'Expense_3')
    st.plotly_chart(fig_weekly_filtered, use_container_width=True)

with tab4:
    fig_monthly_filtered = create_time_chart(filtered_df, 'monthly', 'Expense_3')
    st.plotly_chart(fig_monthly_filtered, use_container_width=True)
