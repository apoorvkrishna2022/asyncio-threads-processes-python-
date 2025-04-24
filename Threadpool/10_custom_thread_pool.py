"""
# Python Threading Tutorial - Custom Thread Pool
# ==========================================
#
# This file demonstrates how to implement a custom thread pool.
"""

import threading
import queue
import time
import random
from typing import List, Callable, Any, Dict

def custom_thread_pool():
    """
    Implement a simple thread pool from scratch.
    This helps understand how thread pools work internally.
    """
    print("\n=== Custom Thread Pool Implementation ===")
    
    class SimpleThreadPool:
        """A simple thread pool implementation."""
        
        def __init__(self, num_workers: int):
            """Initialize the thread pool with a number of worker threads."""
            self.task_queue = queue.Queue()
            self.workers = []
            self.running = True
            
            # Create and start worker threads
            for i in range(num_workers):
                worker = threading.Thread(target=self._worker_thread, args=(i,))
                worker.daemon = True  # Make worker threads daemon threads
                worker.start()
                self.workers.append(worker)
            
            print(f"Thread pool initialized with {num_workers} workers")
        
        def _worker_thread(self, worker_id: int):
            """Worker thread that processes tasks from the queue."""
            print(f"Worker {worker_id}: started")
            
            while self.running:
                try:
                    # Try to get a task from the queue
                    task, args, kwargs, result_slot = self.task_queue.get(timeout=0.5)
                    
                    # Execute the task
                    try:
                        result = task(*args, **kwargs)
                        result_slot['result'] = result
                        result_slot['completed'] = True
                    except Exception as e:
                        result_slot['exception'] = e
                        result_slot['completed'] = True
                    
                    # Mark the task as done
                    self.task_queue.task_done()
                
                except queue.Empty:
                    # No tasks available, continue the loop
                    continue
            
            print(f"Worker {worker_id}: shutting down")
        
        def submit(self, task_func: Callable, *args, **kwargs) -> Dict:
            """
            Submit a task to the thread pool.
            
            Returns a result slot dictionary that will be updated when the task completes.
            """
            result_slot = {
                'completed': False,
                'result': None,
                'exception': None
            }
            
            # Put the task in the queue
            self.task_queue.put((task_func, args, kwargs, result_slot))
            
            return result_slot
        
        def submit_all(self, task_func: Callable, args_list: List[tuple]) -> List[Dict]:
            """
            Submit multiple tasks to the thread pool.
            
            Args:
                task_func: The function to execute
                args_list: A list of argument tuples, one per task
                
            Returns a list of result slots that will be updated when tasks complete.
            """
            result_slots = []
            
            for args in args_list:
                result_slot = self.submit(task_func, *args)
                result_slots.append(result_slot)
            
            return result_slots
        
        def wait_for_all(self):
            """Wait for all submitted tasks to complete."""
            self.task_queue.join()
        
        def shutdown(self):
            """Shutdown the thread pool."""
            print("Shutting down thread pool")
            self.running = False
            
            # Wait for all workers to exit
            for worker in self.workers:
                worker.join()
            
            print("Thread pool shutdown complete")
        
        def map(self, func: Callable, iterable: List):
            """
            Apply a function to every item of an iterable.
            
            Args:
                func: The function to apply
                iterable: The items to process
                
            Returns a list of results in the same order as the input.
            """
            # Submit all tasks and get result slots
            result_slots = [self.submit(func, item) for item in iterable]
            
            # Wait for all tasks to complete
            self.wait_for_all()
            
            # Collect results in the correct order
            results = []
            for slot in result_slots:
                if slot['exception'] is not None:
                    raise slot['exception']
                results.append(slot['result'])
            
            return results
    
    # Example usage of our custom thread pool
    def example_task(name, duration):
        """An example task that sleeps for a while then returns a result."""
        thread_name = threading.current_thread().name
        print(f"Task {name} running in {thread_name} for {duration} seconds")
        time.sleep(duration)
        return f"Result from task {name}"
    
    # Create a thread pool with 3 workers
    pool = SimpleThreadPool(3)
    
    # Submit individual tasks
    print("Submitting individual tasks:")
    result1 = pool.submit(example_task, "A", 2)
    result2 = pool.submit(example_task, "B", 1)
    result3 = pool.submit(example_task, "C", 3)
    
    # Submit multiple tasks at once
    print("\nSubmitting multiple tasks:")
    task_args = [
        ("D", 1.5),
        ("E", 0.5),
        ("F", 2.5)
    ]
    batch_results = pool.submit_all(example_task, task_args)
    
    # Wait for all tasks to complete
    print("\nWaiting for all tasks to complete")
    pool.wait_for_all()
    
    # Print results
    print("\nResults from individual tasks:")
    print(f"Task A: {result1['result']}")
    print(f"Task B: {result2['result']}")
    print(f"Task C: {result3['result']}")
    
    print("\nResults from batch tasks:")
    for i, result in enumerate(batch_results):
        print(f"Task {chr(68 + i)}: {result['result']}")
    
    # Demonstrate map functionality
    print("\nDemonstrating map functionality:")
    
    def square(x):
        time.sleep(random.uniform(0.1, 0.5))
        return x * x
    
    numbers = [1, 2, 3, 4, 5]
    squares = pool.map(square, numbers)
    print(f"Squares: {squares}")
    
    # Demonstrate error handling
    print("\nDemonstrating error handling:")
    
    def error_task(id):
        """A task that sometimes raises an exception."""
        time.sleep(random.uniform(0.1, 0.3))
        
        if id % 2 == 0:
            raise ValueError(f"Error in task {id}")
        
        return f"Success from task {id}"
    
    # Submit some tasks that will raise exceptions
    error_results = []
    for i in range(4):
        error_results.append(pool.submit(error_task, i))
    
    # Wait for all tasks to complete
    pool.wait_for_all()
    
    # Check results
    for i, result in enumerate(error_results):
        if result['exception'] is not None:
            print(f"Task {i} failed: {result['exception']}")
        else:
            print(f"Task {i} succeeded: {result['result']}")
    
    # Shutdown the thread pool
    pool.shutdown()
    
    print("\nHow our thread pool implementation works:")
    print("1. Creates a pool of worker threads and a task queue")
    print("2. Workers continually pull tasks from the queue")
    print("3. Tasks can be submitted individually or in batches")
    print("4. Results are stored in result dictionaries")
    print("5. Exceptions are caught and stored in the result dictionaries")
    print("6. Thread pool can be shut down, stopping all workers")
    
    print("\nThis is a simplified example. A full implementation would have:")
    print("- Better exception handling")
    print("- Future-like objects for tracking results")
    print("- Cancellation support")
    print("- Thread lifecycle management")
    print("- More sophisticated queue management")

if __name__ == "__main__":
    custom_thread_pool() 