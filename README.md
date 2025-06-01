# Web Content Analyzer

A powerful tool for analyzing web content quality and extracting valuable insights.

## Features

- Content Discovery: Automatically discover URLs from a base website
- Content Extraction: Extract structured content including text, metadata, and media
- Content Analysis: Performs comprehensive content analysis including:
  - Word count and text statistics
  - Section and heading analysis
  - Image and media count
  - Link extraction and analysis
  - Basic readability scoring
  - Sentiment analysis
  - Content complexity metrics
  - Structural analysis
- Batch Processing: Process multiple URLs efficiently with configurable batch sizes
- Output Formats: Save results in both JSON and CSV formats for easy analysis
- Configurable: Customize delays, retries, and batch sizes for optimal performance

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with any required API keys (if needed):
```
CONTENT_ANALYZER_API_KEY=your_api_key_here
OUTPUT_DIR=output
CACHE_DIR=.cache
```

## Usage

### Discover URLs

Discover URLs from a base website:
```bash
python main.py discover --url https://example.com --output discovered_urls.json
```

### Process Content

Process content from a file containing URLs:
```bash
python main.py process --urls urls.txt --batch-size 5 --delay 1.0
```

### Command Line Options

```bash
usage: main.py [-h] {discover,process} ...

Web Content Analyzer - Analyze web content for quality metrics

positional arguments:
  {discover,process}
    discover            Discover URLs from a base URL
    process             Process content from URLs

optional arguments:
  -h, --help            show this help message and exit
```

## Output

The tool generates two types of output files:

1. JSON file with detailed content analysis
2. CSV file with summary statistics

Both files are saved in the configured output directory (default: `output/`).

## Requirements

- Python 3.7+
- Required packages (see requirements.txt):
  - httpx
  - beautifulsoup4
  - pandas
  - python-dotenv

## License

MIT License
