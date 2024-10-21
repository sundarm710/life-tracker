"""
This module provides functionality for parsing and processing time blocks from Obsidian daily notes.

The main features of this module include:
1. Parsing time blocks from Markdown files
2. Processing multiple files within a date range
3. Categorizing activities based on predefined keywords
4. Saving parsed data to CSV files
5. Creating a pandas DataFrame with processed time block data

Functions:
- parse_time_blocks(file_path, file_date): Parse time blocks from a single file
- process_files(base_path): Process all files within a specified date range
- fetch_activities(): Return a dictionary of activity categories and their associated keywords
- assign_activity(row): Assign an activity category to a given row of data
- save_to_csv(results, output_file): Save processed results to a CSV file
- fetch_time_blocks(): Main function to process all time blocks and return a DataFrame

Usage:
To use this module, ensure that the OBSIDIAN_DAILY_NOTES_PATH environment variable is set to the
directory containing your Obsidian daily notes. Then, call the fetch_time_blocks() function to
process all time blocks and get a pandas DataFrame with the results.

Dependencies:
- os
- csv
- datetime
- re
- streamlit
- dotenv
- pandas

Environment Variables:
- OBSIDIAN_DAILY_NOTES_PATH: Path to the directory containing Obsidian daily notes

Output Files:
- files/time_blocks.csv: Raw parsed time blocks
- files/time_blocks_parsed.csv: Processed time blocks with additional information

Note: This module uses Streamlit's caching mechanism (@st.cache_data) to improve performance
when fetching time blocks repeatedly.
"""

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
OBSIDIAN_BASE_PATH = os.getenv('OBSIDIAN_BASE_PATH')
OBSIDIAN_DAILY_NOTES_PATH = os.path.join(OBSIDIAN_BASE_PATH, os.getenv('OBSIDIAN_DAILY_NOTES_PATH'))
time_blocks_file = "files/time_blocks.csv"

def parse_time_blocks(file_path, file_date):
    """
    Parse time blocks from a single file.

    Args:
    file_path (str): Path to the Markdown file
    file_date (datetime.date): Date of the file

    Returns:
    list: List of tuples containing (start_datetime, end_datetime, duration, activity)
    """
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
    """
    Process all files within a specified date range.

    Args:
    base_path (str): Path to the directory containing daily note files

    Returns:
    list: List of lists containing [date, start_time, end_time, duration, activity]
    """
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
        print(current_date)
    
    return results

def fetch_activities():
    """
    Return a dictionary of activity categories and their associated keywords.

    Returns:
    dict: Dictionary of activity categories with their colors and keywords
    """
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
    """
    Assign an activity category to a given row of data.

    Args:
    row (pandas.Series): A row from the DataFrame containing an 'Activity' column

    Returns:
    str: The assigned activity category
    """
    activities = fetch_activities()

    for activity, details in activities.items():
        if any(keyword.lower() in row['Activity'].lower() for keyword in details['keywords']):
            return activity
    return 'Other'  # Fallback if no match is found

def save_to_csv(results, output_file):
    """
    Save processed results to a CSV file.

    Args:
    results (list): List of lists containing time block data
    output_file (str): Path to the output CSV file
    """
    with open(output_file, 'w', newline='') as csvfile:
        print ("Writing File")
        writer = csv.writer(csvfile)
        writer.writerow(['Date', 'Start Time', 'End Time', 'Duration', 'Activity'])
        writer.writerows(results)

def fetch_time_blocks():
    """
    Main function to process all time blocks and return a DataFrame.

    This function is cached using Streamlit's caching mechanism to improve performance.

    Returns:
    pandas.DataFrame: DataFrame containing processed time block data
    """
    print ("Processing Files")
    results = process_files(OBSIDIAN_DAILY_NOTES_PATH)
    save_to_csv(results, time_blocks_file)

    df = pd.read_csv(time_blocks_file)
    print (df.head())
    df['Date'] = pd.to_datetime(df['Date'])
    df['Start Time'] = pd.to_datetime(df['Start Time'], format='%H:%M').dt.time
    df['End Time'] = pd.to_datetime(df['End Time'], format='%H:%M').dt.time
    df['Day of Week'] = df['Date'].dt.day_name()  # Add day of the week
    df['Duration'] = pd.to_timedelta(df['Duration'])
    df['Duration_Hours'] = df['Duration'].dt.total_seconds() / 3600
    df['Activity Category'] = df.apply(assign_activity, axis=1)
    df.to_csv('files/time_blocks_parsed.csv', index=False)
    return df

def main():
    """
    Main function to execute the time block fetching process.
    """
    fetch_time_blocks()

if __name__ == "__main__":
    main()
