import os
from contextlib import contextmanager
from typing import Optional, Dict, Any
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseDatabaseManager:
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

    def close(self):
        """Close the connection pool"""
        if self.pool:
            self.pool.closeall()
            logger.info("Database connection pool closed")