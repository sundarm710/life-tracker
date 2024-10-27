import pandas as pd
from datetime import datetime
import re
import streamlit as st  # For debugging output

class WorkoutLogParser:
    def __init__(self):
        # Define schema
        self.columns = [
            'date',
            'muscle_group',
            'exercise_name',
            'set_number',
            'weight_kg',
            'reps',
            'volume',
            'notes'
        ]
        
        # Initialize empty DataFrame
        self.df = pd.DataFrame(columns=self.columns)
        
        # Define common rep patterns
        self.rep_patterns = {
            'usual_4': [15, 12, 10, 8],
            'usual_3': [15, 12, 10],
            # Add more patterns as needed
        }

    def _extract_notes(self, line):
        """Extract and remove notes from the line."""
        notes = ''
        notes_match = re.search(r'\((.*?)\)', line)
        if notes_match:
            notes = notes_match.group(1).strip()
            line = re.sub(r'\(.*?\)', '', line).strip()
        return line, notes

    def _parse_reps(self, reps_str, num_weights):
        """Parse reps string, handling 'usual' case and validation."""
        reps_str = reps_str.strip().lower()
        
        if reps_str == 'usual':
            if num_weights == 4:
                return self.rep_patterns['usual_4']
            elif num_weights == 3:
                return self.rep_patterns['usual_3']
            else:
                raise ValueError(f"Unexpected number of weights ({num_weights}) for 'usual' reps")
        
        try:
            return [int(r.strip()) for r in reps_str.split(',')]
        except ValueError as e:
            raise ValueError(f"Error parsing reps: {reps_str}. {str(e)}")

    def _parse_weights(self, weights_str):
        """Parse weights string with validation."""
        try:
            return [float(w.strip()) for w in weights_str.split(',')]
        except ValueError as e:
            raise ValueError(f"Error parsing weights: {weights_str}. {str(e)}")

    def parse_workout_text(self, text, date=None, debug=False):
        """
        Parse workout text and convert to DataFrame rows.
        
        Args:
            text (str): The workout log text
            date (str or datetime, optional): The workout date
            debug (bool): Whether to print debug information
        
        Returns:
            pd.DataFrame: Parsed workout data
        """
        # Handle date
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        elif isinstance(date, datetime):
            date = date.strftime('%Y-%m-%d')
            
        # Split into lines and get muscle group
        lines = text.strip().split('\n')
        if not lines:
            raise ValueError("Empty workout log")
            
        muscle_group = lines[0].strip()
        data = []

        # Process each exercise line
        for line in lines[1:]:
            if not line.strip():
                continue
                
            if debug:
                st.write(f"Processing line: {line}")

            # Extract and remove notes
            line, notes = self._extract_notes(line)

            # Split line into components
            try:
                exercise_parts = line.split(' - ')
                if len(exercise_parts) != 3:
                    raise ValueError(f"Invalid line format: {line}")
                    
                exercise_name, weights_str, reps_str = exercise_parts
            except ValueError as e:
                raise ValueError(f"Error parsing line: {line}. {str(e)}")

            # Parse weights and reps
            weights = self._parse_weights(weights_str)
            reps = self._parse_reps(reps_str, len(weights))

            # Validate weights and reps have same length
            if len(weights) != len(reps):
                raise ValueError(
                    f"Mismatch between weights ({len(weights)}) and reps ({len(reps)}) "
                    f"for exercise: {exercise_name}"
                )
            set_num = 1
            # Create entries for each set
            for weight, rep in zip(weights, reps):
                data.append({
                    'date': date,
                    'muscle_group': muscle_group,
                    'exercise_name': exercise_name.strip(),
                    'set_number': set_num,
                    'weight_kg': weight,
                    'reps': rep,
                    'volume': weight * rep,
                    'notes': notes
                })
                set_num += 1

        # Convert to DataFrame
        new_df = pd.DataFrame(data)
        self.df = pd.concat([self.df, new_df], ignore_index=True)
        return new_df

    def get_exercise_summary(self, exercise_name=None, start_date=None, end_date=None):
        """Get summary statistics for specified exercise(s)."""
        df = self.df.copy()
        
        if exercise_name:
            df = df[df['exercise_name'] == exercise_name]
        if start_date:
            df = df[df['date'] >= start_date]
        if end_date:
            df = df[df['date'] <= end_date]
            
        return df.groupby('exercise_name').agg({
            'volume': ['mean', 'max', 'sum'],
            'weight_kg': ['mean', 'max'],
            'reps': ['mean', 'sum']
        }).round(2)

    def get_progress_data(self, exercise_name):
        """Get exercise progress over time."""
        return (self.df[self.df['exercise_name'] == exercise_name]
                .groupby('date')
                .agg({
                    'volume': ['mean', 'max'],
                    'weight_kg': 'max',
                    'reps': 'sum'
                })
                .reset_index())

# # Example usage
# if __name__ == "__main__":
#     sample_log = """Pull 1
#     Barbell bench press - 20, 25, 45, 10 - usual
#     Shoulder press - 20, 15, 8, 10 - 15, 12, 10, 10 (increase weight next time)"""

#     parser = WorkoutLogParser()
#     try:
#         df = parser.parse_workout_text(sample_log, debug=True)
#         st.write("\nParsed Data:")
#         st.write(df)
        
#         st.write("\nExercise Summary:")
#         st.write(parser.get_exercise_summary())

#         st.write("\nExercise Progress:")
#         for exercise in ['Barbell bench press', 'Shoulder press']:
#             st.write(exercise)
#             st.write(parser.get_progress_data(exercise))
#     except ValueError as e:
#         print(f"Error parsing workout log: {str(e)}")