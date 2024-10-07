import os
from datetime import datetime
import streamlit as st
from utility.time_spent import main as time_dash
from components.budget_manager import BudgetManager
import pandas as pd
import plotly.graph_objects as go
from utility.time_block_parsing import fetch_time_blocks, fetch_activities, assign_activity

def fetch_hover_text(df):
    return [f"Activity: {activity}<br>"
            f"Date: {date.date()}<br>"
            f"Day: {day}<br>"
            f"Time: {start_time} - {end_time}<br>"
            f"Duration: {duration}"
            for activity, day, date, start_time, end_time, duration
            in zip(df['Activity'],
                   df['Day of Week'],
                   df['Date'],
                   df['Start Time'],
                   df['End Time'],
                   df['Duration'])]

def create_time_chart(df, view_type, budget_name):
    """
    Create a stacked bar chart based on the view type.
    
    :param df: DataFrame containing the budget data
    :param view_type: String indicating the type of view ('daily', 'weekly', or 'monthly')
    :param budget_name: Name of the budget for the chart title
    :return: Plotly figure object
    """
    if view_type == 'daily':
        df['DateGroup'] = df['Date'].dt.strftime('%Y-%m-%d')
        x_values = 'DateGroup'
        title = f"Daily Breakdown - {budget_name}"
        xaxis_title = "Date"
    elif view_type == 'weekly':
        df['Week'] = df['Date'].dt.to_period('W').astype(str)
        x_values = 'Week'
        title = f"Weekly Breakdown - {budget_name}"
        xaxis_title = "Week"
    elif view_type == 'monthly':
        df['Month'] = df['Date'].dt.to_period('M').astype(str)
        x_values = 'Month'
        title = f"Monthly Breakdown - {budget_name}"
        xaxis_title = "Month"
    else:
        raise ValueError("Invalid view type. Choose 'daily', 'weekly', or 'monthly'.")

    # Group the data by Date and Assigned Activity
    grouped_df = df.groupby([x_values, 'Date', 'Activity', 'Activity Category', 'Day of Week', 'Start Time', 'End Time'])['Duration'].sum().reset_index()

    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=grouped_df[x_values],
        y=grouped_df['Duration'].dt.total_seconds() / 3600,
        hovertext=fetch_hover_text(grouped_df),
        hoverinfo='text'  # Only display hover text
    ))

    fig.update_layout(
        title=title,
        xaxis_title=xaxis_title,
        yaxis_title="Hours",
        barmode='stack',
    )

    return fig

def main():
    df = fetch_time_blocks()

    df['Activity Category'] = df.apply(assign_activity, axis=1)
    
    budget_manager = BudgetManager()
    active_budgets = budget_manager.get_active_budgets()
    st.subheader("Active Budgets")

    for budget in active_budgets:
        with st.expander(f"{budget['name']}"):
            budget_df = df[(df['Activity Category'] == budget['name'])]
            print("budget_df")
            print(budget_df)
            actual_value = budget_df['Duration'].sum().total_seconds() / 3600  # Convert to hours
            progress = budget_manager.calculate_progress(budget['name'], actual_value)

            if progress:
                st.progress(min(progress['progress_percentage'] / 100, 1.0))
                st.write(f"Progress: {progress['progress_percentage']:.1f}%")

            total_hours = budget_df['Duration'].sum().total_seconds() / 3600
            st.write(f"Target: {budget['target']} {budget['unit']}, Actual: {total_hours:.1f} hours")
            start_date = datetime.strptime(budget['start_date'], "%Y-%m-%d").strftime("%d %b %Y")
            end_date = datetime.strptime(budget['end_date'], "%Y-%m-%d").strftime("%d %b %Y")
            st.write(f"Dates: {start_date} - {end_date}")

            tab1, tab2, tab3 = st.tabs(["Daily View", "Weekly View", "Monthly View"])

            if not budget_df.empty:
                with tab1:
                    fig_daily = create_time_chart(budget_df, 'daily', budget['name'])
                    st.plotly_chart(fig_daily, use_container_width=True)

                with tab2:
                    fig_weekly = create_time_chart(budget_df, 'weekly', budget['name'])
                    st.plotly_chart(fig_weekly, use_container_width=True)

                with tab3:
                    fig_monthly = create_time_chart(budget_df, 'monthly', budget['name'])
                    st.plotly_chart(fig_monthly, use_container_width=True)
            else:
                st.write("No data available for this budget in the selected date range.")

if __name__ == "__main__":
    main()
