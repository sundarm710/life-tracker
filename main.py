import os
from datetime import datetime, timedelta
import csv
import re
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from budget_manager import BudgetManager
import plotly.graph_objects as go

st.set_page_config(layout="wide")

# Load environment variables
load_dotenv()

# Get the path to Obsidian daily notes from environment variable
OBSIDIAN_DAILY_NOTES_PATH = os.getenv('OBSIDIAN_DAILY_NOTES_PATH')

def parse_time_blocks(file_path, file_date):
    with open(file_path, 'r') as file:
        content = file.read()

    time_blocks = re.findall(r'- \[x\] (\d{2}:\d{2}) - (\d{2}:\d{2})(?:[:\s]*)(.+?)(?:\s✅.*)?$', content, re.MULTILINE)
    
    parsed_blocks = []
    for start_time, end_time, activity in time_blocks:
        start_datetime = datetime.combine(file_date, datetime.strptime(start_time, "%H:%M").time())
        end_datetime = datetime.combine(file_date, datetime.strptime(end_time, "%H:%M").time())

        duration = end_datetime - start_datetime
        
        if duration.total_seconds() < 0:
            end_datetime += timedelta(days=1)
            duration = end_datetime - start_datetime

        parsed_blocks.append((start_datetime, end_datetime, duration, activity.strip()))
    
    return parsed_blocks

def process_files(start_date, end_date, base_path):
    current_date = start_date
    results = []

    while current_date <= end_date:
        file_name = current_date.strftime("%Y-%m-%d") + ".md"
        file_path = os.path.join(base_path, file_name)
        
        if os.path.exists(file_path):
            time_blocks = parse_time_blocks(file_path, current_date)
            for start_datetime, end_datetime, duration, activity in time_blocks:
                results.append([
                    start_datetime.strftime("%Y-%m-%d"),
                    start_datetime.strftime("%H:%M"),
                    end_datetime.strftime("%H:%M"),
                    str(duration),
                    activity
                ])
        
        current_date += timedelta(days=1)
    
    return results

def save_to_csv(results, output_file):
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Date', 'Start Time', 'End Time', 'Duration', 'Activity'])
        writer.writerows(results)

def read_csv_file(file_path):
    df = pd.read_csv(file_path)
    df['Date'] = pd.to_datetime(df['Date'])
    df['Start Time'] = pd.to_datetime(df['Start Time'], format='%H:%M').dt.time
    df['End Time'] = pd.to_datetime(df['End Time'], format='%H:%M').dt.time
    df['Day of Week'] = df['Date'].dt.day_name()
    df['Activity Category'] = df.apply(assign_activity, axis=1)
    df['Duration'] = pd.to_timedelta(df['Duration'])
    return df

def time_to_float(t):
    return t.hour + t.minute / 60

def fetch_activities():
    return {
        'Sleep': {'color': 'black', 'keywords': ['Sleep', 'Nap', 'Bed']},
        'Admin': {'color': 'orange', 'keywords': ['Chores', 'Prep', 'Dishes', 'Bath', 'Dinner', 'Lunch', 'Commute', 'Breakfast']},
        'Workout': {'color': 'green', 'keywords': ['Workout', 'Gym']},
        'Work': {'color': 'blue', 'keywords': ['Office', 'Work', 'Grind', 'Push', 'Toplyne']},
        'Projects': {'color': 'purple', 'keywords': ['Project', 'Obsidian']},
        'Chill': {'color': 'red', 'keywords': ['Chill', 'YouTube', 'Movie', 'TV', 'Standup']},
        'Catchup': {'color': 'yellow', 'keywords': ['Catchup']},
        'Chess': {'color': 'pink', 'keywords': ['Chess']},
        'Reading-Writing': {'color': 'purple', 'keywords': ['Read', 'Book', 'Writing', 'Journal', 'Learning']},
        'Meditation': {'color': 'cyan', 'keywords': ['Meditation', 'Mindfulness']},
        'Filler': {'color': 'white', 'keywords': ['']},
    }

def assign_activity(row):
    activities = fetch_activities()
    for activity, details in activities.items():
        if any(keyword.lower() in row['Activity'].lower() for keyword in details['keywords']):
            return activity
    return 'Other'

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
    st.title("Life Tracker Dashboard")

    st.sidebar.header("Data Input")
    start_date = st.sidebar.date_input("Start Date", datetime(2024, 7, 1))
    end_date = st.sidebar.date_input("End Date", datetime(2024, 12, 31))
    
    if st.sidebar.button("Process Data"):
        results = process_files(start_date, end_date, OBSIDIAN_DAILY_NOTES_PATH)
        output_file = "time_blocks.csv"
        save_to_csv(results, output_file)
        st.sidebar.success(f"CSV file '{output_file}' has been created successfully.")

    budget_manager = BudgetManager()

    if os.path.exists("time_blocks.csv"):
        df = read_csv_file("time_blocks.csv")

    # Example: Display active budgets
    active_budgets = budget_manager.get_active_budgets(date=start_date)
    st.write(active_budgets)
    st.subheader("Active Budgets")

    # Example: Calculate and display progress
    if os.path.exists("time_blocks.csv"):
        df = read_csv_file("time_blocks.csv")
        df['Activity Category'] = df.apply(assign_activity, axis=1)
        
        for budget in active_budgets:
            with st.expander(f"{budget['name']}"):
                budget_df = df[(df['Activity Category'] == budget['name']) & (df['Date'] >= budget['start_date']) & (df['Date'] <= budget['end_date'])]

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

    else:
        st.info("No data available. Please process data first.")

        
if __name__ == "__main__":
    main()