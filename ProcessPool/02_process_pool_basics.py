#!/usr/bin/env python3
"""
02_process_pool_basics.py - Introduction to ProcessPoolExecutor

This file covers:
- What a process pool is and why it's useful
- How to create a ProcessPoolExecutor
- Basic usage patterns
- Performance comparison with sequential execution
"""

import os
import time
import concurrent.futures


def cpu_bound_task(number):
    """
    A CPU-intensive function that calculates the sum of squares up to a number.
    This simulates a computationally expensive task.
    """
    result = 0
    for i in range(number):
        result += i * i
    return result


def show_process_info():
    """Show the current process ID."""
    return f"Process ID: {os.getpid()}"


def main():
    """Main function demonstrating process pool basics."""
    print("=== Process Pool Basics ===")
    
    # SECTION 1: Introduction to Process Pools
    print("\nSECTION 1: What is a Process Pool?")
    print("A process pool maintains a pool of worker processes that are ready")
    print("to execute tasks. This avoids the overhead of creating new processes")
    print("for each task, which is especially important for short-running tasks.")
    print("\nThe main advantages are:")
    print("1. Reuse of processes (avoid process creation overhead)")
    print("2. Limiting concurrent processes (prevent system overload)")
    print("3. Managing a queue of work when there are more tasks than processes")
    print("4. Simplified interface compared to using the multiprocessing module directly")
    
    # SECTION 2: Creating a ProcessPoolExecutor
    print("\nSECTION 2: Creating a ProcessPoolExecutor")
    
    # Create a ProcessPoolExecutor with the default number of processes
    # (which is usually the number of CPUs in the system)
    print("\nCreating a process pool with default number of workers...")
    with concurrent.futures.ProcessPoolExecutor() as executor:
        # Get process IDs of workers in the pool
        futures = [executor.submit(show_process_info) for _ in range(5)]
        worker_pids = [future.result() for future in futures]
        
        print(f"Main process ID: {os.getpid()}")
        print(f"Worker processes: {set(worker_pids)}")
        
        # Notice that there might be fewer unique PIDs than tasks,
        # as the processes are reused
    
    # Create a ProcessPoolExecutor with a specific number of processes
    print("\nCreating a process pool with 2 workers...")
    with concurrent.futures.ProcessPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(show_process_info) for _ in range(5)]
        worker_pids = [future.result() for future in futures]
        
        print(f"Main process ID: {os.getpid()}")
        print(f"Worker processes: {set(worker_pids)}")
        print("Note: Even though we ran 5 tasks, only 2 unique process IDs are used")
    
    # SECTION 3: Simple example - calculate squares
    print("\nSECTION 3: Simple Example - Calculate Squares")
    
    numbers = [10**7, 10**7, 10**7, 10**7]
    
    # Sequential execution (for comparison)
    print("\nExecuting tasks sequentially...")
    start_time = time.time()
    sequential_results = [cpu_bound_task(num) for num in numbers]
    sequential_time = time.time() - start_time
    print(f"Sequential execution time: {sequential_time:.2f} seconds")
    
    # Parallel execution with ProcessPoolExecutor
    print("\nExecuting tasks in parallel with ProcessPoolExecutor...")
    start_time = time.time()
    with concurrent.futures.ProcessPoolExecutor() as executor:
        parallel_results = list(executor.map(cpu_bound_task, numbers))
    parallel_time = time.time() - start_time
    print(f"Parallel execution time: {parallel_time:.2f} seconds")
    
    # Compare results and performance
    print(f"\nResults match: {sequential_results == parallel_results}")
    if sequential_time > 0:  # Avoid division by zero
        print(f"Speedup: {sequential_time / parallel_time:.2f}x faster with process pool")
    
    # SECTION 4: Context Manager vs. Manual Resource Management
    print("\nSECTION 4: Context Manager vs. Manual Resource Management")
    
    print("\nMethod 1: Using context manager (recommended)")
    print("with concurrent.futures.ProcessPoolExecutor() as executor:")
    print("    # code using executor")
    print("# Resources automatically cleaned up when block exits")
    
    print("\nMethod 2: Manual resource management")
    print("executor = concurrent.futures.ProcessPoolExecutor()")
    print("try:")
    print("    # code using executor")
    print("finally:")
    print("    executor.shutdown()")
    
    # SECTION 5: Creating a pool with initialization
    print("\nSECTION 5: Process Pool with Initialization")
    
    def init_worker():
        """Function to initialize each worker process."""
        print(f"Initializing worker process {os.getpid()}")
    
    def worker_task(task_id):
        """Task that will be executed by a worker process."""
        print(f"Task {task_id} running in process {os.getpid()}")
        return task_id * 2
    
    print("\nCreating a process pool with an initializer function...")
    with concurrent.futures.ProcessPoolExecutor(
        initializer=init_worker
    ) as executor:
        futures = [executor.submit(worker_task, i) for i in range(3)]
        results = [future.result() for future in futures]
        print(f"Results: {results}")


if __name__ == "__main__":
    main()
    print("\nKey takeaways from this tutorial:")
    print("1. ProcessPoolExecutor makes it easy to parallelize CPU-bound tasks")
    print("2. A process pool reuses worker processes to reduce overhead")
    print("3. The number of workers defaults to the number of CPUs in your system")
    print("4. Use the 'with' statement for proper resource management")
    print("5. Process pools can significantly speed up CPU-bound tasks") 