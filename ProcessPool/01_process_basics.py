#!/usr/bin/env python3
"""
01_process_basics.py - Introduction to processes in Python

This file covers the basics of processes in Python:
- What a process is
- How to create a process
- How processes differ from threads
- Basic process operations
"""

import os
import time
import multiprocessing


def print_info(title):
    """Print process information."""
    print(f"=== {title} ===")
    print(f"Process ID: {os.getpid()}")
    print(f"Parent Process ID: {os.getppid()}")
    print()


def basic_function():
    """A simple function that runs in a separate process."""
    print_info("Child Process")
    print(f"Hello from child process - sleeping for 2 seconds...")
    time.sleep(2)
    print("Child process finished.")


def main():
    """Main function demonstrating process creation and basic operations."""
    print_info("Main Process")
    
    # SECTION 1: Creating a simple process
    print("SECTION 1: Creating a simple process")
    
    # Create a process object
    process = multiprocessing.Process(target=basic_function)
    
    # Start the process
    print("Starting a new process...")
    process.start()
    
    # Wait for the process to finish
    print("Waiting for the process to finish...")
    process.join()
    
    print("Process has finished execution.")
    print("\n" + "-" * 50 + "\n")
    
    # SECTION 2: Process with arguments
    print("SECTION 2: Process with arguments")
    
    def function_with_args(name, number):
        """Function that accepts arguments."""
        print_info(f"Process with arguments: {name}, {number}")
        print(f"Arguments received: name={name}, number={number}")
    
    # Create a process with arguments
    process_with_args = multiprocessing.Process(
        target=function_with_args,
        args=("Process-A", 42)
    )
    
    process_with_args.start()
    process_with_args.join()
    print("\n" + "-" * 50 + "\n")
    
    # SECTION 3: Multiple processes
    print("SECTION 3: Multiple processes")
    
    def worker(worker_id):
        """Worker function for multiple processes."""
        print(f"Worker {worker_id} starting (PID: {os.getpid()})")
        time.sleep(1)  # Simulate work
        print(f"Worker {worker_id} finished")
    
    # Create multiple processes
    processes = []
    for i in range(3):
        p = multiprocessing.Process(target=worker, args=(i,))
        processes.append(p)
        p.start()
    
    # Wait for all processes to complete
    for p in processes:
        p.join()
    
    print("All workers have finished.")
    print("\n" + "-" * 50 + "\n")
    
    # SECTION 4: Process properties and methods
    print("SECTION 4: Process properties and methods")
    
    def long_running_task():
        """A task that runs for a while."""
        print(f"Long task started (PID: {os.getpid()})")
        time.sleep(10)  # This will take a while
        print("Long task finished")
    
    # Create and start the process
    long_process = multiprocessing.Process(target=long_running_task)
    long_process.start()
    
    # Check if the process is alive
    print(f"Is process alive? {long_process.is_alive()}")
    
    # Get the process ID
    print(f"Process ID: {long_process.pid}")
    
    # Demonstrate process termination
    print("Terminating the process early...")
    long_process.terminate()
    
    # Give it a moment to terminate
    time.sleep(0.5)
    
    # Check if it's still alive
    print(f"Is process still alive? {long_process.is_alive()}")
    
    # Clean up
    long_process.join()
    print("Process terminated and cleaned up.")


if __name__ == "__main__":
    # This is important for multiprocessing to work correctly on all platforms
    main()
    print("\nKey takeaways from this tutorial:")
    print("1. Processes run independently with their own memory space")
    print("2. Each process has a unique Process ID (PID)")
    print("3. The multiprocessing module helps create and manage processes")
    print("4. Processes can be started, joined, and terminated")
    print("5. We can pass arguments to processes") 