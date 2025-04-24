"""
# Python Threading Tutorial - Event
# ==============================
#
# This file demonstrates using Events for thread synchronization.
"""

import threading
import time

def event_example():
    """
    Demonstrate using Events for thread synchronization.
    Events are used to signal between threads.
    """
    print("\n=== Thread Synchronization: Event ===")
    
    # Create an event object
    event = threading.Event()
    
    def waiter(name, delay):
        """Thread that waits for the event to be set."""
        print(f"Waiter {name}: waiting for event")
        # wait() blocks until the event is set
        event_is_set = event.wait(timeout=delay)
        if event_is_set:
            print(f"Waiter {name}: event was set, continuing")
        else:
            print(f"Waiter {name}: timed out after {delay}s")
    
    def setter():
        """Thread that sets the event after a delay."""
        print("Setter: sleeping before setting event")
        time.sleep(2)
        print("Setter: setting event")
        event.set()  # Set the event, unblocking all waiters
    
    # Create and start threads
    t1 = threading.Thread(target=waiter, args=("A", 3))
    t2 = threading.Thread(target=waiter, args=("B", 5))
    t3 = threading.Thread(target=setter)
    
    t1.start()
    t2.start()
    t3.start()
    
    # Wait for all threads to complete
    t1.join()
    t2.join()
    t3.join()
    
    # Events can be cleared and reused
    print("\nClearing and reusing the event:")
    event.clear()  # Reset the event to not set
    
    t4 = threading.Thread(target=waiter, args=("C", 1))
    t4.start()
    t4.join()
    
    # Example of checking event state without waiting
    print("\nChecking event state without waiting:")
    print(f"Is event set? {event.is_set()}")
    
    # Set the event again
    print("Setting the event again")
    event.set()
    print(f"Is event set now? {event.is_set()}")
    
    # Create one more waiter
    t5 = threading.Thread(target=waiter, args=("D", 1))
    t5.start()
    t5.join()

if __name__ == "__main__":
    event_example() 