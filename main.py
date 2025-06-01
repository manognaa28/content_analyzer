import argparse
import asyncio
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional
from content_processor import ContentProcessor
from config import AppConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_parser() -> argparse.ArgumentParser:
    """Create command line argument parser."""
    parser = argparse.ArgumentParser(
        description="Web Content Analyzer - Analyze web content for quality metrics"
    )
    
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # Discover command
    discover_parser = subparsers.add_parser(
        'discover',
        help='Discover URLs from a base URL'
    )
    discover_parser.add_argument(
        '--url',
        default=AppConfig.BASE_URL,
        help='Base URL to discover content from'
    )
    discover_parser.add_argument(
        '--output',
        default=os.path.join(AppConfig.get_output_dir(), 'discovered_urls.json'),
        help='Output file for discovered URLs'
    )
    
    # Process command
    process_parser = subparsers.add_parser(
        'process',
        help='Process content from URLs'
    )
    process_parser.add_argument(
        '--urls',
        required=True,
        help='File containing URLs to process (one per line)'
    )
    process_parser.add_argument(
        '--batch-size',
        type=int,
        default=AppConfig.BATCH_SIZE,
        help='Number of URLs to process in parallel'
    )
    process_parser.add_argument(
        '--delay',
        type=float,
        default=AppConfig.DEFAULT_DELAY,
        help='Delay between batches in seconds'
    )
    
    return parser

async def discover_urls(base_url: str, output_file: str) -> None:
    """Discover URLs from a base URL."""
    print(f"Discovering URLs from {base_url}...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(base_url)
            response.raise_for_status()
            
            # Simple discovery - find all links
            soup = BeautifulSoup(response.text, 'html.parser')
            links = []
            
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.startswith('/'):
                    links.append(href)
                    
            with open(output_file, 'w') as f:
                json.dump(links, f, indent=2)
                
    except Exception as e:
        print(f"Error discovering URLs: {str(e)}")

async def process_url(url: str) -> Dict:
    """Process a single URL and return analysis results."""
    try:
        processor = ContentProcessor(url)
        content = await processor.fetch_content()
        
        if content:
            return {
                'url': url,
                'status': 'success',
                'content': content,
                'length': len(content)
            }
        else:
            return {
                'url': url,
                'status': 'error',
                'error': 'No content extracted'
            }
    except Exception as e:
        logger.error(f"Error processing URL {url}: {str(e)}")
        return {
            'url': url,
            'status': 'error',
            'error': str(e)
        }

async def process_batch(urls: List[str], batch_size: int = 3, delay: float = 2.0) -> List[Dict]:
    """Process a batch of URLs with rate limiting."""
    results = []
    
    for i in range(0, len(urls), batch_size):
        batch = urls[i:i + batch_size]
        logger.info(f"Processing batch {i//batch_size + 1}/{(len(urls) + batch_size - 1)//batch_size}")
        
        # Process batch asynchronously
        batch_results = await asyncio.gather(*[
            process_url(url) for url in batch
        ])
        results.extend(batch_results)
        
        # Delay between batches
        if i + batch_size < len(urls):
            logger.info(f"Waiting {delay} seconds before next batch...")
            await asyncio.sleep(delay)
    
    return results

async def main():
    parser = argparse.ArgumentParser(description="Documentation Content Analyzer")
    parser.add_argument('urls', nargs='*', help='URLs to analyze')
    parser.add_argument('--urls-file', help='File containing URLs to analyze')
    parser.add_argument('--batch-size', type=int, default=3, help='Number of URLs to process in parallel')
    parser.add_argument('--delay', type=float, default=2.0, help='Delay between batches in seconds')
    parser.add_argument('--output-dir', default='output', help='Directory to save results')
    
    args = parser.parse_args()
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # Get URLs to process
    urls = args.urls
    if args.urls_file:
        with open(args.urls_file, 'r') as f:
            urls.extend(line.strip() for line in f if line.strip())
    
    if not urls:
        parser.error("No URLs provided")
        return
    
    logger.info(f"Processing {len(urls)} URLs")
    
    # Process URLs
    results = await process_batch(urls, args.batch_size, args.delay)
    
    # Save results
    json_output = output_dir / 'processed_content.json'
    csv_output = output_dir / 'processed_summary.csv'
    
    # Save JSON
    with open(json_output, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Save CSV summary
    with open(csv_output, 'w', encoding='utf-8') as f:
        f.write("URL,Status,Content Length,Error\n")
        for result in results:
            f.write(f"{result['url']},{result['status']},{result.get('length', 0)},""")
            if result['status'] == 'error':
                f.write(f"{result['error']}")
            f.write("\n")
    
    # Print statistics
    successful = len([r for r in results if r['status'] == 'success'])
    failed = len([r for r in results if r['status'] == 'error'])
    total = len(results)
    
    logger.info("\nProcessing complete!")
    logger.info(f"Results saved to:")
    logger.info(f"  JSON: {json_output}")
    logger.info(f"  CSV: {csv_output}")
    logger.info("\nStatistics:")
    logger.info(f"  Total URLs: {total}")
    logger.info(f"  Successful: {successful}")
    logger.info(f"  Failed: {failed}")
    logger.info(f"  Success rate: {(successful/total)*100:.1f}%")

if __name__ == "__main__":
    asyncio.run(main())
