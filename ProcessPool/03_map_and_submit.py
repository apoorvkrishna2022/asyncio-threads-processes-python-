#!/usr/bin/env python3
"""
03_map_and_submit.py - Different ways to run tasks in ProcessPoolExecutor

This file covers:
- The difference between map() and submit() methods
- When to use each method
- How to handle results with each approach
- Performance considerations
"""

import time
import random
import concurrent.futures
from concurrent.futures import ProcessPoolExecutor


def process_item(item):
    """A function that simulates processing an item with variable duration."""
    # Simulate variable processing time
    process_time = random.uniform(0.1, 1.0)
    time.sleep(process_time)
    return f"Processed {item} in {process_time:.2f} seconds"


def complex_calculation(x):
    """A more complex calculation function."""
    # Simulate CPU-bound work
    result = 0
    for i in range(10**6):
        result += i * x
    return result


def main():
    """Main function demonstrating map and submit methods."""
    print("=== Map vs Submit Methods ===\n")
    
    # SECTION 1: The map() Method
    print("SECTION 1: The map() Method")
    print("The map() method applies a function to each item in an iterable.")
    print("It returns results in the same order as the input items.\n")
    
    # Create some sample data
    items = ["item1", "item2", "item3", "item4", "item5"]
    
    # Using map with ProcessPoolExecutor
    print("Using map() to process items in parallel:")
    start_time = time.time()
    
    with ProcessPoolExecutor() as executor:
        # map() applies the function to each item and returns results in order
        results = executor.map(process_item, items)
        
        # Convert the iterator to a list to get all results
        result_list = list(results)
    
    end_time = time.time()
    
    # Print results
    for result in result_list:
        print(f"  {result}")
    
    print(f"\nTotal time using map(): {end_time - start_time:.2f} seconds")
    print("Note: Results are returned in the same order as inputs\n")
    
    # SECTION 2: The submit() Method
    print("\nSECTION 2: The submit() Method")
    print("The submit() method schedules a single function to be executed")
    print("and returns a Future object representing the execution.\n")
    
    # Using submit with ProcessPoolExecutor
    print("Using submit() to process items in parallel:")
    start_time = time.time()
    
    with ProcessPoolExecutor() as executor:
        # Create a list to store Future objects
        future_to_item = {executor.submit(process_item, item): item for item in items}
        
        # Process results as they complete (potentially out of order)
        for future in concurrent.futures.as_completed(future_to_item):
            item = future_to_item[future]
            try:
                result = future.result()
                print(f"  {result}")
            except Exception as e:
                print(f"  {item} generated an exception: {e}")
    
    end_time = time.time()
    print(f"\nTotal time using submit(): {end_time - start_time:.2f} seconds")
    print("Note: Results are returned as they complete (potentially out of order)\n")
    
    # SECTION 3: When to use map() vs submit()
    print("\nSECTION 3: When to use map() vs submit()")
    print("Use map() when:")
    print("  - You want to apply the same function to each item in a collection")
    print("  - You need results in the same order as inputs")
    print("  - You have a simple workflow with no dependencies between tasks")
    print("\nUse submit() when:")
    print("  - You need to submit different functions for different inputs")
    print("  - You want to process results as they complete (for faster feedback)")
    print("  - You need more control over individual tasks")
    print("  - You have complex workflows with dependencies between tasks\n")
    
    # SECTION 4: Advanced Usage of submit()
    print("\nSECTION 4: Advanced Usage of submit()")
    
    # Submit different functions for different inputs
    print("Submitting different functions for different inputs:")
    
    def square(x):
        return x * x
    
    def cube(x):
        return x * x * x
    
    with ProcessPoolExecutor() as executor:
        # Submit different functions
        future1 = executor.submit(square, 10)
        future2 = executor.submit(cube, 10)
        
        # Get results
        result1 = future1.result()
        result2 = future2.result()
        
        print(f"  Square of 10: {result1}")
        print(f"  Cube of 10: {result2}")
    
    # SECTION 5: Handling Timeouts
    print("\nSECTION 5: Handling Timeouts")
    
    def slow_function():
        """A function that takes a long time to complete."""
        time.sleep(2)
        return "Slow function completed"
    
    with ProcessPoolExecutor() as executor:
        future = executor.submit(slow_function)
        
        try:
            # Try to get the result with a timeout
            result = future.result(timeout=1)
            print(f"  Result: {result}")
        except concurrent.futures.TimeoutError:
            print("  Function took too long, timeout occurred")
            
            # We can cancel the future if we don't need the result anymore
            # Note: This doesn't actually stop the running process,
            # it just tells the executor we're not interested in the result
            print("  Cancelling the future...")
            future.cancel()
    
    # SECTION 6: Performance Comparison for Different Task Types
    print("\nSECTION 6: Performance Comparison - Sequential vs map() vs submit()")
    
    # Create a list of numbers for calculation
    numbers = list(range(1, 11))
    
    # Sequential execution
    print("\nSequential execution:")
    start_time = time.time()
    sequential_results = [complex_calculation(num) for num in numbers]
    sequential_time = time.time() - start_time
    print(f"  Sequential time: {sequential_time:.2f} seconds")
    
    # Using map()
    print("\nUsing map():")
    start_time = time.time()
    with ProcessPoolExecutor() as executor:
        map_results = list(executor.map(complex_calculation, numbers))
    map_time = time.time() - start_time
    print(f"  map() time: {map_time:.2f} seconds")
    
    # Using submit()
    print("\nUsing submit() with as_completed():")
    start_time = time.time()
    with ProcessPoolExecutor() as executor:
        futures = [executor.submit(complex_calculation, num) for num in numbers]
        submit_results = [future.result() for future in concurrent.futures.as_completed(futures)]
    submit_time = time.time() - start_time
    print(f"  submit() time: {submit_time:.2f} seconds")
    
    print("\nResults comparison:")
    print(f"  Sequential vs map: Results match: {sequential_results == map_results}")
    print(f"  Sequential vs submit: Results contain same values: "
          f"{sorted(sequential_results) == sorted(submit_results)}")
    
    print("\nSpeedup factors:")
    if sequential_time > 0:
        print(f"  map() speedup: {sequential_time / map_time:.2f}x")
        print(f"  submit() speedup: {sequential_time / submit_time:.2f}x")


if __name__ == "__main__":
    main()
    print("\nKey takeaways from this tutorial:")
    print("1. map() is simpler and maintains input order in results")
    print("2. submit() offers more control and can process results as they complete")
    print("3. as_completed() can be used with submit() for faster feedback")
    print("4. Both methods provide significant performance improvements over sequential code")
    print("5. Choose the method based on your specific use case requirements") 