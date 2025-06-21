# Advanced Usage Guide

Advanced features and power user capabilities for the Instagram to YouTube automation tool.

## Advanced Configuration

### Multi-Profile Management

Manage multiple Instagram accounts with separate profiles:

```python
# config_profiles.py
PROFILES = {
    'main': {
        'instagram_urls': ['https://www.instagram.com/account1/'],
        'profile_path': './profiles/main_profile',
        'spreadsheet_id': 'sheet_id_1'
    },
    'secondary': {
        'instagram_urls': ['https://www.instagram.com/account2/'],
        'profile_path': './profiles/secondary_profile', 
        'spreadsheet_id': 'sheet_id_2'
    }
}

# Usage
python run_scraper.py --profile main
python run_scraper.py --profile secondary
```

### Custom Scraping Patterns

Define custom patterns for different content types:

```python
# In config.py
CONTENT_PATTERNS = {
    'reels': r'/reel/[A-Za-z0-9_-]+',
    'posts': r'/p/[A-Za-z0-9_-]+',
    'stories': r'/stories/[A-Za-z0-9_-]+',
    'igtv': r'/tv/[A-Za-z0-9_-]+'
}

# Selective scraping
SCRAPE_CONTENT_TYPES = ['reels', 'posts']  # Only these types
```

### Dynamic Configuration

Load configuration from external sources:

```python
# config_dynamic.py
import json
import requests

def load_remote_config():
    """Load configuration from remote API"""
    response = requests.get('https://api.yoursite.com/scraper-config')
    return response.json()

def load_database_config():
    """Load configuration from database"""
    # Your database logic here
    pass

# Use dynamic configuration
DYNAMIC_CONFIG = True
CONFIG_SOURCE = 'remote'  # 'remote', 'database', 'file'
CONFIG_UPDATE_INTERVAL = 3600  # Update every hour
```

## Advanced Scraping Techniques

### Smart Scrolling Algorithm

Implement intelligent scrolling based on content discovery:

```python
# Advanced scrolling configuration
SMART_SCROLLING = {
    'enabled': True,
    'initial_fast_scrolls': 5,
    'content_detection_threshold': 3,  # Stop if no new content found
    'adaptive_pause': True,           # Adjust pause based on load time
    'scroll_acceleration': 1.2,       # Increase speed over time
    'max_empty_scrolls': 3            # Stop after N empty scrolls
}

# Performance monitoring
PERFORMANCE_MONITORING = {
    'track_scroll_performance': True,
    'optimize_scroll_timing': True,
    'log_performance_metrics': True
}
```

### Content Filtering and Validation

Advanced filtering before saving to sheets:

```python
# Content filtering configuration
CONTENT_FILTERS = {
    'min_duration': 15,        # Minimum video duration (seconds)
    'max_duration': 180,       # Maximum video duration (seconds)
    'min_views': 1000,         # Minimum view count
    'exclude_keywords': ['ads', 'sponsored', 'promotion'],
    'required_keywords': ['motivation', 'fitness'],
    'language_filter': ['en', 'es'],
    'quality_threshold': 720   # Minimum video quality
}

# AI-powered content analysis
AI_FILTERING = {
    'enabled': True,
    'content_analysis': True,   # Analyze video content
    'text_sentiment': True,     # Sentiment analysis on captions
    'brand_safety': True,       # Brand safety checks
    'duplicate_detection': True # Advanced duplicate detection
}
```

### Parallel Processing

Process multiple accounts simultaneously:

```python
# Parallel processing configuration
PARALLEL_PROCESSING = {
    'enabled': True,
    'max_workers': 4,           # Number of parallel browsers
    'accounts_per_worker': 2,   # Accounts per browser instance
    'memory_limit_mb': 2048,    # Memory limit per worker
    'timeout_per_account': 1800 # Timeout per account (seconds)
}

# Resource management
RESOURCE_MANAGEMENT = {
    'restart_browser_after': 50,    # Restart after N reels
    'garbage_collect_frequency': 25, # Clean memory every N operations
    'disk_space_check': True,       # Check available disk space
    'memory_monitoring': True       # Monitor memory usage
}
```

## Advanced Data Management

### Custom Data Processing Pipeline

Implement custom data processing before saving:

```python
# data_processors.py
class DataProcessor:
    def __init__(self, config):
        self.config = config
    
    def process_reel_data(self, reel_data):
        """Custom processing for each reel"""
        # Extract additional metadata
        reel_data['hashtags'] = self.extract_hashtags(reel_data['caption'])
        reel_data['mentions'] = self.extract_mentions(reel_data['caption'])
        reel_data['engagement_score'] = self.calculate_engagement(reel_data)
        
        # Content analysis
        if self.config.get('ai_analysis'):
            reel_data['content_category'] = self.classify_content(reel_data)
            reel_data['sentiment_score'] = self.analyze_sentiment(reel_data)
        
        return reel_data
    
    def extract_hashtags(self, caption):
        """Extract hashtags from caption"""
        import re
        return re.findall(r'#\w+', caption or '')
    
    def calculate_engagement(self, reel_data):
        """Calculate engagement score"""
        likes = reel_data.get('likes', 0)
        comments = reel_data.get('comments', 0)
        views = reel_data.get('views', 1)
        
        return (likes + comments * 2) / views * 100

# Usage in config.py
DATA_PROCESSING = {
    'enabled': True,
    'processors': ['hashtag_extraction', 'engagement_calculation'],
    'ai_analysis': True,
    'custom_fields': True
}
```

### Advanced Database Integration

Store data in multiple databases:

```python
# database_config.py
DATABASE_CONFIGS = {
    'postgres': {
        'host': 'localhost',
        'database': 'instagram_data',
        'user': 'scraper_user',
        'password': 'password'
    },
    'mongodb': {
        'connection_string': 'mongodb://localhost:27017/',
        'database': 'instagram_reels',
        'collection': 'reels_data'
    },
    'elasticsearch': {
        'hosts': ['localhost:9200'],
        'index': 'instagram_reels'
    }
}

# Multi-database storage
STORAGE_BACKENDS = ['google_sheets', 'postgres', 'mongodb']
```

### Data Synchronization

Keep multiple data sources in sync:

```python
# sync_config.py
SYNC_CONFIGURATION = {
    'enabled': True,
    'primary_source': 'google_sheets',
    'sync_targets': ['postgres', 'mongodb'],
    'sync_frequency': 3600,  # Sync every hour
    'conflict_resolution': 'latest_wins',
    'backup_before_sync': True
}

# Bidirectional sync
BIDIRECTIONAL_SYNC = {
    'enabled': True,
    'master_source': 'postgres',
    'sync_direction': 'both',  # 'to_master', 'from_master', 'both'
    'change_tracking': True
}
```

## Advanced Automation

### Webhook Integration

Integrate with external systems via webhooks:

```python
# webhook_config.py
WEBHOOKS = {
    'enabled': True,
    'endpoints': {
        'new_reel': 'https://your-api.com/webhook/new-reel',
        'scraping_complete': 'https://your-api.com/webhook/complete',
        'error_notification': 'https://your-api.com/webhook/error'
    },
    'authentication': {
        'type': 'bearer_token',
        'token': 'your_webhook_token'
    },
    'retry_policy': {
        'max_retries': 3,
        'backoff_factor': 2,
        'timeout': 30
    }
}

# Webhook payload customization
WEBHOOK_PAYLOADS = {
    'new_reel': {
        'include_metadata': True,
        'include_analytics': True,
        'custom_fields': ['engagement_score', 'content_category']
    }
}
```

### Event-Driven Processing

Implement event-driven architecture:

```python
# events.py
from typing import Dict, Any
import asyncio

class EventSystem:
    def __init__(self):
        self.listeners = {}
    
    def on(self, event_name: str, callback):
        """Register event listener"""
        if event_name not in self.listeners:
            self.listeners[event_name] = []
        self.listeners[event_name].append(callback)
    
    async def emit(self, event_name: str, data: Dict[str, Any]):
        """Emit event to all listeners"""
        if event_name in self.listeners:
            tasks = []
            for callback in self.listeners[event_name]:
                tasks.append(callback(data))
            await asyncio.gather(*tasks)

# Usage
event_system = EventSystem()

@event_system.on('reel_discovered')
async def process_new_reel(data):
    # Process new reel
    pass

@event_system.on('scraping_complete')
async def send_notification(data):
    # Send completion notification
    pass
```

### Scheduled Operations

Advanced scheduling beyond basic cron:

```python
# scheduler_config.py
SCHEDULED_OPERATIONS = {
    'daily_scraping': {
        'schedule': 'cron(0 9 * * *)',  # 9 AM daily
        'accounts': ['main_accounts'],
        'max_reels': 50
    },
    'weekly_full_scrape': {
        'schedule': 'cron(0 6 * * 1)',  # 6 AM Monday
        'accounts': ['all_accounts'],
        'max_reels': 0,  # Unlimited
        'full_history': True
    },
    'hourly_trending': {
        'schedule': 'cron(0 * * * *)',  # Every hour
        'accounts': ['trending_accounts'],
        'max_reels': 10,
        'priority': 'high'
    }
}

# Dynamic scheduling
DYNAMIC_SCHEDULING = {
    'enabled': True,
    'adjust_frequency': True,    # Adjust based on activity
    'peak_hours': [9, 12, 18, 21],  # More frequent during peaks
    'off_hours_reduction': 0.5,  # 50% reduction during off hours
    'weekend_schedule': 'reduced'  # Different weekend schedule
}
```

## Advanced Monitoring and Analytics

### Performance Monitoring

Detailed performance tracking:

```python
# monitoring_config.py
PERFORMANCE_MONITORING = {
    'enabled': True,
    'metrics': [
        'scraping_speed',       # Reels per minute
        'success_rate',         # Successful operations %
        'error_rate',           # Error rate %
        'memory_usage',         # Memory consumption
        'cpu_usage',            # CPU utilization
        'network_usage',        # Network bandwidth
        'response_times'        # API response times
    ],
    'alerting': {
        'enabled': True,
        'thresholds': {
            'success_rate': 95,     # Alert if below 95%
            'error_rate': 5,        # Alert if above 5%
            'memory_usage': 80,     # Alert if above 80%
            'response_time': 30     # Alert if above 30s
        }
    }
}

# Real-time monitoring dashboard
DASHBOARD_CONFIG = {
    'enabled': True,
    'port': 8080,
    'update_interval': 5,  # Update every 5 seconds
    'metrics_retention': 24 * 7  # Keep 7 days of metrics
}
```

### Analytics and Reporting

Advanced analytics capabilities:

```python
# analytics_config.py
ANALYTICS = {
    'enabled': True,
    'data_sources': ['google_sheets', 'logs', 'performance_metrics'],
    'reports': {
        'daily_summary': {
            'enabled': True,
            'schedule': 'cron(0 23 * * *)',  # 11 PM daily
            'recipients': ['admin@yoursite.com'],
            'metrics': ['reels_collected', 'accounts_processed', 'success_rate']
        },
        'weekly_trends': {
            'enabled': True,
            'schedule': 'cron(0 9 * * 1)',   # 9 AM Monday
            'include_charts': True,
            'trend_analysis': True
        }
    }
}

# Custom analytics
CUSTOM_ANALYTICS = {
    'content_analysis': True,    # Analyze content trends
    'engagement_tracking': True, # Track engagement metrics
    'performance_trends': True,  # Performance over time
    'predictive_analytics': True # Predict optimal scraping times
}
```

## Advanced Error Handling and Recovery

### Sophisticated Error Recovery

Implement intelligent error recovery:

```python
# error_handling.py
class AdvancedErrorHandler:
    def __init__(self, config):
        self.config = config
        self.error_history = []
        self.recovery_strategies = {
            'rate_limit': self.handle_rate_limit,
            'network_error': self.handle_network_error,
            'auth_error': self.handle_auth_error,
            'browser_crash': self.handle_browser_crash
        }
    
    def handle_error(self, error, context):
        """Intelligent error handling with context"""
        error_type = self.classify_error(error)
        strategy = self.recovery_strategies.get(error_type)
        
        if strategy:
            return strategy(error, context)
        else:
            return self.generic_recovery(error, context)
    
    def handle_rate_limit(self, error, context):
        """Handle rate limiting with exponential backoff"""
        wait_time = min(300, 60 * (2 ** len(self.error_history)))
        time.sleep(wait_time)
        return True  # Retry
    
    def handle_auth_error(self, error, context):
        """Handle authentication errors"""
        # Attempt to refresh session
        if self.refresh_session():
            return True  # Retry
        else:
            # Trigger manual login
            self.trigger_manual_login()
            return False  # Don't retry automatically
```

### Circuit Breaker Pattern

Prevent cascade failures:

```python
# circuit_breaker.py
class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        if self.state == 'OPEN':
            if time.time() - self.last_failure_time > self.timeout:
                self.state = 'HALF_OPEN'
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            raise e
    
    def on_success(self):
        self.failure_count = 0
        self.state = 'CLOSED'
    
    def on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = 'OPEN'
```

## Integration Examples

### Custom API Integration

Integrate with your own API:

```python
# api_integration.py
import requests
from typing import List, Dict

class CustomAPIIntegration:
    def __init__(self, api_base_url: str, api_key: str):
        self.base_url = api_base_url
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        })
    
    def send_reels(self, reels: List[Dict]):
        """Send reel data to custom API"""
        endpoint = f"{self.base_url}/reels/batch"
        
        for batch in self.chunk_data(reels, 10):
            response = self.session.post(endpoint, json={'reels': batch})
            response.raise_for_status()
    
    def get_processing_status(self, reel_ids: List[str]):
        """Check processing status from API"""
        endpoint = f"{self.base_url}/reels/status"
        response = self.session.post(endpoint, json={'ids': reel_ids})
        return response.json()
```

### Machine Learning Integration

Add ML capabilities:

```python
# ml_integration.py
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

class ContentClassifier:
    def __init__(self, model_path=None):
        if model_path:
            self.model = joblib.load(model_path)
            self.vectorizer = joblib.load(f"{model_path}_vectorizer.pkl")
        else:
            self.model = MultinomialNB()
            self.vectorizer = TfidfVectorizer(max_features=5000)
    
    def classify_content(self, caption: str, hashtags: List[str]) -> str:
        """Classify content based on caption and hashtags"""
        text = f"{caption} {' '.join(hashtags)}"
        features = self.vectorizer.transform([text])
        prediction = self.model.predict(features)[0]
        confidence = max(self.model.predict_proba(features)[0])
        
        return {
            'category': prediction,
            'confidence': confidence
        }
    
    def train_model(self, training_data: List[Dict]):
        """Train the classification model"""
        texts = []
        labels = []
        
        for item in training_data:
            text = f"{item['caption']} {' '.join(item['hashtags'])}"
            texts.append(text)
            labels.append(item['category'])
        
        X = self.vectorizer.fit_transform(texts)
        self.model.fit(X, labels)
```

## Command Line Advanced Usage

### Custom Commands

Create custom command-line operations:

```python
# cli_advanced.py
import click

@click.group()
def cli():
    """Advanced Instagram scraper commands"""
    pass

@cli.command()
@click.option('--profile', required=True, help='Profile name')
@click.option('--accounts', help='Comma-separated account list')
@click.option('--output', help='Output format (sheets/json/csv)')
def scrape_profile(profile, accounts, output):
    """Scrape specific profile with custom settings"""
    # Implementation here
    pass

@cli.command()
@click.option('--start-date', help='Start date (YYYY-MM-DD)')
@click.option('--end-date', help='End date (YYYY-MM-DD)')
def historical_scrape(start_date, end_date):
    """Perform historical scraping for date range"""
    # Implementation here
    pass

@cli.command()
def analyze_performance():
    """Analyze scraping performance and generate report"""
    # Implementation here
    pass

if __name__ == '__main__':
    cli()
```

### Batch Operations

Run batch operations efficiently:

```bash
# Batch scraping with different configurations
python run_scraper.py --batch-config configs/ --parallel 4

# Process multiple profiles
python run_scraper.py --profiles main,secondary,backup --async

# Historical data collection
python run_scraper.py --historical --start-date 2024-01-01 --end-date 2024-12-31

# Analytics and reporting
python run_scraper.py --generate-report --period monthly --output pdf
```

---

**Advanced Features Summary:**
- Multi-profile management
- Parallel processing
- Custom data pipelines
- Event-driven architecture
- Advanced monitoring
- ML integration
- Circuit breaker patterns
- Webhook integrations

For more specific use cases, check the other documentation files or create custom configurations based on these examples.
