"""
# Python Threading Tutorial - Thread-Safe Queue
# =========================================
#
# This file demonstrates using Queue for thread-safe data exchange.
"""

import threading
import queue
import time
import random

def queue_example():
    """
    Demonstrate using Queue for thread-safe data exchange.
    Queues are ideal for producer-consumer patterns.
    """
    print("\n=== Thread-Safe Queue ===")
    
    # Create a thread-safe queue
    task_queue = queue.Queue(maxsize=10)
    
    def producer(num_tasks):
        """Produces tasks and adds them to the queue."""
        for i in range(num_tasks):
            task = f"Task-{i}"
            print(f"Producer: creating {task}")
            task_queue.put(task)  # Blocks if queue is full
            time.sleep(random.uniform(0.1, 0.3))
        
        # Signal that no more tasks will be added
        for _ in range(3):  # One sentinel for each consumer
            task_queue.put(None)
    
    def consumer(name):
        """Consumes tasks from the queue."""
        while True:
            task = task_queue.get()  # Blocks if queue is empty
            
            if task is None:  # Check for sentinel value
                print(f"Consumer {name}: no more tasks")
                task_queue.task_done()
                break
            
            print(f"Consumer {name}: processing {task}")
            time.sleep(random.uniform(0.5, 1.0))  # Simulate work
            task_queue.task_done()  # Signal task completion
    
    # Create and start threads
    producer_thread = threading.Thread(target=producer, args=(12,))
    consumer_threads = [
        threading.Thread(target=consumer, args=(name,))
        for name in ["A", "B", "C"]
    ]
    
    producer_thread.start()
    for t in consumer_threads:
        t.start()
    
    # Wait for the producer to finish
    producer_thread.join()
    
    # Wait for the queue to be fully processed
    task_queue.join()
    
    # Wait for consumers to exit
    for t in consumer_threads:
        t.join()
    
    print("All tasks processed")
    
    # LIFO Queue example
    print("\n=== LIFO Queue Example ===")
    lifo_queue = queue.LifoQueue(maxsize=5)
    
    # Put some items in the LIFO queue
    for i in range(5):
        item = f"LIFO-Item-{i}"
        print(f"Adding {item}")
        lifo_queue.put(item)
    
    # Get items from the LIFO queue
    print("\nGetting items from LIFO queue:")
    while not lifo_queue.empty():
        item = lifo_queue.get()
        print(f"Got: {item}")
        lifo_queue.task_done()
    
    # Priority Queue example
    print("\n=== Priority Queue Example ===")
    pq = queue.PriorityQueue(maxsize=5)
    
    # Add items with priorities
    items = [
        (3, "Medium priority"),
        (1, "Highest priority"),
        (5, "Lowest priority"),
        (2, "High priority"),
        (4, "Low priority")
    ]
    
    for priority, item in items:
        print(f"Adding: ({priority}) {item}")
        pq.put((priority, item))
    
    # Get items by priority
    print("\nGetting items by priority:")
    while not pq.empty():
        priority, item = pq.get()
        print(f"Got: ({priority}) {item}")
        pq.task_done()
    
    print("\nQueue methods overview:")
    print("- put(item): Add an item to the queue (blocks if full)")
    print("- put_nowait(item): Add an item without blocking (raises exception if full)")
    print("- get(): Remove and return an item (blocks if empty)")
    print("- get_nowait(): Remove and return an item without blocking (raises exception if empty)")
    print("- task_done(): Indicate that a formerly enqueued task is complete")
    print("- join(): Block until all items have been processed")
    print("- qsize(): Return the approximate size of the queue")
    print("- empty(): Return True if the queue is empty")
    print("- full(): Return True if the queue is full")

if __name__ == "__main__":
    queue_example() 