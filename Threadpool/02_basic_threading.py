"""
# Python Threading Tutorial - Basic Threading
# =========================================
#
# This file demonstrates how to create and use basic threads.
"""

import threading
import time

def basic_threading_example():
    """Demonstrate basic thread creation and execution."""
    print("\n=== Basic Threading ===")
    
    # Define a simple function to run in a thread
    def task(name, delay):
        """A simple function that will run in a separate thread."""
        print(f"Thread {name}: starting")
        time.sleep(delay)  # Simulate work
        print(f"Thread {name}: finished after {delay} seconds")
    
    # Create threads
    # A Thread object represents a separate thread of control
    thread1 = threading.Thread(target=task, args=("A", 2))
    thread2 = threading.Thread(target=task, args=("B", 1))
    
    # Start the threads - this begins their execution
    print("Main thread: starting threads")
    thread1.start()
    thread2.start()
    
    # Wait for both threads to complete with join()
    # join() blocks until the thread terminates
    print("Main thread: waiting for threads to finish")
    thread1.join()
    thread2.join()
    
    print("Main thread: all threads completed")

if __name__ == "__main__":
    basic_threading_example() 