import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load biến môi trường từ file .env
load_dotenv()

class DatabaseConnection:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance.connection = None
        return cls._instance

    def connect(self):
        """Tạo kết nối đến database"""
        if self.connection is None:
            try:
                self.connection = psycopg2.connect(
                    host=os.getenv("DB_HOST"),
                    port=os.getenv("DB_PORT"),
                    database=os.getenv("DB_NAME"),
                    user=os.getenv("DB_USER"),
                    password=os.getenv("DB_PASSWORD")
                )
                print("Database connection successful")
            except Exception as e:
                print(f"Error connecting to database: {e}")
                raise

    def get_connection(self):
        """Trả về connection hiện tại hoặc tạo mới nếu chưa có"""
        if self.connection is None:
            self.connect()
        return self.connection

    def close(self):
        """Đóng kết nối database"""
        if self.connection is not None:
            self.connection.close()
            self.connection = None

    def execute_query(self, query, params=None):
        """Thực thi câu query và trả về kết quả dạng dict"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(query, params)
                    if cur.description:  # Nếu query trả về dữ liệu
                        return cur.fetchall()
                    return None
        except Exception as e:
            print(f"Error executing query: {e}")
            raise

    def execute_transaction(self, queries):
        """Thực thi nhiều câu query trong một transaction"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    for query, params in queries:
                        cur.execute(query, params)
                    conn.commit()
        except Exception as e:
            print(f"Error executing transaction: {e}")
            conn.rollback()
            raise