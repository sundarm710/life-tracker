import os
from datetime import datetime, timedelta
import csv
import re
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

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

def main():
    st.title("Life Tracker Dashboard")

    st.sidebar.header("Data Input")
    start_date = st.sidebar.date_input("Start Date", datetime(2024, 4, 1))
    end_date = st.sidebar.date_input("End Date", datetime(2024, 12, 31))
    
    if st.sidebar.button("Process Data"):
        results = process_files(start_date, end_date, OBSIDIAN_DAILY_NOTES_PATH)
        output_file = "time_blocks.csv"
        save_to_csv(results, output_file)
        st.sidebar.success(f"CSV file '{output_file}' has been created successfully.")

    st.header("Data Visualization")
    if os.path.exists("time_blocks.csv"):
        df = read_csv_file("time_blocks.csv")
        df['Activity Category'] = df.apply(assign_activity, axis=1)
        
        # Display basic statistics
        st.subheader("Activity Summary")
        activity_summary = df['Activity Category'].value_counts()
        st.bar_chart(activity_summary)

        # Display raw data
        st.subheader("Raw Data")
        st.dataframe(df)
    else:
        st.info("No data available. Please process data first.")

if __name__ == "__main__":
    main()