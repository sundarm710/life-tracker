import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, time
from utility.time_block_parsing import fetch_time_blocks, fetch_activities, assign_activity
import streamlit as st

def time_to_float(t):
    return t.hour + t.minute / 60

def calculate_duration(start_time, end_time):
    """Calculate duration in hours between two time objects"""
    # Convert times to minutes since midnight
    start_minutes = start_time.hour * 60 + start_time.minute
    end_minutes = end_time.hour * 60 + end_time.minute
    
    # Calculate duration in minutes
    duration_minutes = end_minutes - start_minutes
    
    # Convert to hours
    duration_hours = duration_minutes / 60
    
    return duration_hours

def fetch_productive_time_blocks():
    df = fetch_time_blocks()
    df = df[df['Activity Category'].isin(['Workout', 'Work', 'Projects', 'Learning', 'Reading-Writing', 'Meditation', 'Chess', 'Reflection'])]
    return df

def fetch_chill_time_blocks():
    df = fetch_time_blocks()
    df = df[df['Activity Category'].isin(['Chill', 'Social'])]
    return df

def fetch_hover_text(df):
    # Ensure columns exist in DataFrame
    if all(col in df.columns for col in ['Activity', 'Activity Category', 'Day of Week', 'Date', 'Start Time', 'End Time', 'Duration_Hours']):
        return [f"{activity} ({category}) ({day}, {date.date()}, {start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}, {duration:.2f}h)" 
                for activity, category, day, date, start_time, end_time, duration  
                in zip(df['Activity'],
                       df['Activity Category'], 
                       df['Day of Week'], 
                       df['Date'], 
                       df['Start Time'], 
                       df['End Time'],
                       df['Duration_Hours'])]
    else:
        return [''] * len(df)

def generate_time_blocks_heatmap(df):
    fig = go.Figure()

    for activity, details in fetch_activities().items():
        activity_df = df[df['Activity Category'] == activity]
        
        # Calculate durations using Duration_Hours column instead of recalculating
        fig.add_trace(go.Bar(
            x=activity_df['Date'],
            y=activity_df['Duration_Hours'],  # Use the pre-calculated Duration_Hours
            base=[time_to_float(start) for start in activity_df['Start Time']],
            name=activity,
            marker_color=details['color'],
            hovertext=fetch_hover_text(activity_df),
            hoverinfo='text',
            hoverlabel=dict(namelength=-1),
            customdata=activity_df[['Activity', 'Day of Week', 'Start Time', 'End Time']],
            hovertemplate="<b>%{customdata[0]}</b> (%{customdata[0]})<br>" +
                          "Date: %{x|%Y-%m-%d}<br>" +
                          "Day: %{customdata[1]}<br>" +
                          "Time: %{customdata[2]} - %{customdata[3]}<br>" +
                          "Duration: %{y:.2f} hours<extra></extra>"
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


def generate_duration_count_chart(df):
    fig = go.Figure()

    # Calculate durations before grouping
    df['Duration_Hours'] = [calculate_duration(start, end) 
                           for start, end in zip(df['Start Time'], df['End Time'])]
    
    # Group by Date and Activity Category and sum the Duration_Hours
    grouped_df = df.groupby(['Date', 'Activity Category', 'Day of Week'])['Duration_Hours'].sum().reset_index()

    for activity, details in fetch_activities().items():
        activity_df = grouped_df[grouped_df['Activity Category'] == activity]

        fig.add_trace(go.Bar(
            x=activity_df['Date'],
            y=activity_df['Duration_Hours'],
            name=activity,
            marker_color=details['color'],
            customdata=activity_df[['Activity Category', 'Day of Week', 'Duration_Hours']],
            hovertext=[f"{category} ({day}, {date.date()}, {duration:.2f}h)"
                      for category, day, date, duration
                      in zip(activity_df['Activity Category'],
                            activity_df['Day of Week'],
                            activity_df['Date'],
                            activity_df['Duration_Hours'])],
            hoverinfo='text',
            hoverlabel=dict(namelength=-1)
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
    productive_df = fetch_productive_time_blocks()
    chill_df = fetch_chill_time_blocks()
    # Plot the time blocks as a stacked bar chart
    fig1 = generate_time_blocks_heatmap(df)
    st.plotly_chart(fig1)
    # Plot the total duration spent on each activity per day as a line chart
    fig2 = generate_duration_count_chart(df)
    st.plotly_chart(fig2)

    fig3 = generate_time_blocks_heatmap(productive_df)
    st.plotly_chart(fig3)

    fig5 = generate_duration_count_chart(productive_df)
    st.plotly_chart(fig5)

    fig6 = generate_time_blocks_heatmap(chill_df)
    st.plotly_chart(fig6)

    fig7 = generate_duration_count_chart(chill_df)
    st.plotly_chart(fig7)

if __name__ == "__main__":
    main()

