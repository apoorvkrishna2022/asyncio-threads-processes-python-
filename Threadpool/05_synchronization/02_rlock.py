"""
# Python Threading Tutorial - RLock (Reentrant Lock)
# ===============================================
#
# This file demonstrates using RLock for thread synchronization.
"""

import threading
import time

def rlock_example():
    """
    Demonstrate using RLock (Reentrant Lock).
    An RLock can be acquired multiple times by the same thread.
    """
    print("\n=== Thread Synchronization: RLock ===")
    
    # Create a reentrant lock
    rlock = threading.RLock()
    
    def outer_function():
        """Function that acquires the lock and calls another function."""
        print("Outer function: trying to acquire lock")
        with rlock:  # First acquire
            print("Outer function: lock acquired")
            inner_function()  # This function will try to acquire the same lock
            print("Outer function: work complete")
            
    def inner_function():
        """Function that also acquires the same lock."""
        print("Inner function: trying to acquire lock")
        with rlock:  # Second acquire by the same thread - this works with RLock
            print("Inner function: lock acquired again by same thread")
            time.sleep(1)
            print("Inner function: work complete")
    
    # Run in a thread
    thread = threading.Thread(target=outer_function)
    thread.start()
    thread.join()
    
    print("Note: With a regular Lock, the inner function would deadlock")
    
    # Demonstrate the difference between Lock and RLock
    print("\nDemonstrating why a regular Lock would deadlock:")
    
    # First with RLock (works correctly)
    print("Using RLock:")
    nested_rlock = threading.RLock()
    
    def nested_example(lock_type, lock):
        with lock:
            print(f"First {lock_type} acquisition - success")
            try:
                with lock:
                    print(f"Second {lock_type} acquisition - success")
            except Exception as e:
                print(f"Second {lock_type} acquisition - failed: {e}")
    
    # Try with RLock
    nested_example("RLock", nested_rlock)
    
    # Now with regular Lock (would deadlock, so we use a timeout)
    print("\nUsing regular Lock:")
    nested_lock = threading.Lock()
    
    def attempt_nested_lock():
        with nested_lock:
            print("First Lock acquisition - success")
            print("Trying to acquire lock again (this will hang without timeout)")
            # In a real situation this would deadlock
            # For demonstration, we'll use the acquire method with a timeout
            if nested_lock.acquire(timeout=1):
                try:
                    print("Second Lock acquisition - success (shouldn't happen)")
                finally:
                    nested_lock.release()
            else:
                print("Second Lock acquisition - failed (as expected)")
    
    attempt_nested_lock()

if __name__ == "__main__":
    rlock_example() 