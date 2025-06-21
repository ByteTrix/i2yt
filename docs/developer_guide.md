# Developer Guide

Complete guide for developers who want to understand, modify, or contribute to the Instagram to YouTube automation tool.

## Project Architecture

### High-Level Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CLI Layer     │    │  Configuration  │    │   Logging       │
│ (run_scraper.py)│    │   (config.py)   │    │   System        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
         ┌─────────────────────────────────────────────────────────┐
         │            Core Scraper Engine                          │
         │         (instagram_reel_scraper.py)                     │
         └─────────────────────────────────────────────────────────┘
                                 │
    ┌────────────────┬───────────┼───────────┬────────────────────┐
    │                │           │           │                    │
┌───▼───┐    ┌──────▼──────┐   ▼   ┌───────▼────┐    ┌─────────▼──────┐
│Browser│    │Data         │  API  │Google      │    │Error           │
│Control│    │Processing   │       │Sheets      │    │Handling        │
│       │    │& Validation │       │Integration │    │& Recovery      │
└───────┘    └─────────────┘       └────────────┘    └────────────────┘
```

### Core Components

#### 1. Main Scraper Engine (`instagram_reel_scraper.py`)

**Purpose**: Core scraping logic and coordination

**Key Classes**:
- `InstagramReelScraper`: Main scraper class
- `ChromeManager`: Browser management
- `DataProcessor`: Data processing and validation
- `SheetsIntegration`: Google Sheets operations

**Responsibilities**:
- Browser automation
- Content discovery and extraction
- Data processing and validation
- Google Sheets integration
- Error handling and logging

#### 2. CLI Interface (`run_scraper.py`)

**Purpose**: Command-line interface and script orchestration

**Key Functions**:
- `main()`: Entry point and argument parsing
- `setup_logging()`: Configure logging system
- `load_config()`: Load and validate configuration
- `run_scraper()`: Execute scraping operation

#### 3. Configuration System (`config.py`)

**Purpose**: Centralized configuration management

**Configuration Categories**:
- Instagram URLs and account settings
- Google Sheets API configuration
- Browser and scraping behavior
- Logging and debugging options
- Performance and optimization settings

### Data Flow

```
1. Configuration Loading
   ↓
2. Browser Initialization
   ↓
3. Instagram Authentication
   ↓
4. Account Processing Loop
   ├── Navigate to Account
   ├── Scroll and Discover Content
   ├── Extract Reel Data
   ├── Validate and Process Data
   └── Save to Google Sheets
   ↓
5. Cleanup and Reporting
```

## Code Structure and Standards

### File Organization

```
project_root/
├── instagram_reel_scraper.py    # Core scraper implementation
├── run_scraper.py               # CLI interface
├── config_template.py           # Configuration template
├── config.py                    # User configuration (gitignored)
├── tests/                       # Test files
│   ├── test_google_api.py
│   ├── test_sheets.py
│   └── demo.py
├── docs/                        # Documentation
│   ├── quick_start.md
│   ├── configuration.md
│   ├── google_sheets_setup.md
│   ├── n8n_integration.md
│   ├── troubleshooting.md
│   ├── advanced_usage.md
│   └── developer_guide.md
├── .github/workflows/           # CI/CD pipelines
│   └── download.yml
├── login_to_instagram.bat       # Login helper script
├── start_chrome_debug.bat       # Debug helper script
├── requirements.txt             # Python dependencies
├── setup.py                     # Package configuration
├── insta to yt.json            # n8n workflow template
└── README.md                    # Main documentation
```

### Code Standards

#### Python Style Guide

Follow PEP 8 with these specific conventions:

```python
# Imports organization
import os
import sys
import json
from typing import List, Dict, Optional, Union
from datetime import datetime, timedelta

# Third-party imports
import requests
from selenium import webdriver
from googleapiclient.discovery import build

# Local imports
from config import *

# Class naming: PascalCase
class InstagramReelScraper:
    """Main scraper class for Instagram reels."""
    
    def __init__(self, config: Dict):
        """Initialize scraper with configuration."""
        self.config = config
        self.logger = self._setup_logger()
    
    # Method naming: snake_case
    def scrape_account_reels(self, account_url: str) -> List[Dict]:
        """Scrape reels from a specific Instagram account."""
        pass
    
    # Private methods: underscore prefix
    def _setup_logger(self) -> logging.Logger:
        """Set up logging configuration."""
        pass

# Constants: UPPER_SNAKE_CASE
DEFAULT_TIMEOUT = 30
MAX_RETRIES = 3
REEL_LINK_PATTERN = r'/reel/[A-Za-z0-9_-]+'

# Variables: snake_case
reel_count = 0
user_data = {}
```

#### Documentation Standards

```python
def scrape_reels(self, account_url: str, days: int = 30, limit: int = 0) -> List[Dict]:
    """
    Scrape Instagram reels from a specific account.
    
    Args:
        account_url (str): Full Instagram account URL
        days (int, optional): Number of days to look back. Defaults to 30.
        limit (int, optional): Maximum reels to collect. 0 means unlimited.
    
    Returns:
        List[Dict]: List of reel data dictionaries containing:
            - date: Posting date
            - username: Instagram username
            - link: Direct reel URL
            - reel_id: Unique reel identifier
            - caption: Reel caption text
            - hashtags: List of hashtags
    
    Raises:
        ScrapingError: If account cannot be accessed
        TimeoutError: If operation times out
        
    Example:
        >>> scraper = InstagramReelScraper(config)
        >>> reels = scraper.scrape_reels('https://instagram.com/account', days=7)
        >>> print(f"Found {len(reels)} reels")
    """
    pass
```

#### Error Handling Patterns

```python
# Custom exceptions
class ScrapingError(Exception):
    """Base exception for scraping operations."""
    pass

class AuthenticationError(ScrapingError):
    """Raised when Instagram authentication fails."""
    pass

class DataValidationError(ScrapingError):
    """Raised when scraped data fails validation."""
    pass

# Error handling with logging
def safe_operation(self, operation, *args, **kwargs):
    """Execute operation with error handling and logging."""
    try:
        return operation(*args, **kwargs)
    except AuthenticationError as e:
        self.logger.error(f"Authentication failed: {e}")
        self._handle_auth_error(e)
        raise
    except DataValidationError as e:
        self.logger.warning(f"Data validation failed: {e}")
        return None
    except Exception as e:
        self.logger.error(f"Unexpected error in {operation.__name__}: {e}")
        raise ScrapingError(f"Operation failed: {e}") from e
```

## Key Components Deep Dive

### Browser Management

The `ChromeManager` class handles all browser operations:

```python
class ChromeManager:
    """Manages Chrome browser instance for scraping."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.driver = None
        self.profile_path = config.get('CHROME_PROFILE_PATH', './instagram_profile')
    
    def initialize_browser(self) -> webdriver.Chrome:
        """Initialize Chrome browser with configuration."""
        options = self._get_chrome_options()
        
        try:
            self.driver = webdriver.Chrome(options=options)
            self._configure_browser()
            return self.driver
        except Exception as e:
            raise BrowserInitializationError(f"Failed to initialize browser: {e}")
    
    def _get_chrome_options(self) -> webdriver.ChromeOptions:
        """Configure Chrome options based on configuration."""
        options = webdriver.ChromeOptions()
        
        # Profile management
        options.add_argument(f"--user-data-dir={self.profile_path}")
        
        # Performance optimization
        if self.config.get('HEADLESS_MODE', False):
            options.add_argument('--headless')
        
        if self.config.get('USE_FAST_MODE', False):
            options.add_argument('--disable-images')
            options.add_argument('--disable-javascript')
        
        # Security and stability
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        return options
```

### Data Processing Pipeline

The data processing follows a clear pipeline:

```python
class DataProcessor:
    """Processes and validates scraped data."""
    
    def process_reel_data(self, raw_data: Dict) -> Optional[Dict]:
        """
        Process raw reel data through validation pipeline.
        
        Pipeline stages:
        1. Data extraction and cleaning
        2. Validation against schema
        3. Duplicate detection
        4. Enrichment with metadata
        5. Format standardization
        """
        try:
            # Stage 1: Extract and clean
            cleaned_data = self._clean_raw_data(raw_data)
            
            # Stage 2: Validate
            if not self._validate_data(cleaned_data):
                return None
            
            # Stage 3: Check duplicates
            if self._is_duplicate(cleaned_data):
                self.logger.info(f"Duplicate reel detected: {cleaned_data['reel_id']}")
                return None
            
            # Stage 4: Enrich
            enriched_data = self._enrich_data(cleaned_data)
            
            # Stage 5: Standardize format
            return self._standardize_format(enriched_data)
            
        except Exception as e:
            self.logger.error(f"Data processing failed: {e}")
            return None
    
    def _validate_data(self, data: Dict) -> bool:
        """Validate data against required schema."""
        required_fields = ['reel_id', 'link', 'username']
        return all(field in data and data[field] for field in required_fields)
```

### Google Sheets Integration

The Sheets integration is modular and reusable:

```python
class SheetsIntegration:
    """Handles Google Sheets operations."""
    
    def __init__(self, credentials_file: str, spreadsheet_id: str):
        self.credentials_file = credentials_file
        self.spreadsheet_id = spreadsheet_id
        self.service = self._build_service()
        self.batch_data = []
    
    def _build_service(self):
        """Build Google Sheets service with authentication."""
        try:
            credentials = Credentials.from_service_account_file(
                self.credentials_file,
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
            return build('sheets', 'v4', credentials=credentials)
        except Exception as e:
            raise AuthenticationError(f"Failed to authenticate with Google Sheets: {e}")
    
    def append_data(self, data: List[Dict], worksheet_name: str = 'Sheet1'):
        """Append data to specified worksheet."""
        if not data:
            return
        
        # Convert dict data to rows
        rows = self._convert_to_rows(data)
        
        body = {'values': rows}
        
        try:
            result = self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range=f"{worksheet_name}!A:Z",
                valueInputOption='RAW',
                body=body
            ).execute()
            
            self.logger.info(f"Added {len(rows)} rows to Google Sheets")
            return result
            
        except Exception as e:
            raise SheetsOperationError(f"Failed to append data: {e}")
    
    def batch_append(self, data: Dict):
        """Add data to batch for efficient bulk operations."""
        self.batch_data.append(data)
        
        if len(self.batch_data) >= self.batch_size:
            self.flush_batch()
    
    def flush_batch(self):
        """Flush accumulated batch data to sheets."""
        if self.batch_data:
            self.append_data(self.batch_data)
            self.batch_data.clear()
```

## Testing Framework

### Unit Tests

```python
# tests/test_data_processor.py
import unittest
from unittest.mock import Mock, patch
from instagram_reel_scraper import DataProcessor

class TestDataProcessor(unittest.TestCase):
    """Test cases for DataProcessor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            'REMOVE_DUPLICATES': True,
            'VALIDATE_DATA': True
        }
        self.processor = DataProcessor(self.config)
    
    def test_valid_data_processing(self):
        """Test processing of valid reel data."""
        raw_data = {
            'reel_id': 'ABC123',
            'link': 'https://instagram.com/reel/ABC123',
            'username': 'testuser',
            'caption': 'Test caption #test'
        }
        
        result = self.processor.process_reel_data(raw_data)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['reel_id'], 'ABC123')
        self.assertIn('hashtags', result)
    
    def test_invalid_data_rejection(self):
        """Test rejection of invalid data."""
        invalid_data = {
            'reel_id': '',  # Empty required field
            'link': 'invalid-link',
            'username': 'testuser'
        }
        
        result = self.processor.process_reel_data(invalid_data)
        self.assertIsNone(result)
    
    @patch('instagram_reel_scraper.DataProcessor._is_duplicate')
    def test_duplicate_detection(self, mock_is_duplicate):
        """Test duplicate detection logic."""
        mock_is_duplicate.return_value = True
        
        data = {
            'reel_id': 'ABC123',
            'link': 'https://instagram.com/reel/ABC123',
            'username': 'testuser'
        }
        
        result = self.processor.process_reel_data(data)
        self.assertIsNone(result)
        mock_is_duplicate.assert_called_once()

if __name__ == '__main__':
    unittest.main()
```

### Integration Tests

```python
# tests/test_integration.py
import unittest
from unittest.mock import patch
import tempfile
import os

class TestInstagramScraping(unittest.TestCase):
    """Integration tests for Instagram scraping."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_config = {
            'INSTAGRAM_URLS': ['https://instagram.com/test_account'],
            'DAYS_TO_SCRAPE': 1,
            'MAX_REELS_PER_ACCOUNT': 5,
            'USE_FAST_MODE': True,
            'HEADLESS_MODE': True
        }
    
    @patch('instagram_reel_scraper.SheetsIntegration')
    def test_end_to_end_scraping(self, mock_sheets):
        """Test complete scraping workflow."""
        # Mock sheets integration
        mock_sheets_instance = Mock()
        mock_sheets.return_value = mock_sheets_instance
        
        # Run scraper
        scraper = InstagramReelScraper(self.test_config)
        results = scraper.run()
        
        # Verify results
        self.assertIsInstance(results, dict)
        self.assertIn('total_reels', results)
        self.assertIn('accounts_processed', results)
        
        # Verify sheets integration was called
        mock_sheets_instance.append_data.assert_called()
```

### Test Configuration

```python
# tests/conftest.py
import pytest
import tempfile
import os
from unittest.mock import Mock

@pytest.fixture
def test_config():
    """Provide test configuration."""
    return {
        'INSTAGRAM_URLS': ['https://instagram.com/test_account'],
        'SPREADSHEET_ID': 'test_sheet_id',
        'CREDENTIALS_FILE': 'test_credentials.json',
        'CHROME_PROFILE_PATH': tempfile.mkdtemp(),
        'HEADLESS_MODE': True,
        'USE_FAST_MODE': True
    }

@pytest.fixture
def mock_browser():
    """Provide mock browser instance."""
    browser = Mock()
    browser.get.return_value = None
    browser.find_elements.return_value = []
    return browser

@pytest.fixture
def sample_reel_data():
    """Provide sample reel data for testing."""
    return {
        'reel_id': 'ABC123XYZ',
        'link': 'https://instagram.com/reel/ABC123XYZ',
        'username': 'testuser',
        'date': '2024-01-15',
        'caption': 'Test reel caption #test #example'
    }
```

## Performance Optimization

### Profiling and Benchmarking

```python
# performance/profiler.py
import cProfile
import pstats
from functools import wraps
import time

class PerformanceProfiler:
    """Performance profiling utilities."""
    
    @staticmethod
    def profile_function(func):
        """Decorator to profile function execution."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            profiler = cProfile.Profile()
            profiler.enable()
            
            try:
                result = func(*args, **kwargs)
            finally:
                profiler.disable()
                
                # Save profile data
                stats = pstats.Stats(profiler)
                stats.sort_stats('cumulative')
                stats.dump_stats(f'{func.__name__}_profile.stats')
                
            return result
        return wrapper
    
    @staticmethod
    def benchmark_operation(operation, iterations=10):
        """Benchmark operation performance."""
        times = []
        
        for _ in range(iterations):
            start_time = time.time()
            operation()
            end_time = time.time()
            times.append(end_time - start_time)
        
        return {
            'mean_time': sum(times) / len(times),
            'min_time': min(times),
            'max_time': max(times),
            'total_time': sum(times)
        }
```

### Memory Management

```python
# utils/memory_manager.py
import gc
import psutil
import os

class MemoryManager:
    """Memory management utilities."""
    
    def __init__(self, threshold_mb=1024):
        self.threshold_mb = threshold_mb
        self.process = psutil.Process(os.getpid())
    
    def get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        return self.process.memory_info().rss / 1024 / 1024
    
    def check_memory_threshold(self) -> bool:
        """Check if memory usage exceeds threshold."""
        return self.get_memory_usage() > self.threshold_mb
    
    def force_garbage_collection(self):
        """Force garbage collection to free memory."""
        collected = gc.collect()
        return collected
    
    def monitor_memory(self, operation):
        """Monitor memory usage during operation."""
        initial_memory = self.get_memory_usage()
        
        try:
            result = operation()
        finally:
            final_memory = self.get_memory_usage()
            
            return {
                'result': result,
                'initial_memory': initial_memory,
                'final_memory': final_memory,
                'memory_delta': final_memory - initial_memory
            }
```

## Contributing Guidelines

### Development Setup

1. **Fork and Clone**:
   ```bash
   git clone https://github.com/bytetrix/i2yt.git
   cd i2yt
   ```

2. **Create Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```

4. **Run Tests**:
   ```bash
   python -m pytest tests/
   python -m unittest discover tests/
   ```

### Code Review Process

1. **Pre-commit Checks**:
   ```bash
   # Code formatting
   black .
   
   # Linting
   flake8 .
   
   # Type checking
   mypy .
   
   # Security scan
   bandit -r .
   ```

2. **Pull Request Requirements**:
   - All tests must pass
   - Code coverage > 80%
   - Documentation updated
   - CHANGELOG.md updated
   - No breaking changes without major version bump

### Feature Development Workflow

1. **Create Feature Branch**:
   ```bash
   git checkout -b feature/new-feature-name
   ```

2. **Implement Feature**:
   - Write tests first (TDD approach)
   - Implement feature
   - Update documentation
   - Add configuration options if needed

3. **Test Thoroughly**:
   ```bash
   # Run all tests
   python -m pytest tests/ -v
   
   # Run integration tests
   python -m pytest tests/integration/ -v
   
   # Performance tests
   python -m pytest tests/performance/ -v
   ```

4. **Submit Pull Request**:
   - Descriptive title and description
   - Link to related issues
   - Screenshots/recordings for UI changes
   - Performance impact analysis

### Documentation Guidelines

1. **Code Documentation**:
   - Docstrings for all public functions/classes
   - Type hints for function parameters and returns
   - Inline comments for complex logic

2. **User Documentation**:
   - Update relevant .md files in docs/
   - Include examples and use cases
   - Update README.md if needed

3. **API Documentation**:
   ```python
   # Generate API docs
   sphinx-apidoc -o docs/api/ .
   sphinx-build -b html docs/ docs/_build/
   ```

## Debugging and Development Tools

### Debug Configuration

```python
# debug_config.py
DEBUG_CONFIG = {
    'enabled': True,
    'log_level': 'DEBUG',
    'save_screenshots': True,
    'preserve_browser': True,
    'detailed_timing': True,
    'memory_profiling': True,
    'network_logging': True
}

# Enable debug mode
def enable_debug_mode():
    """Enable comprehensive debugging."""
    import logging
    
    # Set up detailed logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('debug.log'),
            logging.StreamHandler()
        ]
    )
    
    # Enable Selenium logging
    logging.getLogger('selenium').setLevel(logging.DEBUG)
```

### Development Scripts

```bash
# scripts/dev_setup.sh
#!/bin/bash
# Development environment setup script

echo "Setting up development environment..."

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Set up pre-commit hooks
pre-commit install

# Create development config
cp config_template.py config_dev.py

echo "Development environment ready!"
```

## Deployment and Distribution

### Package Configuration

```python
# setup.py
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="instagram-youtube-automation",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Automate Instagram reel collection and YouTube upload workflow",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/instagram-youtube-automation",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "instagram-scraper=run_scraper:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.json", "*.bat"],
    },
)
```

### CI/CD Pipeline

```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, '3.10', 3.11]

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v3
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Lint with flake8
      run: |
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
    
    - name: Type check with mypy
      run: mypy .
    
    - name: Test with pytest
      run: |
        pytest tests/ --cov=. --cov-report=xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

---

**Next Steps for Contributors:**
1. Read through the existing codebase
2. Set up development environment
3. Run tests to ensure everything works
4. Pick an issue from GitHub Issues
5. Follow the contribution workflow
6. Submit a pull request

For specific development questions, check the existing code, tests, and documentation, or create an issue for discussion.
