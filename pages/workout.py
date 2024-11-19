import streamlit as st
st.set_page_config(layout="wide")

st.title("WIP")
"""
import psutil
import platform
from datetime import datetime
import logging
import threading
import pandas as pd
import re
import plotly.graph_objects as go
from components.workout_log_parser import WorkoutLogParser
from components.workout_database_manager import WorkoutDatabaseManager
from components.workout_data_processor import WorkoutDataProcessor


st.session_state['debug'] = False

# Initialize the database manager and data processor
db_manager = WorkoutDatabaseManager()
data_processor = WorkoutDataProcessor(db_manager)

def generate_workout_data(parsed_df, date):
    
    Generate workout data with sets grouped by exercise.
    
    Args:
        parsed_df (pd.DataFrame): DataFrame containing parsed workout data
        date (datetime.date): Workout date
    
    Returns:
        dict: Workout data with exercises and their sets grouped together

    # Create final workout data structure
    workout_data = {
        'date': date,
        'muscle_group': parsed_df['muscle_group'].iloc[0],
        'exercises': parsed_df.to_dict(orient='records')
    }
    
    return workout_data

if 'submit_success' not in st.session_state:
    st.session_state['submit_success'] = False

if st.session_state['submit_success']:
    st.success("Workout added successfully!")

log = st.text_area("Enter your workout log here:", placeholder="Pull 1\nBarbell bench press - 20, 25, 45, 10 - 15, 12, 10, 9\nShoulder press - 20, 15, 8, 10 - 15, 12, 10, 10 (push next)")
date = st.date_input("Enter the date of the workout:") 

df = None

if st.button("Parse"): 
    parser = WorkoutLogParser()
    try:
        st.write("Parsing workout log...")
        df = parser.parse_workout_text(log, debug=True)
        df['date'] = date  # Add the date to the dataframe
        st.session_state['parsed_df'] = df
        
        st.write("\nExercise Summary:")
        st.write(parser.get_exercise_summary())
    except ValueError as e:
        st.write(f"Error parsing workout log: {str(e)}")
    
    st.write("Parsed DataFrame from session state:")
    st.write(st.session_state['parsed_df'])

if st.button("Submit"):
    db_manager.setup_tables()

    parsed_df = st.session_state['parsed_df']

    if parsed_df is None:
        st.error("No data to submit. Please parse the log first.")
    else:
        st.write(parsed_df)
        st.write("Submitting data to the database...")
        try:
            user_id = 1  # Replace with actual user_id logic
            workout_data = generate_workout_data(parsed_df, date)
            st.write(workout_data)
            workout_id = db_manager.add_workout(workout_data)
            st.success(f"Data submitted successfully! Workout ID: {workout_id}")

            # Clean and process the submitted data
            cleaned_df = data_processor.clean_exercise_names(parsed_df)
            st.write("Cleaned and standardized exercise names:")
            st.write(cleaned_df)

        except Exception as e:
            st.error(f"Error submitting data: {str(e)}")

# Add a new section for data visualization
st.header("Workout Analysis")

# Date range selection for analysis
start_date = st.date_input("Start Date")
end_date = st.date_input("End Date")

if st.button("Generate Analysis"):
    user_id = 1  # Replace with actual user_id logic

    # Volume progression for a specific exercise
    data_processor.prepare_volume_progression_data(start_date, end_date)

    # Exercise frequency
    data_processor.prepare_exercise_frequency_data(start_date, end_date)
    
# Close the database manager when the app is stopped
def on_app_close():
    db_manager.close()
"""