import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, time
from utility.time_block_parsing import fetch_time_blocks, fetch_activities, assign_activity
import streamlit as st

def time_to_float(t):
    return t.hour + t.minute / 60


def fetch_hover_text(df):
    # Ensure columns exist in DataFrame
    if all(col in df.columns for col in ['Activity', 'Day of Week', 'Date', 'Start Time', 'End Time', 'Duration_Hours']):
        return [f"{activity} ({day}, {date.date()}, {start_time} - {end_time}, {duration:.2f} hrs)" 
                for activity, day, date, start_time, end_time, duration  
                in zip(df['Activity'], 
                       df['Day of Week'], 
                       df['Date'], 
                       df['Start Time'], 
                       df['End Time'],
                       df['Duration_Hours'])]
    else:
        return [''] * len(df)  # Return empty strings if columns are missing

def generate_time_blocks_chart(df):
    fig = go.Figure()

    # Assign a single activity to each row based on priority order
    df['Assigned Activity'] = df.apply(assign_activity, axis=1)

    # Add traces for each activity
    for activity, details in fetch_activities().items():
        activity_df = df[df['Assigned Activity'] == activity]

        fig.add_trace(go.Bar(
            x=activity_df['Date'],
            y=[time_to_float(end) - time_to_float(start) for start, end in zip(activity_df['Start Time'], activity_df['End Time'])],
            base=[time_to_float(start) for start in activity_df['Start Time']],
            name=activity,
            marker_color=details['color'],
            hovertext=fetch_hover_text(activity_df),
            hoverinfo='text'  # Only display hover text
        ))

    # Customize the layout
    fig.update_layout(
        title='Time Blocks',
        xaxis_title='Date',
        yaxis_title='Time of Day',
        barmode='stack',
        yaxis=dict(
            tickmode='array',
            tickvals=[0, 6, 12, 18, 24],
            ticktext=['12 AM', '6 AM', '12 PM', '6 PM', '12 AM'],
            range=[24, 0],  # Invert the y-axis
            autorange='reversed'  # Ensure the axis is reversed
        )
    )

    return fig


def aggregate_weekly_data(df, duration_col):
    """
    Aggregates data by week and calculates the average duration per day.

    Args:
    df (pd.DataFrame): DataFrame containing activity data.
    duration_col (str): Column name for duration.

    Returns:
    pd.DataFrame: DataFrame with weekly aggregated data.
    """
    # Ensure 'Date' column is datetime
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Set the index to 'Date' for resampling
    df.set_index('Date', inplace=True)

    # Aggregate total duration per week
    weekly_data = df.resample('W-MON').agg({duration_col: 'sum'}).reset_index()
    
    # Count distinct days per week
    daily_count = df.resample('W-MON').apply(lambda x: x.index.normalize().nunique()).reset_index()
    # daily_count.columns = ['Date', 'Day Count']  # Rename columns
    
    # Merge total duration and day count
    weekly_data = weekly_data.merge(daily_count, on='Date')
    
    # Calculate average duration per day
    weekly_data['Average Duration'] = weekly_data[duration_col] / weekly_data['Day Count']
    
    return weekly_data


def create_line_chart(df):
    fig = go.Figure()
    
    activities = fetch_activities()

    # Assign activity types
    df['Assigned Activity'] = df.apply(assign_activity, axis=1)
    df['Duration'] = df.apply(lambda row: time_to_float(row['End Time']) - time_to_float(row['Start Time']), axis=1)
    
    for activity, details in activities.items():
        # Filter data for the activity
        activity_df = df[df['Assigned Activity'] == activity]
        
        # Aggregate and calculate average duration per day
        weekly_data = aggregate_weekly_data(activity_df, 'Duration')
        
        fig.add_trace(go.Scatter(
            x=weekly_data['Date'],
            y=weekly_data['Average Duration'],
            mode='lines+markers',
            name=activity,
            line=dict(color=details['color'], shape='spline'),  # Smooth line
            hovertext=[f"{activity} (Week of {date.date()}, Avg. Duration: {avg_duration:.2f} hrs/day)" 
                       for date, avg_duration 
                       in zip(weekly_data['Date'], 
                              weekly_data['Average Duration'])],
            hoverinfo='text'
        ))

    fig.update_layout(
        title='Average Duration Spent on Activities per Day per Week',
        xaxis_title='Week',
        yaxis_title='Average Duration (Hours per Day)',
        xaxis=dict(
            tickformat='%d %b\n%Y',
            tickmode='auto',
            nticks=12
        ),
        yaxis=dict(range=[0, weekly_data['Average Duration'].max() + 1])
    )

    return fig


def create_stacked_duration_chart(df):
    fig = go.Figure()

    # Assign a single activity to each row based on priority order
    df['Assigned Activity'] = df.apply(assign_activity, axis=1)

    # Calculate total duration for each activity per day
    df['Duration'] = df.apply(lambda row: time_to_float(row['End Time']) - time_to_float(row['Start Time']), axis=1)

    # Add Day of Week column for hovertext
    df['Day of Week'] = df['Date'].dt.day_name()

    # Group the data by Date and Assigned Activity
    grouped_df = df.groupby(['Date', 'Activity', 'Assigned Activity', 'Day of Week', 'Start Time', 'End Time'])['Duration'].sum().reset_index()

    # Add traces for each activity
    for activity, details in fetch_activities().items():
        activity_df = grouped_df[grouped_df['Assigned Activity'] == activity]

        fig.add_trace(go.Bar(
            x=activity_df['Date'],
            y=activity_df['Duration'],
            name=activity,
            marker_color=details['color'],
            
            hovertext=fetch_hover_text(activity_df),
            hoverinfo='text',  # Only display hover text
            hoverlabel=dict(namelength=-1),  # Show full activity name in hover label
            customdata=activity_df[['Activity', 'Day of Week', 'Start Time', 'End Time']],
            hovertemplate="<b>%{customdata[0]}</b><br>" +
                          "Date: %{x|%Y-%m-%d}<br>" +
                          "Day: %{customdata[1]}<br>" +
                          "Time: %{customdata[2]} - %{customdata[3]}<br>" +
                          "Duration: %{y:.2f} hours<extra></extra>"
        ))

    # Customize the layout
    fig.update_layout(
        title='Total Duration Spent on Activities per Day',
        xaxis_title='Date',
        yaxis_title='Total Duration (Hours)',
        barmode='stack',  # Stack the bars
        yaxis=dict(range=[0, 24])  # Total hours in a day
    )

    return fig

def main():
    df = fetch_time_blocks()

    # Plot the time blocks as a stacked bar chart
    fig1 = generate_time_blocks_chart(df)
    st.plotly_chart(fig1)
    # Plot the total duration spent on each activity per day as a line chart
    fig2 = create_stacked_duration_chart(df)
    st.plotly_chart(fig2)

    # Plot the total duration spent on each activity per day as a line chart
    # fig3 = create_line_chart(df)
    # fig3.show()

if __name__ == "__main__":
    main()

