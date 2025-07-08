import sys
import os
import time

log_file_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "debug_log.txt")

def log_message(message):
    with open(log_file_path, "a") as f:
        f.write(f"{message}\n")

# Clear log file at the start
if os.path.exists(log_file_path):
    os.remove(log_file_path)

log_message("--- Starting individual import test. ---")

# Manually add the project root to the Python path
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

log_message("--- Path configured. ---")

# List of all modules imported by database_manager.py
imports_to_test = [
    "asyncio",
    "pathlib",
    "sqlite3",
    "time",
    "logging",
    "os",
    "traceback",
    "uuid",
    "contextlib",
    "re",
    "itertools",
    "hashlib",
    "json",
    "random",
    "weakref",
    "aiofiles",
    "async_timeout",
    "sqlalchemy",
    "aiosqlite",
    "bettensor.validator.utils.database.database_init",
]

for lib in imports_to_test:
    log_message(f"--- Attempting to import: {lib} ---")
    try:
        __import__(lib)
        log_message(f"--- Successfully imported: {lib} ---")
    except Exception as e:
        log_message(f"--- FAILED to import {lib}: {e} ---")
    time.sleep(0.1) # Small delay

log_message("--- Finished individual import test. ---")

