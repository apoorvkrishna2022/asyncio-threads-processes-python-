"""
# Python Threading Tutorial - Condition
# ==================================
#
# This file demonstrates using Condition objects for thread synchronization.
"""

import threading
import time
import random

def condition_example():
    """
    Demonstrate using Condition objects.
    Conditions combine a lock and a notification mechanism.
    """
    print("\n=== Thread Synchronization: Condition ===")
    
    # A shared buffer with limited capacity
    buffer = []
    max_size = 5
    
    # Create a condition
    condition = threading.Condition()
    
    def producer():
        """Produces items and adds them to the buffer."""
        for i in range(10):
            # Acquire the condition's lock
            with condition:
                while len(buffer) >= max_size:
                    print("Producer: buffer full, waiting")
                    condition.wait()  # Releases the lock and blocks until notified
                
                # Add item to buffer
                item = f"item-{i}"
                buffer.append(item)
                print(f"Producer: added {item} to buffer")
                
                # Notify consumers that an item is available
                condition.notify()
            
            time.sleep(random.uniform(0.1, 0.5))  # Simulate production time
    
    def consumer(name):
        """Consumes items from the buffer."""
        items_consumed = 0
        
        while items_consumed < 5:  # Each consumer gets 5 items
            # Acquire the condition's lock
            with condition:
                while len(buffer) == 0:
                    print(f"Consumer {name}: buffer empty, waiting")
                    condition.wait()  # Releases the lock and blocks until notified
                
                # Get item from buffer
                item = buffer.pop(0)
                print(f"Consumer {name}: got {item} from buffer")
                items_consumed += 1
                
                # Notify producers that space is available
                condition.notify()
            
            time.sleep(random.uniform(0.1, 1.0))  # Simulate consumption time
    
    # Create and start threads
    producer_thread = threading.Thread(target=producer)
    consumer1_thread = threading.Thread(target=consumer, args=("A",))
    consumer2_thread = threading.Thread(target=consumer, args=("B",))
    
    producer_thread.start()
    consumer1_thread.start()
    consumer2_thread.start()
    
    # Wait for all threads to complete
    producer_thread.join()
    consumer1_thread.join()
    consumer2_thread.join()
    
    print("\nCondition vs. Event:")
    print("- Events are for simple signaling: 'something happened'")
    print("- Conditions are for more complex coordination: 'wait until this condition is true'")
    print("- Conditions combine a lock with wait/notify mechanism")
    print("- Conditions support notifying just one waiting thread (notify) or all (notify_all)")

if __name__ == "__main__":
    condition_example() 