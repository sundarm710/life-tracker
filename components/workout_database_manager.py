from components.base_database_manager import BaseDatabaseManager
from typing import Dict, Any, Optional
import pandas as pd
import logging
import streamlit as st
logger = logging.getLogger(__name__)

class WorkoutDatabaseManager(BaseDatabaseManager):
    def setup_tables(self):
        """Create necessary tables for the workout application"""
        create_tables_sql = """
        -- Workouts table
        CREATE TABLE IF NOT EXISTS workouts (
            workout_id SERIAL PRIMARY KEY,
            date DATE NOT NULL,
            muscle_group TEXT NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );

        -- Exercises table
        CREATE TABLE IF NOT EXISTS exercises (
            exercise_id SERIAL PRIMARY KEY,
            workout_id INTEGER REFERENCES workouts(workout_id),
            exercise_name TEXT NOT NULL,
            set_number INTEGER NOT NULL,  -- Changed back to set_number
            weight_kg NUMERIC(5,2) NOT NULL,
            reps INTEGER NOT NULL,
            volume NUMERIC(10,2) NOT NULL,
            notes TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );

        -- Create indices for better performance
        CREATE INDEX IF NOT EXISTS idx_workouts_date ON workouts(date);
        CREATE INDEX IF NOT EXISTS idx_exercises_workout ON exercises(workout_id);
        """
        
        with self.get_cursor() as cursor:
            try:
                cursor.execute(create_tables_sql)
                logger.info("Database tables created successfully")
            except Exception as e:
                logger.error(f"Database connection error: {e}")

    def add_workout(self, workout_data: Dict[str, Any]) -> int:
        """Add a new workout with exercises"""
        with self.get_cursor() as cursor:
            try:
                # Debug print
                if st.session_state.get('debug'):
                    st.write("Received workout_data:", workout_data)

                # Insert workout
                cursor.execute(
                    """
                    INSERT INTO workouts (date, muscle_group)
                    VALUES (%s, %s)
                    RETURNING workout_id
                    """,
                    (workout_data['date'], workout_data['muscle_group'])
                )
                workout_id = cursor.fetchone()['workout_id']

                # Insert exercises
                for exercise in workout_data['exercises']:
                    # Debug print
                    if st.session_state.get('debug'):
                        st.write(f"Processing exercise: {exercise}")
                    
                    # Extract values while handling potential list/non-list formats
                    exercise_name = exercise['exercise_name']
                    set_numbers = exercise['set_number'] if isinstance(exercise['set_number'], list) else [exercise['set_number']]
                    weights = exercise['weight_kg'] if isinstance(exercise['weight_kg'], list) else [exercise['weight_kg']]
                    reps = exercise['reps'] if isinstance(exercise['reps'], list) else [exercise['reps']]
                    volumes = exercise['volume'] if isinstance(exercise['volume'], list) else [exercise['volume']]
                    notes = exercise['notes'] if isinstance(exercise['notes'], list) else [exercise['notes']]
                    
                    # Ensure all lists have the same length
                    for set_number, weight, rep, volume, note in zip(set_numbers, weights, reps, volumes, notes):
                        if st.session_state.get('debug'):
                            st.write(f"Adding set: {exercise_name} - Set {set_number}")
                            st.write(f"Weight: {weight}, Reps: {rep}, Volume: {volume}, Notes: {note}")
                        
                        cursor.execute(
                            """
                            INSERT INTO exercises (workout_id, exercise_name, set_number, weight_kg, reps, volume, notes)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                            """,
                            (workout_id, exercise_name, set_number, weight, rep, volume, note)
                        )

                # Success notification
                st.success("Workout added successfully!")
                return workout_id
            except Exception as e:
                # Error notification
                st.error("Failed to add workout. Please try again.")
                logger.error(f"Database connection error: {e}")
                st.error(f"Error details: {str(e)}")
                raise

    def get_workouts(
        self, 
        start_date: Optional[str] = None, 
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """Get user workouts with optional date filtering"""
        query = """
        SELECT 
            w.date,
            w.muscle_group,
            e.exercise_name,
            e.set_number,  -- Changed back to set_number
            e.weight_kg,
            e.reps,
            e.notes
        FROM workouts w
        JOIN exercises e ON w.workout_id = e.workout_id
        WHERE 1=1
        """
        params = []

        if start_date:
            query += " AND w.date >= %s"
            params.append(start_date)
        if end_date:
            query += " AND w.date <= %s"
            params.append(end_date)

        query += " ORDER BY w.date DESC, e.exercise_name, e.set_number"  # Changed back to set_number

        with self.get_cursor() as cursor:
            try:
                if st.session_state.get('debug'):
                    st.write("Executing query:", query, "With params:", params)
                cursor.execute(query, params)
                result = cursor.fetchall()
                if st.session_state.get('debug'):
                    st.write("Query result:", result)
                return pd.DataFrame(result)
            except Exception as e:
                logger.error(f"Database connection error: {e}")
                raise
