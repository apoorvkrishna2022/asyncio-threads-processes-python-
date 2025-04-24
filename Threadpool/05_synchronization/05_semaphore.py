"""
# Python Threading Tutorial - Semaphore
# ==================================
#
# This file demonstrates using Semaphores for thread synchronization.
"""

import threading
import time
import random

def semaphore_example():
    """
    Demonstrate using Semaphores.
    Semaphores limit the number of threads that can access a resource.
    """
    print("\n=== Thread Synchronization: Semaphore ===")
    
    # Create a semaphore that allows 3 concurrent accesses
    semaphore = threading.Semaphore(3)
    
    def worker(name):
        """A worker that acquires the semaphore before accessing a resource."""
        print(f"Worker {name}: waiting to access the resource")
        
        # Try to acquire the semaphore
        with semaphore:
            print(f"Worker {name}: resource acquired")
            time.sleep(2)  # Simulate using the resource
            print(f"Worker {name}: resource released")
    
    # Create and start 5 worker threads
    threads = []
    for i in range(5):
        thread = threading.Thread(target=worker, args=(i,))
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    print("\nUsing BoundedSemaphore (safer, raises error if released too many times):")
    bounded_semaphore = threading.BoundedSemaphore(2)
    
    def bounded_worker(name):
        with bounded_semaphore:
            print(f"Bounded worker {name} acquired semaphore")
            time.sleep(1)
        print(f"Bounded worker {name} released semaphore")
    
    # Create and start 3 bounded worker threads
    bounded_threads = []
    for i in range(3):
        thread = threading.Thread(target=bounded_worker, args=(i,))
        bounded_threads.append(thread)
        thread.start()
    
    # Wait for completion
    for thread in bounded_threads:
        thread.join()
        
    # Real-world example: Connection pool
    print("\nReal-world example: Connection Pool")
    
    class ConnectionPool:
        """A simple connection pool that limits the number of concurrent connections."""
        
        def __init__(self, max_connections):
            self.semaphore = threading.BoundedSemaphore(max_connections)
            self.connections = []
            self.lock = threading.Lock()
        
        def get_connection(self):
            """Get a connection from the pool (blocks if none available)."""
            self.semaphore.acquire()
            with self.lock:
                # Simulate creating a new connection
                conn = f"Connection-{random.randint(1000, 9999)}"
                self.connections.append(conn)
                print(f"Created {conn}")
                return conn
        
        def release_connection(self, conn):
            """Return a connection to the pool."""
            with self.lock:
                if conn in self.connections:
                    self.connections.remove(conn)
                    print(f"Released {conn}")
                    self.semaphore.release()
                else:
                    print(f"Error: {conn} not in pool")
    
    # Create a connection pool with max 3 connections
    pool = ConnectionPool(3)
    
    def connection_user(user_id):
        """Simulate a user that gets a connection, uses it, then releases it."""
        print(f"User {user_id}: Requesting connection")
        conn = pool.get_connection()
        print(f"User {user_id}: Got {conn}")
        
        # Simulate using the connection
        time.sleep(random.uniform(1, 3))
        
        # Release the connection
        print(f"User {user_id}: Finished with {conn}")
        pool.release_connection(conn)
    
    # Create and start user threads
    user_threads = []
    for i in range(5):
        thread = threading.Thread(target=connection_user, args=(i,))
        user_threads.append(thread)
        thread.start()
    
    # Wait for all users to finish
    for thread in user_threads:
        thread.join()

if __name__ == "__main__":
    semaphore_example() 