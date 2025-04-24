"""
# Python Threading Tutorial - Locks
# ===============================
#
# This file demonstrates using locks to prevent race conditions.
"""

import threading
import time

def lock_example():
    """
    Demonstrate using locks to prevent race conditions.
    Race conditions occur when multiple threads access and modify shared data.
    """
    print("\n=== Thread Synchronization: Locks ===")
    
    # A shared counter
    counter = 0
    
    def increment_counter(count, lock=None):
        """Increment the counter 'count' times, optionally using a lock."""
        nonlocal counter
        
        for _ in range(count):
            # The "race condition" occurs in this section
            if lock:
                # With a lock: thread-safe incrementing
                with lock:  # equivalent to lock.acquire() and lock.release()
                    current = counter
                    time.sleep(0.0001)  # Simulate processing time to make race condition obvious
                    counter = current + 1
            else:
                # Without a lock: race condition can occur
                current = counter
                time.sleep(0.0001)  # Simulate processing time to make race condition obvious
                counter = current + 1
    
    # First, demonstrate the race condition problem
    print("Without a lock (race condition):")
    counter = 0
    
    # Create threads that increment the counter
    threads = []
    for i in range(5):
        thread = threading.Thread(target=increment_counter, args=(10,))
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    print(f"Final counter value without lock: {counter}")
    print(f"Expected value: {5 * 10}")
    
    # Now, demonstrate proper synchronization with a lock
    print("\nWith a lock (thread-safe):")
    counter = 0
    lock = threading.Lock()  # Create a lock object
    
    # Create threads that increment the counter with a lock
    threads = []
    for i in range(5):
        thread = threading.Thread(target=increment_counter, args=(10, lock))
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    print(f"Final counter value with lock: {counter}")
    print(f"Expected value: {5 * 10}")

if __name__ == "__main__":
    lock_example() 