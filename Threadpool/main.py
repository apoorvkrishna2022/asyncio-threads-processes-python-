"""
# Python Threading and ThreadPool Tutorial
# ========================================
#
# A comprehensive tutorial covering threading in Python from basic concepts to advanced usage.
# This main file provides an overview and can run individual examples.
"""

import os
import sys
import importlib.util

def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)

def list_tutorials():
    """List all available tutorials."""
    print_header("Available Tutorials")
    
    tutorials = [
        ("01_introduction.py", "Introduction to threading concepts"),
        ("02_basic_threading.py", "Basic thread creation and execution"),
        ("03_thread_subclassing.py", "Creating custom thread classes"),
        ("04_daemon_threads.py", "Working with daemon threads"),
        ("05_synchronization/01_locks.py", "Thread synchronization with locks"),
        ("05_synchronization/02_rlock.py", "Using reentrant locks (RLock)"),
        ("05_synchronization/03_event.py", "Using Event for thread signaling"),
        ("05_synchronization/04_condition.py", "Using Condition for complex synchronization"),
        ("05_synchronization/05_semaphore.py", "Limiting concurrent access with Semaphores"),
        ("05_synchronization/06_barrier.py", "Synchronizing multiple threads with Barrier"),
        ("06_thread_safe_queue.py", "Thread-safe data exchange with Queue"),
        ("07_thread_local.py", "Using thread-local storage"),
        ("08_timer_threads.py", "Executing functions after a delay with Timer"),
        ("09_thread_pool_executor.py", "Using ThreadPoolExecutor"),
        ("10_custom_thread_pool.py", "Implementing a custom thread pool"),
    ]
    
    print("This tutorial includes the following topics:\n")
    
    for i, (file, desc) in enumerate(tutorials, 1):
        print(f"{i:2d}. {desc} [{file}]")
    
    return tutorials

def run_tutorial(tutorial_path):
    """Run a specific tutorial by file path."""
    # Get the absolute path to the module file
    if os.path.sep in tutorial_path:
        dir_path = os.path.join('Threadpool', os.path.dirname(tutorial_path))
        file_name = os.path.basename(tutorial_path)
        full_path = os.path.join(dir_path, file_name)
    else:
        full_path = os.path.join('Threadpool', tutorial_path)
    
    # Ensure the file exists
    if not os.path.exists(full_path):
        print(f"Error: File {full_path} not found")
        return
    
    try:
        # Load the module from file path
        module_name = tutorial_path.replace(os.path.sep, '_').replace('.py', '')
        spec = importlib.util.spec_from_file_location(module_name, full_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Mapping of file names to the functions they contain
        function_map = {
            '01_introduction.py': 'introduction_to_threading',
            '02_basic_threading.py': 'basic_threading_example',
            '03_thread_subclassing.py': 'thread_subclassing_example', 
            '04_daemon_threads.py': 'daemon_thread_example',
            '05_synchronization/01_locks.py': 'lock_example',
            '05_synchronization/02_rlock.py': 'rlock_example',
            '05_synchronization/03_event.py': 'event_example',
            '05_synchronization/04_condition.py': 'condition_example',
            '05_synchronization/05_semaphore.py': 'semaphore_example',
            '05_synchronization/06_barrier.py': 'barrier_example',
            '06_thread_safe_queue.py': 'queue_example',
            '07_thread_local.py': 'thread_local_example',
            '08_timer_threads.py': 'timer_example',
            '09_thread_pool_executor.py': 'thread_pool_example',
            '10_custom_thread_pool.py': 'custom_thread_pool',
        }
        
        # Get the appropriate function to call
        if tutorial_path in function_map and hasattr(module, function_map[tutorial_path]):
            func_name = function_map[tutorial_path]
            func = getattr(module, func_name)
            
            # Run the function
            print_header(f"Running: {tutorial_path} ({func_name})")
            func()
        else:
            print(f"Could not find suitable function in {tutorial_path}")
    
    except Exception as e:
        print(f"Error running {tutorial_path}: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main function that runs the tutorial."""
    print_header("Python Threading and ThreadPool Tutorial")
    
    print("""
This tutorial covers threading concepts in Python, including:
- Basic thread creation and management
- Thread synchronization primitives
- Thread-safe data structures
- ThreadPoolExecutor and custom thread pools
- Thread-local storage
- Timer threads
- And more!

Each file focuses on a specific concept and can be run individually.
""")
    
    tutorials = list_tutorials()
    
    while True:
        print("\nOptions:")
        print("1. Run a specific tutorial")
        print("2. Run all tutorials")
        print("0. Exit")
        
        choice = input("\nEnter your choice (0-2): ").strip()
        
        if choice == '0':
            print("\nThank you for using this tutorial!")
            break
        elif choice == '1':
            num = input(f"Enter tutorial number (1-{len(tutorials)}): ").strip()
            try:
                num = int(num)
                if 1 <= num <= len(tutorials):
                    run_tutorial(tutorials[num-1][0])
                else:
                    print(f"Please enter a number between 1 and {len(tutorials)}")
            except ValueError:
                print("Please enter a valid number")
        elif choice == '2':
            print_header("Running All Tutorials")
            for tutorial, _ in tutorials:
                run_tutorial(tutorial)
            print_header("All Tutorials Completed")
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
