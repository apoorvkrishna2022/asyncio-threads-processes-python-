"""
# Advanced AsyncIO Use Cases
# ========================
#
# This tutorial explores advanced use cases and patterns for asyncio.
# Learn about async generators, subprocesses, networking, and more complex patterns.
"""

import asyncio
import aiohttp
import aiofiles
import asyncio.subprocess
import json
import random
import signal
import sys
import time
from asyncio import Queue
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, AsyncIterable, Set
from datetime import datetime
from collections import deque


# 1. Async Generators and Asynchronous Iteration
# --------------------------------------------
# Async generators use 'async yield' to create asynchronous iterators

async def async_generator_example():
    print("\n== Async Generators and Iteration ==")
    
    async def async_range(start, stop):
        """A simple async generator that yields numbers in a range"""
        for i in range(start, stop):
            # Simulate some async work before yielding
            await asyncio.sleep(0.1)
            yield i
    
    # Using an async generator with async for
    print("Using async for with an async generator:")
    async for num in async_range(1, 5):
        print(f"Got number: {num}")
    
    # Creating an async generator that streams data
    async def data_streamer(items):
        """Stream items with random delays"""
        for item in items:
            await asyncio.sleep(random.uniform(0.05, 0.2))
            yield item
    
    # Collect results from an async generator
    data = ["Item 1", "Item 2", "Item 3", "Item 4", "Item 5"]
    results = []
    
    print("\nStreaming data:")
    async for item in data_streamer(data):
        print(f"Received: {item}")
        results.append(item)
    
    print(f"Collected: {results}")
    
    # Async generator expression
    print("\nUsing async generator expression:")
    async_gen = (item async for item in data_streamer(data))
    async for item in async_gen:
        print(f"From expression: {item}")


# 2. Subprocess Management with AsyncIO
# ----------------------------------
# Run and communicate with subprocesses asynchronously

async def subprocess_example():
    print("\n== Asynchronous Subprocess Management ==")
    
    # Run a simple command and get the output
    print("Running a simple command (ls/dir):")
    
    # Choose the command based on the platform
    cmd = "ls" if sys.platform != "win32" else "dir"
    
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    stdout, stderr = await proc.communicate()
    
    print(f"Command exited with status {proc.returncode}")
    if stdout:
        print(f"Standard Output: {stdout.decode().splitlines()[:3]} ...")
    if stderr:
        print(f"Standard Error: {stderr.decode()}")
    
    # Running multiple commands concurrently
    print("\nRunning multiple commands concurrently:")
    
    async def run_command(cmd):
        print(f"Starting command: {cmd}")
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        return cmd, proc.returncode, stdout, stderr
    
    # Define commands to run
    commands = [
        "echo 'Hello from async subprocess'",
        f"python -c 'import time; time.sleep(1); print(\"Slept for 1 second\")'",
        "python --version"
    ]
    
    # Run all commands concurrently
    tasks = [run_command(cmd) for cmd in commands]
    results = await asyncio.gather(*tasks)
    
    # Process results
    for cmd, returncode, stdout, stderr in results:
        print(f"Command '{cmd}' completed with status {returncode}")
        if stdout:
            print(f"  Output: {stdout.decode().strip()}")
    
    # Streaming output from a long-running process
    print("\nStreaming output from a long-running process:")
    
    proc = await asyncio.create_subprocess_shell(
        "for i in 1 2 3 4 5; do echo $i; sleep 0.5; done",
        stdout=asyncio.subprocess.PIPE
    )
    
    print("Streaming output:")
    while True:
        # Read one line at a time
        line = await proc.stdout.readline()
        if not line:
            break
        print(f"  Received line: {line.decode().strip()}")
    
    await proc.wait()
    print(f"Process exited with status {proc.returncode}")


# 3. Real-time Notifications with WebSockets
# ---------------------------------------
# Simple websocket client implementation

async def websocket_example():
    print("\n== WebSocket Real-time Communication ==")
    print("Note: This example requires an echo websocket server to work properly.")
    print("We'll simulate the behavior instead.")
    
    class MockWebSocket:
        """A mock WebSocket class that simulates WebSocket behavior"""
        
        def __init__(self):
            self.closed = False
            self.messages = Queue()
            # Add some sample messages
            asyncio.create_task(self._add_messages())
        
        async def _add_messages(self):
            """Simulate incoming messages"""
            messages = [
                "Welcome to the WebSocket server",
                "This is message 1",
                "This is message 2",
                "This is the final message"
            ]
            
            for msg in messages:
                await asyncio.sleep(1)  # Delay between messages
                await self.messages.put(msg)
        
        async def connect(self, url):
            print(f"Connected to {url}")
            return self
        
        async def send(self, message):
            print(f"Sending message: {message}")
            # Echo the message back
            await asyncio.sleep(0.5)  # Simulate network latency
            await self.messages.put(f"Echo: {message}")
        
        async def receive(self):
            if self.closed:
                raise Exception("WebSocket is closed")
            # Wait for a message
            return await self.messages.get()
        
        async def close(self):
            print("Closing WebSocket connection")
            self.closed = True
    
    # Real WebSocket code would use a library like aiohttp or websockets
    # Here we'll use our mock implementation
    
    async def connect_and_listen():
        # In a real app you would use:
        # async with aiohttp.ClientSession() as session:
        #     async with session.ws_connect('wss://echo.websocket.org') as ws:
        
        # Create a mock WebSocket
        ws = MockWebSocket()
        await ws.connect("wss://example.com/ws")
        
        # Set up a listener task
        async def listener():
            try:
                while True:
                    msg = await ws.receive()
                    print(f"Received message: {msg}")
                    if msg == "This is the final message":
                        break
            except Exception as e:
                print(f"WebSocket error: {e}")
        
        # Start the listener task
        listener_task = asyncio.create_task(listener())
        
        # Send some messages
        await ws.send("Hello from AsyncIO!")
        await asyncio.sleep(1)
        await ws.send("How are you today?")
        
        # Wait for the listener to finish
        await listener_task
        
        # Close the connection
        await ws.close()
    
    await connect_and_listen()


# 4. Rate Limiting and Throttling
# ----------------------------
# Implementing a rate limiter for API calls

async def rate_limiting_example():
    print("\n== Rate Limiting and Throttling ==")
    
    class RateLimiter:
        """A rate limiter that limits the number of operations per time period"""
        
        def __init__(self, rate_limit, time_period=60):
            """
            Initialize the rate limiter
            
            Args:
                rate_limit: Maximum number of operations allowed
                time_period: Time period in seconds
            """
            self.rate_limit = rate_limit
            self.time_period = time_period
            self.timestamps = []
            self._lock = asyncio.Lock()
        
        async def acquire(self):
            """
            Acquire permission to proceed
            
            Blocks until permission is granted
            """
            async with self._lock:
                now = time.monotonic()
                
                # Remove timestamps outside the time window
                self.timestamps = [ts for ts in self.timestamps if now - ts <= self.time_period]
                
                # If we haven't reached the limit
                if len(self.timestamps) < self.rate_limit:
                    self.timestamps.append(now)
                    return True
                
                # Calculate time to wait
                oldest = self.timestamps[0]
                wait_time = self.time_period - (now - oldest)
                
                if wait_time <= 0:
                    # We can remove the oldest and add a new timestamp
                    self.timestamps.pop(0)
                    self.timestamps.append(now)
                    return True
            
            # Wait and retry
            print(f"Rate limit reached. Waiting {wait_time:.2f} seconds...")
            await asyncio.sleep(wait_time)
            return await self.acquire()
        
        @asynccontextmanager
        async def limit(self):
            """Context manager for rate limiting"""
            await self.acquire()
            try:
                yield
            finally:
                pass  # Nothing to clean up
    
    # Create a rate limiter with 5 requests per 3 seconds
    limiter = RateLimiter(rate_limit=5, time_period=3)
    
    async def make_api_call(call_id):
        """Simulate making an API call"""
        async with limiter.limit():
            print(f"Making API call {call_id} at {time.time():.2f}")
            # Simulate API call duration
            await asyncio.sleep(0.2)
            return f"Result of call {call_id}"
    
    # Make 10 API calls which should be rate-limited
    print("Making 10 API calls with rate limiting (5 per 3 seconds):")
    start = time.time()
    
    tasks = [make_api_call(i) for i in range(1, 11)]
    results = await asyncio.gather(*tasks)
    
    elapsed = time.time() - start
    print(f"All API calls completed in {elapsed:.2f} seconds")
    print(f"Results: {results}")


# 5. Circuit Breaker Pattern
# ------------------------
# Implementing the circuit breaker pattern for fault tolerance

async def circuit_breaker_example():
    print("\n== Circuit Breaker Pattern ==")
    
    class CircuitBreaker:
        """
        Circuit breaker implementation to prevent repeated failures
        
        States:
        - CLOSED: Normal operation, requests pass through
        - OPEN: Circuit is broken, requests fail fast
        - HALF_OPEN: Testing if the service is back, allows a single request
        """
        
        # States
        CLOSED = "CLOSED"
        OPEN = "OPEN"
        HALF_OPEN = "HALF_OPEN"
        
        def __init__(self, failure_threshold=5, recovery_timeout=5, name="default"):
            self.name = name
            self.failure_threshold = failure_threshold
            self.recovery_timeout = recovery_timeout
            self.state = self.CLOSED
            self.failure_count = 0
            self.last_failure_time = 0
            self._lock = asyncio.Lock()
        
        async def __call__(self, func, *args, **kwargs):
            """
            Execute the function with circuit breaker protection
            
            Args:
                func: The async function to call
                *args, **kwargs: Arguments to pass to the function
            
            Returns:
                The result of the function call
            
            Raises:
                CircuitBreakerOpenError: If the circuit is open
                Any exception raised by the function
            """
            async with self._lock:
                if self.state == self.OPEN:
                    if time.time() - self.last_failure_time >= self.recovery_timeout:
                        # Recovery timeout has passed, try a single request
                        self.state = self.HALF_OPEN
                        print(f"Circuit {self.name}: OPEN -> HALF_OPEN")
                    else:
                        # Circuit is open, fail fast
                        print(f"Circuit {self.name}: OPEN (failing fast)")
                        raise Exception("Circuit is OPEN - failing fast")
            
            try:
                # Execute the function
                result = await func(*args, **kwargs)
                
                # If we get here, the call succeeded
                async with self._lock:
                    if self.state == self.HALF_OPEN:
                        # Success in half-open state means we can close the circuit
                        self.state = self.CLOSED
                        self.failure_count = 0
                        print(f"Circuit {self.name}: HALF_OPEN -> CLOSED")
                    elif self.state == self.CLOSED:
                        # Reset failure count on success
                        self.failure_count = 0
                
                return result
                
            except Exception as e:
                async with self._lock:
                    self.last_failure_time = time.time()
                    
                    if self.state == self.HALF_OPEN:
                        # Failed in half-open state, reopen the circuit
                        self.state = self.OPEN
                        print(f"Circuit {self.name}: HALF_OPEN -> OPEN (failed again)")
                    elif self.state == self.CLOSED:
                        # Increment failure count
                        self.failure_count += 1
                        if self.failure_count >= self.failure_threshold:
                            # Too many failures, open the circuit
                            self.state = self.OPEN
                            print(f"Circuit {self.name}: CLOSED -> OPEN (threshold reached)")
                
                # Re-raise the exception
                raise
    
    # Create a circuit breaker
    breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=2, name="api_service")
    
    # Service that sometimes fails
    async def unreliable_service(succeed=True):
        """Simulates an unreliable service that sometimes fails"""
        await asyncio.sleep(0.1)  # Simulate network delay
        if not succeed:
            raise Exception("Service unavailable")
        return "Service response"
    
    # Function to call with circuit breaker protection
    async def call_service(succeed=True):
        try:
            result = await breaker(unreliable_service, succeed)
            print(f"Call succeeded: {result}")
            return True
        except Exception as e:
            print(f"Call failed: {e}")
            return False
    
    # Demonstrate circuit breaker behavior
    print("Testing circuit breaker pattern:")
    
    print("\n1. Initial successful calls:")
    await call_service(succeed=True)
    await call_service(succeed=True)
    
    print("\n2. Multiple failures to trigger OPEN state:")
    await call_service(succeed=False)
    await call_service(succeed=False)
    await call_service(succeed=False)  # This should trigger OPEN state
    
    print("\n3. Calls during OPEN state (should fail fast):")
    await call_service(succeed=True)  # Should fail fast
    await call_service(succeed=True)  # Should fail fast
    
    print("\n4. Waiting for recovery timeout...")
    await asyncio.sleep(2.1)  # Just over recovery timeout
    
    print("\n5. First call after timeout (HALF_OPEN state):")
    await call_service(succeed=True)  # Should succeed and close the circuit
    
    print("\n6. Circuit should now be CLOSED again:")
    await call_service(succeed=True)
    await call_service(succeed=True)


# 6. Asynchronous Workers Pool
# -------------------------
# Implementing a pool of worker tasks that process a queue of jobs

async def worker_pool_example():
    print("\n== Asynchronous Worker Pool ==")
    
    class WorkerPool:
        """A pool of worker tasks that process jobs from a queue"""
        
        def __init__(self, num_workers=5, max_queue_size=100):
            self.queue = asyncio.Queue(maxsize=max_queue_size)
            self.num_workers = num_workers
            self.workers = []
            self.results = []
            self._stop_event = asyncio.Event()
            self._jobs_complete = asyncio.Event()
        
        async def start(self):
            """Start the worker tasks"""
            self.workers = [
                asyncio.create_task(self._worker(f"Worker-{i+1}"))
                for i in range(self.num_workers)
            ]
            print(f"Started {self.num_workers} workers")
        
        async def stop(self):
            """Stop the worker tasks"""
            print("Stopping worker pool...")
            
            # Signal workers to stop
            self._stop_event.set()
            
            # Cancel all workers
            for worker in self.workers:
                worker.cancel()
            
            # Wait for all workers to stop
            try:
                await asyncio.gather(*self.workers, return_exceptions=True)
            except asyncio.CancelledError:
                pass
            
            print("Worker pool stopped")
        
        async def submit(self, job):
            """Submit a job to the worker pool"""
            await self.queue.put(job)
        
        async def submit_many(self, jobs):
            """Submit multiple jobs to the worker pool"""
            for job in jobs:
                await self.queue.put(job)
        
        async def wait_for_completion(self):
            """Wait for all submitted jobs to complete"""
            # Wait for the queue to be empty
            await self.queue.join()
            # Signal that all jobs are complete
            self._jobs_complete.set()
        
        async def _worker(self, name):
            """Worker task that processes jobs from the queue"""
            print(f"{name} started")
            try:
                while not self._stop_event.is_set():
                    try:
                        # Get a job with a timeout
                        job = await asyncio.wait_for(
                            self.queue.get(),
                            timeout=0.5
                        )
                        
                        # Process the job
                        print(f"{name} processing job: {job}")
                        try:
                            # Execute the job function with its arguments
                            func, args, kwargs = job
                            result = await func(*args, **kwargs)
                            self.results.append((job, result))
                            print(f"{name} completed job with result: {result}")
                        except Exception as e:
                            print(f"{name} job failed with error: {e}")
                            self.results.append((job, None))
                        finally:
                            # Mark the job as done
                            self.queue.task_done()
                    
                    except asyncio.TimeoutError:
                        # No job available, check if we should stop
                        if self._jobs_complete.is_set() and self.queue.empty():
                            break
                        continue
            
            except asyncio.CancelledError:
                print(f"{name} was cancelled")
                raise
            
            print(f"{name} stopped")
    
    # Define a job function
    async def job_func(job_id, duration):
        """A job that takes some time to complete"""
        print(f"Job {job_id} running (duration: {duration}s)")
        await asyncio.sleep(duration)
        return f"Result from job {job_id}"
    
    # Create and use a worker pool
    pool = WorkerPool(num_workers=3)
    
    try:
        # Start the worker pool
        await pool.start()
        
        # Create some jobs
        jobs = [
            (job_func, (i, random.uniform(0.5, 1.5)), {})
            for i in range(1, 10)
        ]
        
        # Submit the jobs
        print(f"Submitting {len(jobs)} jobs")
        await pool.submit_many(jobs)
        
        # Wait for all jobs to complete
        print("Waiting for all jobs to complete")
        await pool.wait_for_completion()
        
        # Print results
        print("\nJob results:")
        for (job, args, _), result in pool.results:
            job_id = args[0]
            print(f"Job {job_id} result: {result}")
    
    finally:
        # Stop the worker pool
        await pool.stop()


# 7. Distributed Task Processing
# --------------------------
# Simple implementation of a distributed task processing system

async def distributed_processing_example():
    print("\n== Distributed Task Processing ==")
    
    # This is a simulated example. In a real system, you would use
    # actual network communication, message queues, or distributed databases.
    
    @dataclass
    class Task:
        """A task to be executed by a worker"""
        id: str
        type: str
        data: Dict[str, Any]
        created_at: float = 0
        status: str = "pending"
        result: Optional[Any] = None
    
    class TaskManager:
        """Manages tasks and assigns them to workers"""
        
        def __init__(self):
            self.task_queue = asyncio.Queue()
            self.completed_tasks = {}
            self.workers = set()
            self.running = False
            self._lock = asyncio.Lock()
        
        async def register_worker(self, worker_id):
            """Register a worker"""
            async with self._lock:
                self.workers.add(worker_id)
                print(f"Worker {worker_id} registered")
        
        async def unregister_worker(self, worker_id):
            """Unregister a worker"""
            async with self._lock:
                if worker_id in self.workers:
                    self.workers.remove(worker_id)
                    print(f"Worker {worker_id} unregistered")
        
        async def add_task(self, task):
            """Add a task to the queue"""
            task.created_at = time.time()
            await self.task_queue.put(task)
            print(f"Task {task.id} ({task.type}) added to queue")
        
        async def get_task(self):
            """Get a task from the queue"""
            return await self.task_queue.get()
        
        async def complete_task(self, task_id, result):
            """Mark a task as completed"""
            async with self._lock:
                if task_id in self.completed_tasks:
                    print(f"Task {task_id} already completed")
                    return
                
                self.completed_tasks[task_id] = result
                print(f"Task {task_id} completed with result: {result}")
                self.task_queue.task_done()
        
        async def wait_for_tasks(self):
            """Wait for all tasks to complete"""
            await self.task_queue.join()
    
    class Worker:
        """A worker that processes tasks"""
        
        def __init__(self, worker_id, task_manager):
            self.worker_id = worker_id
            self.task_manager = task_manager
            self._stop_event = asyncio.Event()
            self._task = None
        
        async def start(self):
            """Start processing tasks"""
            await self.task_manager.register_worker(self.worker_id)
            self._task = asyncio.create_task(self._process_tasks())
            print(f"Worker {self.worker_id} started")
        
        async def stop(self):
            """Stop processing tasks"""
            print(f"Stopping worker {self.worker_id}")
            self._stop_event.set()
            if self._task:
                await asyncio.wait_for(self._task, timeout=5)
            await self.task_manager.unregister_worker(self.worker_id)
            print(f"Worker {self.worker_id} stopped")
        
        async def _process_tasks(self):
            """Process tasks from the task manager"""
            try:
                while not self._stop_event.is_set():
                    # Get a task to process
                    try:
                        task = await asyncio.wait_for(
                            self.task_manager.get_task(),
                            timeout=1
                        )
                    except asyncio.TimeoutError:
                        continue
                    
                    print(f"Worker {self.worker_id} processing task {task.id} ({task.type})")
                    
                    # Process the task based on its type
                    if task.type == "compute":
                        # Simulate computation
                        await asyncio.sleep(random.uniform(0.5, 1.5))
                        result = sum(range(1, task.data.get("n", 10)))
                    elif task.type == "io":
                        # Simulate I/O operation
                        await asyncio.sleep(random.uniform(0.2, 0.8))
                        result = f"Processed {task.data.get('data', 'unknown')}"
                    else:
                        # Unknown task type
                        result = "Unknown task type"
                    
                    # Complete the task
                    await self.task_manager.complete_task(task.id, result)
            
            except asyncio.CancelledError:
                print(f"Worker {self.worker_id} processing was cancelled")
                raise
    
    # Create the task manager
    manager = TaskManager()
    
    # Create some workers
    workers = [
        Worker(f"worker-{i}", manager)
        for i in range(1, 4)
    ]
    
    try:
        # Start the workers
        for worker in workers:
            await worker.start()
        
        # Create some tasks
        tasks = [
            Task(id=f"task-{i}", 
                 type="compute" if i % 2 == 0 else "io",
                 data={"n": i * 10} if i % 2 == 0 else {"data": f"data-{i}"})
            for i in range(1, 10)
        ]
        
        # Add the tasks to the manager
        for task in tasks:
            await manager.add_task(task)
        
        # Wait for all tasks to complete
        print("Waiting for all tasks to complete")
        await manager.wait_for_tasks()
        
        # Print completed tasks
        print("\nCompleted tasks:")
        for task_id, result in manager.completed_tasks.items():
            print(f"{task_id}: {result}")
    
    finally:
        # Stop the workers
        for worker in workers:
            await worker.stop()


# 8. Backpressure Handling
# ---------------------
# Implementing backpressure to prevent overwhelming a system

async def backpressure_example():
    print("\n== Backpressure Handling ==")
    
    class Producer:
        """Produces items at a specific rate"""
        
        def __init__(self, rate=10, name="Producer"):
            """
            Initialize the producer
            
            Args:
                rate: Items per second to produce
                name: Name of the producer
            """
            self.rate = rate
            self.name = name
            self.produced = 0
            self._stop_event = asyncio.Event()
        
        async def start(self, consumer):
            """Start producing items"""
            print(f"{self.name} starting (rate: {self.rate} items/s)")
            
            interval = 1.0 / self.rate
            self.produced = 0
            
            while not self._stop_event.is_set():
                start_time = time.time()
                
                # Create an item
                item = f"Item-{self.produced + 1}"
                
                # Try to send it to the consumer
                try:
                    # Apply backpressure - block if consumer is overwhelmed
                    await consumer.receive(item, self.name)
                    self.produced += 1
                except Exception as e:
                    print(f"{self.name} error: {e}")
                
                # Calculate time to sleep to maintain the rate
                elapsed = time.time() - start_time
                sleep_time = max(0, interval - elapsed)
                await asyncio.sleep(sleep_time)
        
        async def stop(self):
            """Stop producing items"""
            self._stop_event.set()
            print(f"{self.name} stopped after producing {self.produced} items")
    
    class Consumer:
        """Consumes items at a specific rate"""
        
        def __init__(self, rate=5, buffer_size=20, name="Consumer"):
            """
            Initialize the consumer
            
            Args:
                rate: Items per second to consume
                buffer_size: Maximum number of items to buffer
                name: Name of the consumer
            """
            self.rate = rate
            self.buffer_size = buffer_size
            self.name = name
            self.buffer = asyncio.Queue(maxsize=buffer_size)
            self.consumed = 0
            self._stop_event = asyncio.Event()
            self._task = None
        
        async def start(self):
            """Start consuming items"""
            print(f"{self.name} starting (rate: {self.rate} items/s, buffer: {self.buffer_size})")
            self._task = asyncio.create_task(self._consume())
        
        async def stop(self):
            """Stop consuming items"""
            if self._task:
                self._stop_event.set()
                await self._task
                print(f"{self.name} stopped after consuming {self.consumed} items")
        
        async def receive(self, item, sender_name):
            """
            Receive an item from a producer
            
            If the buffer is full, this will block, applying backpressure
            to the producer.
            """
            buffer_size = self.buffer.qsize()
            if buffer_size >= self.buffer_size * 0.8:
                print(f"⚠️ {self.name} buffer filling up: {buffer_size}/{self.buffer_size}")
            
            try:
                # This will block if the queue is full
                await self.buffer.put(item)
                print(f"{sender_name} -> {self.name}: {item} (buffer: {self.buffer.qsize()}/{self.buffer_size})")
            except asyncio.CancelledError:
                print(f"{self.name} receive cancelled")
                raise
        
        async def _consume(self):
            """Consume items from the buffer"""
            interval = 1.0 / self.rate
            self.consumed = 0
            
            try:
                while not self._stop_event.is_set():
                    start_time = time.time()
                    
                    try:
                        # Get an item with a timeout
                        item = await asyncio.wait_for(
                            self.buffer.get(),
                            timeout=0.5
                        )
                        
                        # Process the item
                        print(f"{self.name} processing: {item}")
                        await asyncio.sleep(interval * 0.8)  # Simulate processing time
                        self.buffer.task_done()
                        self.consumed += 1
                        
                    except asyncio.TimeoutError:
                        # No item available
                        continue
                    
                    # Calculate time to sleep to maintain the rate
                    elapsed = time.time() - start_time
                    sleep_time = max(0, interval - elapsed)
                    await asyncio.sleep(sleep_time)
            
            except asyncio.CancelledError:
                print(f"{self.name} consumption cancelled")
                raise
    
    # Create producer and consumer with different rates to demonstrate backpressure
    consumer = Consumer(rate=5, buffer_size=10, name="SlowConsumer")
    producer = Producer(rate=10, name="FastProducer")
    
    # Run for a few seconds to demonstrate backpressure
    try:
        # Start the consumer
        await consumer.start(producer)
        
        # Start the producer
        producer_task = asyncio.create_task(producer.start(consumer))
        
        # Run for 5 seconds
        print("Running producer and consumer for 5 seconds...")
        await asyncio.sleep(5)
        
        # Stop the producer and consumer
        await producer.stop()
        producer_task.cancel()
        await consumer.stop()
        
        # Print summary
        print("\nBackpressure example summary:")
        print(f"Producer rate: {producer.rate} items/s")
        print(f"Consumer rate: {consumer.rate} items/s")
        print(f"Buffer size: {consumer.buffer_size} items")
        print(f"Items produced: {producer.produced}")
        print(f"Items consumed: {consumer.consumed}")
        print(f"Items in buffer: {consumer.buffer.qsize()}")
        
    except asyncio.CancelledError:
        # Handle cancellation
        await producer.stop()
        await consumer.stop()


async def main():
    """Run all examples."""
    print("=== AsyncIO Advanced Use Cases ===")
    
    try:
        # Run demonstrations
        await process_data_stream()
        await demonstrate_subprocess()
        await demonstrate_websocket()
        await demonstrate_rate_limiting()
        await demonstrate_circuit_breaker()
        await demonstrate_worker_pool()
        await demonstrate_distributed_tasks()
        await demonstrate_backpressure()
        
        print("\n=== All examples completed ===")
    
    except KeyboardInterrupt:
        print("\nExamples stopped by user")
    except Exception as e:
        print(f"\nError running examples: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 