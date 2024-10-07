import os
import csv
from datetime import datetime, timedelta
import re
import streamlit as st
from dotenv import load_dotenv
import pandas as pd
# Load environment variables
load_dotenv()
# Get the path to Obsidian daily notes from environment variable
OBSIDIAN_DAILY_NOTES_PATH = os.getenv('OBSIDIAN_DAILY_NOTES_PATH')
time_blocks_file = "files/time_blocks.csv"

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

    
def process_files(base_path):
    start_date = datetime(2024, 7, 1).date()
    current_date = datetime.now().date()
    results = []

    while current_date >= start_date:
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
        
        current_date -= timedelta(days=1)
    
    return results

def fetch_activities():
    return{
            'Sleep': {'color': 'black', 'keywords': ['Sleep', 'Nap', 'Bed', 'Wind Down']},
            'Admin': {'color': 'orange', 'keywords': ['Chores', 'Prep', 'Dishes', 'Bath', 'Breakfast', 'Dinner', 'Lunch', 'Commute', 'Travel', 'Bus']},
            'Workout': {'color': 'green', 'keywords': ['Workout', 'Gym', 'Stretch']},
            'Work': {'color': 'blue', 'keywords': ['Office', 'Work', 'Toplyne']},
            'Projects': {'color': 'purple', 'keywords': ['Project', 'Obsidian', 'Budgeting and Expense', 'Ledger', 'Life Admin', 'Maintenance', 'Push', 'Grind' ]},
            'Learning': {'color': 'purple', 'keywords': ['Learning', 'Learn', 'Brilliant.org']},
            'Reflection': {'color': 'purple', 'keywords': ['Journal', 'Review', 'Plan']},
            'Chill': {'color': 'red', 'keywords': ['Chill', 'YouTube', 'Movie', 'TV', 'Standup', 'Trip']},
            'Social': {'color': 'yellow', 'keywords': ['Catchup', 'Social']},
            'Chess': {'color': 'pink', 'keywords': ['Chess']},
            'Reading-Writing': {'color': 'purple', 'keywords': ['Read', 'Book', 'Writing']},
            'Meditation': {'color': 'cyan', 'keywords': ['Meditation', 'Mindfulness']},
            'Filler': {'color': 'white', 'keywords': ['']},
        }

def assign_activity(row):
     # Define activities and their colors
    activities = fetch_activities()

    # Check the activity in the priority order defined in the activities dictionary
    for activity, details in activities.items():
        if any(keyword.lower() in row['Activity'].lower() for keyword in details['keywords']):
            return activity
    return 'Other'  # Fallback if no match is found

def save_to_csv(results, output_file):
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Date', 'Start Time', 'End Time', 'Duration', 'Activity'])
        writer.writerows(results)

def fetch_time_blocks():
    results = process_files(OBSIDIAN_DAILY_NOTES_PATH)
    save_to_csv(results, time_blocks_file)

    df = pd.read_csv(time_blocks_file)
    df['Date'] = pd.to_datetime(df['Date'])
    df['Start Time'] = pd.to_datetime(df['Start Time'], format='%H:%M').dt.time
    df['End Time'] = pd.to_datetime(df['End Time'], format='%H:%M').dt.time
    df['Day of Week'] = df['Date'].dt.day_name()  # Add day of the week
    df['Duration'] = pd.to_timedelta(df['Duration'])
    df['Duration_Hours'] = df['Duration'].dt.total_seconds() / 3600
    df['Activity Category'] = df.apply(assign_activity, axis=1)
    return df

def main():
    fetch_time_blocks()
if __name__ == "__main__":
    main()
