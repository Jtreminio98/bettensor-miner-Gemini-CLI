#!/usr/bin/env python3
"""
initialize_database.py

Script to initialize the validator database with all required tables.
This script uses the database initialization statements from the bettensor validator
to create all necessary tables including predictions, game_data, miner_stats, etc.
"""

import sqlite3
import os
import sys
from pathlib import Path

# Add the bettensor module to path
sys.path.append(str(Path(__file__).parent))

from bettensor.validator.utils.database.database_init import initialize_database

def main():
    # Database file path
    db_path = "./validator.db"
    
    print(f"Initializing database: {db_path}")
    
    # Get all initialization statements
    statements = initialize_database()
    
    # Connect to database
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print(f"Executing {len(statements)} database initialization statements...")
        
        # Execute each statement
        for i, statement in enumerate(statements, 1):
            try:
                cursor.execute(statement)
                print(f"  [{i}/{len(statements)}] Executed successfully")
            except Exception as e:
                print(f"  [{i}/{len(statements)}] Error: {e}")
                print(f"  Statement: {statement[:100]}...")
                # Continue with other statements
                
        # Commit all changes
        conn.commit()
        print("Database initialization completed successfully!")
        
        # Verify tables were created
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"\nCreated tables ({len(tables)}):")
        for table in tables:
            print(f"  - {table[0]}")
            
    except Exception as e:
        print(f"Error initializing database: {e}")
        return 1
    finally:
        if conn:
            conn.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
