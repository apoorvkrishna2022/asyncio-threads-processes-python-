#!/usr/bin/env python3
"""
08_real_world_example.py - A practical example of using process pools

This file demonstrates a complete real-world application of process pools:
- Image processing application that resizes and applies filters to images
- Progress tracking and reporting
- Error handling and recovery
- Resource management
- Performance comparison with sequential processing
"""

import os
import time
import random
import logging
import concurrent.futures
from PIL import Image, ImageFilter, ImageEnhance
from concurrent.futures import ProcessPoolExecutor
import multiprocessing
import argparse
from pathlib import Path


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(processName)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Shared data to track progress across processes
class ProgressTracker:
    """Track progress across multiple processes."""
    
    def __init__(self):
        """Initialize the progress tracker with shared memory objects."""
        self.total_images = multiprocessing.Value('i', 0)
        self.processed_images = multiprocessing.Value('i', 0)
        self.lock = multiprocessing.Lock()
    
    def set_total(self, total):
        """Set the total number of images to process."""
        with self.lock:
            self.total_images.value = total
    
    def increment(self):
        """Increment the number of processed images."""
        with self.lock:
            self.processed_images.value += 1
            return self.processed_images.value
    
    def get_progress(self):
        """Get the current progress as a tuple (processed, total)."""
        with self.lock:
            return (self.processed_images.value, self.total_images.value)


# Global progress tracker
progress_tracker = ProgressTracker()


def process_image(input_path, output_dir, size=(800, 600), effects=None, quality=85):
    """
    Process a single image: resize and apply effects.
    
    Args:
        input_path: Path to the input image
        output_dir: Directory to save the processed image
        size: Tuple of (width, height) for resizing
        effects: List of effects to apply (blur, sharpen, enhance)
        quality: JPEG quality (1-100)
        
    Returns:
        Tuple of (success, result)
        If success is True, result is the output path
        If success is False, result is the error message
    """
    try:
        # Get the input file name
        input_path = Path(input_path)
        file_name = input_path.name
        output_path = Path(output_dir) / file_name
        
        logger.info(f"Processing {file_name}")
        
        # Open the image
        img = Image.open(input_path)
        
        # Resize the image - use an appropriate resampling filter
        # To avoid PIL version compatibility issues, use integer values
        # 1: NEAREST, 2: BOX, 3: BILINEAR, 4: HAMMING, 5: BICUBIC, 6: LANCZOS
        img = img.resize(size, 5)  # Use BICUBIC (5) as a safe default
        
        # Apply effects
        if effects:
            for effect in effects:
                if effect == 'blur':
                    img = img.filter(ImageFilter.BLUR)
                elif effect == 'sharpen':
                    img = img.filter(ImageFilter.SHARPEN)
                elif effect == 'enhance':
                    enhancer = ImageEnhance.Contrast(img)
                    img = enhancer.enhance(1.5)
        
        # Save the image
        img.save(output_path, quality=quality)
        
        # Update progress
        processed = progress_tracker.increment()
        _, total = progress_tracker.get_progress()
        logger.info(f"Processed {processed}/{total}: {file_name}")
        
        return (True, str(output_path))
    
    except Exception as e:
        logger.error(f"Error processing {input_path}: {e}")
        return (False, str(e))


def process_images_parallel(input_dir, output_dir, num_workers=None, size=(800, 600), 
                           effects=None, quality=85):
    """
    Process images in parallel using ProcessPoolExecutor.
    
    Args:
        input_dir: Directory containing input images
        output_dir: Directory to save processed images
        num_workers: Number of worker processes (default: number of CPUs)
        size: Tuple of (width, height) for resizing
        effects: List of effects to apply
        quality: JPEG quality (1-100)
        
    Returns:
        Tuple of (successful, failed, total_time)
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all image files
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
    input_dir = Path(input_dir)
    image_files = [
        f for f in input_dir.iterdir() 
        if f.is_file() and f.suffix.lower() in image_extensions
    ]
    
    # Set total images in progress tracker
    progress_tracker.set_total(len(image_files))
    
    # Process images in parallel
    successful = []
    failed = []
    
    start_time = time.time()
    
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        # Create future to file mapping
        future_to_file = {}
        for image_file in image_files:
            future = executor.submit(
                process_image, image_file, output_dir, size, effects, quality
            )
            future_to_file[future] = image_file
        
        # Process results as they complete
        for future in concurrent.futures.as_completed(future_to_file):
            file = future_to_file[future]
            try:
                success, result = future.result()
                if success:
                    successful.append((file, result))
                else:
                    failed.append((file, result))
            except Exception as e:
                logger.error(f"Exception processing {file}: {e}")
                failed.append((file, str(e)))
    
    total_time = time.time() - start_time
    
    return successful, failed, total_time


def process_images_sequential(input_dir, output_dir, size=(800, 600), 
                             effects=None, quality=85):
    """
    Process images sequentially for performance comparison.
    
    Args:
        input_dir: Directory containing input images
        output_dir: Directory to save processed images
        size: Tuple of (width, height) for resizing
        effects: List of effects to apply
        quality: JPEG quality (1-100)
        
    Returns:
        Tuple of (successful, failed, total_time)
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all image files
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
    input_dir = Path(input_dir)
    image_files = [
        f for f in input_dir.iterdir() 
        if f.is_file() and f.suffix.lower() in image_extensions
    ]
    
    # Set total images in progress tracker
    progress_tracker.set_total(len(image_files))
    
    # Process images sequentially
    successful = []
    failed = []
    
    start_time = time.time()
    
    for image_file in image_files:
        success, result = process_image(
            image_file, output_dir, size, effects, quality
        )
        if success:
            successful.append((image_file, result))
        else:
            failed.append((image_file, result))
    
    total_time = time.time() - start_time
    
    return successful, failed, total_time


def generate_sample_images(output_dir, num_images=10, size=(1920, 1080)):
    """
    Generate sample images for testing.
    
    Args:
        output_dir: Directory to save generated images
        num_images: Number of images to generate
        size: Size of generated images
    """
    os.makedirs(output_dir, exist_ok=True)
    
    for i in range(num_images):
        # Create a new image with random color
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        
        img = Image.new('RGB', size, color=(r, g, b))
        
        # Add some shapes to make the image more interesting
        for _ in range(20):
            shape_r = random.randint(0, 255)
            shape_g = random.randint(0, 255)
            shape_b = random.randint(0, 255)
            
            shape_size = random.randint(50, 200)
            x = random.randint(0, size[0] - shape_size)
            y = random.randint(0, size[1] - shape_size)
            
            # Draw a rectangle
            for px in range(x, x + shape_size):
                for py in range(y, y + shape_size):
                    if 0 <= px < size[0] and 0 <= py < size[1]:
                        img.putpixel((px, py), (shape_r, shape_g, shape_b))
        
        # Save the image
        img.save(os.path.join(output_dir, f"sample_{i+1}.jpg"), quality=90)
    
    logger.info(f"Generated {num_images} sample images in {output_dir}")


def initialize_worker():
    """Initialize worker process."""
    # Set up worker-specific state
    pid = os.getpid()
    worker_name = f"ImageWorker-{pid}"
    multiprocessing.current_process().name = worker_name
    
    logger.info(f"Initialized worker process {worker_name}")


def main():
    """Main function handling command-line arguments and execution."""
    parser = argparse.ArgumentParser(description="Process images in parallel using process pools")
    
    # Input and output options
    parser.add_argument("--input", "-i", type=str, help="Input directory with images")
    parser.add_argument("--output", "-o", type=str, help="Output directory for processed images")
    parser.add_argument("--generate", "-g", type=int, help="Generate N sample images for testing")
    
    # Processing options
    parser.add_argument("--width", type=int, default=800, help="Output image width")
    parser.add_argument("--height", type=int, default=600, help="Output image height")
    parser.add_argument("--quality", type=int, default=85, help="JPEG quality (1-100)")
    parser.add_argument("--effects", type=str, nargs="+", choices=["blur", "sharpen", "enhance"],
                       help="Effects to apply to images")
    
    # Execution options
    parser.add_argument("--workers", "-w", type=int, help="Number of worker processes")
    parser.add_argument("--sequential", "-s", action="store_true", 
                       help="Process images sequentially (for comparison)")
    parser.add_argument("--compare", "-c", action="store_true",
                       help="Compare parallel and sequential performance")
    
    args = parser.parse_args()
    
    # Generate sample images if requested
    if args.generate:
        sample_dir = args.input or "sample_images"
        generate_sample_images(sample_dir, args.generate)
        if not args.input:
            args.input = sample_dir
    
    # Validate input and output directories
    if not args.input:
        parser.error("Input directory is required (--input)")
    if not args.output:
        args.output = os.path.join(args.input, "processed")
    
    # Get processing parameters
    size = (args.width, args.height)
    effects = args.effects
    
    # Process images
    if args.compare:
        # Run both sequential and parallel for comparison
        print(f"\n=== Processing images in {args.input} ===")
        print(f"Output directory: {args.output}")
        print(f"Target size: {size[0]}x{size[1]}")
        print(f"Effects: {effects or 'None'}")
        print(f"JPEG quality: {args.quality}")
        
        # Sequential processing
        print("\n--- Sequential Processing ---")
        reset_progress_tracker()
        successful_seq, failed_seq, time_seq = process_images_sequential(
            args.input, os.path.join(args.output, "sequential"),
            size, effects, args.quality
        )
        
        # Parallel processing
        print("\n--- Parallel Processing ---")
        reset_progress_tracker()
        successful_par, failed_par, time_par = process_images_parallel(
            args.input, os.path.join(args.output, "parallel"),
            args.workers, size, effects, args.quality
        )
        
        # Compare results
        print("\n=== Performance Comparison ===")
        print(f"Sequential: Processed {len(successful_seq)} images in {time_seq:.2f} seconds "
              f"({len(successful_seq)/time_seq:.2f} images/sec)")
        print(f"Parallel: Processed {len(successful_par)} images in {time_par:.2f} seconds "
              f"({len(successful_par)/time_par:.2f} images/sec)")
        
        if time_seq > 0:
            speedup = time_seq / time_par
            print(f"Speedup: {speedup:.2f}x faster with process pool")
        
    elif args.sequential:
        # Sequential processing only
        print(f"\n=== Processing images sequentially ===")
        successful, failed, total_time = process_images_sequential(
            args.input, args.output, size, effects, args.quality
        )
        
        print(f"\nProcessed {len(successful)} images in {total_time:.2f} seconds "
              f"({len(successful)/total_time:.2f} images/sec)")
        if failed:
            print(f"Failed to process {len(failed)} images:")
            for file, error in failed[:5]:  # Show first 5 failures
                print(f"  {file.name}: {error}")
            if len(failed) > 5:
                print(f"  ... and {len(failed) - 5} more")
    
    else:
        # Parallel processing only
        print(f"\n=== Processing images in parallel ===")
        successful, failed, total_time = process_images_parallel(
            args.input, args.output, args.workers, size, effects, args.quality
        )
        
        # CPU count information
        cpu_count = multiprocessing.cpu_count()
        workers_used = args.workers or cpu_count
        
        print(f"\nProcessed {len(successful)} images in {total_time:.2f} seconds "
              f"({len(successful)/total_time:.2f} images/sec)")
        print(f"Used {workers_used} worker processes on a system with {cpu_count} CPU cores")
        
        if failed:
            print(f"Failed to process {len(failed)} images:")
            for file, error in failed[:5]:  # Show first 5 failures
                print(f"  {file.name}: {error}")
            if len(failed) > 5:
                print(f"  ... and {len(failed) - 5} more")


def reset_progress_tracker():
    """Reset the progress tracker for a new run."""
    global progress_tracker
    progress_tracker = ProgressTracker()


if __name__ == "__main__":
    # Fix for Windows systems (required for multiprocessing)
    multiprocessing.freeze_support()
    
    # Run the main function
    main()
    
    print("\nKey takeaways from this real-world example:")
    print("1. Process pools provide significant speedup for CPU-bound tasks like image processing")
    print("2. Tracking progress across processes requires shared memory objects")
    print("3. Error handling is crucial for robust applications")
    print("4. Command-line interfaces make your tools more flexible")
    print("5. Performance comparisons help quantify the benefits of parallelization") 