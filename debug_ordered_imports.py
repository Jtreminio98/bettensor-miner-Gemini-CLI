import sys
import os
import time

log_file_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "debug_ordered_log.txt")

def log_message(message):
    with open(log_file_path, "a") as f:
        f.write(f"{message}\n")

# Clear log file at the start
if os.path.exists(log_file_path):
    os.remove(log_file_path)

log_message("--- Starting ordered import test. ---")

# Manually add the project root to the Python path
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

log_message("--- Path configured. ---")

# List of modules in the exact order they are imported in database_manager.py
imports_to_test = [
    "asyncio",
    "pathlib",
    "sqlite3",
    "time",
    "aiosqlite",
    "logging",
    "os",
    "traceback",
    "sqlalchemy",
    "bettensor.validator.utils.database.database_init",
    "async_timeout",
    "uuid",
    "sqlalchemy.ext.asyncio",
    "sqlalchemy.orm",
    "sqlalchemy.pool",
    "contextlib",
    "re",
    "itertools",
    "aiofiles",
    "hashlib",
    "json",
    "random",
    "weakref",
]

for lib in imports_to_test:
    log_message(f"--- Attempting to import: {lib} ---")
    try:
        __import__(lib, fromlist=['*'])
        log_message(f"--- Successfully imported: {lib} ---")
    except Exception as e:
        log_message(f"--- FAILED to import {lib}: {e} ---")
    time.sleep(0.1)

log_message("--- Finished ordered import test. ---")
