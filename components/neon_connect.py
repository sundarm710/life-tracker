import os
from contextlib import contextmanager
from typing import Optional, List, Dict, Any
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NeonDatabaseManager:
    def __init__(self, min_conn: int = 1, max_conn: int = 10):
        """Initialize database manager with connection pooling"""
        load_dotenv()
        
        self.connection_params = {
            'dbname': os.getenv('NEON_DB_NAME'),
            'user': os.getenv('NEON_USER'),
            'password': os.getenv('NEON_PASSWORD'),
            'host': os.getenv('NEON_HOST'),
            'port': os.getenv('NEON_PORT', '5432'),
            'sslmode': 'require'
        }
        
        # Alternative: use full URL if provided
        if database_url := os.getenv('DATABASE_URL'):
            self.connection_params = database_url
            
        self.min_conn = min_conn
        self.max_conn = max_conn
        self.pool = None
        self._initialize_pool()

    def _initialize_pool(self) -> None:
        """Initialize the connection pool with error handling"""
        try:
            if isinstance(self.connection_params, dict):
                self.pool = pool.SimpleConnectionPool(
                    self.min_conn,
                    self.max_conn,
                    **self.connection_params
                )
            else:
                self.pool = pool.SimpleConnectionPool(
                    self.min_conn,
                    self.max_conn,
                    dsn=self.connection_params
                )
            logger.info("Database connection pool initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize connection pool: {str(e)}")
            raise

    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = None
        try:
            conn = self.pool.getconn()
            yield conn
        except Exception as e:
            logger.error(f"Database connection error: {str(e)}")
            raise
        finally:
            if conn:
                self.pool.putconn(conn)

    @contextmanager
    def get_cursor(self, cursor_factory=RealDictCursor):
        """Context manager for database cursors"""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=cursor_factory)
            try:
                yield cursor
                conn.commit()
            except Exception as e:
                conn.rollback()
                logger.error(f"Database operation error: {str(e)}")
                raise
            finally:
                cursor.close()

    def setup_tables(self):
        """Create necessary tables for the workout application"""
        create_tables_sql = """
        -- Users table
        CREATE TABLE IF NOT EXISTS users (
            user_id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );

        -- Workouts table
        CREATE TABLE IF NOT EXISTS workouts (
            workout_id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(user_id),
            date DATE NOT NULL,
            muscle_group TEXT NOT NULL,
            notes TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );

        -- Exercises table
        CREATE TABLE IF NOT EXISTS exercises (
            exercise_id SERIAL PRIMARY KEY,
            workout_id INTEGER REFERENCES workouts(workout_id),
            exercise_name TEXT NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );

        -- Sets table
        CREATE TABLE IF NOT EXISTS sets (
            set_id SERIAL PRIMARY KEY,
            exercise_id INTEGER REFERENCES exercises(exercise_id),
            set_number INTEGER NOT NULL,
            weight_kg NUMERIC(5,2) NOT NULL,
            reps INTEGER NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );

        -- Create indices for better performance
        CREATE INDEX IF NOT EXISTS idx_workouts_user_date ON workouts(user_id, date);
        CREATE INDEX IF NOT EXISTS idx_exercises_workout ON exercises(workout_id);
        CREATE INDEX IF NOT EXISTS idx_sets_exercise ON sets(exercise_id);
        """
        
        with self.get_cursor() as cursor:
            cursor.execute(create_tables_sql)
            logger.info("Database tables created successfully")

    def add_workout(self, user_id: int, workout_data: Dict[str, Any]) -> int:
        """Add a new workout with exercises and sets"""
        with self.get_cursor() as cursor:
            # Insert workout
            cursor.execute(
                """
                INSERT INTO workouts (user_id, date, muscle_group, notes)
                VALUES (%s, %s, %s, %s)
                RETURNING workout_id
                """,
                (user_id, workout_data['date'], workout_data['muscle_group'], 
                 workout_data.get('notes'))
            )
            workout_id = cursor.fetchone()['workout_id']

            # Insert exercises and sets
            for exercise in workout_data['exercises']:
                cursor.execute(
                    """
                    INSERT INTO exercises (workout_id, exercise_name)
                    VALUES (%s, %s)
                    RETURNING exercise_id
                    """,
                    (workout_id, exercise['name'])
                )
                exercise_id = cursor.fetchone()['exercise_id']

                # Insert sets
                for set_num, (weight, reps) in enumerate(
                    zip(exercise['weights'], exercise['reps']), 1
                ):
                    cursor.execute(
                        """
                        INSERT INTO sets (exercise_id, set_number, weight_kg, reps)
                        VALUES (%s, %s, %s, %s)
                        """,
                        (exercise_id, set_num, weight, reps)
                    )

            return workout_id

    def get_user_workouts(
        self, 
        user_id: int, 
        start_date: Optional[str] = None, 
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """Get user workouts with optional date filtering"""
        query = """
        SELECT 
            w.date,
            w.muscle_group,
            e.exercise_name,
            s.set_number,
            s.weight_kg,
            s.reps,
            w.notes
        FROM workouts w
        JOIN exercises e ON w.workout_id = e.workout_id
        JOIN sets s ON e.exercise_id = s.exercise_id
        WHERE w.user_id = %s
        """
        params = [user_id]

        if start_date:
            query += " AND w.date >= %s"
            params.append(start_date)
        if end_date:
            query += " AND w.date <= %s"
            params.append(end_date)

        query += " ORDER BY w.date DESC, e.exercise_name, s.set_number"

        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            return pd.DataFrame(cursor.fetchall())

    def close(self):
        """Close the connection pool"""
        if self.pool:
            self.pool.closeall()
            logger.info("Database connection pool closed")

# Example usage
if __name__ == "__main__":
    # Initialize database manager
    db = NeonDatabaseManager()

    try:
        # Setup tables
        db.setup_tables()

        # Example: Add a user
        with db.get_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO users (username, email)
                VALUES (%s, %s)
                RETURNING user_id
                """,
                ('testuser', 'test@example.com')
            )
            user_id = cursor.fetchone()['user_id']

        # Example: Add a workout
        workout_data = {
            'date': datetime.now().date(),
            'muscle_group': 'Pull',
            'notes': 'Good session',
            'exercises': [
                {
                    'name': 'Bench Press',
                    'weights': [20, 25, 30],
                    'reps': [15, 12, 10]
                }
            ]
        }
        
        workout_id = db.add_workout(user_id, workout_data)
        print(f"Added workout with ID: {workout_id}")

        # Get user workouts
        workouts_df = db.get_user_workouts(user_id)
        print("\nUser workouts:")
        print(workouts_df)

    except Exception as e:
        logger.error(f"Error in database operations: {str(e)}")
    finally:
        db.close()