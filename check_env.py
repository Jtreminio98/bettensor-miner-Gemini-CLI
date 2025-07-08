import sys
import os

print("--- Python Environment Diagnostic ---")
print(f"Python Executable: {sys.executable}")
print("\nPython Path (sys.path):")
for path in sys.path:
    print(f"  - {path}")
print("-----------------------------------")
