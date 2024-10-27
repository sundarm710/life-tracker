import pandas as pd
from fuzzywuzzy import process
from components.workout_database_manager import WorkoutDatabaseManager
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

class WorkoutDataProcessor:
    def __init__(self, db_manager: WorkoutDatabaseManager):
        self.db_manager = db_manager
        self.exercise_name_mapping = {}  # Cache for exercise name mapping

    def clean_exercise_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and standardize exercise names using fuzzy matching.
        """
        unique_exercises = df['exercise_name'].unique()
        for exercise in unique_exercises:
            if exercise not in self.exercise_name_mapping:
                # Use fuzzy matching to find the closest standard name
                standard_name, _ = process.extractOne(exercise, self.get_standard_exercise_names())
                print(f"Mapping {exercise} to {standard_name}")
                self.exercise_name_mapping[exercise] = standard_name
        
        df['exercise_name'] = df['exercise_name'].map(self.exercise_name_mapping)
        return df

    def get_standard_exercise_names(self) -> list:
        """
        Retrieve a list of standard exercise names from the database or a predefined list.
        """
        # TODO: Implement logic to get standard exercise names
        return ["Back squat", "Leg curl", "Leg press", "Calf raises", "Bench press", "Front raise", "Incline bench", "Lateral raise", "Triceps extension", "Shoulder press", "Arnold press", "Ez skull crusher", "Forearm bar roll", "Dumbbell press", "Triceps cable pushdown", "Deadlift", "RDL", "T row barbell", "Leg extension", "Pull ups", "Barbell row", "Preacher curl", "Biceps curl", "Cable row", "Hammer curl", "Lat pull", "One Arm Dumbbell Row", "Rear delt flyes", "Face pull", "Concentration curl", "Seated chest flyes"]

    def get_workouts(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Retrieve workouts for a given user and date range.
        """
        workouts = self.db_manager.get_workouts(start_date, end_date)
        df = pd.DataFrame(workouts)
        df['date'] = pd.to_datetime(df['date'])
        df['week'] = df['date'].dt.to_period('W').apply(lambda r: r.start_time)
        df['volume'] = df['weight_kg'] * df['reps']
        
        return self.clean_exercise_names(df)

    def aggregate_workout_data(self, df: pd.DataFrame, groupby: list, agg_func: dict) -> pd.DataFrame:
        """
        Aggregate workout data based on specified grouping and aggregation functions.
        """
        return df.groupby(groupby).agg(agg_func).reset_index()

    def prepare_volume_progression_data(self, start_date: str, end_date: str) -> tuple[go.Figure, go.Figure, go.Figure]:
        """
        Prepare data for volume progression visualization using stacked bar charts.
        Groups exercises by muscle group and stacks them to show total volume contribution.
        """

        df = self.get_workouts(start_date, end_date)
        st.write(df)
        volume_data_grouped = self.aggregate_workout_data(df, ['date', 'week', 'muscle_group', 'exercise_name'], {'weight_kg': 'max', 'reps': 'sum', 'volume': 'sum', 'set_number': 'max'})
        st.write(volume_data_grouped)

        fig = px.bar(volume_data_grouped, x="muscle_group", y="volume",
             color='week', barmode='group',
             hover_data="exercise_name",
             height=400)
        st.write(fig)

        # Create separate figures for each visualization
        fig_volume = go.Figure()
        fig_weight = go.Figure()
        fig_reps = go.Figure()

        # Get unique muscle groups and assign colors
        muscle_groups = volume_data_grouped['muscle_group'].unique()
        colors = px.colors.qualitative.Set3[:len(muscle_groups)]
        color_map = dict(zip(muscle_groups, colors))

        # Create stacked bar charts
        for muscle_group in muscle_groups:
            muscle_group_data = volume_data_grouped[volume_data_grouped['muscle_group'] == muscle_group]
            base_color = color_map[muscle_group]
            
            # Generate slightly different shades for exercises within the same muscle group
            exercises = muscle_group_data['exercise_name'].unique()
        
            for idx, exercise_name in enumerate(exercises):
                exercise_data = muscle_group_data[muscle_group_data['exercise_name'] == exercise_name]
                
            # Volume chart
            fig_volume.add_trace(go.Bar(
                x=exercise_data['date'],
                y=exercise_data['volume'],
                name=f"{muscle_group} - {exercise_name}",
                legendgroup=muscle_group,
                marker_color=base_color,
                showlegend=True
            ))
            
            # Weight chart
            fig_weight.add_trace(go.Bar(
                x=exercise_data['date'],
                y=exercise_data['weight_kg'],
                name=f"{muscle_group} - {exercise_name}",
                legendgroup=muscle_group,
                marker_color=base_color,
                showlegend=True
            ))
            
            # Reps chart
            fig_reps.add_trace(go.Bar(
                x=exercise_data['date'],
                y=exercise_data['reps'],
                name=f"{muscle_group} - {exercise_name}",
                legendgroup=muscle_group,
                marker_color=base_color,
                showlegend=True
            ))

        # Update layout for all charts
        for fig, title, ylabel in [
            (fig_volume, "Daily Volume (Weight × Reps) by Exercise", "Volume"),
            (fig_weight, "Daily Maximum Weight by Exercise", "Weight (kg)"),
            (fig_reps, "Daily Total Reps by Exercise", "Reps")
        ]:
            fig.update_layout(
                title=title,
                xaxis_title="Day",
                yaxis_title=ylabel,
                template="plotly_white",
                height=600,
                width=1000,
                barmode='stack',
                legend=dict(
                yanchor="top",
                y=-0.1,
                xanchor="left",
                x=0,
                orientation="h"
            ),
            margin=dict(b=150)  # Add bottom margin for legend
        )

        # Display charts in Streamlit
        st.write("### Volume Progression")
        st.plotly_chart(fig_volume, use_container_width=True)
        
        st.write("### Weight Progression")
        st.plotly_chart(fig_weight, use_container_width=True)
        
        st.write("### Reps Progression")
        st.plotly_chart(fig_reps, use_container_width=True)

        return fig_volume, fig_weight, fig_reps

    def prepare_exercise_frequency_data(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Prepare data for exercise frequency visualization.
        """
        df = self.get_workouts(start_date, end_date)
        df['week'] = pd.to_datetime(df['date']).dt.to_period('W').apply(lambda r: r.start_time)
        frequency_data_grouped = df.groupby(['week', 'muscle_group']).size().reset_index(name='count')

        fig_frequency = go.Figure()
        for muscle_group in frequency_data_grouped['muscle_group'].unique():
            muscle_group_data = frequency_data_grouped[frequency_data_grouped['muscle_group'] == muscle_group]
            fig_frequency.add_trace(go.Bar(x=muscle_group_data['week'], y=muscle_group_data['count'], name=muscle_group))

        st.plotly_chart(fig_frequency)

        return fig_frequency

    # Add more methods for different types of data processing and visualization preparation

