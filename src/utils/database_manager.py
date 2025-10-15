"""Module for handling database-related operations."""

import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager

# Load environment variables
load_dotenv()

class DatabaseManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance.connection = None
        return cls._instance

    def __init__(self):
        """Initialize database connection parameters."""
        self.db_params = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'database': os.getenv('DB_NAME', 'wan_ly_kho_cam_mix'),
            'user': os.getenv('DB_USER', 'wanly_admin'),
            'password': os.getenv('DB_PASSWORD', '')
        }

    @contextmanager
    def get_connection(self):
        """Get a database connection."""
        if self.connection is None:
            try:
                self.connection = psycopg2.connect(**self.db_params)
            except Exception as e:
                print(f"Error connecting to database: {e}")
                raise

        try:
            yield self.connection
        except Exception as e:
            self.connection.rollback()
            raise
        else:
            self.connection.commit()

    @contextmanager
    def get_cursor(self):
        """Get a database cursor."""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            try:
                yield cursor
            finally:
                cursor.close()

    def initialize_tables(self):
        """Create necessary database tables if they don't exist."""
        with self.get_cursor() as cur:
            # Create inventory table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS inventory (
                    id SERIAL PRIMARY KEY,
                    product_name VARCHAR(100) NOT NULL UNIQUE,
                    quantity DECIMAL(10,2) NOT NULL DEFAULT 0,
                    bag_size INTEGER NOT NULL DEFAULT 0,
                    warehouse_type VARCHAR(10) NOT NULL,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_inventory_product_name
                ON inventory(product_name);
            """)

            # Create formulas table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS formulas (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    components JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_formulas_name
                ON formulas(name);
            """)

            # Create thresholds table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS thresholds (
                    id SERIAL PRIMARY KEY,
                    product_name VARCHAR(100) NOT NULL UNIQUE,
                    min_threshold DECIMAL(10,2) NOT NULL,
                    max_threshold DECIMAL(10,2) NOT NULL,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_thresholds_product_name
                ON thresholds(product_name);
            """)

            # Create inventory_history table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS inventory_history (
                    id SERIAL PRIMARY KEY,
                    product_name VARCHAR(100) NOT NULL,
                    quantity_change DECIMAL(10,2) NOT NULL,
                    operation_type VARCHAR(20) NOT NULL,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_inventory_history_product_name
                ON inventory_history(product_name);
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_inventory_history_created_at
                ON inventory_history(created_at);
            """)

    def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None

    def test_connection(self):
        """Test the database connection."""
        try:
            with self.get_cursor() as cur:
                cur.execute("SELECT version();")
                version = cur.fetchone()
                print(f"Successfully connected to PostgreSQL. Version: {version['version']}")
                return True
        except Exception as e:
            print(f"Error testing database connection: {e}")
            return False