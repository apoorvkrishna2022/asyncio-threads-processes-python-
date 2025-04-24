"""
# AsyncIO Tutorial Series
# ======================
#
# A comprehensive tutorial series on asynchronous programming in Python using AsyncIO.
# This series covers everything from basic concepts to advanced patterns and real-world applications.
#
# To run the tutorials, execute each file independently.
"""

import asyncio
import os
import sys

async def main():
    """
    Main entry point for the AsyncIO Tutorial Series.
    This function provides an overview of the tutorial contents.
    """
    print("\n=== AsyncIO Tutorial Series ===")
    print("A comprehensive guide to asynchronous programming in Python\n")

    # List all tutorial files
    tutorial_files = [
        "1_intro_to_async.py - Introduction to asynchronous programming",
        "2_coroutines.py - Working with coroutines and awaitables",
        "3_tasks.py - Understanding tasks and futures",
        "4_event_loops.py - Event loop management",
        "5_async_io.py - Asynchronous I/O operations",
        "6_async_with.py - Async context managers",
        "7_sync_primitives.py - Synchronization primitives",
        "8_error_handling.py - Error handling in async code",
        "9_real_world_example.py - Web crawler application",
        "10_advanced_use_cases.py - Advanced patterns and use cases"
    ]

    print("Tutorial contents:")
    for i, file in enumerate(tutorial_files, 1):
        print(f"{i}. {file}")

    print("\nTo run a tutorial, execute the corresponding Python file.")
    print("Example: python 1_intro_to_async.py\n")

    print("It's recommended to go through the tutorials in order, as concepts build upon each other.")
    print("For the final examples, make sure to install the required packages:")
    print("pip install -r requirements.txt\n")

if __name__ == "__main__":
    asyncio.run(main())
