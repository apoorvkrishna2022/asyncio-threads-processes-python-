"""
# Python Threading Tutorial - Thread Local Data
# =========================================
#
# This file demonstrates using thread-local storage.
"""

import threading
import time
import random

def thread_local_example():
    """
    Demonstrate using thread local storage.
    Thread local data is data that is specific to each thread.
    """
    print("\n=== Thread Local Data ===")
    
    # Create a thread local object
    # Each thread will have its own 'value' attribute
    thread_data = threading.local()
    
    def worker(name):
        """Worker function that uses thread-local storage."""
        # Set a thread-local value (only visible to this thread)
        thread_data.value = name
        
        # Simulate some work
        time.sleep(random.uniform(0.1, 0.5))
        
        # Access the thread-local value
        print(f"Worker {name}: thread_data.value = {thread_data.value}")
        
        # Each thread can have multiple thread-local attributes
        thread_data.count = random.randint(1, 10)
        print(f"Worker {name}: thread_data.count = {thread_data.count}")
    
    # Create and start threads
    threads = []
    for i in range(3):
        thread = threading.Thread(target=worker, args=(f"Thread-{i}",))
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    print("Note: Each thread sees its own value in thread_data.value")
    
    # Real-world example: Database connections
    print("\n=== Real-world example: Database connections ===")
    
    # Mock database connection class
    class DatabaseConnection:
        def __init__(self, thread_name):
            self.thread_name = thread_name
            self.connection_id = random.randint(1000, 9999)
            print(f"Creating connection {self.connection_id} for {thread_name}")
        
        def query(self, query_string):
            return f"Result of '{query_string}' from connection {self.connection_id}"
        
        def close(self):
            print(f"Closing connection {self.connection_id} for {self.thread_name}")
    
    # Connection manager using thread-local storage
    class ConnectionManager:
        def __init__(self):
            self.local = threading.local()
        
        def get_connection(self):
            # Check if this thread already has a connection
            if not hasattr(self.local, 'connection'):
                # Create a new connection for this thread
                thread_name = threading.current_thread().name
                self.local.connection = DatabaseConnection(thread_name)
            
            return self.local.connection
        
        def close_all(self):
            # This only closes the connection for the current thread
            # In a real implementation, you would need a way to track all connections
            if hasattr(self.local, 'connection'):
                self.local.connection.close()
                del self.local.connection
    
    # Create a connection manager
    manager = ConnectionManager()
    
    def database_worker(worker_id):
        """Simulates a worker that uses a database connection."""
        thread_name = threading.current_thread().name
        print(f"Worker {worker_id} ({thread_name}) starting")
        
        # Get a connection (thread-local)
        conn = manager.get_connection()
        
        # Simulate multiple queries using the same connection
        for i in range(2):
            query = f"SELECT * FROM table{i} WHERE id = {worker_id}"
            result = conn.query(query)
            print(f"Worker {worker_id}: {result}")
            time.sleep(random.uniform(0.1, 0.3))
        
        # Connection automatically stays with the thread
        # If we get the connection again, it's the same one
        conn2 = manager.get_connection()
        
        # Verify it's the same connection
        if conn.connection_id == conn2.connection_id:
            print(f"Worker {worker_id}: Verified same connection is reused")
        
        # Clean up
        manager.close_all()
    
    # Create and start database worker threads
    db_threads = []
    for i in range(3):
        thread = threading.Thread(target=database_worker, args=(i,), name=f"DBWorker-{i}")
        db_threads.append(thread)
        thread.start()
    
    # Wait for all database workers to complete
    for thread in db_threads:
        thread.join()
    
    print("\nWhen to use thread-local storage:")
    print("1. Storing per-thread database connections")
    print("2. Per-thread context or state information")
    print("3. When you need thread-specific data without explicitly passing it between functions")
    print("4. User session data in web applications (each request in its own thread)")

if __name__ == "__main__":
    thread_local_example() 