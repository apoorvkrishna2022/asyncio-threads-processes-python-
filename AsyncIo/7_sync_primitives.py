"""
# Synchronization Primitives in AsyncIO
# ===================================
#
# This tutorial explores synchronization primitives provided by asyncio.
# These tools help coordinate concurrent tasks and manage shared resources.
"""

import asyncio
import random
import time


# Introduction to Synchronization Primitives
# ---------------------------------------

def intro_to_sync_primitives():
    print("== Introduction to Synchronization Primitives ==")
    print("AsyncIO provides several synchronization primitives:")
    print("1. Lock - Mutual exclusion lock for critical sections")
    print("2. Event - For notifying multiple tasks about an occurrence")
    print("3. Condition - Combination of a lock and an event")
    print("4. Semaphore - Allows a limited number of concurrent accesses")
    print("5. BoundedSemaphore - Semaphore that raises an error if released too many times")
    print("6. Barrier - Synchronizes multiple tasks at a specific point")
    print("7. Queue - For producer-consumer pattern and coordinating work")


# Locks
# -----
# Locks provide mutual exclusion, allowing only one task to access a critical section.

async def lock_example():
    print("\n== Lock Example ==")
    
    # Create a shared resource (in this case, just a counter)
    shared_counter = 0
    
    # Create a lock to protect the shared resource
    lock = asyncio.Lock()
    
    async def increment_counter(name):
        nonlocal shared_counter
        
        # Simulate some initial work
        await asyncio.sleep(random.uniform(0.1, 0.5))
        
        print(f"{name} is waiting to acquire the lock...")
        
        # Acquire the lock before accessing the shared resource
        async with lock:
            # Now we have exclusive access to the shared resource
            print(f"{name} acquired the lock")
            
            # Read the current value
            current = shared_counter
            
            # Simulate some processing time (during which other tasks must wait)
            await asyncio.sleep(random.uniform(0.1, 0.3))
            
            # Update the value
            shared_counter = current + 1
            print(f"{name} incremented counter to {shared_counter}")
            
            # The lock is automatically released when exiting the async with block
        
        print(f"{name} released the lock")
    
    # Create several tasks that will try to access the shared resource concurrently
    tasks = [
        increment_counter(f"Task {i}")
        for i in range(1, 6)
    ]
    
    # Run all tasks concurrently
    await asyncio.gather(*tasks)
    
    print(f"Final counter value: {shared_counter}")
    
    # Without the lock, the final value might not be 5 due to race conditions
    print("Without locks, this might result in lost updates due to race conditions")


# Events
# ------
# Events are used to notify multiple tasks that something has happened.

async def event_example():
    print("\n== Event Example ==")
    
    # Create an event
    event = asyncio.Event()
    
    async def waiter(name):
        print(f"{name} is waiting for the event")
        
        # Wait for the event to be set
        await event.wait()
        
        print(f"{name} was notified and is now proceeding")
        await asyncio.sleep(random.uniform(0.1, 0.5))
        print(f"{name} finished its work")
    
    async def setter():
        # Simulate some initialization time
        print("Initializing...")
        await asyncio.sleep(2)
        
        print("Setting the event - notifying all waiters")
        # Set the event, notifying all waiters
        event.set()
    
    # Create several tasks that wait for the event
    waiters = [waiter(f"Waiter {i}") for i in range(1, 6)]
    
    # Run all tasks concurrently, including the setter
    await asyncio.gather(setter(), *waiters)
    
    # Clear the event for reuse if needed
    event.clear()
    print("Event has been cleared and can be reused")


# Conditions
# ---------
# Conditions combine a lock and an event, allowing tasks to wait for a condition to be true.

async def condition_example():
    print("\n== Condition Example ==")
    
    # Create a condition
    condition = asyncio.Condition()
    
    # Shared data (initially empty)
    queue = []
    
    async def consumer(name):
        print(f"{name} is waiting for data")
        
        # Acquire the condition's lock
        async with condition:
            # Wait for data to be available
            while not queue:  # This prevents spurious wakeups
                print(f"{name} is waiting on the condition")
                await condition.wait()
            
            # Process the data
            data = queue.pop(0)
            print(f"{name} got data: {data}")
    
    async def producer():
        # Simulate some work before producing data
        await asyncio.sleep(1)
        
        # Acquire the condition's lock
        async with condition:
            # Add data to the queue
            queue.append("Important Data")
            print("Producer added data and is notifying consumers")
            
            # Notify one waiting consumer
            condition.notify(1)
        
        # Produce more data later
        await asyncio.sleep(1)
        
        async with condition:
            queue.append("More Data")
            print("Producer added more data and is notifying all consumers")
            
            # Notify all waiting consumers
            condition.notify_all()
    
    # Create several consumer tasks and one producer
    consumers = [consumer(f"Consumer {i}") for i in range(1, 4)]
    
    # Run all tasks concurrently
    await asyncio.gather(producer(), *consumers)


# Semaphores
# ---------
# Semaphores limit the number of tasks that can access a resource concurrently.

async def semaphore_example():
    print("\n== Semaphore Example ==")
    
    # Create a semaphore allowing 2 concurrent accesses
    semaphore = asyncio.Semaphore(2)
    
    async def worker(name):
        print(f"{name} is waiting to access the resource")
        
        # Acquire the semaphore
        async with semaphore:
            # Now we have access to the resource
            print(f"{name} is accessing the resource")
            
            # Simulate some work
            await asyncio.sleep(random.uniform(0.5, 1.5))
            
            print(f"{name} is releasing the resource")
            # The semaphore is automatically released when exiting the async with block
    
    # Create several worker tasks
    workers = [worker(f"Worker {i}") for i in range(1, 6)]
    
    # Run all tasks concurrently
    await asyncio.gather(*workers)
    
    print("All workers have finished")


# Bounded Semaphores
# ----------------
# BoundedSemaphore is like Semaphore but raises an error if released too many times.

async def bounded_semaphore_example():
    print("\n== BoundedSemaphore Example ==")
    
    # Create a bounded semaphore with initial value 2
    semaphore = asyncio.BoundedSemaphore(2)
    
    async def safe_worker(name):
        # Acquire the semaphore properly
        await semaphore.acquire()
        try:
            print(f"{name} is accessing the resource")
            await asyncio.sleep(0.5)
        finally:
            print(f"{name} is releasing the resource")
            # Always release in finally block to ensure release even if an exception occurs
            semaphore.release()
    
    async def buggy_worker(name):
        # This function incorrectly releases the semaphore twice
        await semaphore.acquire()
        print(f"{name} is accessing the resource")
        await asyncio.sleep(0.5)
        print(f"{name} is releasing the resource")
        semaphore.release()
        
        try:
            print(f"{name} is incorrectly releasing the semaphore again")
            # This will raise a ValueError with BoundedSemaphore
            semaphore.release()
        except ValueError as e:
            print(f"Error caught: {e}")
    
    # Run the workers
    await safe_worker("Safe Worker")
    await buggy_worker("Buggy Worker")


# Queues
# -----
# Queues are useful for producer-consumer patterns and task distribution.

async def queue_example():
    print("\n== Queue Example ==")
    
    # Create a queue with a maximum size of 3
    queue = asyncio.Queue(maxsize=3)
    
    async def producer(name, count):
        for i in range(count):
            # Simulate producing an item
            item = f"Item {i+1} from {name}"
            
            # Put the item in the queue (will block if queue is full)
            print(f"{name} is putting {item}")
            await queue.put(item)
            
            print(f"{name} added {item} to the queue (size: {queue.qsize()})")
            
            # Simulate variable production time
            await asyncio.sleep(random.uniform(0.1, 0.5))
    
    async def consumer(name, count):
        for i in range(count):
            # Get an item from the queue (will block if queue is empty)
            print(f"{name} is waiting for an item")
            item = await queue.get()
            
            print(f"{name} got {item} from the queue")
            
            # Simulate processing time
            await asyncio.sleep(random.uniform(0.2, 0.8))
            
            # Mark the task as done
            queue.task_done()
            print(f"{name} finished processing {item}")
    
    # Create multiple producers and consumers
    producers = [
        producer("Producer 1", 5),
        producer("Producer 2", 3)
    ]
    
    consumers = [
        consumer("Consumer 1", 4),
        consumer("Consumer 2", 4)
    ]
    
    # Start all producers and consumers
    all_tasks = producers + consumers
    await asyncio.gather(*all_tasks)
    
    # Wait for all items to be processed
    # This is optional but ensures everything is properly processed
    await queue.join()
    
    print("All items have been produced and consumed")


# Priority Queue
# ------------
# AsyncIO doesn't provide a priority queue directly, but we can implement one.

async def priority_queue_example():
    print("\n== Priority Queue Example ==")
    
    class PriorityQueue:
        """A simple priority queue implementation using asyncio.Queue"""
        
        def __init__(self):
            self._queue = asyncio.Queue()
        
        async def put(self, item, priority=0):
            # Lower numbers = higher priority
            await self._queue.put((priority, time.time(), item))
        
        async def get(self):
            priority, _, item = await self._queue.get()
            return item
        
        def task_done(self):
            self._queue.task_done()
        
        async def join(self):
            await self._queue.join()
    
    # Create a priority queue
    pq = PriorityQueue()
    
    async def priority_producer():
        # Add items with different priorities
        await pq.put("Low priority task", 3)
        print("Added low priority task")
        
        await asyncio.sleep(0.1)
        
        await pq.put("High priority task", 1)
        print("Added high priority task")
        
        await asyncio.sleep(0.1)
        
        await pq.put("Medium priority task", 2)
        print("Added medium priority task")
    
    async def priority_consumer():
        # Process 3 items
        for i in range(3):
            item = await pq.get()
            print(f"Processing: {item}")
            await asyncio.sleep(0.5)
            pq.task_done()
    
    # Run producer and consumer
    await asyncio.gather(priority_producer(), priority_consumer())
    
    # Wait for queue to be fully processed
    await pq.join()
    print("Priority queue processing complete")


# Barriers
# -------
# Barriers synchronize multiple tasks at a specific point.
# Note: asyncio doesn't provide Barrier directly, so we'll implement a simple one.

async def barrier_example():
    print("\n== Barrier Example ==")
    
    class AsyncBarrier:
        """A simple implementation of a barrier for asyncio tasks"""
        
        def __init__(self, n):
            self.n = n
            self.count = 0
            self.condition = asyncio.Condition()
        
        async def wait(self):
            async with self.condition:
                self.count += 1
                if self.count == self.n:
                    # Last one to arrive, notify all
                    print("Last task arrived, releasing all")
                    self.count = 0
                    self.condition.notify_all()
                    return True
                else:
                    # Wait for the last one
                    print(f"Task waiting at barrier ({self.count}/{self.n})")
                    await self.condition.wait()
                    return False
    
    # Create a barrier for 3 tasks
    barrier = AsyncBarrier(3)
    
    async def barrier_task(name):
        # Do some initial work
        print(f"{name} is doing initial work")
        await asyncio.sleep(random.uniform(0.5, 2))
        
        print(f"{name} arrived at the barrier")
        is_last = await barrier.wait()
        
        if is_last:
            print(f"{name} was the last to arrive")
        
        # Continue with synchronized work
        print(f"{name} is continuing after the barrier")
        await asyncio.sleep(random.uniform(0.1, 0.5))
        print(f"{name} completed")
    
    # Create several tasks to synchronize
    tasks = [barrier_task(f"Task {i}") for i in range(1, 6)]
    
    # Run all tasks concurrently
    await asyncio.gather(*tasks)
    
    print("All tasks have crossed the barrier and completed")


# Run all examples
if __name__ == "__main__":
    print("Synchronization Primitives in AsyncIO\n")
    
    # Introduction
    intro_to_sync_primitives()
    
    # Run all async examples
    asyncio.run(lock_example())
    asyncio.run(event_example())
    asyncio.run(condition_example())
    asyncio.run(semaphore_example())
    asyncio.run(bounded_semaphore_example())
    asyncio.run(queue_example())
    asyncio.run(priority_queue_example())
    asyncio.run(barrier_example())
    
    print("\nNext tutorial: 8_error_handling.py - Error handling in asynchronous code") 