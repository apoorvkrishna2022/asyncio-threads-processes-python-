"""
# Real-World Async Application Example
# ==================================
#
# This tutorial builds a complete real-world application using AsyncIO.
# The application is a simple web crawler that fetches and processes web pages concurrently.
"""

import asyncio
import aiohttp
import aiofiles
import logging
import time
import os
import re
import sys
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup  # pip install beautifulsoup4

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


# Web Crawler Application
# ---------------------
# A complete application that demonstrates asyncio in a real-world scenario

class AsyncWebCrawler:
    """Asynchronous web crawler that fetches and processes web pages concurrently."""
    
    def __init__(self, start_url, max_depth=2, max_tasks=10, output_dir="crawler_output"):
        self.start_url = start_url
        self.max_depth = max_depth
        self.max_tasks = max_tasks  # Maximum number of concurrent tasks
        self.output_dir = output_dir
        
        # Set to keep track of visited URLs
        self.visited_urls = set()
        
        # Semaphore to limit concurrent requests
        self.semaphore = asyncio.Semaphore(max_tasks)
        
        # Session for HTTP requests
        self.session = None
        
        # Queue for URLs to be processed
        self.url_queue = asyncio.Queue()
        
        # URL normalization
        self.base_domain = urlparse(start_url).netloc
    
    async def initialize(self):
        """Initialize the crawler by setting up output directory and session."""
        # Create output directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            logger.info(f"Created output directory: {self.output_dir}")
        
        # Create an HTTP session with cookies support and connection pooling
        self.session = aiohttp.ClientSession(
            headers={"User-Agent": "AsyncWebCrawler/1.0"}
        )
        
        # Add the start URL to the queue
        await self.url_queue.put((self.start_url, 0))  # (url, depth)
    
    async def close(self):
        """Close resources when done."""
        if self.session:
            await self.session.close()
            logger.info("HTTP session closed")
    
    def normalize_url(self, url, base_url):
        """Normalize a URL to avoid duplicates."""
        # Make relative URLs absolute
        full_url = urljoin(base_url, url)
        
        # Parse the URL
        parsed = urlparse(full_url)
        
        # Only keep URLs from the same domain
        if parsed.netloc != self.base_domain:
            return None
        
        # Remove fragments
        normalized = parsed._replace(fragment="").geturl()
        
        return normalized
    
    def generate_filename(self, url):
        """Generate a safe filename from a URL."""
        # Extract the path from the URL
        path = urlparse(url).path
        
        # Use the last part of the path as the filename
        if path and path != "/":
            filename = path.strip("/").replace("/", "_")
            if not filename:
                filename = "index"
        else:
            filename = "index"
        
        # Add the domain to make the filename unique
        domain = urlparse(url).netloc.replace(".", "_")
        
        # Return the full path
        return os.path.join(self.output_dir, f"{domain}_{filename}.html")
    
    async def fetch_url(self, url, depth):
        """Fetch a URL and process it."""
        # Skip if already visited
        if url in self.visited_urls:
            return
        
        # Mark as visited to avoid duplicates
        self.visited_urls.add(url)
        
        # Use semaphore to limit concurrent requests
        async with self.semaphore:
            try:
                logger.info(f"Fetching URL: {url} (Depth: {depth})")
                
                # Fetch the URL with a timeout
                async with self.session.get(url, timeout=10) as response:
                    if response.status != 200:
                        logger.warning(f"Failed to fetch {url}: HTTP {response.status}")
                        return
                    
                    # Read the content
                    content = await response.text()
                    
                    # Process the content
                    await self.process_content(url, content, depth)
                    
                    # Save the content to a file
                    await self.save_content(url, content)
                
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                logger.error(f"Error fetching {url}: {e}")
            except Exception as e:
                logger.exception(f"Unexpected error processing {url}: {e}")
    
    async def process_content(self, url, content, depth):
        """Process the content of a page, extracting links and other information."""
        # Only extract links if we haven't reached the maximum depth
        if depth >= self.max_depth:
            return
        
        # Use BeautifulSoup to parse the HTML
        soup = BeautifulSoup(content, 'html.parser')
        
        # Find all links
        links = soup.find_all('a', href=True)
        
        # Process each link
        for link in links:
            href = link['href']
            
            # Normalize the URL
            normalized_url = self.normalize_url(href, url)
            
            # Skip if None (external domain) or already visited
            if normalized_url is None or normalized_url in self.visited_urls:
                continue
            
            # Add to the queue for processing
            await self.url_queue.put((normalized_url, depth + 1))
            logger.debug(f"Queued URL: {normalized_url} (Depth: {depth + 1})")
    
    async def save_content(self, url, content):
        """Save the page content to a file."""
        filename = self.generate_filename(url)
        
        # Add some metadata to the content
        metadata = f"""<!--
URL: {url}
Fetched at: {time.strftime('%Y-%m-%d %H:%M:%S')}
-->

"""
        content_with_metadata = metadata + content
        
        # Save to file
        async with aiofiles.open(filename, 'w', encoding='utf-8') as f:
            await f.write(content_with_metadata)
            
        logger.info(f"Saved content to {filename}")
    
    async def process_queue(self):
        """Process URLs from the queue until it's empty."""
        tasks = []
        
        # Start with the initial URL
        while not self.url_queue.empty() or tasks:
            # Process new URLs from the queue
            while not self.url_queue.empty() and len(tasks) < self.max_tasks:
                url, depth = await self.url_queue.get()
                
                # Create a task for this URL
                task = asyncio.create_task(self.fetch_url(url, depth))
                tasks.append(task)
            
            # Wait for at least one task to complete if we have tasks
            if tasks:
                done, tasks = await asyncio.wait(
                    tasks, return_when=asyncio.FIRST_COMPLETED
                )
                
                # Check for exceptions
                for task in done:
                    if task.exception():
                        logger.error(f"Task error: {task.exception()}")
            else:
                # No tasks running, likely waiting for the queue
                await asyncio.sleep(0.1)
    
    async def crawl(self):
        """Run the crawler."""
        start_time = time.time()
        logger.info(f"Starting crawler with URL: {self.start_url}")
        
        try:
            # Initialize
            await self.initialize()
            
            # Process the queue of URLs
            await self.process_queue()
            
        finally:
            # Clean up
            await self.close()
        
        elapsed = time.time() - start_time
        logger.info(f"Crawling completed in {elapsed:.2f} seconds")
        logger.info(f"Visited {len(self.visited_urls)} URLs")
        
        return self.visited_urls


# Stats Collector
# ------------
# A class to aggregate and analyze the crawler results

class CrawlerStats:
    """Collects and analyzes statistics from the crawler results."""
    
    def __init__(self, output_dir):
        self.output_dir = output_dir
    
    async def collect_stats(self):
        """Collect statistics from the crawled pages."""
        # Count files and total size
        file_count = 0
        total_size = 0
        
        # Dictionaries to store stats
        domain_counts = {}
        word_frequencies = {}
        
        for filename in os.listdir(self.output_dir):
            if not filename.endswith('.html'):
                continue
            
            file_count += 1
            file_path = os.path.join(self.output_dir, filename)
            total_size += os.path.getsize(file_path)
            
            # Extract domain from filename
            if '_' in filename:
                domain = filename.split('_')[0]
                domain_counts[domain] = domain_counts.get(domain, 0) + 1
            
            # Read the file content and analyze
            try:
                async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    
                    # Extract text from HTML
                    soup = BeautifulSoup(content, 'html.parser')
                    text = soup.get_text()
                    
                    # Count word frequencies
                    words = re.findall(r'\w+', text.lower())
                    for word in words:
                        if len(word) > 3:  # Only count words longer than 3 letters
                            word_frequencies[word] = word_frequencies.get(word, 0) + 1
            
            except Exception as e:
                logger.error(f"Error analyzing file {filename}: {e}")
        
        return {
            'file_count': file_count,
            'total_size_kb': total_size / 1024,
            'domain_counts': domain_counts,
            'top_words': sorted(word_frequencies.items(), key=lambda x: x[1], reverse=True)[:20]
        }
    
    def print_stats(self, stats):
        """Print the collected statistics."""
        print("\n" + "=" * 40)
        print("CRAWLER STATISTICS")
        print("=" * 40)
        
        print(f"\nTotal files: {stats['file_count']}")
        print(f"Total size: {stats['total_size_kb']:.2f} KB")
        
        print("\nDomain distribution:")
        for domain, count in stats['domain_counts'].items():
            print(f"  {domain}: {count} files")
        
        print("\nTop 20 words:")
        for word, count in stats['top_words']:
            print(f"  {word}: {count} occurrences")
        
        print("\n" + "=" * 40)


# Main Application
# -------------

async def main():
    """Main application entry point."""
    
    # Display introduction
    print("AsyncIO Web Crawler Example")
    print("==========================")
    print("This application demonstrates a real-world async application.")
    print("It will crawl a website, extracting links and saving pages concurrently.")
    print("Required packages: aiohttp, aiofiles, beautifulsoup4\n")
    
    # Check if we have the required packages
    try:
        import aiohttp
        import aiofiles
        import bs4
    except ImportError as e:
        print(f"Error: Missing required package - {e}")
        print("Please install the required packages:")
        print("pip install aiohttp aiofiles beautifulsoup4")
        return
    
    # Default URL to crawl if not provided
    default_url = "https://quotes.toscrape.com/"
    
    # Get URL from command line or use default
    url = sys.argv[1] if len(sys.argv) > 1 else default_url
    
    # Create output directory
    output_dir = "crawler_output"
    
    # Create and run the crawler
    crawler = AsyncWebCrawler(
        start_url=url,
        max_depth=2,
        max_tasks=10,
        output_dir=output_dir
    )
    
    visited_urls = await crawler.crawl()
    
    # Collect and display statistics
    stats_collector = CrawlerStats(output_dir)
    stats = await stats_collector.collect_stats()
    stats_collector.print_stats(stats)
    
    # End message
    print("\nThe web crawler has completed its job.")
    print(f"All pages have been saved to the '{output_dir}' directory.")
    print("You can open these HTML files in your browser to view the content.")


# Running the Application
# --------------------

if __name__ == "__main__":
    print("Real-World Async Application Example\n")
    
    # Check if we have the required packages before running
    packages_missing = False
    
    try:
        import aiohttp
    except ImportError:
        packages_missing = True
        print("Missing package: aiohttp")
    
    try:
        import aiofiles
    except ImportError:
        packages_missing = True
        print("Missing package: aiofiles")
    
    try:
        import bs4
    except ImportError:
        packages_missing = True
        print("Missing package: beautifulsoup4")
    
    if packages_missing:
        print("\nPlease install the required packages with:")
        print("pip install aiohttp aiofiles beautifulsoup4")
    else:
        # Run the main application
        asyncio.run(main()) 