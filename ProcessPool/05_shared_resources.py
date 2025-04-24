#!/usr/bin/env python3
"""
05_shared_resources.py - Working with shared data between processes

This file covers:
- Sharing data between processes
- Using shared memory
- Using multiprocessing's Value and Array
- Safe concurrent access with locks
- Working with managers
- Best practices for sharing resources
"""

import os
import time
import random
import multiprocessing
from multiprocessing import Process, Value, Array, Lock, Manager
from concurrent.futures import ProcessPoolExecutor


def print_process_info(name):
    """Print process information."""
    print(f"Process '{name}' (PID: {os.getpid()})")


# SECTION 1: The Challenge with Process Isolation
def demonstrate_process_isolation():
    """Demonstrate that processes don't share memory by default."""
    print("\nSECTION 1: Process Isolation")
    print("Unlike threads, processes don't share memory by default.")
    
    # Global variable in the main process
    counter = 0
    
    def modify_counter():
        """Try to modify the global counter variable."""
        # This creates a new local 'counter' in the child process
        # It doesn't affect the parent process's counter
        nonlocal counter
        counter = 100
        print(f"  Child process: counter = {counter}")
    
    # Start a new process
    print(f"  Main process before: counter = {counter}")
    
    # Create and start a process
    p = Process(target=modify_counter)
    p.start()
    p.join()
    
    # The counter in the main process is unchanged
    print(f"  Main process after: counter = {counter}")
    print("  Notice that the counter did not change in the main process.")


# SECTION 2: Using multiprocessing.Value and multiprocessing.Array
def demonstrate_shared_value_and_array():
    """Demonstrate using Value and Array to share data between processes."""
    print("\nSECTION 2: Using multiprocessing.Value and multiprocessing.Array")
    print("Value and Array objects can be shared between processes.")
    
    # Create a shared Value (a single value)
    shared_value = Value('i', 0)  # 'i' is for integer
    
    # Create a shared Array (multiple values)
    shared_array = Array('i', [0, 0, 0, 0, 0])  # 'i' is for integer
    
    def modify_shared_values(value, array):
        """Modify the shared value and array."""
        print_process_info("modify_shared_values")
        
        # Modify the shared value
        value.value = 100
        
        # Modify the shared array
        for i in range(len(array)):
            array[i] = i * 10
    
    # Print initial values
    print(f"  Initial shared value: {shared_value.value}")
    print(f"  Initial shared array: {list(shared_array)}")
    
    # Start a process to modify the shared objects
    p = Process(target=modify_shared_values, args=(shared_value, shared_array))
    p.start()
    p.join()
    
    # Print the modified values
    print(f"  Modified shared value: {shared_value.value}")
    print(f"  Modified shared array: {list(shared_array)}")


# SECTION 3: Race Conditions and Locks
def demonstrate_race_conditions():
    """Demonstrate race conditions and how to fix them with locks."""
    print("\nSECTION 3: Race Conditions and Locks")
    print("Multiple processes updating shared data can lead to race conditions.")
    
    # WITHOUT a lock - race condition
    print("\n  WITHOUT a lock (race condition):")
    counter_without_lock = Value('i', 0)
    
    def increment_without_lock(counter, iterations):
        """Increment counter without lock - susceptible to race conditions."""
        for _ in range(iterations):
            # This is not atomic - it involves multiple operations:
            # 1. Read counter.value
            # 2. Add 1
            # 3. Write back to counter.value
            counter.value = counter.value + 1
    
    # Create processes to increment counter in parallel
    processes = []
    for _ in range(4):
        p = Process(target=increment_without_lock, args=(counter_without_lock, 10000))
        processes.append(p)
        p.start()
    
    # Wait for all processes to complete
    for p in processes:
        p.join()
    
    print(f"  Expected final count: 40000")
    print(f"  Actual final count: {counter_without_lock.value}")
    print("  The actual value is often less due to race conditions")
    
    # WITH a lock - no race condition
    print("\n  WITH a lock (synchronized):")
    counter_with_lock = Value('i', 0)
    lock = Lock()  # Create a lock for synchronization
    
    def increment_with_lock(counter, lock, iterations):
        """Increment counter with lock - prevents race conditions."""
        for _ in range(iterations):
            # Acquire the lock before modifying the counter
            with lock:
                # Now this operation is atomic - other processes must wait
                counter.value = counter.value + 1
    
    # Create processes to increment counter in parallel
    processes = []
    for _ in range(4):
        p = Process(target=increment_with_lock, args=(counter_with_lock, lock, 10000))
        processes.append(p)
        p.start()
    
    # Wait for all processes to complete
    for p in processes:
        p.join()
    
    print(f"  Expected final count: 40000")
    print(f"  Actual final count: {counter_with_lock.value}")
    print("  With a lock, the count is accurate")


# SECTION 4: Using Managers for Shared Resources
def demonstrate_managers():
    """Demonstrate using Manager objects to share resources."""
    print("\nSECTION 4: Using Managers for Shared Resources")
    print("Managers provide a more flexible way to share objects between processes.")
    
    # Create a Manager
    with Manager() as manager:
        # Create shared objects
        shared_dict = manager.dict()
        shared_list = manager.list()
        
        def modify_shared_objects(dictionary, list_obj):
            """Modify the shared dictionary and list."""
            print_process_info("modify_shared_objects")
            
            # Modify the shared dictionary
            dictionary['name'] = 'ProcessPool'
            dictionary['version'] = 1.0
            
            # Modify the shared list
            list_obj.append('item1')
            list_obj.append('item2')
            list_obj.append('item3')
        
        # Print initial values
        print(f"  Initial shared dict: {dict(shared_dict)}")
        print(f"  Initial shared list: {list(shared_list)}")
        
        # Start a process to modify the shared objects
        p = Process(target=modify_shared_objects, args=(shared_dict, shared_list))
        p.start()
        p.join()
        
        # Print the modified values
        print(f"  Modified shared dict: {dict(shared_dict)}")
        print(f"  Modified shared list: {list(shared_list)}")
        
        # Show that the manager supports many types of shared objects
        print("\n  Available shared object types:")
        print("  - dict: Standard dictionary")
        print("  - list: Standard list")
        print("  - Namespace: Attribute access to shared data")
        print("  - Lock: Process-safe lock")
        print("  - RLock: Reentrant lock")
        print("  - Semaphore: Counting semaphore")
        print("  - BoundedSemaphore: Bounded semaphore")
        print("  - Condition: Condition variable")
        print("  - Event: Event for process synchronization")
        print("  - Queue: Shared queue")
        print("  - Value: Single shared value")
        print("  - Array: Shared array")


# SECTION 5: When to Use Shared Resources
def when_to_use_shared_resources():
    """Discuss when to use shared resources vs. other approaches."""
    print("\nSECTION 5: When to Use Shared Resources")
    print("Sharing resources between processes can be useful but has tradeoffs.")
    
    print("\n  Advantages of shared resources:")
    print("  - Allows communication between processes")
    print("  - Can be more memory-efficient for large data")
    print("  - Enables coordination between processes")
    
    print("\n  Disadvantages/Challenges:")
    print("  - Requires careful synchronization (locks, etc.)")
    print("  - Can lead to performance bottlenecks")
    print("  - Increases code complexity")
    print("  - May cause deadlocks if not used carefully")
    
    print("\n  When to use:")
    print("  - When processes need to share large amounts of data")
    print("  - When processes need to communicate during execution")
    print("  - For progress tracking or status updates")
    
    print("\n  Alternatives to consider:")
    print("  - Return values: Let processes return their results")
    print("  - Input parameters: Pass all needed data to processes at start")
    print("  - Pipes/Queues: Use for message passing between processes")
    print("  - External storage: Use files, databases, etc., for sharing data")


# SECTION 6: Using Shared Memory with ProcessPoolExecutor
def demonstrate_process_pool_shared_memory():
    """Demonstrate how to use shared memory with ProcessPoolExecutor."""
    print("\nSECTION 6: Using Shared Memory with ProcessPoolExecutor")
    print("ProcessPoolExecutor doesn't directly support shared memory.")
    print("We need to initialize shared objects before creating the executor.")
    
    # Create shared counter
    counter = Value('i', 0)
    counter_lock = Lock()
    
    def increment_counter(item):
        """Increment the shared counter and process the item."""
        # Access the global shared counter
        nonlocal counter, counter_lock
        
        # Simulate processing
        result = f"Processed: {item}"
        
        # Increment the counter safely
        with counter_lock:
            counter.value += 1
        
        return result
    
    items = list(range(10))
    
    print(f"  Initial counter value: {counter.value}")
    
    # Use ProcessPoolExecutor to process items
    with ProcessPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(increment_counter, items))
    
    print(f"  Results: {results}")
    print(f"  Final counter value: {counter.value}")
    print("  The counter was correctly incremented across multiple processes")
    
    # NOTE: A better approach with ProcessPoolExecutor is often to 
    # avoid shared state and use return values instead


# SECTION 7: Best Practices and Patterns
def shared_memory_best_practices():
    """Present best practices for working with shared memory."""
    print("\nSECTION 7: Best Practices and Patterns")
    
    print("\n  Best Practices:")
    print("  1. Minimize shared state - use it only when necessary")
    print("  2. Always use locks when modifying shared data")
    print("  3. Keep critical sections (locked code) as small as possible")
    print("  4. Be aware of potential deadlocks")
    print("  5. Consider using Process Pools instead of managing processes directly")
    print("  6. Use higher-level primitives (Queue, Event) rather than raw locks when possible")
    
    print("\n  Common Patterns:")
    print("  1. Producer-Consumer pattern with shared Queue")
    print("  2. Worker Pool pattern with result aggregation")
    print("  3. Shared progress counter for monitoring")
    print("  4. Shared configuration for dynamic settings")


def main():
    """Main function running all demonstrations."""
    print("=== Working with Shared Resources ===")
    
    demonstrate_process_isolation()
    demonstrate_shared_value_and_array()
    demonstrate_race_conditions()
    demonstrate_managers()
    when_to_use_shared_resources()
    demonstrate_process_pool_shared_memory()
    shared_memory_best_practices()


if __name__ == "__main__":
    main()
    print("\nKey takeaways from this tutorial:")
    print("1. Processes don't share memory by default - explicit sharing is required")
    print("2. Value and Array provide simple shared memory objects")
    print("3. Always use locks when modifying shared data to prevent race conditions")
    print("4. Managers provide more flexible shared objects but with more overhead")
    print("5. Minimize shared state to keep parallel code simple and efficient") 