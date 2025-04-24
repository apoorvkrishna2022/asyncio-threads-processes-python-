#!/usr/bin/env python3
"""
07_advanced_techniques.py - Advanced patterns and best practices for process pools

This file covers:
- Process pool initializers
- Handling Process Lifecycle
- Resource management and cleanup
- Handling long-running processes
- Process Pool Patterns
- Context Manager implementation
- Custom Process Pool implementation
"""

import os
import time
import signal
import logging
import random
import functools
import concurrent.futures
import multiprocessing
from contextlib import contextmanager
from concurrent.futures import ProcessPoolExecutor


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(processName)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# SECTION 1: Process Pool Initializers
def demonstrate_initializers():
    """Demonstrate using initializers to set up worker processes."""
    print("\nSECTION 1: Process Pool Initializers")
    print("Initializers allow you to prepare each worker process before tasks run.")
    
    def initializer(logger_level):
        """
        Function that runs once in each worker process when it starts.
        This is useful for setting up resources that will be used by all tasks.
        """
        # Set up process-specific state
        worker_id = os.getpid()
        process_name = f"Worker-{worker_id}"
        
        # Configure the current process
        multiprocessing.current_process().name = process_name
        
        # Set up logging for this process
        logger = logging.getLogger()
        logger.setLevel(logger_level)
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        
        logger.info(f"Initialized process {process_name}")
    
    def worker_task(item):
        """Task that will be executed by a worker process."""
        logger.info(f"Processing item {item}")
        # Simulate work
        time.sleep(random.uniform(0.1, 0.5))
        return f"Processed {item} in process {multiprocessing.current_process().name}"
    
    print("\nCreating a process pool with initializer:")
    with ProcessPoolExecutor(
        max_workers=3,
        initializer=initializer,
        initargs=(logging.INFO,)
    ) as executor:
        items = ['A', 'B', 'C', 'D', 'E', 'F']
        results = list(executor.map(worker_task, items))
        
        for result in results:
            print(f"  {result}")
    
    print("\nKey benefits of initializers:")
    print("  - Set up process-specific resources")
    print("  - Configure logging for each process")
    print("  - Set up signal handlers")
    print("  - Load data that will be used by all tasks")
    print("  - Set up database connections or other shared resources")


# SECTION 2: Graceful Shutdown and Cleanup
def demonstrate_graceful_shutdown():
    """Demonstrate how to handle graceful shutdown of process pools."""
    print("\nSECTION 2: Graceful Shutdown and Cleanup")
    print("Proper resource management is important for process pools.")
    
    # Task that uses some resource
    def task_with_resource(item):
        """A task that simulates using a resource that needs cleanup."""
        pid = os.getpid()
        logger.info(f"Starting task with resource: {item}")
        try:
            # Simulate some work
            time.sleep(random.uniform(0.1, 0.5))
            return f"Processed {item} in process {pid}"
        except Exception as e:
            logger.error(f"Error processing {item}: {e}")
            raise
    
    # Create a context manager for a process pool with cleanup
    @contextmanager
    def managed_process_pool(max_workers=None):
        """A context manager that ensures proper cleanup of process pool."""
        pool = ProcessPoolExecutor(max_workers=max_workers)
        try:
            yield pool
        except Exception as e:
            logger.error(f"Error during pool execution: {e}")
            
            # Cancel all pending tasks
            for future in list(pool._pending_work_items.values()):
                future.cancel()
            
            # Shutdown the pool immediately without waiting
            pool.shutdown(wait=False)
            
            # Re-raise the exception
            raise
        finally:
            # Ensure the pool is shut down properly
            logger.info("Shutting down process pool")
            pool.shutdown(wait=True)
    
    print("\nUsing a managed process pool for proper cleanup:")
    try:
        with managed_process_pool(max_workers=3) as executor:
            items = ['A', 'B', 'C', 'D', 'E', 'F']
            futures = [executor.submit(task_with_resource, item) for item in items]
            
            # As each task completes, process its result
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    print(f"  {result}")
                except Exception as e:
                    print(f"  Task generated an exception: {e}")
    except Exception as e:
        print(f"  Pool execution failed: {e}")
    
    print("\nShutdown strategies:")
    print("  - pool.shutdown(wait=True): Wait for all tasks to complete (default)")
    print("  - pool.shutdown(wait=False): Stop accepting new tasks but return immediately")
    print("  - Cancel pending futures with future.cancel()")
    print("  - Use a timeout with future.result(timeout)")
    print("  - Use signal handlers to catch SIGINT, SIGTERM, etc.")


# SECTION 3: Managing Worker Process Lifecycles
def demonstrate_worker_lifecycle():
    """Demonstrate techniques for managing worker process lifecycles."""
    print("\nSECTION 3: Managing Worker Process Lifecycles")
    print("Controlling when worker processes are created and destroyed.")
    
    def worker_info():
        """Return information about the current worker process."""
        pid = os.getpid()
        name = multiprocessing.current_process().name
        return f"Worker {name} (PID: {pid})"
    
    # Strategy 1: Default behavior - processes are created as needed
    print("\n  Strategy 1: Default behavior (processes created as needed)")
    with ProcessPoolExecutor(max_workers=2) as executor:
        # Submit just one task to start
        future1 = executor.submit(worker_info)
        result1 = future1.result()
        print(f"  First task ran in: {result1}")
        
        # Submit another task, may use same or different worker
        future2 = executor.submit(worker_info)
        result2 = future2.result()
        print(f"  Second task ran in: {result2}")
    
    # Strategy 2: Eager initialization - start all workers up front
    print("\n  Strategy 2: Eager initialization (start all workers up front)")
    
    def init_worker():
        """Initialize worker and report."""
        pid = os.getpid()
        logger.info(f"Worker process {pid} initialized")
    
    def dummy_task():
        """Simple task that returns worker information."""
        time.sleep(0.1)  # Just a small delay
        return worker_info()
    
    with ProcessPoolExecutor(
        max_workers=3,
        initializer=init_worker
    ) as executor:
        # Force creation of all workers by submitting enough tasks
        warmup_futures = [executor.submit(dummy_task) for _ in range(3)]
        
        # Wait for all warmup tasks to complete
        for future in concurrent.futures.as_completed(warmup_futures):
            print(f"  Warmup task ran in: {future.result()}")
        
        print("  All workers are now initialized")
        
        # Use the warmed-up pool for real tasks
        real_future = executor.submit(worker_info)
        print(f"  Real task ran in: {real_future.result()}")
    
    # Strategy 3: Worker lifetime management
    print("\n  Strategy 3: Worker lifetime management (control worker lifetime)")
    print("  ProcessPoolExecutor doesn't directly support worker lifetime control.")
    print("  For advanced control, consider using a custom pool implementation.")


# SECTION 4: Advanced Task Patterns
def demonstrate_advanced_task_patterns():
    """Demonstrate advanced patterns for task submission and execution."""
    print("\nSECTION 4: Advanced Task Patterns")
    
    # Pattern 1: Task chaining
    print("\n  Pattern 1: Task Chaining")
    print("  Submit new tasks based on results of completed tasks.")
    
    def first_stage(item):
        """First stage of processing."""
        logger.info(f"First stage processing {item}")
        time.sleep(random.uniform(0.1, 0.5))
        return f"First:{item}"
    
    def second_stage(result):
        """Second stage of processing, depends on first stage."""
        logger.info(f"Second stage processing {result}")
        time.sleep(random.uniform(0.1, 0.5))
        return f"Second:{result}"
    
    def third_stage(result):
        """Third stage of processing, depends on second stage."""
        logger.info(f"Third stage processing {result}")
        time.sleep(random.uniform(0.1, 0.5))
        return f"Third:{result}"
    
    with ProcessPoolExecutor(max_workers=3) as executor:
        # Initial items
        items = ['A', 'B', 'C']
        
        # Submit first stage tasks
        first_futures = [executor.submit(first_stage, item) for item in items]
        
        # Chain second stage tasks as first stage completes
        second_futures = []
        for future in concurrent.futures.as_completed(first_futures):
            result = future.result()
            print(f"  First stage result: {result}")
            # Submit second stage task with this result
            second_future = executor.submit(second_stage, result)
            second_futures.append(second_future)
        
        # Chain third stage tasks as second stage completes
        third_futures = []
        for future in concurrent.futures.as_completed(second_futures):
            result = future.result()
            print(f"  Second stage result: {result}")
            # Submit third stage task with this result
            third_future = executor.submit(third_stage, result)
            third_futures.append(third_future)
        
        # Wait for all third stage tasks to complete
        for future in concurrent.futures.as_completed(third_futures):
            result = future.result()
            print(f"  Third stage result: {result}")
    
    # Pattern 2: Map-Reduce
    print("\n  Pattern 2: Map-Reduce")
    print("  Parallel processing followed by aggregation.")
    
    def map_function(item):
        """Map function that processes an individual item."""
        logger.info(f"Mapping {item}")
        time.sleep(random.uniform(0.1, 0.5))
        return len(item) * item  # Example: multiply by length
    
    def reduce_function(results):
        """Reduce function that aggregates results."""
        logger.info("Reducing results")
        # Example: concatenate all results
        return "".join(results)
    
    with ProcessPoolExecutor(max_workers=3) as executor:
        # Items to process
        items = ['A', 'BB', 'CCC', 'DDDD']
        
        # Map phase: process each item in parallel
        map_futures = [executor.submit(map_function, item) for item in items]
        map_results = [future.result() for future in concurrent.futures.as_completed(map_futures)]
        
        print(f"  Map results: {map_results}")
        
        # Reduce phase: aggregate the results
        # Note: The reduce phase could also be parallelized for larger datasets
        final_result = reduce_function(map_results)
        
        print(f"  Reduce result: {final_result}")
    
    # Pattern 3: Dynamic task generation
    print("\n  Pattern 3: Dynamic Task Generation")
    print("  Tasks can generate new tasks based on their results.")
    
    def process_and_maybe_split(item, depth=0, max_depth=2):
        """
        Process an item and potentially split it into sub-tasks.
        Returns a tuple of (result, sub_items).
        """
        logger.info(f"Processing {item} at depth {depth}")
        time.sleep(random.uniform(0.1, 0.3))
        
        result = f"Processed:{item}"
        
        # At max depth, don't generate more tasks
        if depth >= max_depth:
            return result, []
        
        # Randomly decide to split into more tasks
        if random.random() < 0.7:  # 70% chance to split
            # Generate 2 sub-items
            sub_items = [f"{item}-{i}" for i in range(2)]
            logger.info(f"Splitting {item} into {sub_items}")
            return result, sub_items
        else:
            return result, []
    
    with ProcessPoolExecutor(max_workers=3) as executor:
        # Initial items
        items = ['X', 'Y']
        
        # Keep track of all pending futures
        pending_futures = []
        all_results = []
        
        # Submit initial tasks
        for item in items:
            future = executor.submit(process_and_maybe_split, item)
            pending_futures.append(future)
        
        # Process tasks as they complete, potentially adding new ones
        while pending_futures:
            # Wait for a task to complete
            done, pending_futures = concurrent.futures.wait(
                pending_futures, 
                return_when=concurrent.futures.FIRST_COMPLETED
            )
            
            # Process completed tasks
            for future in done:
                result, sub_items = future.result()
                all_results.append(result)
                print(f"  Got result: {result}, generated {len(sub_items)} sub-tasks")
                
                # Submit new tasks for any sub-items
                for sub_item in sub_items:
                    # Pass the current depth + 1
                    depth = int(len(sub_item.split('-')))  # Estimate depth from item name
                    new_future = executor.submit(
                        process_and_maybe_split, sub_item, depth
                    )
                    pending_futures.append(new_future)
        
        print(f"  All results: {all_results}")
        print(f"  Total results: {len(all_results)}")


# SECTION 5: Custom Process Pool Implementation
def demonstrate_custom_pool():
    """Demonstrate a simple custom process pool implementation."""
    print("\nSECTION 5: Custom Process Pool Implementation")
    print("Sometimes you need more control than ProcessPoolExecutor provides.")
    
    class SimpleProcessPool:
        """
        A simple process pool implementation with more direct control
        over worker lifecycle and task distribution.
        """
        def __init__(self, num_workers=None, initializer=None, initargs=()):
            self.num_workers = num_workers or multiprocessing.cpu_count()
            self.initializer = initializer
            self.initargs = initargs
            self.task_queue = multiprocessing.Queue()
            self.result_queue = multiprocessing.Queue()
            self.workers = []
            self.running = False
        
        def worker_process(self, task_queue, result_queue):
            """The function each worker process runs."""
            # Run initializer if provided
            if self.initializer:
                self.initializer(*self.initargs)
            
            # Process tasks until receiving None (shutdown signal)
            while True:
                task = task_queue.get()
                if task is None:
                    break
                
                task_id, func, args, kwargs = task
                try:
                    result = func(*args, **kwargs)
                    result_queue.put((task_id, True, result))
                except Exception as e:
                    result_queue.put((task_id, False, e))
        
        def start(self):
            """Start the pool's worker processes."""
            if self.running:
                return
            
            # Create and start worker processes
            for i in range(self.num_workers):
                p = multiprocessing.Process(
                    target=self.worker_process,
                    args=(self.task_queue, self.result_queue)
                )
                p.daemon = True
                p.start()
                self.workers.append(p)
            
            self.running = True
            logger.info(f"Started process pool with {self.num_workers} workers")
        
        def submit(self, func, *args, **kwargs):
            """Submit a task to the pool."""
            if not self.running:
                self.start()
            
            # Generate a task ID
            task_id = random.randint(1, 10000000)
            
            # Put the task in the queue
            self.task_queue.put((task_id, func, args, kwargs))
            
            return task_id
        
        def get_result(self, timeout=None):
            """Get a result from the pool, returns (task_id, success, result)."""
            if not self.running:
                raise RuntimeError("Pool is not running")
            
            return self.result_queue.get(timeout=timeout)
        
        def shutdown(self, wait=True):
            """Shut down the pool."""
            if not self.running:
                return
            
            # Send shutdown signal to all workers
            for _ in range(self.num_workers):
                self.task_queue.put(None)
            
            # Wait for workers to terminate if requested
            if wait:
                for p in self.workers:
                    p.join()
            
            # Reset state
            self.workers = []
            self.running = False
            logger.info("Pool shut down")
    
    # Demonstration of the custom pool
    print("\nUsing a custom process pool:")
    
    def compute_factorial(n):
        """Compute factorial of n."""
        result = 1
        for i in range(2, n + 1):
            result *= i
        return result
    
    # Initialize the pool
    pool = SimpleProcessPool(num_workers=3)
    
    try:
        # Start the pool
        pool.start()
        
        # Submit some tasks
        task_ids = []
        for n in range(5, 10):
            task_id = pool.submit(compute_factorial, n)
            task_ids.append(task_id)
            print(f"  Submitted factorial({n}) as task {task_id}")
        
        # Get results as they complete
        for _ in range(len(task_ids)):
            task_id, success, result = pool.get_result()
            if success:
                print(f"  Task {task_id} succeeded: {result}")
            else:
                print(f"  Task {task_id} failed: {result}")
    finally:
        # Ensure the pool is shut down
        pool.shutdown()
    
    print("\nBenefits of a custom pool implementation:")
    print("  - More control over worker lifecycle")
    print("  - Custom task distribution strategies")
    print("  - Direct access to worker processes")
    print("  - Custom resource management")
    print("  - Can implement advanced features like worker reassignment or restart")


def main():
    """Main function running all demonstrations."""
    print("=== Advanced Process Pool Techniques ===")
    
    demonstrate_initializers()
    demonstrate_graceful_shutdown()
    demonstrate_worker_lifecycle()
    demonstrate_advanced_task_patterns()
    demonstrate_custom_pool()


if __name__ == "__main__":
    main()
    print("\nKey takeaways from this tutorial:")
    print("1. Use initializers to set up resources in worker processes")
    print("2. Implement proper error handling and graceful shutdown")
    print("3. Consider worker process lifecycle for long-running applications")
    print("4. Advanced patterns like task chaining and map-reduce can solve complex problems")
    print("5. For maximum control, consider implementing a custom process pool") 