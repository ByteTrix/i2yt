#!/usr/bin/env python3
"""
Simple Instagram Reel Scraper Runner
This script loads configuration and runs the Instagram scraper.
"""

import sys
import os
from instagram_reel_scraper import InstagramReelScraper, Config

def load_config():
    """Load configuration from config.py file."""
    try:
        # Try to import config.py
        import config
        
        # Get Instagram URLs - support both single URL and list of URLs
        instagram_urls = getattr(config, 'INSTAGRAM_URLS', [config.INSTAGRAM_URL])
        return Config(
            instagram_url=config.INSTAGRAM_URL,  # Kept for backwards compatibility
            instagram_urls=instagram_urls,
            target_links=getattr(config, 'TARGET_LINKS', 0),
            days_limit=getattr(config, 'DAYS_LIMIT', 30),
            google_sheets_id=config.GOOGLE_SHEETS_ID,
            credentials_file=config.CREDENTIALS_FILE,
            max_scrolls=config.MAX_SCROLLS,
            scroll_delay=config.SCROLL_DELAY,
            batch_size=getattr(config, 'BATCH_SIZE', 25),
            implicit_wait=config.IMPLICIT_WAIT,
            page_load_timeout=config.PAGE_LOAD_TIMEOUT,
            headless=config.HEADLESS,
            fast_mode=getattr(config, 'FAST_MODE', True)
        )
    except ImportError:
        print("❌ Error: config.py file not found!")
        print("📝 Please copy config_template.py to config.py and update with your values")
        sys.exit(1)
    except AttributeError as e:
        print(f"❌ Error: Missing configuration in config.py: {e}")
        print("📝 Please check config_template.py for required configuration")
        sys.exit(1)

def check_requirements():
    """Check if required files exist."""
    try:
        import config
        
        # Check if credentials file exists
        if not os.path.exists(config.CREDENTIALS_FILE):
            print(f"❌ Error: Credentials file '{config.CREDENTIALS_FILE}' not found!")
            print("📝 Please download your Google Service Account credentials JSON file")
            return False
            
        # Basic validation of URLs
        if "your_target_account" in config.INSTAGRAM_URL:
            print("❌ Error: Please update INSTAGRAM_URL in config.py with actual Instagram URL")
            return False
            
        # Check if INSTAGRAM_URLS is properly configured
        if hasattr(config, 'INSTAGRAM_URLS'):
            if not isinstance(config.INSTAGRAM_URLS, list) or len(config.INSTAGRAM_URLS) == 0:
                print("❌ Error: INSTAGRAM_URLS in config.py must be a non-empty list")
                return False
            
            for url in config.INSTAGRAM_URLS:
                if "instagram.com" not in url:
                    print(f"❌ Error: Invalid Instagram URL in INSTAGRAM_URLS: {url}")
                    print("URLs should be in the format 'https://www.instagram.com/username/'")
                    return False
        
        # Check TARGET_LINKS if it exists
        if hasattr(config, 'TARGET_LINKS'):
            if not isinstance(config.TARGET_LINKS, int) or config.TARGET_LINKS < 0:
                print("❌ Error: TARGET_LINKS in config.py must be a non-negative integer")
                return False
            
        if "your_google_sheets_id_here" in config.GOOGLE_SHEETS_ID:
            print("❌ Error: Please update GOOGLE_SHEETS_ID in config.py with actual Sheets ID")
            return False
            
        return True
        
    except ImportError:
        return False

def main():
    """Main function to run the scraper with proper setup checks."""
    # Setup UTF-8 encoding for Windows console
    import sys
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass  # Fallback for older Python versions
    
    print("🤖 Instagram Reel Scraper")
    print("=" * 50)
    
    # Load configuration
    print("📝 Loading configuration...")
    config = load_config()
    print("✅ Configuration loaded successfully")
    
    # Display configuration summary
    print("\n📊 Scraper Configuration:")
    print(f"  • URLs to scrape: {len(config.instagram_urls)}")
    
    # Display target info if set
    if config.target_links > 0:
        print(f"  • Target links to collect: {config.target_links}")
    else:
        print("  • No link limit (will collect all available)")
        
    print(f"  • Max scrolls per URL: {config.max_scrolls}")
    print(f"  • Fast mode: {'Enabled' if config.fast_mode else 'Disabled'}")
    print(f"  • Headless mode: {'Enabled' if config.headless else 'Disabled'}")
    
    # Check requirements
    print("\n🔍 Checking requirements...")
    if not check_requirements():
        print("❌ Requirements check failed. Please fix the issues above.")
        sys.exit(1)
    print("✅ Requirements check passed")
    
    # Run scraper
    print("\n🚀 Starting Instagram Reel Scraper...")
    try:
        scraper = InstagramReelScraper(config)
        collected_links = scraper.run()
        
        # Display results
        print("\n📈 Scraping Results:")
        print(f"  • Total URLs processed: {len(config.instagram_urls)}")
        print(f"  • Total links collected: {len(collected_links)}")
        
        if config.target_links > 0:
            target_percentage = min(100, len(collected_links) / config.target_links * 100)
            print(f"  • Target completion: {target_percentage:.1f}% ({len(collected_links)}/{config.target_links})")
            
        print("\n✅ Scraping completed successfully!")
        
    except KeyboardInterrupt:
        print("\n⚠️  Scraping interrupted by user")
    except Exception as e:
        print(f"❌ Scraping failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
