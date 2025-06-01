import os
from typing import Dict, Optional
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Log loaded environment variables
logger.info(f"Loaded environment variables: {os.environ.keys()}")

class AppConfig:
    """Configuration class for the application."""
    
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # API configuration
        self.API_KEY = os.getenv('CONTENT_ANALYZER_API_KEY')
        self.API_URL = os.getenv('CONTENT_ANALYZER_API_URL', 'http://localhost:8000/api')
        
        # Scraping configuration
        self.USER_AGENTS = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15'
        ]
        
        # Network configuration
        self.TIMEOUT = 300000  # 5 minute timeout
        self.DELAY = 10.0  # Increased delay for MoEngage
        self.BATCH_SIZE = 1  # Process one URL at a time
        self.RETRIES = 20  # Increased retries for MoEngage
        
        # Output configuration
        self.OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output")
        
        # Proxy configuration
        self.PROXY = os.getenv('CONTENT_ANALYZER_PROXY', "http://127.0.0.1:8080")  # Local proxy for testing
        
        # Validate required settings
        if not self.API_KEY:
            raise ValueError("API_KEY must be provided in environment variables")
        
        # Log configuration
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
        self.LOG_FILE = os.getenv('LOG_FILE', 'content_analyzer.log')
        
    @staticmethod
    def get_user_agent() -> str:
        """Get a random user agent from the list."""
        return random.choice(AppConfig().USER_AGENTS)
    
    @staticmethod
    def get_api_key() -> str:
        """Get the API key."""
        return AppConfig().API_KEY
    
    @classmethod
    def get_delay(cls) -> float:
        """Get random delay between min and max values."""
        import random
        min_delay = cls().DELAY * 0.8
        max_delay = cls().DELAY * 1.2
        return random.uniform(min_delay, max_delay)
    
    @classmethod
    def get_proxy(cls) -> Optional[str]:
        """Get proxy configuration from environment variables."""
        return cls().PROXY
        proxy = os.getenv("CONTENT_ANALYZER_PROXY")
        if proxy:
            return proxy
        return cls.PROXY
    
    @classmethod
    def get_user_agent(cls) -> str:
        """Get a random user agent."""
        import random
        return random.choice(cls.USER_AGENTS)
    
    @classmethod
    def get_api_key(cls) -> str:
        """Get the API key from environment variables."""
        api_key = os.getenv("CONTENT_ANALYZER_API_KEY")
        if not api_key:
            logger.error("API key not found in environment variables")
            raise ValueError("API key not found. Please set CONTENT_ANALYZER_API_KEY in your .env file")
        return api_key
    
    @classmethod
    def is_api_key_valid(cls) -> bool:
        """Check if API key is valid."""
        api_key = cls.get_api_key()
        return bool(api_key)
    
    @classmethod
    def get_output_dir(cls) -> str:
        """Get the default output directory."""
        output_dir = os.getenv("OUTPUT_DIR", "output")
        os.makedirs(output_dir, exist_ok=True)
        return output_dir
    
    @classmethod
    def get_cache_dir(cls) -> str:
        """Get the cache directory for storing intermediate results."""
        cache_dir = os.getenv("CACHE_DIR", ".cache")
        os.makedirs(cache_dir, exist_ok=True)
        return cache_dir
    
    @classmethod
    def get_default_headers(cls) -> Dict[str, str]:
        """Get default HTTP headers."""
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0"
        }
    
    @classmethod
    def get_proxy(cls) -> Optional[str]:
        """Get proxy configuration from environment variables."""
        return os.getenv("CONTENT_ANALYZER_PROXY")
    
    @classmethod
    def get_timeout(cls) -> int:
        """Get the timeout in milliseconds."""
        timeout = os.getenv("CONTENT_ANALYZER_TIMEOUT")
        if timeout:
            return int(timeout)
        return cls.TIMEOUT
    
    @classmethod
    def get_delay(cls) -> float:
        """Get the delay between requests."""
        delay = os.getenv("CONTENT_ANALYZER_DELAY")
        if delay:
            return float(delay)
        return cls.DEFAULT_DELAY
    
    @classmethod
    def get_retries(cls) -> int:
        """Get the number of retries."""
        retries = os.getenv("CONTENT_ANALYZER_RETRIES")
        if retries:
            return int(retries)
        return cls.MAX_RETRIES
