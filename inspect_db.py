import sqlite3
import os

# Define the path to the database
project_root = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(project_root, "bettensor", "validator", "state", "validator.db")

print(f"Inspecting database at: {db_path}")

if not os.path.exists(db_path):
    print("Database file does not exist. Please run data_extractor.py first to create it.")
else:
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Function to print table schema
        def print_schema(table_name):
            print(f"\n--- Schema for '{table_name}' table ---")
            cursor.execute(f"PRAGMA table_info({table_name});")
            schema = cursor.fetchall()

            if schema:
                print(f"{'cid':<5} {'name':<25} {'type':<15} {'notnull':<10} {'dflt_value':<15} {'pk':<5}")
                print("-" * 80)
                for col in schema:
                    print(f"{col[0]:<5} {col[1]:<25} {col[2]:<15} {col[3]:<10} {str(col[4]):<15} {col[5]:<5}")
            else:
                print(f"'{table_name}' table not found.")

        print_schema("game_data")
        print_schema("predictions")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()
            print("\nDatabase connection closed.")
