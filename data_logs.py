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
        INSERT_QUERY = "INSERT INTO recycle_data (recycle_type) VALUES (?);"
        cursor.execute(INSERT_QUERY, (recycle_type,))
        connection.commit()
        print(f"Data inserted successfully: {recycle_type}")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        connection.close()

def get_all_records():
    """Retrieves all records from the recycle_data table."""
    connection = sqlite3.connect(DATABASE_NAME)
    try:
        cursor = connection.cursor()
        SELECT_QUERY = "SELECT recycle_type, timestamp FROM recycle_data ORDER BY timestamp DESC;"
        cursor.execute(SELECT_QUERY)
        rows = cursor.fetchall()
        records = [{"recycle_type": row[0], "timestamp": row[1]} for row in rows]
        return records
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return []
    finally:
        connection.close()

def get_recycle_type_counts():
    """Returns a dictionary with counts for each recycle_type."""
    connection = sqlite3.connect(DATABASE_NAME)
    try:
        cursor = connection.cursor()
        COUNT_QUERY = """
        SELECT recycle_type, COUNT(*) as count
        FROM recycle_data
        GROUP BY recycle_type;
        """
        cursor.execute(COUNT_QUERY)
        rows = cursor.fetchall()
        result = {row[0]: row[1] for row in rows}
        return result
    except sqlite3.Error as e:
        print(f"An error occurred while counting: {e}")
        return {}
    finally:
        connection.close()

if __name__ == "__main__":
    # Create the database and table
    create_database_and_table()

    # Example insertions (uncomment to test)
    # insert_data("plastic")
    # insert_data("metal")
    # insert_data("paper")
    # insert_data("general")

    # Fetch and print all records
    records = get_all_records()
    print("All records:", records)

    # Count each type and print the summary
    counts = get_recycle_type_counts()
    print("Recycle Type Counts:")
    for type_, count in counts.items():
        print(f"{type_.capitalize()}: {count}")
