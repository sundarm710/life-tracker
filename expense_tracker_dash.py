import streamlit as st
import pandas as pd
import plotly.graph_objs as go

st.set_page_config(layout="wide")

# Load data
@st.cache
def load_data():
    # Load the CSV into a DataFrame
    df = pd.read_csv("ledger_output.csv", parse_dates=["Date"])
    return df

df = load_data()

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
        df['DateGroup'] = df['Date'].dt.strftime('%Y-%m-%d')
        x_values = 'DateGroup'
        title = f"Daily Expense Breakdown"
        xaxis_title = "Date"
    elif view_type == 'weekly':
        df['Week'] = df['Date'].dt.to_period('W').astype(str)
        x_values = 'Week'
        title = f"Weekly Expense Breakdown"
        xaxis_title = "Week"
    elif view_type == 'monthly':
        df['Month'] = df['Date'].dt.to_period('M').astype(str)
        x_values = 'Month'
        title = f"Monthly Expense Breakdown"
        xaxis_title = "Month"
    else:
        raise ValueError("Invalid view type. Choose 'daily', 'weekly', or 'monthly'.")

    # Group the data by the chosen expense level and date grouping
    grouped_df = df.groupby([x_values, group_by])['Amount'].sum().reset_index()

    # Create the figure and add traces
    fig = go.Figure()

    for expense in grouped_df[group_by].unique():
        expense_data = grouped_df[grouped_df[group_by] == expense]
        fig.add_trace(go.Bar(
            x=expense_data[x_values],
            y=expense_data['Amount'],
            name=expense
        ))

    fig.update_layout(
        title=title,
        xaxis_title=xaxis_title,
        yaxis_title="Amount (₹)",
        barmode='stack',
        showlegend=True
    )

    return fig

# Streamlit UI
st.title("Expense Dashboard")

# Group by options (Expense_1, Expense_2, Expense_3)
group_by_option = st.selectbox("Group by", ["Expense_1", "Expense_2", "Expense_3"])

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
