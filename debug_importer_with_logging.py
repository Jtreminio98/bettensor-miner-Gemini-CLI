import sys
import os

log_file_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "importer_log.txt")

def log_message(message):
    with open(log_file_path, "a") as f:
        f.write(f"{message}\n")

# Clear log file at the start
if os.path.exists(log_file_path):
    os.remove(log_file_path)

log_message("--- Importer script started. ---")

# Manually add the project root to the Python path
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

log_message("--- Path configured. ---")

log_message("--- About to execute import statement... ---")
try:
    from bettensor.validator.utils.database.database_manager import DatabaseManager
    log_message("--- Import statement finished successfully. ---")
except Exception as e:
    log_message(f"--- FAILED to import: {e} ---")

log_message("--- Importer script finished. ---")
