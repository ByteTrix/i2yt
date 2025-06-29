#!/usr/bin/env python3
"""
Enhanced Instagram Reel Scraper with Professional Parallel Processing
Focuses on link collection and saves to Google Sheets with optimized performance.
Uses advanced parallel processing for maximum efficiency.
"""

import time
import re
import json
import logging
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from urllib.parse import urlparse, parse_qs
import config

# Import our professional parallel processor
from parallel_processor import get_parallel_processor, parallel_process
from tqdm import tqdm

# Selenium imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Import our new modular components
from google_sheets_manager import GoogleSheetsManager
from main_processor import InstagramProcessor

# Setup logging - separate file and console logging

# Clear any existing handlers first
root_logger = logging.getLogger()
root_logger.handlers.clear()

# Configure file logging (all levels) with UTF-8 encoding
file_handler = logging.FileHandler('instagram_scraper.log', encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)

# Configure console logging (INFO for minimal, DEBUG for verbose)
console_handler = logging.StreamHandler()
console_level = logging.INFO if getattr(config, 'MINIMAL_OUTPUT', True) else logging.DEBUG
console_handler.setLevel(console_level)

# Enhanced console formatter with uniform format
class UniformFormatter(logging.Formatter):
    """Clean, uniform formatter: time-module-level-message"""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green  
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record):
        # Get color for log level
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        # Format timestamp (HH:MM:SS)
        timestamp = datetime.fromtimestamp(record.created).strftime('%H:%M:%S')
        
        # Get short module name
        module_name = record.name.split('.')[-1] if '.' in record.name else record.name
        if module_name == '__main__':
            module_name = 'scraper'
        elif module_name == 'instagram_scraper':
            module_name = 'scraper'
        
        # Uniform format: time-module-level-message
        formatted_msg = f"{timestamp}-{color}{module_name}-{record.levelname}{reset}-{record.getMessage()}"
        
        return formatted_msg

console_formatter = UniformFormatter()
console_handler.setFormatter(console_formatter)

# Setup root logger
root_logger.setLevel(logging.DEBUG)
root_logger.addHandler(file_handler)
root_logger.addHandler(console_handler)

# Silence third-party library logs on console but keep in file
for lib in ['urllib3', 'selenium', 'googleapiclient', 'google', 'requests']:
    lib_logger = logging.getLogger(lib)
    lib_logger.setLevel(logging.WARNING)  # Only warnings and errors in console
    # Remove console handler but keep file handler
    for handler in lib_logger.handlers:
        if isinstance(handler, logging.StreamHandler) and not isinstance(handler, logging.FileHandler):
            lib_logger.removeHandler(handler)

# DO NOT prevent propagation - we want logs to reach our handlers!

logger = logging.getLogger(__name__)

@dataclass
class ScrapingConfig:
    """Configuration class for Instagram scraping"""
    instagram_urls: List[str]
    max_scrolls: int = 15
    target_links: int = 0  # 0 = unlimited
    days_limit: int = 30
    scroll_delay: float = 0.3
    batch_size: int = 30
    implicit_wait: int = 1
    page_load_timeout: int = 10
    headless: bool = True
    fast_mode: bool = True

class InstagramReelScraper:
    """Scrapes Instagram reels and saves URLs to Google Sheets"""
    
    def __init__(self):
        self.logger = logger
        self.driver = None
        self.sheets_manager = GoogleSheetsManager()
        self.processor = InstagramProcessor()
        
        # Load config from config.py
        self.scraping_config = ScrapingConfig(
            instagram_urls=config.INSTAGRAM_URLS,
            max_scrolls=config.MAX_SCROLLS,
            target_links=config.TARGET_LINKS,
            days_limit=config.DAYS_LIMIT,
            scroll_delay=config.SCROLL_DELAY,
            batch_size=config.BATCH_SIZE,
            implicit_wait=config.IMPLICIT_WAIT,
            page_load_timeout=config.PAGE_LOAD_TIMEOUT,
            headless=config.HEADLESS,
            fast_mode=config.FAST_MODE
        )
        
        # Cache for tracking collected URLs and duplicate detection
        self.collected_urls = set()
        self.existing_reel_ids = set()
        self.reel_id_cache_loaded = False
        
    def setup_driver(self):
        """Setup Chrome driver with all optimized settings from original scraper"""
        try:
            if not getattr(config, 'MINIMAL_OUTPUT', True):
                self.logger.info("Setting up Chrome driver with maximum optimizations...")
            
            chrome_options = Options()
            
            # Profile and user data directory
            profile_path = os.path.join(os.getcwd(), "instagram_profile")
            chrome_options.add_argument(f"--user-data-dir={profile_path}")
            chrome_options.add_argument("--profile-directory=Default")
            
            # Core stability and security flags
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            
            # Suppress Chrome warnings and errors in terminal (if configured)
            if getattr(config, 'SUPPRESS_CHROME_WARNINGS', True):
                chrome_options.add_argument("--log-level=3")  # Suppress INFO, WARNING, ERROR logs
                chrome_options.add_argument("--silent")
                chrome_options.add_argument("--disable-logging")
                chrome_options.add_argument("--disable-gpu-logging")
                chrome_options.add_argument("--disable-shared-image-interface-in-renderer")
                chrome_options.add_experimental_option('useAutomationExtension', False)
                chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
            
            # Performance optimizations for MAXIMUM SPEED
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-notifications") 
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-logging")
            chrome_options.add_argument("--disable-default-apps")
            chrome_options.add_argument("--disable-background-timer-throttling")
            chrome_options.add_argument("--disable-backgrounding-occluded-windows")
            chrome_options.add_argument("--disable-renderer-backgrounding")
            chrome_options.add_argument("--disable-features=TranslateUI")
            chrome_options.add_argument("--disable-ipc-flooding-protection")
            chrome_options.add_argument("--no-default-browser-check")
            chrome_options.add_argument("--no-first-run")
            chrome_options.add_argument("--disable-component-update")
            chrome_options.add_argument("--disable-sync")
            chrome_options.add_argument("--disable-background-networking")
            chrome_options.add_argument("--disable-client-side-phishing-detection")
            chrome_options.add_argument("--disable-hang-monitor")
            chrome_options.add_argument("--disable-prompt-on-repost")
            chrome_options.add_argument("--disable-domain-reliability")
            chrome_options.add_argument("--disable-features=AudioServiceOutOfProcess")
            chrome_options.add_argument("--aggressive-cache-discard")
            chrome_options.add_argument("--memory-pressure-off")
            chrome_options.add_argument("--max_old_space_size=4096")
            
            # Ultra-fast loading optimizations
            chrome_options.add_argument("--disable-features=VizDisplayCompositor")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--allow-running-insecure-content")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled,TrustedDOMTypes,RequireTrustedTypesForDOM")
            chrome_options.add_argument("--use-fake-ui-for-media-stream")
            chrome_options.add_argument("--enable-unsafe-swiftshader")
            
            # Fast mode optimizations
            if self.scraping_config.fast_mode:
                if not getattr(config, 'MINIMAL_OUTPUT', True):
                    self.logger.info("ULTRA-FAST mode enabled: blocking images, videos, CSS, fonts for maximum speed")
                prefs = {
                    "profile.managed_default_content_settings.images": 2,  # Block images
                    "profile.default_content_setting_values.notifications": 2,  # Block notifications
                    "profile.managed_default_content_settings.stylesheets": 2,  # Block CSS (faster loading)
                    "profile.managed_default_content_settings.fonts": 2,  # Block fonts
                    "profile.managed_default_content_settings.plugins": 2,  # Block plugins
                    "profile.managed_default_content_settings.popups": 2,  # Block popups
                    "profile.managed_default_content_settings.geolocation": 2,  # Block location
                    "profile.managed_default_content_settings.media_stream": 2,  # Block media
                    "profile.managed_default_content_settings.midi_sysex": 2,  # Block MIDI
                    "profile.managed_default_content_setting_values.cookies": 1,  # Allow cookies (required)
                    "profile.managed_default_content_settings.javascript": 1,  # Allow JS (required for Instagram)
                }
                chrome_options.add_experimental_option("prefs", prefs)
                
                # Additional ultra-fast loading flags
                chrome_options.add_argument("--disable-images")
                chrome_options.add_argument("--disable-javascript-harmony-shipping")
                chrome_options.add_argument("--disable-background-media-suspend")
                chrome_options.add_argument("--disable-new-avatar-menu")
            
            # User agent
            if hasattr(config, 'USER_AGENT'):
                chrome_options.add_argument(f"--user-agent={config.USER_AGENT}")
            else:
                chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
            
            # Headless mode
            if self.scraping_config.headless:
                self.logger.warning("Running in headless mode. Note that Instagram may detect this.")
                chrome_options.add_argument("--headless")
            
            # Initialize driver
            driver = webdriver.Chrome(options=chrome_options)
            driver.implicitly_wait(self.scraping_config.implicit_wait)
            driver.set_page_load_timeout(self.scraping_config.page_load_timeout)
            
            # Attempt to hide automation
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Inject CSS to hide animations for faster performance if fast_mode is enabled
            if self.scraping_config.fast_mode:
                try:
                    driver.execute_script("""
                    try {
                        var style = document.createElement('style');
                        style.type = 'text/css';
                        style.textContent = '* { animation-duration: 0.001s !important; transition-duration: 0.001s !important; }';
                        document.getElementsByTagName('head')[0].appendChild(style);
                    } catch(e) {
                        console.log('Style injection failed:', e);
                    }
                    """)
                except Exception as js_error:
                    self.logger.warning(f"Could not inject CSS styles: {js_error}")
            
            self.logger.info("Chrome browser started successfully with dedicated profile and maximum optimizations")
            return driver
            
        except Exception as e:
            self.logger.error(f"Failed to setup Chrome driver: {str(e)}")
            raise
    
    def navigate_to_instagram(self, url: str):
        """Navigate to Instagram profile/page."""
        try:
            self.logger.info(f"Navigating to: {url}")
            self.driver.get(url)
            
            # Wait for page to load more efficiently
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Handle potential login popup or cookie banner
            self.handle_popups()
            
            # Reduced wait time
            time.sleep(0.5)  # Reduced from 1 second for faster navigation
            
        except TimeoutException:
            self.logger.error(f"Timeout while loading {url}")
            raise
        except Exception as e:
            self.logger.error(f"Error navigating to Instagram: {e}")
            raise
    
    def handle_popups(self):
        """Handle login popups, cookie banners, etc."""
        try:
            # Handle "Not Now" for notifications
            not_now_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Not Now')]")
            for button in not_now_buttons:
                if button.is_displayed():
                    button.click()
                    time.sleep(0.3)  # Faster popup handling
                    
            # Handle cookie banner
            accept_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Accept')]")
            for button in accept_buttons:
                if button.is_displayed():
                    button.click()
                    time.sleep(0.3)  # Faster popup handling
                    
        except Exception as e:
            self.logger.warning(f"Could not handle popups: {e}")
    
    def navigate_to_reels(self):
        """Navigate to the reels section of the profile."""
        try:
            # Look for reels tab - try multiple selectors
            reels_selectors = [
                "//a[contains(@href, '/reels/')]",
                "//a[contains(text(), 'Reels')]",
                "//div[contains(@class, 'reel')]//a",
                "[aria-label*='Reels']"
            ]
            
            reels_link = None
            for selector in reels_selectors:
                try:
                    if selector.startswith("//"):
                        elements = self.driver.find_elements(By.XPATH, selector)
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        
                    for element in elements:
                        if element.is_displayed():
                            reels_link = element
                            break
                    if reels_link:
                        break                
                except:
                    continue
                    
            if reels_link:
                self.logger.info("Found reels section, clicking...")
                self.driver.execute_script("arguments[0].click();", reels_link)
                time.sleep(1.5)  # Reduced from 3 seconds for faster navigation
            else:
                self.logger.warning("Could not find reels section, proceeding with current page")
        except Exception as e:
            self.logger.warning(f"Could not navigate to reels section: {e}")
    
    def extract_reel_id(self, url: str) -> str:
        """Extract reel ID from Instagram URL"""
        try:
            match = re.search(r'/(?:p|reel)/([A-Za-z0-9_-]+)', url)
            if match:
                return match.group(1)
            return f"unknown_{int(time.time())}"
        except:
            return f"unknown_{int(time.time())}"
    
    def scroll_and_collect_links(self, target_remaining: int = 0) -> List[str]:
        """Scroll through the page and collect reel links with enhanced duplicate filtering and parallel processing.
        
        Args:
            target_remaining: Stop collecting when this many links are found (0 = no limit)
        """
        links = set()
        scroll_count = 0
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        consecutive_no_new_links = 0
        last_link_count = 0
        
        if not getattr(config, 'MINIMAL_OUTPUT', True):
            self.logger.info("Starting to scroll and collect reel links with enhanced filtering...")
        if target_remaining > 0:
            self.logger.info(f"Target: {target_remaining} reels")
        
        # Load existing reel IDs for duplicate checking
        if not self.reel_id_cache_loaded:
            self.logger.info("Loading existing reel IDs from Google Sheets...")
            initial_cache_size = len(self.existing_reel_ids)
            self.load_existing_reel_ids()
            final_cache_size = len(self.existing_reel_ids)
            self.logger.info(f"Loaded {final_cache_size - initial_cache_size} existing reel IDs from sheets")
        else:
            self.logger.info(f"Using cached reel IDs: {len(self.existing_reel_ids)} in cache")
        
        # Apply browser optimizations
        self.optimize_browser_performance()
        
        # Preload the page to ensure the DOM is ready
        time.sleep(1)
        
        # First batch collection (without scrolling)
        self.logger.info("Initial page scan...")
        current_links = self.collect_visible_reel_links()
        
        # Filter duplicates and process in parallel
        if current_links:
            self.logger.info(f"Found {len(current_links)} potential reels, checking for duplicates...")
            filtered_links, duplicate_count = self.filter_duplicate_reels(current_links)
            
            self.logger.info(f"After duplicate filtering: {len(filtered_links)} new links, {duplicate_count} duplicates")
            
            if filtered_links:
                if config.ENABLE_CONCURRENT_PROCESSING:
                    # Use professional parallel processor
                    processor = get_parallel_processor(self.logger)
                    processed_links = processor.process_in_parallel(
                        filtered_links,
                        self._process_single_link,
                        task_type='scraping',
                        progress_callback=self._progress_callback
                    )
                    # Filter out None results
                    processed_links = [link for link in processed_links if link is not None]
                else:
                    # Sequential processing with detailed output
                    processed_links = []
                    self.logger.info("🔄 Processing links sequentially...")
                    for i, link in enumerate(filtered_links, 1):
                        reel_id = self.extract_reel_id(link)
                        self.logger.info(f"   [{i}/{len(filtered_links)}] {link} (ID: {reel_id})")
                        if reel_id and 'unknown_' not in reel_id:
                            processed_links.append(link)
                            self.logger.info(f"      ✅ Valid - Added to collection")
                        else:
                            self.logger.info(f"      ⚠️  Invalid reel ID - Skipped")
                
                links.update(processed_links)
                self.logger.info(f"✅ Initial collection complete: {len(processed_links)} valid links added")
            else:
                self.logger.info("⚠️  All found reels were duplicates")
                
            self.logger.info(f"Initial collection: Found {len(current_links)} links, "
                           f"filtered {duplicate_count} duplicates, "
                           f"processed {len(filtered_links)} valid links")
        else:
            self.logger.info("⚠️  No reels found on initial page scan")
        
        # Start batch saving process if enabled
        batch_size = self.scraping_config.batch_size
        self.logger.info(f"Batch processing enabled: Will save every {batch_size} new links")
        self.logger.info(f"📦 Batch processing enabled: Will save every {batch_size} new links")
            
        # Check if we've already reached the target        
        if target_remaining > 0 and len(links) >= target_remaining:
            self.logger.info(f"Already collected enough links ({len(links)}/{target_remaining}) without scrolling")
            return list(links)[:target_remaining]
            
        while scroll_count < self.scraping_config.max_scrolls:
            # Ultra-fast scrolling for maximum speed
            current_delay = self.scraping_config.scroll_delay
            if consecutive_no_new_links > 2:
                # If we're not finding new links, increase delay slightly
                current_delay = min(1.0, current_delay * 1.2)
            
            # Fast scroll technique - fewer intermediate scrolls
            for i in range(1, 3):  # Only 2 small scrolls instead of 3
                scroll_height = last_height / 3 * i
                self.driver.execute_script(f"window.scrollTo(0, {scroll_height});")
                time.sleep(current_delay / 4)  # Even faster scroll distribution
            
            # Final scroll to bottom with aggressive caching
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(current_delay / 4)  # Faster final scroll delay
            
            # Collect links with enhanced processing
            current_links = self.collect_visible_reel_links()
            old_count = len(links)
            
            if current_links:
                # Filter duplicates and process
                filtered_links, duplicate_count = self.filter_duplicate_reels(current_links)
                
                if filtered_links:
                    if config.ENABLE_CONCURRENT_PROCESSING:
                        # Use professional parallel processor
                        processor = get_parallel_processor(self.logger)
                        processed_links = processor.process_in_parallel(
                            filtered_links,
                            self._process_single_link,
                            task_type='scraping'
                        )
                        # Filter out None results
                        processed_links = [link for link in processed_links if link is not None]
                    else:
                        processed_links = filtered_links
                    
                    links.update(processed_links)
                    
                    # Only log detailed scroll info if not in minimal mode
                    if not getattr(config, 'MINIMAL_OUTPUT', True):
                        self.logger.info(f"Scroll {scroll_count + 1}: Found {len(current_links)} links, "
                                       f"filtered {duplicate_count} duplicates, "
                                       f"added {len(processed_links)} new valid links")
                    elif len(processed_links) > 0:
                        # In minimal mode, only show when we actually find new reels
                        self.logger.info(f"📍 Scroll {scroll_count + 1}: +{len(processed_links)} new reels")
            
            new_count = len(links)
            new_links_found = new_count - old_count
            
            # Check if we've reached the target number of links
            if target_remaining > 0 and new_count >= target_remaining:
                self.logger.info(f"Reached target of {target_remaining} links, stopping scroll")
                break
            
            # Check if we should save the batch
            if batch_size > 0 and new_count >= last_link_count + batch_size:
                self.logger.info(f"Reached batch size of {batch_size} new links, saving intermediate results...")
                self.save_batch_to_sheets(list(links))
                last_link_count = new_count
            
            # Check if new content loaded
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            
            # Track if we're finding new content
            if new_links_found == 0:
                consecutive_no_new_links += 1
            else:
                consecutive_no_new_links = 0
                
            # Stop conditions (updated for better target collection):
            # 1. No new height AND no new links found for 2 consecutive scrolls (end of page content)
            # 2. No new links found for 5 consecutive scrolls (if we have a target to meet)
            # 3. No new links found for 3 consecutive scrolls (if no target specified)
            
            max_no_new_links = 5 if target_remaining > 0 else 3
            
            if new_height == last_height and consecutive_no_new_links >= 2:
                self.logger.info("Reached end of page content (no new height and no new links)")
                break
            elif consecutive_no_new_links >= max_no_new_links:
                if target_remaining > 0:
                    self.logger.info(f"No new valid links found in {max_no_new_links} consecutive scrolls while trying to reach target")
                else:
                    self.logger.info(f"No new links found in {max_no_new_links} consecutive scrolls")
                break
                
            last_height = new_height
            scroll_count += 1
        
        # Show final statistics
        cache_stats = self.get_cache_stats()
        logger.info(f"Scrolling complete - {len(links)} reel links collected")
        logger.debug(f"Cache stats: {cache_stats['cached_reel_ids']} total IDs, cache loaded: {cache_stats['cache_loaded']}")
        
        self.logger.info(f"Scrolling complete. Collected {len(links)} unique reel links")
        self.logger.info(f"Cache stats: {cache_stats['cached_reel_ids']} cached IDs, "
                        f"cache loaded: {cache_stats['cache_loaded']}")
        
        # Return all links, or just up to the target limit if specified
        if target_remaining > 0 and len(links) > target_remaining:
            return list(links)[:target_remaining]
        return list(links)
    
    def extract_reel_links(self) -> List[str]:
        """Extract ONLY reel links from current page (no posts with /p/)"""
        links = []
        
        try:
            # Only look for reel links, not posts
            selectors = [
                "a[href*='/reel/']"
            ]
            
            for selector in selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                
                for element in elements:
                    try:
                        href = element.get_attribute('href')
                        if href and '/reel/' in href:
                            # Clean and validate URL
                            if 'instagram.com' in href:
                                # Remove query parameters
                                clean_url = href.split('?')[0]
                                if clean_url not in links:
                                    links.append(clean_url)
                    except Exception as e:
                        self.logger.debug(f"Error extracting reel link: {str(e)}")
                        continue
            
            self.logger.debug(f"Extracted {len(links)} reel links from current page")
            return links
            
        except Exception as e:
            self.logger.error(f"Error extracting reel links: {str(e)}")
            return links
    
    def save_batch_to_sheets(self, links: List[str]):
        """Save a batch of links to Google Sheets"""
        try:
            if not links:
                return
            
            self.logger.info(f"Saving batch of {len(links)} links to sheets")
            
            # Prepare batch data
            current_date = datetime.now().strftime("%d-%b-%y").upper()
            reels_data = []
            
            for url in links:
                if not self.sheets_manager.url_exists(url):
                    username = self.extract_username_from_url(url)
                    reel_id = self.extract_reel_id_from_url(url)
                    
                    reel_data = {
                        'date': current_date,
                        'username': username,
                        'url': url,
                        'reel_id': reel_id,
                        'description': '',
                        'status': 'pending',
                        'yt_posted_date': '',
                        'yt_id': ''
                    }
                    reels_data.append(reel_data)
            
            if reels_data:
                self.sheets_manager.batch_add_reels(reels_data)
                self.logger.info(f"Successfully saved {len(reels_data)} new reels to sheets")
            else:
                self.logger.info("No new URLs to save (all already exist)")
                
        except Exception as e:
            self.logger.error(f"Error saving batch to sheets: {str(e)}")
    
    def run_scraping(self) -> List[str]:
        """Main scraping execution with enhanced statistics and error handling"""
        all_collected_links = []
        
        try:
            # Display startup information
            self.show_startup_info()
            
            # Initialize the browser driver
            self.logger.info("🔧 Setting up Chrome browser...")
            self.driver = self.setup_driver()
            self.logger.info("✅ Chrome browser ready")
            
            # Track progress toward target
            target_reached = False
            total_collected = 0
            
            # Process each URL
            for i, url in enumerate(self.scraping_config.instagram_urls):
                if target_reached:
                    break
                    
                self.logger.info(f"\n📍 PROCESSING URL {i+1}/{len(self.scraping_config.instagram_urls)}")
                self.logger.info(f"🔗 {url}")
                self.logger.info("-" * 60)
                
                try:
                    # Navigate to Instagram
                    self.logger.info("🌐 Navigating to Instagram profile...")
                    self.navigate_to_instagram(url)
                    self.logger.info("🎬 Navigating to reels section...")
                    self.navigate_to_reels()
                    
                    # Calculate remaining target
                    remaining_target = 0
                    if self.scraping_config.target_links > 0:
                        remaining_target = self.scraping_config.target_links - total_collected
                        if remaining_target <= 0:
                            target_reached = True
                            break
                        self.logger.info(f"🎯 Need {remaining_target} more reels to reach target")
                    
                    # Collect links from this URL
                    self.logger.info(f"🔄 Starting reel collection...")
                    url_links = self.scroll_and_collect_links(remaining_target)
                    
                    if url_links:
                        # Save the links from this URL
                        total_collected += len(url_links)
                        all_collected_links.extend(url_links)
                        
                        self.logger.info("=" * 60)
                        self.logger.info(f"✅ URL {i+1} COMPLETED")
                        self.logger.info(f"📊 Links from this URL: {len(url_links)}")
                        self.logger.info(f"📊 Total links collected: {total_collected}")
                        
                        # Show collected links
                        self.logger.info("📝 COLLECTED REELS:")
                        for j, link in enumerate(url_links, 1):
                            reel_id = self.extract_reel_id(link)
                            self.logger.info(f"   {j}. {link} (ID: {reel_id})")
                        
                        # Check if we've reached our target
                        if self.scraping_config.target_links > 0 and total_collected >= self.scraping_config.target_links:
                            target_reached = True
                            self.logger.info(f"🎯 TARGET REACHED! Collected {total_collected}/{self.scraping_config.target_links} reels")
                            break
                        elif self.scraping_config.target_links > 0:
                            remaining = self.scraping_config.target_links - total_collected
                            self.logger.info(f"🎯 Progress: {total_collected}/{self.scraping_config.target_links} ({remaining} remaining)")
                        
                        self.logger.info("=" * 60)
                    else:
                        self.logger.info(f"⚠️  No reels collected from {url}")
                        
                except Exception as e:
                    self.logger.info(f"❌ Error processing URL {url}: {str(e)}")
                    self.logger.error(f"Error processing URL {url}: {str(e)}")
                    continue
            
            # Final statistics
            self.logger.info("\n" + "=" * 80)
            self.logger.info("🎉 SCRAPING COMPLETED!")
            self.logger.info("=" * 80)
            self.logger.info(f"📊 FINAL RESULTS:")
            self.logger.info(f"   📈 Total reels collected: {len(all_collected_links)}")
            self.logger.info(f"   🔗 URLs processed: {len(self.scraping_config.instagram_urls)}")
            if len(self.scraping_config.instagram_urls) > 0:
                avg = len(all_collected_links) / len(self.scraping_config.instagram_urls)
                self.logger.info(f"   📊 Average reels per URL: {avg:.1f}")
            
            if self.scraping_config.target_links > 0:
                percentage = (len(all_collected_links) / self.scraping_config.target_links) * 100
                self.logger.info(f"   🎯 Target completion: {percentage:.1f}% ({len(all_collected_links)}/{self.scraping_config.target_links})")
                
                if len(all_collected_links) >= self.scraping_config.target_links:
                    self.logger.info("✅ Target successfully reached!")
                else:
                    self.logger.info("⚠️  Target not fully reached")
            
            # Cache statistics
            cache_stats = self.get_cache_stats()
            self.logger.info(f"   🗂️  Duplicate cache: {cache_stats['cached_reel_ids']} IDs loaded")
            
            # Show all collected links summary
            if all_collected_links:
                self.logger.info("\n📋 ALL COLLECTED REELS SUMMARY:")
                for i, link in enumerate(all_collected_links, 1):
                    reel_id = self.extract_reel_id(link)
                    username = self.extract_username_from_url(link)
                    self.logger.info(f"   {i:2d}. {username} - {reel_id}")
                    self.logger.info(f"       🔗 {link}")
            
            self.logger.info("=" * 80)
            
            # Save backup if we collected links
            if all_collected_links:
                self.save_to_local_backup(all_collected_links)
                self.logger.info("💾 Backup saved to local file")
            
            return all_collected_links
            
        except Exception as e:
            error_msg = f"💥 Critical error in run_scraping: {str(e)}"
            self.logger.info(error_msg)
            self.logger.error(error_msg)
            return all_collected_links
            
        finally:
            self.cleanup_browser()
    
    def run_full_workflow(self):
        """Run complete workflow: scrape + process"""
        try:
            # Show enhanced startup information
            self.show_startup_info()
            
            # Step 1: Scrape Instagram reels
            self.logger.info("📋 Step 1: Scraping Instagram reels...")
            scraped_links = self.run_scraping()
            
            # Step 2: Run the full processing workflow
            if scraped_links:
                self.logger.info(f"✅ Scraped {len(scraped_links)} reel links")
                self.logger.info("🔄 Step 2: Processing reels with modular system...")
                self.logger.info("Running post-scraping processing workflow...")
                self.processor.run_full_workflow(scraped_links)
                
                # Completion message
                self.logger.info(f"Scraping workflow completed - {len(scraped_links)} new reels discovered")
            else:
                self.logger.info("No new reels found")
                self.logger.info("No new links scraped, running processing for existing data...")
                self.processor.run_full_workflow()
                
                # Completion message for existing data processing
                self.logger.info("")  # Empty line
                logger.info("Processing workflow completed - descriptions and uploads processed")
                self.logger.info("🌟 Processing workflow completed!")
                
        except Exception as e:
            self.logger.info(f"❌ Error in workflow: {str(e)}")
            self.logger.error(f"Error in run_full_workflow: {str(e)}")

    @staticmethod
    def extract_username_from_url(url: str) -> str:
        """Extract Instagram username from URL"""
        try:
            # Handle different URL patterns:
            # 1. https://www.instagram.com/username/reel/ABC123/ 
            # 2. https://www.instagram.com/reel/ABC123/ (direct reel link)
            # 3. https://www.instagram.com/username/
            
            import re
            
            if 'instagram.com/' in url:
                # Split by instagram.com/
                parts = url.split('instagram.com/')
                if len(parts) > 1:
                    path = parts[1]
                    
                    # Check if it's a reel URL with username before /reel/
                    if '/reel/' in path:
                        # Extract username before /reel/
                        username_part = path.split('/reel/')[0]
                        # Remove any query parameters and clean
                        username = username_part.split('?')[0].strip('/')
                        if username and username != "reel" and username:
                            # Clean up any @ symbols and add just one
                            clean_username = username.lstrip('@')
                            return f"@{clean_username}" if clean_username else ""
                    else:
                        # Profile URL like instagram.com/username/
                        username_part = path.split('/')[0]
                        # Remove any query parameters
                        username = username_part.split('?')[0]
                        if username and username != "reel" and username:
                            # Clean up any @ symbols and add just one
                            clean_username = username.lstrip('@')
                            return f"@{clean_username}" if clean_username else ""
            return ""
        except Exception as e:
            logger.debug(f"Error extracting username from URL: {str(e)}")
            return ""
    
    @staticmethod
    def extract_reel_id_from_url(url: str) -> str:
        """Extract reel ID from Instagram reel URL"""
        try:
            # Extract from URLs like https://www.instagram.com/reel/ABC123def/
            import re
            match = re.search(r'/reel/([^/\?]+)', url)
            if match:
                return match.group(1)
            return ""
        except Exception as e:
            logger.debug(f"Error extracting reel ID from URL: {str(e)}")
            return ""

    def extract_username_from_url(self, url: str) -> str:
        """Extract Instagram username from URL."""
        try:
            # Handle different URL patterns:
            # 1. https://www.instagram.com/username/reel/ABC123/ 
            # 2. https://www.instagram.com/reel/ABC123/ (from username's profile)
            # 3. https://www.instagram.com/username/
            
            if 'instagram.com/' in url:
                # Split by instagram.com/
                parts = url.split('instagram.com/')
                if len(parts) > 1:
                    path = parts[1]
                    
                    # Check if it's a reel URL with username before /reel/
                    if '/reel/' in path:
                        # Extract username before /reel/
                        username_part = path.split('/reel/')[0]
                        # Remove any query parameters
                        username = username_part.split('?')[0].strip('/')
                        if username and username != "reel":
                            # Clean up any @ symbols and add just one
                            clean_username = username.lstrip('@')
                            return f"@{clean_username}" if clean_username else "Unknown"
                    else:
                        # Profile URL like instagram.com/username/
                        username_part = path.split('/')[0]
                        # Remove any query parameters
                        username = username_part.split('?')[0]
                        if username and username != "reel":
                            # Clean up any @ symbols and add just one
                            clean_username = username.lstrip('@')
                            return f"@{clean_username}" if clean_username else "Unknown"
            return "Unknown"
        except Exception as e:
            self.logger.debug(f"Error extracting username from URL {url}: {e}")
            return "Unknown"
    
    def optimize_browser_performance(self):
        """Apply additional browser performance optimizations after startup"""
        try:
            # Inject aggressive performance CSS
            performance_css = """
            var style = document.createElement('style');
            style.type = 'text/css';
            style.innerHTML = `
                * { 
                    animation-duration: 0.001s !important; 
                    transition-duration: 0.001s !important;
                    animation-delay: 0s !important;
                    transition-delay: 0s !important;
                }
                img, video { display: none !important; }
                .lazy { display: none !important; }
            `;
            document.head.appendChild(style);
            """
            
            self.driver.execute_script(performance_css)
            self.logger.info("Applied aggressive performance optimizations")
            
        except Exception as e:
            self.logger.warning(f"Could not apply performance optimizations: {e}")

    def collect_visible_reel_links(self) -> List[str]:
        """Collect ONLY reel links from currently visible elements (no posts with /p/).
        Uses fast mode or detailed date checking based on configuration.
        """
        try:
            # JavaScript approach to find ONLY reel links
            links_js = """
            try {
                return Array.from(document.querySelectorAll('a[href*="/reel/"]'))
                    .map(a => a.href)
                    .filter(href => href && href.includes('/reel/'));
            } catch(e) {
                console.log('Reel link collection failed:', e);
                return [];
            }
            """
            js_results = self.driver.execute_script(links_js)
            
            if js_results:
                recent_links = []
                seen = set()
                
                # Check if we should skip date checking for speed
                skip_date_check = getattr(config, 'SKIP_DATE_CHECKING', False)
                
                if skip_date_check:
                    # FAST MODE: Skip date checking, just collect all reel links
                    if getattr(config, 'MINIMAL_OUTPUT', True):
                        self.logger.info(f"⚡ Fast mode: Collecting {len(js_results)} reels (skipping date checks)")
                    
                    for href in js_results:
                        if href and href not in seen:
                            # Clean URL
                            clean_url = href.split('?')[0] if '?' in href else href
                            if not clean_url.startswith('http'):
                                clean_url = f"https://instagram.com{clean_url}"
                            
                            # Ensure it's a reel, not a post
                            if '/reel/' in clean_url:
                                recent_links.append(clean_url)
                                seen.add(href)
                    
                    self.logger.info(f"⚡ Fast collection complete: {len(recent_links)} reels collected")
                    return recent_links
                
                else:
                    # DETAILED MODE: Check dates using parallel processing (faster)
                    if getattr(config, 'MINIMAL_OUTPUT', True):
                        logger.info(f"Filtering {len(js_results)} reels by date (within {self.scraping_config.days_limit} days)")
                    
                    # Prepare URLs for parallel processing
                    reel_urls = []
                    seen = set()
                    
                    for href in js_results:
                        if href and href not in seen:
                            # Clean URL
                            clean_url = href.split('?')[0] if '?' in href else href
                            if not clean_url.startswith('http'):
                                clean_url = f"https://instagram.com{clean_url}"
                            
                            # Ensure it's a reel, not a post
                            if '/reel/' in clean_url:
                                reel_urls.append(clean_url)
                                seen.add(href)
                    
                    # Use parallel processing for date checking
                    recent_links = self._filter_reels_by_date_parallel(reel_urls)
                    
                    if getattr(config, 'MINIMAL_OUTPUT', True):
                        logger.info(f"Date filtering complete: {len(recent_links)}/{len(reel_urls)} reels within {self.scraping_config.days_limit} days")
                        
                    self.logger.info(f"Found {len(recent_links)} recent reels (within {self.scraping_config.days_limit} days) "
                                   f"out of {len(reel_urls)} total using parallel detailed filtering")
                    return recent_links
            
        except Exception as e:
            self.logger.warning(f"Error with JavaScript approach: {e}")
            
        # Fallback to Selenium method
        self.logger.info("Using Selenium fallback method")
        return self.collect_visible_reel_links_selenium()
    
    def collect_visible_reel_links_selenium(self) -> List[str]:
        """Fallback method using pure Selenium to find ONLY reels (no posts).
        Uses detailed date checking for accuracy.
        """
        recent_links = []
        seen = set()
        
        try:
            # Find ONLY reel links, not posts
            selectors = [
                "a[href*='/reel/']"
            ]
            
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    logger.info(f"Selenium fallback: checking {len(elements)} potential reels for dates")
                    
                    for i, element in enumerate(elements, 1):
                        href = element.get_attribute('href')
                        if href and href not in seen and '/reel/' in href:
                            # Clean URL
                            clean_url = href.split('?')[0] if '?' in href else href
                            if not clean_url.startswith('http'):
                                clean_url = f"https://instagram.com{clean_url}"
                            
                            # Double-check it's a reel
                            if '/reel/' not in clean_url:
                                continue
                            
                            logger.debug(f"[{i}/{len(elements)}] Checking: {clean_url}")
                            
                            # Always use detailed date checking
                            if self.check_reel_date_detailed(clean_url):
                                recent_links.append(clean_url)
                                seen.add(href)
                                logger.debug(f"Recent reel added: {clean_url}")
                                self.logger.debug(f"Added recent reel (detailed): {clean_url}")
                            else:
                                logger.debug(f"Old reel skipped: {clean_url}")
                                self.logger.debug(f"Skipped old reel (detailed): {clean_url}")
                                
                except Exception as selector_error:
                    self.logger.debug(f"Error with selector {selector}: {selector_error}")
            
            logger.info(f"Selenium fallback complete: {len(recent_links)} recent reels found")
            self.logger.info(f"Selenium method found {len(recent_links)} recent reels using detailed filtering")
            return recent_links
            
        except Exception as e:
            self.logger.error(f"Error in Selenium fallback method: {e}")
            return []

    def get_performance_stats(self) -> Dict[str, any]:
        """Get performance statistics for the current configuration"""
        return {
            'fast_mode_enabled': self.scraping_config.fast_mode,
            'headless_mode': self.scraping_config.headless,
            'scroll_delay': self.scraping_config.scroll_delay,
            'batch_size': self.scraping_config.batch_size,
            'max_scrolls': self.scraping_config.max_scrolls,
            'target_links': self.scraping_config.target_links,
            'days_limit': self.scraping_config.days_limit,
            'urls_to_scrape': len(self.scraping_config.instagram_urls)
        }

    def save_to_local_backup(self, links: List[str]):
        """Save links to local JSON file as backup."""
        try:
            filename = f"reel_links_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            backup_data = []
            
            current_date = datetime.now().strftime('%d-%b-%y').upper()
            
            for link in links:
                reel_id = self.extract_reel_id(link)
                username = self.extract_username_from_url(link)
                
                backup_data.append({
                    'date': current_date,
                    'username': username,
                    'url': link,
                    'reel_id': reel_id or 'N/A',
                    'status': 'Pending'
                })
                
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Backup saved to {filename}")
            
        except Exception as e:
            self.logger.error(f"Error saving backup: {e}")

    def cleanup_browser(self):
        """Cleanup browser resources"""
        try:
            if self.driver:
                self.driver.quit()
                self.logger.info("Browser cleanup completed")
        except Exception as e:
            self.logger.warning(f"Error during browser cleanup: {e}")

    # =============================================================================
    # DUPLICATE DETECTION AND CACHING FUNCTIONS
    # =============================================================================
    
    def load_existing_reel_ids(self):
        """Load existing reel IDs from Google Sheets for duplicate checking."""
        try:
            self.logger.info("Loading existing reel IDs for duplicate checking...")
            
            # Get all data from sheets
            all_data = self.sheets_manager.get_all_data()
            
            # Extract reel IDs from URLs (assuming URL is in column 2, index 1)
            for row in all_data[1:]:  # Skip header
                if len(row) > 1:  # Has URL column
                    url = row[1]
                    if url:
                        reel_id = self.extract_reel_id(url)
                        if reel_id and reel_id != f"unknown_{int(time.time())}":
                            self.existing_reel_ids.add(reel_id)
            
            self.reel_id_cache_loaded = True
            self.logger.info(f"Loaded {len(self.existing_reel_ids)} existing reel IDs for duplicate checking")
            
        except Exception as e:
            self.logger.warning(f"Could not load existing reel IDs: {e}")
            self.reel_id_cache_loaded = False

    def is_duplicate_reel(self, reel_id: str) -> bool:
        """Fast check if a reel ID already exists in the sheet."""
        if not reel_id or 'unknown_' in reel_id:
            return False
            
        # Ensure cache is loaded
        if not self.reel_id_cache_loaded:
            self.load_existing_reel_ids()
            
        return reel_id in self.existing_reel_ids

    def add_reel_to_cache(self, reel_id: str):
        """Add a new reel ID to the cache when it's successfully saved."""
        if reel_id and 'unknown_' not in reel_id:
            self.existing_reel_ids.add(reel_id)

    def filter_duplicate_reels(self, links: List[str]) -> Tuple[List[str], int]:
        """Filter out duplicate reels from a list of links. Returns (new_links, duplicate_count)."""
        if not links:
            return [], 0
            
        new_links = []
        duplicate_count = 0
        processed_in_batch = set()  # Track what we've processed in this batch
        
        # Ensure cache is loaded
        if not self.reel_id_cache_loaded:
            self.load_existing_reel_ids()
        
        for link in links:
            reel_id = self.extract_reel_id(link)
            
            # Check against existing cache AND current batch
            if reel_id and (reel_id in self.existing_reel_ids or reel_id in processed_in_batch):
                duplicate_count += 1
                self.logger.debug(f"Skipping duplicate reel: {reel_id}")
            else:
                new_links.append(link)
                # Track in current batch but don't add to cache yet
                if reel_id and 'unknown_' not in reel_id:
                    processed_in_batch.add(reel_id)
        
        return new_links, duplicate_count

    def refresh_reel_id_cache(self):
        """Refresh the reel ID cache from Google Sheets."""
        self.existing_reel_ids.clear()
        self.reel_id_cache_loaded = False
        self.load_existing_reel_ids()
        self.logger.info("Reel ID cache refreshed")

    def get_cache_stats(self) -> Dict[str, any]:
        """Get statistics about the reel ID cache."""
        return {
            'cached_reel_ids': len(self.existing_reel_ids),
            'cache_loaded': self.reel_id_cache_loaded
        }

    # =============================================================================
    # ENHANCED PARALLEL PROCESSING FUNCTIONS
    # =============================================================================
    
    def _process_single_link(self, link: str) -> Optional[str]:
        """
        🔧 Process a single link for validation and reel ID extraction
        Optimized for use with professional parallel processor
        
        Args:
            link: Instagram link to process
            
        Returns:
            Valid link or None if invalid
        """
        try:
            reel_id = self.extract_reel_id(link)
            
            # Validate that we have a valid reel ID
            if reel_id and 'unknown_' not in reel_id:
                return link
            else:
                self.logger.debug(f"⚠️  Invalid reel ID for link: {link}")
                return None
                
        except Exception as e:
            self.logger.warning(f"💥 Error processing link {link}: {e}")
            return None
    
    def _progress_callback(self, completed: int, total: int, success: int, failed: int):
        """
        📊 Progress callback for parallel processing updates
        
        Args:
            completed: Number of completed tasks
            total: Total number of tasks
            success: Number of successful tasks
            failed: Number of failed tasks
        """
        if completed % 5 == 0 or completed == total:  # Update every 5 items or at completion
            progress_pct = (completed / total) * 100 if total > 0 else 0
            self.logger.info(f"📊 Link Processing: {completed}/{total} ({progress_pct:.1f}%) - "
                           f"✅ {success} valid, ❌ {failed} invalid")

    # =============================================================================
    # ENHANCED DATE CHECKING FUNCTIONS
    # =============================================================================
    
    def get_detailed_reel_date(self, reel_url: str) -> Optional[datetime]:
        """
        Get detailed date by opening individual reel and extracting precise timestamp.
        This is more accurate but slower than the general date checking.
        
        Args:
            reel_url: Instagram reel URL
            
        Returns:
            datetime object if found, None otherwise
        """
        try:
            self.logger.debug(f"🔍 Getting detailed date for: {reel_url}")
            
            # Store current URL to return to later
            current_url = self.driver.current_url
            self.logger.debug(f"📋 Storing current URL: {current_url}")
            
            # Navigate to the specific reel
            self.logger.debug(f"🌐 Navigating to reel URL...")
            self.driver.get(reel_url)
            
            # Wait for the page to load
            self.logger.debug(f"⏳ Waiting for page elements to load...")
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.TAG_NAME, "time"))
            )
            
            # Look for time elements with datetime attributes
            time_elements = self.driver.find_elements(By.TAG_NAME, "time")
            self.logger.debug(f"🕐 Found {len(time_elements)} time elements")
            
            for i, time_elem in enumerate(time_elements):
                datetime_attr = time_elem.get_attribute('datetime')
                title_attr = time_elem.get_attribute('title')
                text_content = time_elem.text
                
                self.logger.debug(f"   Time element {i+1}:")
                self.logger.debug(f"     datetime: {datetime_attr}")
                self.logger.debug(f"     title: {title_attr}")
                self.logger.debug(f"     text: {text_content}")
                
                if datetime_attr:
                    try:
                        # Parse ISO format datetime
                        post_date = datetime.fromisoformat(datetime_attr.replace('Z', '+00:00'))
                        # Convert to local timezone for comparison
                        post_date = post_date.replace(tzinfo=None)
                        
                        # Return to previous page
                        self.logger.debug(f"🔙 Returning to previous page: {current_url}")
                        self.driver.get(current_url)
                        time.sleep(0.5)  # Brief wait to load
                        
                        self.logger.debug(f"✅ Successfully extracted detailed date: {post_date}")
                        return post_date
                        
                    except Exception as parse_error:
                        self.logger.debug(f"❌ Could not parse datetime {datetime_attr}: {parse_error}")
                        continue
            
            # Look for other date indicators
            date_selectors = [
                "span[title*='202']",  # Year in title
                "time",
                "*[datetime]",
                "span:contains('ago')",
                "*[title*='ago']"
            ]
            
            self.logger.debug(f"🔍 Looking for alternative date selectors...")
            
            for selector in date_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    self.logger.debug(f"   Selector '{selector}': found {len(elements)} elements")
                    
                    for j, elem in enumerate(elements):
                        title = elem.get_attribute('title')
                        text = elem.text
                        
                        self.logger.debug(f"     Element {j+1}: title='{title}', text='{text}'")
                        
                        # Try to parse various date formats
                        for date_text in [title, text]:
                            if date_text:
                                parsed_date = self.parse_date_text(date_text)
                                if parsed_date:
                                    # Return to previous page
                                    self.logger.debug(f"🔙 Returning to previous page: {current_url}")
                                    self.driver.get(current_url)
                                    time.sleep(0.5)
                                    self.logger.debug(f"✅ Found date via alternative method: {parsed_date}")
                                    return parsed_date
                                    
                except Exception as selector_error:
                    self.logger.debug(f"⚠️  Error with selector '{selector}': {selector_error}")
                    continue
            
            # Return to previous page even if no date found
            self.logger.debug(f"🔙 No date found, returning to previous page: {current_url}")
            self.driver.get(current_url)
            time.sleep(0.5)
            
            self.logger.debug(f"❌ No date found for {reel_url}")
            return None
            
        except Exception as e:
            self.logger.debug(f"💥 Error getting detailed date for {reel_url}: {e}")
            # Try to return to previous page
            try:
                self.logger.debug(f"🔙 Error recovery: returning to previous page")
                self.driver.get(current_url)
                time.sleep(0.5)
            except:
                pass
            return None
    
    def parse_date_text(self, date_text: str) -> Optional[datetime]:
        """Parse various date text formats into datetime objects."""
        try:
            if not date_text:
                return None
                
            date_text = date_text.lower().strip()
            
            # Handle relative dates
            if 'ago' in date_text:
                numbers = re.findall(r'\d+', date_text)
                if numbers:
                    num = int(numbers[0])
                    
                    if 'second' in date_text or 's' in date_text:
                        return datetime.now() - timedelta(seconds=num)
                    elif 'minute' in date_text or 'm' in date_text:
                        return datetime.now() - timedelta(minutes=num)
                    elif 'hour' in date_text or 'h' in date_text:
                        return datetime.now() - timedelta(hours=num)
                    elif 'day' in date_text or 'd' in date_text:
                        return datetime.now() - timedelta(days=num)
                    elif 'week' in date_text or 'w' in date_text:
                        return datetime.now() - timedelta(weeks=num)
                    elif 'month' in date_text:
                        return datetime.now() - timedelta(days=num * 30)
                    elif 'year' in date_text:
                        return datetime.now() - timedelta(days=num * 365)
            
            # Try to parse absolute dates
            date_patterns = [
                r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
                r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
                r'\d{2}-\d{2}-\d{4}',  # MM-DD-YYYY
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, date_text)
                if match:
                    try:
                        return datetime.strptime(match.group(), '%Y-%m-%d')
                    except:
                        try:
                            return datetime.strptime(match.group(), '%m/%d/%Y')
                        except:
                            try:
                                return datetime.strptime(match.group(), '%m-%d-%Y')
                            except:
                                continue
            
            return None
            
        except Exception:
            return None
    
    def check_reel_date_detailed(self, reel_url: str) -> bool:
        """
        Check if reel is within days limit using detailed date extraction.
        This opens the individual reel to get precise date information.
        """
        try:
            self.logger.debug(f"🔍 Checking detailed date for reel: {reel_url}")
            
            detailed_date = self.get_detailed_reel_date(reel_url)
            
            if detailed_date:
                cutoff_date = datetime.now() - timedelta(days=self.scraping_config.days_limit)
                is_recent = detailed_date >= cutoff_date
                
                age_days = (datetime.now() - detailed_date).days
                age_hours = (datetime.now() - detailed_date).total_seconds() / 3600
                
                status_emoji = "✅" if is_recent else "❌"
                status_text = "RECENT" if is_recent else "TOO OLD"
                
                self.logger.debug(f"📅 REEL DATE ANALYSIS:")
                self.logger.debug(f"   🔗 URL: {reel_url}")
                self.logger.debug(f"   📆 Reel Date: {detailed_date.strftime('%Y-%m-%d %H:%M:%S')}")
                self.logger.debug(f"   ⏰ Age: {age_days} days ({age_hours:.1f} hours)")
                self.logger.debug(f"   🚫 Cutoff Date: {cutoff_date.strftime('%Y-%m-%d %H:%M:%S')}")
                self.logger.debug(f"   📊 Days Limit: {self.scraping_config.days_limit} days")
                self.logger.debug(f"   {status_emoji} RESULT: {status_text}")
                
                return is_recent
            else:
                # If we can't get detailed date, be conservative and skip it
                self.logger.debug(f"⚠️  Could not extract detailed date for {reel_url}")
                self.logger.debug(f"❌ RESULT: SKIPPED (no date found - conservative approach)")
                return False
                
        except Exception as e:
            self.logger.debug(f"💥 Error in detailed date check for {reel_url}: {e}")
            self.logger.debug(f"❌ RESULT: SKIPPED (error occurred)")
            # Be conservative and skip if there's an error
            return False
            
    def show_startup_info(self):
        """Display startup information including today's date"""
        today = datetime.now()
        
        self.logger.info("=" * 80)
        self.logger.info("🚀 INSTAGRAM REELS SCRAPER STARTING")
        self.logger.info("=" * 80)
        self.logger.info(f"📅 TODAY'S DATE: {today.strftime('%d-%b-%y').upper()}")
        self.logger.info(f"⏰ START TIME: {today.strftime('%H:%M:%S')}")
        self.logger.info(f"🌍 TIMEZONE: {today.astimezone().tzname()}")
        self.logger.info("=" * 80)
        self.logger.info("📊 PERFORMANCE SETTINGS:")
        self.logger.info(f"   🏃 Fast Mode: {self.scraping_config.fast_mode}")
        self.logger.info(f"   👻 Headless: {self.scraping_config.headless}")
        self.logger.info(f"   ⏱️  Scroll Delay: {self.scraping_config.scroll_delay}s")
        self.logger.info(f"   📦 Batch Size: {self.scraping_config.batch_size}")
        self.logger.info(f"   🔄 Max Scrolls: {self.scraping_config.max_scrolls}")
        self.logger.info(f"   📅 Days Limit: {self.scraping_config.days_limit} days")
        # Display date checking mode
        skip_date_check = getattr(config, 'SKIP_DATE_CHECKING', False)
        if skip_date_check:
            self.logger.info(f"   ⚡ Date Checking: Fast mode (skips date verification for speed)")
        else:
            self.logger.info(f"   🔍 Date Checking: Detailed (opens each reel for precise date)")
        self.logger.info(f"🎯 TARGET: {self.scraping_config.target_links} reels")
        self.logger.info(f"🔗 URLS TO PROCESS: {len(self.scraping_config.instagram_urls)}")
        
        for i, url in enumerate(self.scraping_config.instagram_urls, 1):
            self.logger.info(f"   {i}. {url}")
        
        self.logger.info("=" * 80)

def main():
    """Main function"""
    try:
        scraper = InstagramReelScraper()
        
        # Run the complete workflow
        scraper.run_full_workflow()
        
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")

if __name__ == "__main__":
    main()
