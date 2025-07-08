import sys
import traceback

print("--- aiosqlite import debug script started. ---")
sys.stdout.flush()

try:
    print("Attempting to import aiosqlite...")
    sys.stdout.flush()
    
    import aiosqlite
    
    print("Successfully imported aiosqlite.")
    sys.stdout.flush()

except Exception as e:
    print(f"An error occurred during import: {e}")
    traceback.print_exc()
    sys.stdout.flush()

finally:
    print("--- aiosqlite import debug script finished. ---")
    sys.stdout.flush()
