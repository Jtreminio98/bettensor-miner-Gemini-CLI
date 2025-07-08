import sys
import os

print("--- Debug script started. ---")

# Manually add the project root to the Python path
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

print("--- Path configured. Attempting to import DatabaseManager... ---")

try:
    from bettensor.validator.utils.database.database_manager import DatabaseManager
    print("--- DatabaseManager imported successfully. --- ")
except Exception as e:
    print(f"An error occurred during import: {e}")

print("--- Debug script finished. ---")
