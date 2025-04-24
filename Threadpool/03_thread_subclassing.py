"""
# Python Threading Tutorial - Thread Subclassing
# ============================================
#
# This file demonstrates how to create custom thread classes.
"""

import threading
import time

def thread_subclassing_example():
    """
    Demonstrate creating threads by subclassing the Thread class.
    This is useful for more complex thread behavior.
    """
    print("\n=== Thread Subclassing ===")
    
    # Create a custom thread class by inheriting from threading.Thread
    class MyThread(threading.Thread):
        """A custom thread class."""
        
        def __init__(self, name, delay):
            # Always call the parent class's __init__ method
            super().__init__()
            self.name = name
            self.delay = delay
        
        # Override the run method - this is what executes when the thread starts
        def run(self):
            print(f"Custom thread {self.name}: starting")
            time.sleep(self.delay)
            print(f"Custom thread {self.name}: finished after {self.delay} seconds")
            
            # You can store results in instance variables
            self.result = f"Result from thread {self.name}"
    
    # Create and start thread instances
    thread1 = MyThread("X", 2)
    thread2 = MyThread("Y", 1)
    
    thread1.start()
    thread2.start()
    
    # Wait for completion
    thread1.join()
    thread2.join()
    
    # Access results from the threads
    print(f"Got result: {thread1.result}")
    print(f"Got result: {thread2.result}")

if __name__ == "__main__":
    thread_subclassing_example() 