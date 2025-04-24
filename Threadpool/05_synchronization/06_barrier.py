"""
# Python Threading Tutorial - Barrier
# ================================
#
# This file demonstrates using Barrier for thread synchronization.
"""

import threading
import time
import random

def barrier_example():
    """
    Demonstrate using Barrier for thread synchronization.
    Barriers cause threads to wait until a specific number of threads have reached the barrier.
    """
    print("\n=== Thread Synchronization: Barrier ===")
    
    # Number of threads
    n = 4
    
    # Create a barrier that waits for 4 threads
    barrier = threading.Barrier(n)
    
    def worker(name):
        """Worker that waits at the barrier."""
        print(f"Worker {name}: starting")
        
        # Simulate some initial work
        time.sleep(random.uniform(0.5, 2.0))
        print(f"Worker {name}: reached the barrier")
        
        # Wait at the barrier
        barrier.wait()
        
        # After the barrier, all threads proceed simultaneously
        print(f"Worker {name}: passed the barrier")
        
        # Simulate more work
        time.sleep(random.uniform(0.5, 1.0))
        print(f"Worker {name}: finished")
    
    # Create and start threads
    threads = []
    for i in range(n):
        thread = threading.Thread(target=worker, args=(i,))
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    # Example with barrier action
    print("\nBarrier with action:")
    
    # A barrier can execute an action when all threads reach it
    def barrier_action():
        print("Barrier action: All threads have reached the barrier!")
    
    action_barrier = threading.Barrier(3, action=barrier_action)
    
    def action_worker(name):
        print(f"Action worker {name}: working")
        time.sleep(random.uniform(0.5, 1.5))
        print(f"Action worker {name}: waiting at barrier")
        action_barrier.wait()
        print(f"Action worker {name}: continuing after barrier")
    
    # Create and start threads
    action_threads = []
    for i in range(3):
        thread = threading.Thread(target=action_worker, args=(i,))
        action_threads.append(thread)
        thread.start()
    
    # Wait for all threads
    for thread in action_threads:
        thread.join()
    
    # Example with barrier abort
    print("\nBarrier abort example:")
    
    abort_barrier = threading.Barrier(3)
    
    def abort_worker(name, should_abort=False):
        try:
            print(f"Abort worker {name}: working")
            time.sleep(random.uniform(0.2, 1.0))
            
            if should_abort:
                print(f"Abort worker {name}: aborting the barrier")
                abort_barrier.abort()
                return
                
            print(f"Abort worker {name}: waiting at barrier")
            abort_barrier.wait()
            print(f"Abort worker {name}: passed barrier (should not happen if aborted)")
            
        except threading.BrokenBarrierError:
            print(f"Abort worker {name}: caught BrokenBarrierError - barrier was aborted")
    
    # Create and start threads, one will abort the barrier
    abort_threads = []
    for i in range(3):
        should_abort = (i == 1)  # The second thread will abort
        thread = threading.Thread(target=abort_worker, args=(i, should_abort))
        abort_threads.append(thread)
        thread.start()
    
    # Wait for all threads
    for thread in abort_threads:
        thread.join()
    
    print("\nUse cases for Barrier:")
    print("1. Synchronizing threads at specific points in an algorithm")
    print("2. Ensuring all threads are ready before proceeding")
    print("3. Implementing phased computations where all threads must complete a phase")
    print("4. Coordinating parallel operations that require synchronization points")

if __name__ == "__main__":
    barrier_example() 