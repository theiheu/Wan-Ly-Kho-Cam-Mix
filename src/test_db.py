"""Script to test database connection and initialization."""

from utils.database_manager import DatabaseManager

def main():
    # Create database manager instance
    db = DatabaseManager()

    # Test connection
    if db.test_connection():
        print("Database connection successful!")

        # Initialize tables
        try:
            db.initialize_tables()
            print("Database tables initialized successfully!")
        except Exception as e:
            print(f"Error initializing tables: {e}")
    else:
        print("Failed to connect to database!")

    # Close connection
    db.close()

if __name__ == "__main__":
    main()