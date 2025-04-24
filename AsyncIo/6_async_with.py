"""
# Async Context Managers
# ====================
#
# This tutorial explores async context managers in Python, using the 'async with' statement.
# Learn how to create and use asynchronous context managers for resource management.
"""

import asyncio
import contextlib
import time


# Introduction to Async Context Managers
# -----------------------------------

def intro_to_context_managers():
    print("== Introduction to Async Context Managers ==")
    print("Async context managers:")
    print("1. Allow resource setup and cleanup in async code")
    print("2. Use 'async with' statement instead of 'with'")
    print("3. Implement __aenter__ and __aexit__ methods")
    print("4. Can be created using the 'asynccontextmanager' decorator")
    print("5. Help manage async resources like database connections and file handles")


# Using Existing Async Context Managers
# ----------------------------------

async def using_existing_context_managers():
    print("\n== Using Existing Async Context Managers ==")
    
    # Example: Using async with for a timer
    print("Example 1: Simple async timer")
    async with AsyncTimer("Task"):
        await asyncio.sleep(0.5)
        print("Doing some work...")
    
    # Example: Nested async context managers
    print("\nExample 2: Nested async context managers")
    async with AsyncTimer("Outer"):
        print("In outer context")
        async with AsyncTimer("Inner"):
            await asyncio.sleep(0.3)
            print("In inner context")
        print("Back to outer context")


# Creating a Simple Async Context Manager
# ------------------------------------
# Method 1: Using a class with __aenter__ and __aexit__

class AsyncTimer:
    """A simple async context manager that measures execution time"""
    
    def __init__(self, name):
        self.name = name
    
    async def __aenter__(self):
        """Called when entering 'async with' context"""
        self.start = time.time()
        print(f"[{self.name}] Starting timer")
        # Simulate async initialization
        await asyncio.sleep(0.1)
        return self  # Return the context manager itself
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Called when exiting 'async with' context"""
        elapsed = time.time() - self.start
        print(f"[{self.name}] Timer completed in {elapsed:.4f} seconds")
        # Simulate async cleanup
        await asyncio.sleep(0.1)
        
        # Return False to propagate exceptions (default behavior)
        # Return True to suppress exceptions
        return False  # Don't suppress exceptions


# Creating a Context Manager Using a Decorator
# -----------------------------------------
# Method 2: Using the @asynccontextmanager decorator

@contextlib.asynccontextmanager
async def async_resource_manager(name):
    """A context manager created using the asynccontextmanager decorator"""
    
    # Setup phase (before yield)
    print(f"[{name}] Setting up resource")
    try:
        await asyncio.sleep(0.1)  # Simulate async resource acquisition
        print(f"[{name}] Resource ready")
        
        # The yield statement is where the body of the async with executes
        yield f"{name} resource"  # This value is returned from the context manager
        
    finally:
        # Cleanup phase (after yield)
        print(f"[{name}] Cleaning up resource")
        await asyncio.sleep(0.1)  # Simulate async resource release
        print(f"[{name}] Resource released")


async def using_decorator_context_manager():
    print("\n== Context Manager with Decorator ==")
    
    # Using the decorated function as a context manager
    async with async_resource_manager("Database") as resource:
        print(f"Using {resource}")
        await asyncio.sleep(0.3)
        print("Performing operations with the resource")


# Error Handling in Async Context Managers
# -------------------------------------

async def error_handling_example():
    print("\n== Error Handling in Async Context Managers ==")
    
    # Example 1: Error propagation (normal behavior)
    print("Example 1: Error propagation (not suppressed)")
    try:
        async with AsyncTimer("ErrorTask"):
            print("About to raise an exception")
            await asyncio.sleep(0.2)
            raise ValueError("Simulated error")
    except ValueError as e:
        print(f"Exception caught: {e}")
    
    # Example 2: Error suppression
    print("\nExample 2: Error suppression")
    
    class SuppressingManager:
        async def __aenter__(self):
            print("Entering suppressing manager")
            return self
        
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            if exc_type is not None:
                print(f"Suppressing exception: {exc_type.__name__}: {exc_val}")
                return True  # Suppress the exception
            return False
    
    async with SuppressingManager():
        print("About to raise an exception that will be suppressed")
        await asyncio.sleep(0.2)
        raise RuntimeError("This error will be suppressed")
    
    print("Execution continues after suppressed exception")


# Practical Example: Database Connection Manager
# ------------------------------------------

class AsyncDBConnection:
    """Simulated asynchronous database connection"""
    
    def __init__(self, db_name):
        self.db_name = db_name
        self.connected = False
    
    async def connect(self):
        """Simulate connecting to a database"""
        print(f"Connecting to database '{self.db_name}'...")
        await asyncio.sleep(0.5)  # Simulate connection time
        self.connected = True
        print(f"Connected to '{self.db_name}'")
    
    async def execute(self, query):
        """Execute a query on the database"""
        if not self.connected:
            raise RuntimeError("Not connected to the database")
        
        print(f"Executing query: {query}")
        await asyncio.sleep(0.2)  # Simulate query execution
        return {"rows": 5, "result": f"Result of {query}"}
    
    async def close(self):
        """Close the database connection"""
        if self.connected:
            print(f"Closing connection to '{self.db_name}'...")
            await asyncio.sleep(0.3)  # Simulate closing time
            self.connected = False
            print("Connection closed")


class AsyncDBConnectionManager:
    """Async context manager for database connections"""
    
    def __init__(self, db_name):
        self.db_name = db_name
        self.db = None
    
    async def __aenter__(self):
        # Create and connect to the database
        self.db = AsyncDBConnection(self.db_name)
        await self.db.connect()
        return self.db
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Close the connection even if an error occurred
        if self.db is not None:
            await self.db.close()


async def database_example():
    print("\n== Practical Example: Database Connection ==")
    
    # Use the database connection manager
    async with AsyncDBConnectionManager("user_data") as db:
        # The connection is now open
        result1 = await db.execute("SELECT * FROM users")
        print(f"Query result: {result1}")
        
        result2 = await db.execute("UPDATE users SET active = true")
        print(f"Query result: {result2}")
    
    # The connection is automatically closed when exiting the context
    print("After the context, the connection is closed")


# Multiple Context Managers
# ---------------------

async def multiple_context_managers():
    print("\n== Multiple Async Context Managers ==")
    
    # Using multiple context managers in a single async with statement
    print("Using multiple context managers in one statement:")
    async with AsyncTimer("Timer 1") as t1, AsyncTimer("Timer 2") as t2:
        print(f"Using {t1.name} and {t2.name}")
        await asyncio.sleep(0.3)
        print("Performing work with both resources")
    
    # Creating a combined context manager
    print("\nCombining context managers with contextlib.aclosing:")
    
    @contextlib.asynccontextmanager
    async def combined_manager():
        async with AsyncTimer("Combined 1") as t1:
            async with AsyncTimer("Combined 2") as t2:
                yield (t1, t2)
    
    async with combined_manager() as (timer1, timer2):
        print(f"Using combined resources: {timer1.name}, {timer2.name}")
        await asyncio.sleep(0.3)


# Best Practices
# ------------

def best_practices():
    print("\n== Best Practices for Async Context Managers ==")
    
    print("1. Always use 'async with' for async resources")
    print("2. Implement proper cleanup in __aexit__ methods")
    print("3. Handle exceptions appropriately (suppress or propagate)")
    print("4. Use try/finally blocks within __aenter__ if needed")
    print("5. Use asynccontextmanager for simpler implementations")
    print("6. Don't perform blocking operations in async context managers")
    print("7. Document the behavior of your context managers")
    print("8. Test exception handling in your context managers")


# Run all examples
if __name__ == "__main__":
    print("Async Context Managers\n")
    
    # Regular function examples
    intro_to_context_managers()
    
    # Async function examples
    asyncio.run(using_existing_context_managers())
    asyncio.run(using_decorator_context_manager())
    asyncio.run(error_handling_example())
    asyncio.run(database_example())
    asyncio.run(multiple_context_managers())
    
    # Best practices
    best_practices()
    
    print("\nNext tutorial: 7_sync_primitives.py - Synchronization primitives") 