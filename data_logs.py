import sqlite3

# Define the database file
DATABASE_NAME = "database.db"

# Define the SQL command to create the table
CREATE_TABLE_QUERY = """
CREATE TABLE IF NOT EXISTS recycle_data (
    recycle_type TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""

def create_database_and_table():
    """Creates the SQLite database and the recycle_data table."""
    connection = sqlite3.connect(DATABASE_NAME)
    try:
        cursor = connection.cursor()
        cursor.execute(CREATE_TABLE_QUERY)
        print("Table 'recycle_data' created successfully!")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        connection.close()

def insert_data(recycle_type):
    """Inserts a new record into the recycle_data table."""
    connection = sqlite3.connect(DATABASE_NAME)
    try:
        cursor = connection.cursor()
        # SQL command to insert data
        INSERT_QUERY = "INSERT INTO recycle_data (recycle_type) VALUES (?);"
        cursor.execute(INSERT_QUERY, (recycle_type,))
        connection.commit()
        print(f"Data inserted successfully: {recycle_type}")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        connection.close()

if __name__ == "__main__":
    # Create the database and table
    create_database_and_table()

    # Example of inserting data
    # Uncomment to test the insert functionality
    # insert_data("plastic")
    # insert_data("metal")
    # insert_data("paper")