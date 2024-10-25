import pandas as pd
from fuzzywuzzy import process
from components.workout_database_manager import WorkoutDatabaseManager
import plotly.graph_objects as go
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
        return self.clean_exercise_names(df)

    def aggregate_workout_data(self, df: pd.DataFrame, groupby: list, agg_func: dict) -> pd.DataFrame:
        """
        Aggregate workout data based on specified grouping and aggregation functions.
        """
        return df.groupby(groupby).agg(agg_func).reset_index()

    def prepare_volume_progression_data(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Prepare data for volume progression visualization.
        """
        df = self.get_workouts(start_date, end_date)
        df['week'] = pd.to_datetime(df['date']).dt.to_period('W').apply(lambda r: r.start_time)
        volume_data_grouped = df.groupby(['week', 'muscle_group', 'exercise_name']).agg({'weight_kg': 'max', 'reps': 'sum'}).reset_index()
        volume_data_grouped['volume'] = volume_data_grouped['weight_kg'] * volume_data_grouped['reps']

        # Create facet charts for each muscle group
        fig_weight = go.Figure()
        fig_reps = go.Figure()
        fig_volume = go.Figure()

        for muscle_group in volume_data_grouped['muscle_group'].unique():
            muscle_group_data = volume_data_grouped[volume_data_grouped['muscle_group'] == muscle_group]
            
            for exercise_name in muscle_group_data['exercise_name'].unique():
                exercise_data = muscle_group_data[muscle_group_data['exercise_name'] == exercise_name]
                
                fig_weight.add_trace(go.Scatter(
                    x=exercise_data['week'], 
                    y=exercise_data['weight_kg'], 
                    mode='lines+markers', 
                    name=f"{muscle_group} - {exercise_name}",
                    legendgroup=muscle_group,
                    showlegend=True
                ))
                
                fig_reps.add_trace(go.Scatter(
                    x=exercise_data['week'], 
                    y=exercise_data['reps'], 
                    mode='lines+markers', 
                    name=f"{muscle_group} - {exercise_name}",
                    legendgroup=muscle_group,
                    showlegend=True
                ))
                
                fig_volume.add_trace(go.Scatter(
                    x=exercise_data['week'], 
                    y=exercise_data['volume'], 
                    mode='lines+markers', 
                    name=f"{muscle_group} - {exercise_name}",
                    legendgroup=muscle_group,
                    showlegend=True
                ))

        # Update layout for better UI/UX
        fig_weight.update_layout(
            title="Weekly Maximum Weight Lifted per Muscle Group",
            xaxis_title="Week",
            yaxis_title="Weight (kg)",
            template="plotly_white",
            height=600,
            width=1000
        )

        fig_reps.update_layout(
            title="Weekly Total Reps per Muscle Group",
            xaxis_title="Week",
            yaxis_title="Reps",
            template="plotly_white",
            height=600,
            width=1000
        )

        fig_volume.update_layout(
            title="Weekly Volume (Weight x Reps) per Muscle Group",
            xaxis_title="Week",
            yaxis_title="Volume",
            template="plotly_white",
            height=600,
            width=1000
        )

        st.write("Weight")
        st.plotly_chart(fig_weight)
        st.write("Reps")
        st.plotly_chart(fig_reps)
        st.write("Volume")
        st.plotly_chart(fig_volume)

        return fig_weight, fig_reps, fig_volume

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

