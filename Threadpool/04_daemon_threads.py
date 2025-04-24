"""
# Python Threading Tutorial - Daemon Threads
# =======================================
#
# This file demonstrates daemon threads that terminate when the main program exits.
"""

import threading
import time

def daemon_thread_example():
    """
    Demonstrate daemon threads that automatically terminate when the main program exits.
    """
    print("\n=== Daemon Threads ===")
    
    def background_task():
        """This task runs in the background and loops indefinitely."""
        i = 0
        while True:
            i += 1
            print(f"Background task: iteration {i}")
            time.sleep(1)
    
    # Create a daemon thread
    # Daemon threads automatically terminate when the main program exits
    daemon = threading.Thread(target=background_task, daemon=True)
    daemon.start()
    
    print("Main thread: daemon thread started")
    print("Main thread: sleeping for 3 seconds")
    time.sleep(3)  # Let the daemon run for a bit
    print("Main thread: exiting (daemon thread will be terminated)")
    # Notice we don't join() the daemon thread - it will terminate when the program exits

if __name__ == "__main__":
    daemon_thread_example() 