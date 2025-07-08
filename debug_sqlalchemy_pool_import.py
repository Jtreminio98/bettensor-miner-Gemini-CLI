import sys
import traceback

print("--- SQLAlchemy pool import debug script started. ---")
sys.stdout.flush()

try:
    print("Attempting to import AsyncAdaptedQueuePool from sqlalchemy.pool...")
    sys.stdout.flush()
    
    from sqlalchemy.pool import AsyncAdaptedQueuePool
    
    print("Successfully imported AsyncAdaptedQueuePool.")
    sys.stdout.flush()

except Exception as e:
    print(f"An error occurred during import: {e}")
    traceback.print_exc()
    sys.stdout.flush()

finally:
    print("--- SQLAlchemy pool import debug script finished. ---")
    sys.stdout.flush()
