"""
# Python Threading Tutorial - Timer Threads
# ======================================
#
# This file demonstrates using Timer threads to execute functions after a delay.
"""

import threading
import time

def timer_example():
    """
    Demonstrate using Timer threads.
    Timers execute a function after a specified delay.
    """
    print("\n=== Timer Threads ===")
    
    def delayed_task():
        """Function that will be called after a delay."""
        print("Delayed task: executing after delay")
    
    # Create a timer
    timer = threading.Timer(2.0, delayed_task)
    
    print("Starting timer thread")
    timer.start()
    
    print("Main thread: continuing execution immediately")
    
    # Demonstrate canceling a timer
    timer2 = threading.Timer(10.0, lambda: print("This should never run"))
    timer2.start()
    
    time.sleep(1)
    print("Canceling the second timer")
    timer2.cancel()
    
    # Wait for the first timer to complete
    timer.join()
    
    # Multiple timers
    print("\nStarting multiple timers:")
    
    def timed_message(message):
        print(message)
    
    # Create several timers with different delays
    timers = [
        threading.Timer(1.0, timed_message, args=("Message after 1 second",)),
        threading.Timer(2.0, timed_message, args=("Message after 2 seconds",)),
        threading.Timer(3.0, timed_message, args=("Message after 3 seconds",))
    ]
    
    # Start all timers
    print("Starting all timers")
    for timer in timers:
        timer.start()
    
    # Wait for all timers to complete
    for timer in timers:
        timer.join()
    
    # Timer as a delayed execution mechanism
    print("\nUsing Timer as a delayed execution mechanism:")
    
    class DelayedTask:
        def __init__(self, name, delay):
            self.name = name
            self.delay = delay
            self.timer = None
            
        def start(self):
            print(f"Scheduling {self.name} to run in {self.delay} seconds")
            self.timer = threading.Timer(self.delay, self.execute)
            self.timer.start()
            
        def execute(self):
            print(f"Executing {self.name}")
            
        def cancel(self):
            if self.timer:
                self.timer.cancel()
                print(f"{self.name} canceled")
    
    # Create some delayed tasks
    tasks = [
        DelayedTask("Task A", 1.5),
        DelayedTask("Task B", 2.5),
        DelayedTask("Task C", 3.5)
    ]
    
    # Start the tasks
    for task in tasks:
        task.start()
    
    # Cancel one task
    time.sleep(1.0)
    tasks[2].cancel()  # Cancel Task C
    
    # Wait for the remaining tasks to complete
    time.sleep(3.0)
    
    print("\nWhen to use Timer threads:")
    print("1. Executing code after a delay")
    print("2. Implementing timeouts")
    print("3. Creating delayed notifications or alerts")
    print("4. Scheduling tasks to run in the future")
    print("5. Building simple retry mechanisms with increasing delays")

if __name__ == "__main__":
    timer_example() 