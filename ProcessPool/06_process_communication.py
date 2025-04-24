#!/usr/bin/env python3
"""
06_process_communication.py - Communication between processes

This file covers:
- Different ways processes can communicate
- Using Pipes for bidirectional communication
- Using Queues for many-to-many communication
- Using Events and Conditions for synchronization
- Implementing common communication patterns
"""

import os
import time
import random
import multiprocessing
from multiprocessing import Process, Pipe, Queue, Event, Lock, Condition
from concurrent.futures import ProcessPoolExecutor


def print_process_info(name):
    """Print process information."""
    print(f"Process '{name}' (PID: {os.getpid()})")


# SECTION 1: Basic Communication Mechanisms
def demonstrate_communication_basics():
    """Overview of different interprocess communication mechanisms."""
    print("\nSECTION 1: Basic Communication Mechanisms")
    print("Python's multiprocessing module provides several ways for processes to communicate:")
    
    print("\n  1. Pipes:")
    print("     - Two-way communication channel between two processes")
    print("     - Fast and simple, but limited to two endpoints")
    
    print("\n  2. Queues:")
    print("     - Multi-producer, multi-consumer FIFO queue")
    print("     - Good for distributing tasks to worker processes")
    
    print("\n  3. Shared memory (Value, Array):")
    print("     - Direct memory sharing between processes")
    print("     - Fast for large data, but requires careful synchronization")
    
    print("\n  4. Manager objects:")
    print("     - Proxy objects that are synchronized across processes")
    print("     - More flexible but slower than direct shared memory")
    
    print("\n  5. Events:")
    print("     - Simple synchronization primitives for signaling between processes")
    
    print("\n  6. Locks and Conditions:")
    print("     - Advanced synchronization tools for coordinating access to shared resources")


# SECTION 2: Using Pipes for Two-Way Communication
def demonstrate_pipes():
    """Demonstrate using Pipes for communication between two processes."""
    print("\nSECTION 2: Using Pipes for Two-Way Communication")
    print("Pipes provide a simple way for two processes to communicate.")
    
    # Create a pipe
    parent_conn, child_conn = Pipe()
    
    def child_process(conn):
        """Function run by the child process."""
        print_process_info("child_process")
        
        # Receive a message from the parent
        message = conn.recv()
        print(f"  Child received: {message}")
        
        # Send a response back to the parent
        conn.send(f"Hello from child process (PID: {os.getpid()})")
        
        # Close the connection when done
        conn.close()
    
    # Create and start the child process
    p = Process(target=child_process, args=(child_conn,))
    p.start()
    
    # Send a message to the child
    parent_conn.send("Hello from parent process")
    
    # Receive the response from the child
    response = parent_conn.recv()
    print(f"  Parent received: {response}")
    
    # Close the parent connection and wait for the child to finish
    parent_conn.close()
    p.join()
    
    print("\n  Key points about Pipes:")
    print("  - Pipes are bidirectional by default (can be made unidirectional)")
    print("  - Pipes are fast and lightweight")
    print("  - Limited to communication between two endpoints")
    print("  - Objects sent must be picklable")


# SECTION 3: Using Queues for Many-to-Many Communication
def demonstrate_queues():
    """Demonstrate using Queues for communication between multiple processes."""
    print("\nSECTION 3: Using Queues for Many-to-Many Communication")
    print("Queues allow multiple producers and consumers to communicate.")
    
    # Create a queue
    queue = Queue()
    
    def producer(queue, id, num_items):
        """Producer process that puts items into the queue."""
        print_process_info(f"producer-{id}")
        
        for i in range(num_items):
            item = f"Item {i} from Producer {id}"
            queue.put(item)
            print(f"  Producer {id} put: {item}")
            time.sleep(random.uniform(0.1, 0.3))  # Simulate variable work time
        
        # Signal that this producer is done
        queue.put(f"DONE-{id}")
    
    def consumer(queue, id, num_producers):
        """Consumer process that gets items from the queue."""
        print_process_info(f"consumer-{id}")
        
        producers_done = 0
        while producers_done < num_producers:
            item = queue.get()
            
            # Check if a producer is done
            if item.startswith("DONE-"):
                producers_done += 1
                print(f"  Consumer {id} noticed producer {item[5:]} is done")
                continue
            
            # Process the item
            print(f"  Consumer {id} got: {item}")
            time.sleep(random.uniform(0.2, 0.5))  # Simulate processing time
    
    # Number of producers and consumers
    num_producers = 2
    num_consumers = 2
    items_per_producer = 3
    
    # Create and start producer processes
    producers = []
    for i in range(num_producers):
        p = Process(target=producer, args=(queue, i, items_per_producer))
        producers.append(p)
        p.start()
    
    # Create and start consumer processes
    consumers = []
    for i in range(num_consumers):
        c = Process(target=consumer, args=(queue, i, num_producers))
        consumers.append(c)
        c.start()
    
    # Wait for all producers to finish
    for p in producers:
        p.join()
    
    # Wait for all consumers to finish
    for c in consumers:
        c.join()
    
    print("\n  Key points about Queues:")
    print("  - Support multiple producers and consumers")
    print("  - Thread and process safe")
    print("  - Objects must be picklable")
    print("  - Can set a maximum size with the 'maxsize' parameter")
    print("  - Queue operations are atomic and thread-safe")


# SECTION 4: Using Events for Synchronization
def demonstrate_events():
    """Demonstrate using Events for synchronization between processes."""
    print("\nSECTION 4: Using Events for Synchronization")
    print("Events allow processes to signal each other.")
    
    # Create an event
    event = Event()
    
    def waiter(event):
        """Process that waits for an event to be set."""
        print_process_info("waiter")
        print("  Waiter is waiting for the event...")
        
        # Wait for the event to be set
        event.wait()
        
        print("  Waiter received the event and can proceed!")
    
    def setter(event):
        """Process that sets an event after a delay."""
        print_process_info("setter")
        print("  Setter will set the event after 2 seconds...")
        
        # Sleep for a bit before setting the event
        time.sleep(2)
        
        # Set the event - this will wake up all waiters
        event.set()
        print("  Setter has set the event!")
    
    # Create and start the processes
    w = Process(target=waiter, args=(event,))
    s = Process(target=setter, args=(event,))
    
    w.start()
    s.start()
    
    # Wait for the processes to finish
    w.join()
    s.join()
    
    print("\n  Key points about Events:")
    print("  - Simple synchronization primitive")
    print("  - Event starts in cleared state (event.is_set() == False)")
    print("  - event.set() sets the event, waking all waiters")
    print("  - event.clear() clears the event")
    print("  - event.wait() blocks until the event is set")
    print("  - event.wait(timeout) will wait only up to timeout seconds")


# SECTION 5: Condition Variables
def demonstrate_conditions():
    """Demonstrate using Condition variables for complex synchronization."""
    print("\nSECTION 5: Condition Variables")
    print("Conditions provide more complex synchronization than Events.")
    
    # Create a condition variable
    condition = Condition()
    
    # Shared state
    data = []
    
    def producer(condition, data):
        """Producer process that adds items to data when possible."""
        print_process_info("producer")
        
        for i in range(5):
            # Acquire the condition lock
            with condition:
                # Add an item to the shared data
                item = f"item-{i}"
                data.append(item)
                print(f"  Producer added {item} to data")
                
                # Notify one waiting consumer that new data is available
                condition.notify()
            
            # Sleep to simulate variable production time
            time.sleep(random.uniform(0.2, 0.5))
    
    def consumer(condition, data):
        """Consumer process that processes data when available."""
        print_process_info("consumer")
        
        items_consumed = 0
        while items_consumed < 5:  # Consume 5 items in total
            # Acquire the condition lock
            with condition:
                # While there's no data, wait for notification
                while not data:
                    print("  Consumer is waiting for data...")
                    condition.wait()
                
                # Get an item from the data
                item = data.pop(0)
                items_consumed += 1
                print(f"  Consumer got {item} from data")
    
    # Create and start the processes
    p = Process(target=producer, args=(condition, data))
    c = Process(target=consumer, args=(condition, data))
    
    c.start()
    p.start()
    
    # Wait for the processes to finish
    p.join()
    c.join()
    
    print("\n  Key points about Conditions:")
    print("  - Combines a Lock and a waiting mechanism")
    print("  - Allows threads to wait for a condition to be true")
    print("  - condition.wait() releases the lock, then reacquires it when notified")
    print("  - condition.notify() wakes up one waiting thread")
    print("  - condition.notify_all() wakes up all waiting threads")
    print("  - Always use Conditions within a 'with' block to ensure proper lock handling")


# SECTION 6: Producer-Consumer Pattern
def demonstrate_producer_consumer():
    """Demonstrate a complete producer-consumer pattern with a Queue."""
    print("\nSECTION 6: Producer-Consumer Pattern")
    print("A common pattern for parallel data processing.")
    
    # Create a task queue and a result queue
    task_queue = Queue()
    result_queue = Queue()
    
    # Create a poison pill for each consumer
    poison_pill = "STOP"
    
    def producer_process(task_queue, num_tasks, num_consumers):
        """Producer process that generates tasks."""
        print_process_info("producer")
        
        # Put tasks in the queue
        for i in range(num_tasks):
            task = f"Task-{i}"
            task_queue.put(task)
            print(f"  Producer created {task}")
            time.sleep(random.uniform(0.01, 0.1))  # Simulate task creation time
        
        # Put poison pills to stop consumers
        for _ in range(num_consumers):
            task_queue.put(poison_pill)
        
        print("  Producer finished creating all tasks")
    
    def consumer_process(task_queue, result_queue, worker_id):
        """Consumer process that processes tasks."""
        print_process_info(f"consumer-{worker_id}")
        
        while True:
            # Get a task from the queue
            task = task_queue.get()
            
            # Check for poison pill
            if task == poison_pill:
                print(f"  Consumer {worker_id} received poison pill, exiting")
                break
            
            # Process the task
            print(f"  Consumer {worker_id} processing {task}")
            time.sleep(random.uniform(0.1, 0.5))  # Simulate processing time
            
            # Put the result in the result queue
            result = f"Result of {task} processed by Worker-{worker_id}"
            result_queue.put(result)
    
    def result_collector_process(result_queue, num_tasks):
        """Process that collects and processes results."""
        print_process_info("result_collector")
        
        results_collected = 0
        all_results = []
        
        while results_collected < num_tasks:
            # Get a result from the queue
            result = result_queue.get()
            results_collected += 1
            all_results.append(result)
            print(f"  Collector got result: {result}")
        
        print(f"  Collected all {len(all_results)} results")
    
    # Configuration
    num_tasks = 10
    num_consumers = 3
    
    # Create and start the processes
    producer = Process(target=producer_process, args=(task_queue, num_tasks, num_consumers))
    consumers = [Process(target=consumer_process, args=(task_queue, result_queue, i)) 
                for i in range(num_consumers)]
    collector = Process(target=result_collector_process, args=(result_queue, num_tasks))
    
    # Start all processes
    producer.start()
    for c in consumers:
        c.start()
    collector.start()
    
    # Wait for all processes to finish
    producer.join()
    for c in consumers:
        c.join()
    collector.join()
    
    print("\n  Key components of the Producer-Consumer pattern:")
    print("  - Task Queue: Holds tasks to be processed")
    print("  - Result Queue: Collects results from worker processes")
    print("  - Producer: Creates tasks and puts them in the task queue")
    print("  - Consumers/Workers: Take tasks from the queue and process them")
    print("  - Poison Pills: Special messages to signal when to stop processing")
    print("  - Result Collector: Processes or aggregates the results")


# SECTION 7: Communication with ProcessPoolExecutor
def demonstrate_process_pool_communication():
    """Demonstrate communication patterns with ProcessPoolExecutor."""
    print("\nSECTION 7: Communication with ProcessPoolExecutor")
    print("ProcessPoolExecutor simplifies many communication patterns.")
    
    # Example 1: Basic result collection
    print("\n  Example 1: Basic Result Collection")
    
    def compute_square(x):
        """Compute the square of a number."""
        print(f"  Computing square of {x} in process {os.getpid()}")
        return x * x
    
    # Use ProcessPoolExecutor to compute squares
    with ProcessPoolExecutor(max_workers=3) as executor:
        numbers = [1, 2, 3, 4, 5]
        
        # Submit tasks and collect results
        results = list(executor.map(compute_square, numbers))
        
        print(f"  Results: {results}")
    
    # Example 2: Collecting results as they complete
    print("\n  Example 2: Collecting Results as They Complete")
    
    def slow_computation(x):
        """A computation that takes a variable amount of time."""
        sleep_time = random.uniform(0.5, 2.0)
        print(f"  Processing {x}, will take {sleep_time:.2f} seconds")
        time.sleep(sleep_time)
        return (x, x * x)
    
    with ProcessPoolExecutor(max_workers=4) as executor:
        # Submit all tasks
        future_to_number = {executor.submit(slow_computation, x): x for x in range(1, 6)}
        
        # Process results as they complete
        for future in multiprocessing.connection.wait(list(future_to_number.keys())):
            number = future_to_number[future]
            try:
                result = future.result()
                print(f"  Result for {number}: {result}")
            except Exception as e:
                print(f"  {number} generated an exception: {e}")


def main():
    """Main function running all demonstrations."""
    print("=== Process Communication ===")
    
    demonstrate_communication_basics()
    demonstrate_pipes()
    demonstrate_queues()
    demonstrate_events()
    demonstrate_conditions()
    demonstrate_producer_consumer()
    demonstrate_process_pool_communication()


if __name__ == "__main__":
    main()
    print("\nKey takeaways from this tutorial:")
    print("1. Pipes provide fast, bidirectional communication between two processes")
    print("2. Queues allow many-to-many communication patterns")
    print("3. Events and Conditions help synchronize process execution")
    print("4. Producer-Consumer is a powerful pattern for parallel processing")
    print("5. ProcessPoolExecutor simplifies many communication patterns") 