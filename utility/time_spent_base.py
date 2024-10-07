import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, time
from utility.time_block_parsing import fetch_time_blocks, fetch_activities, assign_activity
import streamlit as st

def time_to_float(t):
    return t.hour + t.minute / 60

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

def generate_time_blocks_heatmap(df):
    fig = go.Figure()

    # Assign a single activity to each row based on priority order
    # df['Assigned Activity'] = df.apply(assign_activity, axis=1)

    # Add traces for each activity
    for activity, details in fetch_activities().items():
        activity_df = df[df['Activity Category'] == activity]

        fig.add_trace(go.Bar(
            x=activity_df['Date'],
            y=[time_to_float(end) - time_to_float(start) for start, end in zip(activity_df['Start Time'], activity_df['End Time'])],
            base=[time_to_float(start) for start in activity_df['Start Time']],
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

    # Group the data by Date and Assigned Activity
    grouped_df = df.groupby(['Date', 'Activity Category', 'Day of Week', 'Start Time', 'End Time'])['Duration_Hours'].sum().reset_index()

    # Add traces for each activity
    for activity, details in fetch_activities().items():
        activity_df = grouped_df[grouped_df['Activity Category'] == activity]

        fig.add_trace(go.Bar(
            x=activity_df['Date'],
            y=activity_df['Duration_Hours'],
            name=activity,
            marker_color=details['color'],
            
            hovertext=fetch_hover_text(activity_df),
            hoverinfo='text',  # Only display hover text
            hoverlabel=dict(namelength=-1),  # Show full activity name in hover label
            customdata=activity_df[['Activity Category', 'Day of Week', 'Start Time', 'End Time']],
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

