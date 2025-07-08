import sys

print("--- Bittensor Module Diagnostic ---")
print(f"Python Executable: {sys.executable}")

try:
    import bittensor
    print("\nSuccessfully imported 'bittensor' module.")
    print(f"Module location: {bittensor.__file__}")
except ModuleNotFoundError as e:
    print(f"\nFailed to import 'bittensor': {e}")
    print("\nPlease ensure the module is installed in the correct environment.")

print("---------------------------------")
