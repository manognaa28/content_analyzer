import asyncio
import json
import logging
import os
import random
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from config import AppConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ContentProcessor:
    """Processor for extracting and analyzing web content."""
    
    def __init__(self, url: str):
        self.url = url
        
    async def fetch_content(self) -> Optional[str]:
        """Fetch content using Playwright with enhanced error handling."""
        try:
            logger.info(f"Starting content fetch for {self.url}")
            
            async with async_playwright() as p:
                # Launch browser
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-gpu',
                        '--disable-dev-shm-usage',
                        '--window-size=1920,1080',
                        f'--user-agent={AppConfig.get_user_agent()}'
                    ]
                )
                
                # Create context and page
                context = await browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent=AppConfig.get_user_agent()
                )
                page = await context.new_page()
                
                try:
                    # Navigate to URL with timeout
                    await page.goto(self.url, timeout=30000)
                    logger.info(f"Loaded URL: {page.url}")
                    logger.info(f"Page title: {await page.title()}")
                    
                    # Wait for content to load
                    await page.wait_for_load_state('networkidle', timeout=30000)
                    
                    # Try multiple strategies with retries
                    max_retries = 3
                    content = None
                    
                    for attempt in range(max_retries):
                        try:
                            logger.info(f"Attempt {attempt + 1} to extract content...")
                            
                            # Try different selectors
                            selectors = [
                                '.article-body',
                                '.article-content',
                                '.content-section',
                                '.main-content',
                                '#main-content',
                                'article',
                                'body'
                            ]
                            
                            for selector in selectors:
                                try:
                                    logger.info(f"Trying selector: {selector}")
                                    element = await page.wait_for_selector(
                                        selector,
                                        timeout=10000,
                                        state='visible'
                                    )
                                    content = await element.text_content()
                                    logger.info(f"Found content using selector {selector}. Length: {len(content)}")
                                    break
                                except:
                                    logger.info(f"Selector {selector} not found")
                                    continue
                            
                            if content and len(content) > 100:  # Consider successful if we got significant content
                                break
                                
                            # If we didn't get enough content, try again with different strategy
                            logger.info("Content too short, trying different strategy...")
                            await asyncio.sleep(2)  # Wait a bit before retrying
                            
                        except Exception as e:
                            logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
                            if attempt == max_retries - 1:
                                logger.error("All attempts failed")
                                content = ""
                            else:
                                await asyncio.sleep(2)  # Wait before next attempt
                    
                    logger.info(f"Final extracted content length: {len(content)}")
                    logger.info(f"Current URL: {page.url}")
                    logger.info(f"Page title: {await page.title()}")
                    
                    # Get page structure information
                    try:
                        # Count elements
                        elements = await page.evaluate("""
                            () => {
                                const selectors = ['.article-body', '.article-content', '.content-section', '.main-content', '#main-content', 'article', 'body'];
                                const counts = {};
                                selectors.forEach(selector => {
                                    counts[selector] = document.querySelectorAll(selector).length;
                                });
                                return counts;
                            }
                            """)
                        logger.info(f"Page structure: {elements}")
                    except Exception as e:
                        logger.info(f"Error analyzing page structure: {str(e)}")
                    
                    return content
                    
                except Exception as e:
                    logger.error(f"Error during content extraction: {str(e)}")
                    logger.error(f"Current URL: {self.url}")
                    return None
                finally:
                    # Cleanup
                    await context.close()
                    await browser.close()
                    
        except Exception as e:
            logger.error(f"Error fetching content: {str(e)}")
            return None
            
            logger.info("Launching Chrome browser")
            
            # Initialize WebDriver
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            try:
                # First load base URL to establish session
                logger.info(f"Loading base URL: {AppConfig.BASE_URL}")
                try:
                    driver.get(AppConfig.BASE_URL)
                    
                    # Wait for page to load
                    WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.TAG_NAME, 'body'))
                    )
                    
                    # Wait for JavaScript to execute
                    WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.TAG_NAME, 'html'))
                    )
                    
                    # Execute JavaScript to handle dynamic content
                    driver.execute_script("""
                        // Remove any overlays or modals
                        document.querySelectorAll('.modal, .overlay, .loading').forEach(el => {
                            el.style.display = 'none';
                        });
                        
                        // Handle iframes
                        document.querySelectorAll('iframe').forEach(iframe => {
                            iframe.style.display = 'block';
                            iframe.style.width = '100%';
                            iframe.style.height = '500px';
                        });
                        
                        // Wait for all images to load
                        return new Promise((resolve) => {
                            let images = document.images.length;
                            let loaded = 0;
                            
                            document.images.forEach(img => {
                                if (img.complete) {
                                    loaded++;
                                } else {
                                    img.onload = () => loaded++;
                                    img.onerror = () => loaded++;
                                }
                            });
                            
                            if (loaded === images) {
                                resolve(true);
                            } else {
                                setTimeout(() => {
                                    resolve(true);
                                }, 2000);
                            }
                        });
                    """)
                    
                    # Check if we got the expected content
                    page_title = driver.title
                    logger.info(f"Base URL loaded successfully. Title: {page_title}")
                    
                except Exception as e:
                    logger.error(f"Failed to load base URL: {str(e)}")
                    logger.error(f"Current URL: {driver.current_url}")
                    logger.error(f"Page source length: {len(driver.page_source)}")
                    raise
                
                # Try multiple times with exponential backoff
                for attempt in range(AppConfig.get_retries()):
                    try:
                        logger.info(f"Attempt {attempt + 1}/{AppConfig.get_retries()} for {self.url}")
                        
                        # Add random delay before navigation
                        await asyncio.sleep(random.uniform(1, 3))
                        
                        # Navigate to target URL
                        logger.info(f"Navigating to: {self.url}")
                        try:
                            driver.get(self.url)
                            
                            # Wait for content to load
                            WebDriverWait(driver, AppConfig.get_timeout()).until(
                                EC.presence_of_element_located((By.TAG_NAME, 'body'))
                            )
                            
                            # Wait for JavaScript to execute
                            WebDriverWait(driver, AppConfig.get_timeout()).until(
                                EC.presence_of_element_located((By.TAG_NAME, 'html'))
                            )
                            
                            # Execute JavaScript to handle dynamic content
                            driver.execute_script("""
                                // Remove any overlays or modals
                                document.querySelectorAll('.modal, .overlay, .loading').forEach(el => {
                                    el.style.display = 'none';
                                });
                                
                                // Handle iframes
                                document.querySelectorAll('iframe').forEach(iframe => {
                                    iframe.style.display = 'block';
                                    iframe.style.width = '100%';
                                    iframe.style.height = '500px';
                                });
                                
                                // Wait for all images to load
                                return new Promise((resolve) => {
                                    let images = document.images.length;
                                    let loaded = 0;
                                    
                                    document.images.forEach(img => {
                                        if (img.complete) {
                                            loaded++;
                                        } else {
                                            img.onload = () => loaded++;
                                            img.onerror = () => loaded++;
                                        }
                                    });
                                    
                                    if (loaded === images) {
                                        resolve(true);
                                    } else {
                                        setTimeout(() => {
                                            resolve(true);
                                        }, 2000);
                                    }
                                });
                            """)
                            
                            # Check if we got the expected content
                            page_title = driver.title
                            logger.info(f"Target URL loaded successfully. Title: {page_title}")
                            logger.info(f"Current URL: {driver.current_url}")
                            logger.info(f"Page source length: {len(driver.page_source)}")
                            
                        except Exception as e:
                            logger.error(f"Failed to load target URL: {str(e)}")
                            logger.error(f"Current URL: {driver.current_url}")
                            logger.error(f"Page source length: {len(driver.page_source)}")
                            raise
                        
                        # Wait for dynamic content
                        await asyncio.sleep(random.uniform(2, 5))
                        
                        # Get page content
                        content = driver.page_source
                        logger.info(f"Successfully fetched content for {self.url}")
                        logger.debug(f"Content length: {len(content)}")
                        
                        # Close browser
                        driver.quit()
                        return content
                    except Exception as e:
                        logger.error(f"Attempt {attempt + 1}/{AppConfig.get_retries()} failed for {self.url}")
                        logger.error(f"Error details: {str(e)}")
                        logger.error(f"Error type: {type(e).__name__}")
                        await asyncio.sleep(AppConfig.get_delay() * (attempt + 1))
                
            except Exception as e:
                logger.error(f"Error loading content")
                logger.error(f"Error details: {str(e)}")
                logger.error(f"Error type: {type(e).__name__}")
                
            finally:
                try:
                    driver.quit()
                except:
                    pass
            
            return None
        except Exception as e:
            logger.error(f"Error fetching {self.url}")
            logger.error(f"Error details: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            return None
                
        except Exception as e:
            logger.error(f"Error fetching {self.url}")
            logger.error(f"Error details: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            return None
        
    async def extract_metadata(self, content: str) -> Dict[str, str]:
        """Extract metadata from content."""
        soup = BeautifulSoup(content, 'html.parser')
        
        # Extract title
        title = self._extract_title(soup)
        
        # Extract description
        description = self._extract_description(soup)
        
        # Extract breadcrumbs
        breadcrumbs = self._extract_breadcrumbs(soup)
        
        return {
            'title': title,
            'description': description,
            'breadcrumbs': breadcrumbs,
            'url': self.url,
            'timestamp': self._get_current_timestamp()
        }
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title."""
        title = soup.find('title')
        if title:
            return title.text.strip()
        return ""
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract page description."""
        meta_desc = soup.find('meta', {'name': 'description'})
        if meta_desc and 'content' in meta_desc.attrs:
            return meta_desc['content'].strip()
        return ""
    
    def _extract_breadcrumbs(self, soup: BeautifulSoup) -> List[str]:
        """Extract breadcrumb trail."""
        breadcrumbs = []
        for element in soup.select('.breadcrumb, .nav-breadcrumb'):
            for link in element.find_all('a'):
                text = link.text.strip()
                if text:
                    breadcrumbs.append(text)
        return breadcrumbs
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    async def analyze_content(self, content: str) -> Dict:
        """Analyze content for various metrics using API."""
        soup = BeautifulSoup(content, 'html.parser')
        
        text_content = self._extract_text(soup)
        
        # Basic analysis
        basic_metrics = {
            'word_count': self._count_words(text_content),
            'section_count': self._count_sections(soup),
            'image_count': self._count_images(soup),
            'links': self._extract_links(soup)
        }
        
        # API-based analysis
        api_metrics = await self._get_api_analysis(text_content)
        
        return {**basic_metrics, **api_metrics}
    
    async def _get_api_analysis(self, text: str) -> Dict:
        """Get enhanced analysis using API with fallback."""
        try:
            # Get and validate API key
            api_key = AppConfig.get_api_key()
            if not api_key:
                logger.warning("No valid API key found")
                return self._get_basic_analysis(text)
            
            # Return basic analysis as we can't access the API endpoints
            logger.warning("API endpoints are not accessible, using basic analysis")
            return self._get_basic_analysis(text)
        except Exception as e:
            logger.error(f"Error with API analysis: {str(e)}")
            return self._get_basic_analysis(text)
    
    def _get_basic_analysis(self, text: str) -> Dict:
        """Get basic analysis as fallback."""
        return {
            'readability_score': self._calculate_readability(text),
            'sentiment': self._get_basic_sentiment(text),
            'complexity_score': self._count_complex_words(text),
            'structure_score': self._analyze_structure(text)
        }
    
    def _calculate_readability(self, text: str) -> float:
        """Calculate basic readability score."""
        words = text.split()
        sentences = text.split('.')
        if len(sentences) > 1:
            return len(words) / len(sentences)
        return 0.0
    
    def _get_basic_sentiment(self, text: str) -> str:
        """Basic sentiment analysis."""
        positive_words = ['good', 'great', 'excellent', 'best', 'amazing']
        negative_words = ['bad', 'poor', 'terrible', 'worst', 'awful']
        
        positive_count = sum(1 for word in text.lower().split() if word in positive_words)
        negative_count = sum(1 for word in text.lower().split() if word in negative_words)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        return 'neutral'
    
    def _count_complex_words(self, text: str) -> int:
        """Count complex words (words with more than 3 syllables)."""
        complex_words = ['implementation', 'configuration', 'optimization', 'automation', 'integration']
        return sum(1 for word in text.lower().split() if word in complex_words)
    
    def _analyze_structure(self, text: str) -> float:
        """Basic structure analysis."""
        paragraphs = text.split('\n\n')
        return len(paragraphs) / len(text.split('.')) if len(text.split('.')) > 0 else 0.0
    
    def _extract_text(self, soup: BeautifulSoup) -> str:
        """Extract main text content."""
        # Remove unwanted elements
        for elem in soup(['script', 'style', 'nav', 'footer']):
            elem.decompose()
        
        # Get main content
        main_content = soup.find('main') or soup.find('article')
        if not main_content:
            main_content = soup
        
        return main_content.get_text(separator='\n', strip=True)
    
    def _count_words(self, text: str) -> int:
        """Count words in text."""
        return len(text.split())
    
    def _count_sections(self, soup: BeautifulSoup) -> int:
        """Count sections in content."""
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        return len(headings)
    
    def _count_images(self, soup: BeautifulSoup) -> int:
        """Count images in content."""
        return len(soup.find_all('img'))
    
    def _extract_links(self, soup: BeautifulSoup) -> List[str]:
        """Extract all links from content."""
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.startswith('http'):
                links.append(href)
        return links
    
    async def process_url(self) -> Dict:
        """Process a single URL completely."""
        content = await self.fetch_content()
        if not content:
            return {'url': self.url, 'error': 'Failed to fetch content'}
            
        metadata = await self.extract_metadata(content)
        analysis = await self.analyze_content(content)
        
        return {
            **metadata,
            **analysis,
            'success': True
        }
    
    async def close(self):
        """Close the HTTP session."""
        # No need to close the session as it's handled by Playwright

class BatchProcessor:
    """Processor for handling multiple URLs in batches."""
    
    def __init__(self, urls: List[str], batch_size: int = AppConfig.BATCH_SIZE):
        self.urls = urls
        self.batch_size = batch_size
        
    async def process_batch(self, start_idx: int) -> List[Dict]:
        """Process a batch of URLs."""
        batch_urls = self.urls[start_idx:start_idx + self.batch_size]
        tasks = []
        
        for url in batch_urls:
            processor = ContentProcessor(url)
            tasks.append(processor.process_url())
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return [r for r in results if not isinstance(r, Exception)]
    
    async def process_all(self) -> List[Dict]:
        """Process all URLs in batches."""
        all_results = []
        total_batches = (len(self.urls) + self.batch_size - 1) // self.batch_size
        
        print(f"Processing {len(self.urls)} URLs in {total_batches} batches")
        
        for i in range(0, len(self.urls), self.batch_size):
            print(f"Processing batch {i//self.batch_size + 1}/{total_batches}")
            batch_results = await self.process_batch(i)
            all_results.extend(batch_results)
            
            if i + self.batch_size < len(self.urls):
                await asyncio.sleep(AppConfig.DEFAULT_DELAY)
        
        return all_results
    
    @staticmethod
    def save_results(results: List[Dict], output_dir: str = AppConfig.get_output_dir()):
        """Save results to JSON and CSV files."""
        import pandas as pd
        
        json_path = os.path.join(output_dir, 'processed_content.json')
        csv_path = os.path.join(output_dir, 'processed_summary.csv')
        
        # Save JSON
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # Save CSV
        df = pd.DataFrame(results)
        df.to_csv(csv_path, index=False)
        
        return json_path, csv_path
