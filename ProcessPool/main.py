#!/usr/bin/env python3
"""
Process Pool Tutorial - Main Entry Point

This file serves as the entry point for the Process Pool tutorial.
It provides a menu-driven interface to run each tutorial file.
"""

import os
import sys
import subprocess


def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header():
    """Print the tutorial header."""
    print("=" * 80)
    print("                      PROCESS POOL TUTORIAL")
    print("=" * 80)
    print("Learn how to leverage multiple processes for parallel execution in Python")
    print("This tutorial covers everything from basics to advanced patterns")
    print("=" * 80)
    print()


def print_menu():
    """Print the menu of available tutorials."""
    print("Available Tutorials:")
    print("--------------------")
    print("1. Process Basics")
    print("2. Process Pool Basics")
    print("3. Map and Submit Methods")
    print("4. Error Handling")
    print("5. Shared Resources")
    print("6. Process Communication")
    print("7. Advanced Techniques")
    print("8. Real-World Example")
    print("")
    print("0. Exit Tutorial")
    print("")


def run_tutorial(number):
    """Run the specified tutorial file."""
    tutorial_files = {
        1: "01_process_basics.py",
        2: "02_process_pool_basics.py",
        3: "03_map_and_submit.py",
        4: "04_error_handling.py",
        5: "05_shared_resources.py",
        6: "06_process_communication.py",
        7: "07_advanced_techniques.py",
        8: "08_real_world_example.py"
    }
    
    if number not in tutorial_files:
        print(f"Invalid tutorial number: {number}")
        return
    
    filename = tutorial_files[number]
    
    # Check if the file exists
    if not os.path.exists(filename):
        print(f"Error: Tutorial file '{filename}' not found!")
        return
    
    # Clear screen before running
    clear_screen()
    
    print(f"Running tutorial {number}: {filename}")
    print("-" * 80)
    
    # Run the tutorial file as a separate process
    try:
        result = subprocess.run(
            [sys.executable, filename],
            check=True
        )
        print("-" * 80)
        if result.returncode == 0:
            print(f"Tutorial {number} completed successfully!")
        else:
            print(f"Tutorial {number} exited with code {result.returncode}")
    except subprocess.CalledProcessError as e:
        print(f"Error running tutorial: {e}")
    except KeyboardInterrupt:
        print("\nTutorial interrupted by user.")
    
    print("\nPress Enter to return to the menu...")
    input()


def main():
    """Main function that runs the tutorial menu."""
    while True:
        clear_screen()
        print_header()
        print_menu()
        
        choice = input("Enter tutorial number (0-8): ")
        
        if not choice:
            continue
        
        try:
            number = int(choice)
            
            if number == 0:
                print("Exiting tutorial. Thank you for learning about Process Pools!")
                break
            elif 1 <= number <= 8:
                run_tutorial(number)
            else:
                print("Please enter a number between 0 and 8")
                input("Press Enter to continue...")
        except ValueError:
            print("Please enter a valid number")
            input("Press Enter to continue...")


if __name__ == "__main__":
    main()
