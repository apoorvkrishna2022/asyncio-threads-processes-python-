# Advanced AsyncIO Use Cases

This README explains the concepts covered in `10_advanced_use_cases.py`, providing a detailed understanding of advanced patterns and use cases for Python's asyncio library.

## What this Tutorial Covers

This tutorial explores advanced asyncio concepts and patterns, including:
1. Async generators and asynchronous iteration
2. Asynchronous subprocess management
3. Real-time communication with WebSockets
4. Rate limiting and throttling
5. Circuit breaker pattern for resilience
6. Worker pools for task distribution
7. Distributed processing systems
8. Backpressure handling for flow control

## Key Concepts Explained

### 1. Async Generators and Asynchronous Iteration

Async generators combine generator functionality with async/await syntax:

```python
async def async_range(start, stop):
    for i in range(start, stop):
        await asyncio.sleep(0.1)  # Async operation
        yield i  # Yield a value

# Using async for to iterate over the async generator
async for num in async_range(1, 5):
    print(f"Got number: {num}")
```

Key features:
- Use `async def` with `yield` to create async generators
- Consume with `async for` or `await anext(generator)`
- Can use `await` inside the generator function
- Supports async generator expressions: `(x async for x in async_range(1, 5))`

### 2. Subprocess Management with AsyncIO

AsyncIO provides tools for running and communicating with subprocesses asynchronously:

```python
# Run a simple command
proc = await asyncio.create_subprocess_shell(
    "ls -la",
    stdout=asyncio.subprocess.PIPE,
    stderr=asyncio.subprocess.PIPE
)

# Wait for completion and get output
stdout, stderr = await proc.communicate()

# Stream output line by line
proc = await asyncio.create_subprocess_shell(
    "long_running_command",
    stdout=asyncio.subprocess.PIPE
)

while True:
    line = await proc.stdout.readline()
    if not line:
        break
    print(line.decode())
```

Key features:
- Non-blocking process execution
- Stream output in real-time
- Run multiple processes concurrently
- Collect exit codes and output asynchronously

### 3. Real-time Notifications with WebSockets

WebSockets provide full-duplex communication channels over a single TCP connection:

```python
async def websocket_client():
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect('wss://example.com/ws') as ws:
            # Send messages
            await ws.send_str("Hello, server!")
            
            # Receive messages
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    print(f"Received: {msg.data}")
                elif msg.type == aiohttp.WSMsgType.CLOSED:
                    break
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    break
```

Key features:
- Bidirectional communication
- Real-time updates and notifications
- Long-lived connections
- Event-driven message handling

### 4. Rate Limiting and Throttling

Rate limiting controls the frequency of operations to prevent overloading:

```python
class RateLimiter:
    def __init__(self, rate_limit, time_period=60):
        self.rate_limit = rate_limit  # Operations per time period
        self.time_period = time_period  # Time period in seconds
        self.tokens = rate_limit  # Available tokens
        self.updated_at = time.monotonic()
        self.lock = asyncio.Lock()
    
    async def acquire(self):
        """Acquire a token, waiting if necessary"""
        async with self.lock:
            # Refresh tokens based on elapsed time
            now = time.monotonic()
            elapsed = now - self.updated_at
            self.updated_at = now
            
            # Add tokens based on elapsed time
            self.tokens = min(
                self.rate_limit,
                self.tokens + elapsed * (self.rate_limit / self.time_period)
            )
            
            if self.tokens < 1:
                # Calculate wait time to get a token
                wait_time = (1 - self.tokens) * (self.time_period / self.rate_limit)
                await asyncio.sleep(wait_time)
                self.tokens = 0
            
            self.tokens -= 1
```

Key features:
- Token bucket algorithm implementation
- Fine-grained control over operation rates
- Self-adjusting based on actual time
- Can be used as a context manager

### 5. Circuit Breaker Pattern

The circuit breaker prevents cascading failures in distributed systems:

```python
class CircuitBreaker:
    # States
    CLOSED = "CLOSED"  # Normal operation
    OPEN = "OPEN"      # Circuit is broken
    HALF_OPEN = "HALF_OPEN"  # Testing if service is back
    
    def __init__(self, failure_threshold=5, recovery_timeout=5):
        self.state = self.CLOSED
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.last_failure_time = 0
        self.lock = asyncio.Lock()
    
    async def __call__(self, func, *args, **kwargs):
        """Execute the function if the circuit allows it"""
        async with self.lock:
            if self.state == self.OPEN:
                # Check if recovery timeout has elapsed
                if time.monotonic() - self.last_failure_time >= self.recovery_timeout:
                    self.state = self.HALF_OPEN
                else:
                    raise CircuitOpenError("Circuit is open")
            
        try:
            result = await func(*args, **kwargs)
            
            async with self.lock:
                if self.state == self.HALF_OPEN:
                    # Success in half-open state, close the circuit
                    self.state = self.CLOSED
                    self.failure_count = 0
            
            return result
            
        except Exception as e:
            async with self.lock:
                self.failure_count += 1
                self.last_failure_time = time.monotonic()
                
                if self.state == self.CLOSED and self.failure_count >= self.failure_threshold:
                    self.state = self.OPEN
                elif self.state == self.HALF_OPEN:
                    self.state = self.OPEN
            
            raise
```

Key features:
- Prevents repeated calls to failing services
- Automatically attempts recovery after a timeout
- Three states: CLOSED, OPEN, and HALF-OPEN
- Thread-safe with asyncio.Lock

### 6. Worker Pools

Worker pools distribute tasks among a fixed number of workers:

```python
class WorkerPool:
    def __init__(self, num_workers=5, max_queue_size=100):
        self.num_workers = num_workers
        self.jobs = asyncio.Queue(max_queue_size)
        self.worker_tasks = []
    
    async def start(self):
        """Start the worker tasks"""
        self.worker_tasks = [
            asyncio.create_task(self._worker(f"Worker-{i}"))
            for i in range(self.num_workers)
        ]
    
    async def stop(self):
        """Stop all workers"""
        # Put None in the queue for each worker to signal shutdown
        for _ in range(self.num_workers):
            await self.jobs.put(None)
        
        # Wait for all workers to finish
        if self.worker_tasks:
            await asyncio.gather(*self.worker_tasks)
    
    async def submit(self, job):
        """Submit a job to the pool"""
        await self.jobs.put(job)
    
    async def _worker(self, name):
        """Worker process that executes jobs from the queue"""
        while True:
            job = await self.jobs.get()
            
            if job is None:  # Shutdown signal
                break
                
            try:
                # Execute the job
                func, args, kwargs = job
                await func(*args, **kwargs)
            except Exception as e:
                print(f"{name} job error: {e}")
            finally:
                self.jobs.task_done()
```

Key features:
- Fixed pool of workers
- Queued job distribution
- Graceful shutdown mechanism
- Unlimited job submission (bounded by queue size)

### 7. Distributed Processing Systems

More complex systems distribute work across multiple workers or machines:

```python
class TaskManager:
    def __init__(self):
        self.tasks = {}  # All tasks by ID
        self.pending_tasks = asyncio.Queue()  # Tasks to be processed
        self.workers = set()  # Active workers
        self.lock = asyncio.Lock()
    
    async def add_task(self, task):
        """Add a new task to be processed"""
        async with self.lock:
            self.tasks[task.id] = task
        await self.pending_tasks.put(task)
    
    async def get_task(self):
        """Get the next task to process"""
        return await self.pending_tasks.get()
    
    async def complete_task(self, task_id, result):
        """Mark a task as completed with its result"""
        async with self.lock:
            if task_id in self.tasks:
                task = self.tasks[task_id]
                task.status = "completed"
                task.result = result
```

Key features:
- Task distribution across workers
- Status tracking and result collection
- Task prioritization and scheduling
- Fault tolerance mechanisms

### 8. Backpressure Handling

Backpressure mechanisms prevent fast producers from overwhelming slow consumers:

```python
class Consumer:
    def __init__(self, rate=5, buffer_size=20):
        self.processing_rate = rate  # Items per second
        self.buffer = asyncio.Queue(maxsize=buffer_size)
        self.running = False
    
    async def receive(self, item, sender_name):
        """Receive an item from a producer"""
        try:
            # Try to put item in buffer with timeout
            await asyncio.wait_for(
                self.buffer.put(item),
                timeout=0.5
            )
            return True
        except asyncio.TimeoutError:
            print(f"Buffer full, {sender_name} needs to slow down")
            return False
    
    async def _consume(self):
        """Process items from the buffer"""
        while self.running:
            item = await self.buffer.get()
            
            # Process the item (simulated with sleep)
            await asyncio.sleep(1 / self.processing_rate)
            print(f"Processed: {item}")
            
            self.buffer.task_done()
```

Key features:
- Buffer size limits to prevent memory issues
- Feedback mechanisms to slow down producers
- Rate limiting on consumer side
- Dynamic throttling based on system load

## Practical Applications

These advanced patterns enable sophisticated asyncio applications:

- **API Gateways**: Using rate limiting and circuit breakers
- **Data Pipelines**: Using worker pools and backpressure handling
- **Microservices**: Using distributed processing patterns
- **Monitoring Systems**: Using async generators for streaming data
- **Chat Applications**: Using WebSockets for real-time communication
- **Task Automation**: Using subprocess management
- **Web Crawlers**: Combining multiple patterns for efficient crawling
- **IoT Applications**: Using distributed processing and real-time notifications

## Key Takeaways

- AsyncIO can be extended with advanced patterns for complex applications
- Async generators provide elegant solutions for streaming data
- Proper concurrency control is essential for robust applications
- Resilience patterns like circuit breakers prevent cascading failures
- Worker pools and task distribution optimize resource usage
- Flow control mechanisms like backpressure prevent system overload
- These patterns are composable and can be combined as needed
- Advanced asyncio applications require careful consideration of failure modes

These advanced patterns bring asyncio to the level of industrial-strength frameworks, enabling sophisticated applications that are both efficient and robust. 