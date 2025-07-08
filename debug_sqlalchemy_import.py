import sys
import traceback

print("--- SQLAlchemy import debug script started. ---")
sys.stdout.flush()

try:
    print("Attempting to import create_async_engine from sqlalchemy.ext.asyncio...")
    sys.stdout.flush()
    
    from sqlalchemy.ext.asyncio import create_async_engine
    
    print("Successfully imported create_async_engine.")
    sys.stdout.flush()

except Exception as e:
    print(f"An error occurred during import: {e}")
    traceback.print_exc()
    sys.stdout.flush()

finally:
    print("--- SQLAlchemy import debug script finished. ---")
    sys.stdout.flush()
