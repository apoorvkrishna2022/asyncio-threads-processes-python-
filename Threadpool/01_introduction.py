"""
# Python Threading Tutorial - Introduction
# =======================================
#
# This file introduces the basic concepts of threading in Python.
"""

import threading
import time

def introduction_to_threading():
    """
    Introduction to threading concepts.
    
    Threads are separate flows of execution that share the same memory space.
    They allow your program to perform multiple operations at the same time.
    """
    print("\n=== Introduction to Threading ===")
    
    # Why use threading?
    print("Why use threading?")
    print("1. Perform multiple tasks simultaneously")
    print("2. Improve responsiveness in I/O-bound applications")
    print("3. Utilize multiple CPU cores (limited by GIL)")
    
    # Global Interpreter Lock (GIL)
    print("\nImportant Note - The Global Interpreter Lock (GIL):")
    print("Python has a GIL which allows only one thread to execute Python code at a time.")
    print("This means threading won't help CPU-bound tasks but is great for I/O-bound tasks.")
    print("For CPU-bound tasks, consider using the 'multiprocessing' module instead.")

if __name__ == "__main__":
    introduction_to_threading() 