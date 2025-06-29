#!/usr/bin/env python3
"""
Updated Instagram Reel Scraper
Focuses only on link collection and saves to Google Sheets with "pending" status.
Uses the new modular system for descriptions and uploads.
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
from concurrent.futures import ThreadPoolExecutor
import config

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

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('instagram_scraper.log'),
        logging.StreamHandler()
    ]
)
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
    
    def is_recent_reel(self, post_element) -> bool:
        """Check if reel is within the days limit"""
        try:
            # This is a simplified check - Instagram doesn't always show dates clearly
            # You might need to implement more sophisticated date detection
            return True  # For now, assume all reels are recent
            
        except Exception as e:
            self.logger.debug(f"Error checking reel date: {str(e)}")
            return True
    
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
        
        self.logger.info("Starting to scroll and collect reel links with enhanced filtering...")
        if target_remaining > 0:
            self.logger.info(f"Will stop after collecting {target_remaining} links")
        
        # Load existing reel IDs for duplicate checking
        if not self.reel_id_cache_loaded:
            self.load_existing_reel_ids()
        
        # Apply browser optimizations
        self.optimize_browser_performance()
        
        # Preload the page to ensure the DOM is ready
        time.sleep(1)
        
        # First batch collection (without scrolling)
        use_detailed_check = getattr(config, 'USE_DETAILED_DATE_CHECK', False)
        current_links = self.collect_visible_reel_links(use_detailed_check)
        
        # Filter duplicates and process in parallel
        if current_links:
            filtered_links, duplicate_count = self.filter_duplicate_reels(current_links)
            if hasattr(config, 'ENABLE_CONCURRENT_PROCESSING') and config.ENABLE_CONCURRENT_PROCESSING:
                processed_links = self.process_links_parallel(filtered_links)
            else:
                processed_links = filtered_links
            
            links.update(processed_links)
            self.logger.info(f"Initial collection: Found {len(current_links)} links, "
                           f"filtered {duplicate_count} duplicates, "
                           f"processed {len(processed_links)} valid links")
        
        # Start batch saving process if enabled
        batch_size = self.scraping_config.batch_size
        self.logger.info(f"Batch processing enabled: Will save every {batch_size} new links")
            
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
            use_detailed_check = getattr(config, 'USE_DETAILED_DATE_CHECK', False)
            current_links = self.collect_visible_reel_links(use_detailed_check)
            old_count = len(links)
            
            if current_links:
                # Filter duplicates and process
                filtered_links, duplicate_count = self.filter_duplicate_reels(current_links)
                
                if filtered_links:
                    if hasattr(config, 'ENABLE_CONCURRENT_PROCESSING') and config.ENABLE_CONCURRENT_PROCESSING:
                        processed_links = self.process_links_parallel(filtered_links)
                    else:
                        processed_links = filtered_links
                    
                    links.update(processed_links)
                    
                    self.logger.info(f"Scroll {scroll_count + 1}: Found {len(current_links)} links, "
                                   f"filtered {duplicate_count} duplicates, "
                                   f"added {len(processed_links)} new valid links")
            
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
            current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            reels_data = []
            
            for url in links:
                if not self.sheets_manager.url_exists(url):
                    reel_data = {
                        'date': current_date,
                        'url': url,
                        'status': 'pending',
                        'description': '',
                        'file_id': ''
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
            self.logger.info("=" * 50)
            self.logger.info("🚀 Starting SPEED-OPTIMIZED Instagram Reel Scraper...")
            self.logger.info("=" * 50)
            
            # Show performance stats
            perf_stats = self.get_performance_stats()
            self.logger.info(f"📊 Performance Settings: Fast Mode: {perf_stats['fast_mode_enabled']}, "
                           f"Headless: {perf_stats['headless_mode']}, "
                           f"Scroll Delay: {perf_stats['scroll_delay']}s, "
                           f"Batch Size: {perf_stats['batch_size']}")
            
            # Setup driver
            self.driver = self.setup_driver()
            
            # Track progress toward target
            target_reached = False
            total_collected = 0
            
            # Process each URL
            for i, url in enumerate(self.scraping_config.instagram_urls):
                if target_reached:
                    break
                    
                self.logger.info(f"Processing URL {i+1}/{len(self.scraping_config.instagram_urls)}: {url}")
                
                try:
                    # Navigate to Instagram
                    self.navigate_to_instagram(url)
                    self.navigate_to_reels()
                    
                    # Calculate remaining target
                    remaining_target = 0
                    if self.scraping_config.target_links > 0:
                        remaining_target = self.scraping_config.target_links - total_collected
                        if remaining_target <= 0:
                            target_reached = True
                            break
                        self.logger.info(f"Need {remaining_target} more links to reach target of {self.scraping_config.target_links}")
                    
                    # Collect links from this URL
                    self.logger.info(f"Collecting reels from URL: {url}")
                    url_links = self.scroll_and_collect_links(remaining_target)
                    
                    if url_links:
                        # Save the links from this URL
                        total_collected += len(url_links)
                        all_collected_links.extend(url_links)
                        
                        self.logger.info(f"URL {url} completed. Collected {len(url_links)} links.")
                        self.logger.info(f"Total links collected so far: {total_collected}")
                        
                        # Check if we've reached our target
                        if self.scraping_config.target_links > 0 and total_collected >= self.scraping_config.target_links:
                            target_reached = True
                            self.logger.info(f"🎯 Target of {self.scraping_config.target_links} links reached!")
                            break
                    else:
                        self.logger.warning(f"No links collected from {url}")
                        
                except Exception as e:
                    self.logger.error(f"Error processing URL {url}: {str(e)}")
                    continue
            
            # Final statistics
            self.logger.info("=" * 50)
            self.logger.info(f"✅ Scraping completed! Total links collected: {len(all_collected_links)}")
            
            if self.scraping_config.target_links > 0:
                percentage = (len(all_collected_links) / self.scraping_config.target_links) * 100
                self.logger.info(f"📈 Target completion: {percentage:.1f}% ({len(all_collected_links)}/{self.scraping_config.target_links})")
            
            self.logger.info(f"📊 URLs processed: {len(self.scraping_config.instagram_urls)}")
            self.logger.info(f"🔗 Average links per URL: {len(all_collected_links) / len(self.scraping_config.instagram_urls):.1f}")
            self.logger.info("=" * 50)
            
            # Save backup if we collected links
            if all_collected_links:
                self.save_to_local_backup(all_collected_links)
            
            return all_collected_links
            
        except Exception as e:
            self.logger.error(f"Critical error in run_scraping: {str(e)}")
            return all_collected_links
            
        finally:
            self.cleanup_browser()
    
    def run_full_workflow(self):
        """Run complete workflow: scrape + process"""
        try:
            # Step 1: Scrape Instagram reels
            scraped_links = self.run_scraping()
            
            # Step 2: Run the full processing workflow
            if scraped_links:
                self.logger.info("Running post-scraping processing workflow...")
                self.processor.run_full_workflow(scraped_links)
            else:
                self.logger.info("No new links scraped, running processing for existing data...")
                self.processor.run_full_workflow()
                
        except Exception as e:
            self.logger.error(f"Error in run_full_workflow: {str(e)}")

    def check_reel_date(self, reel_element) -> bool:
        """Check if a reel was posted within the configured days limit."""
        try:
            # Look for time elements or date indicators near the reel
            date_selectors = [
                ".//time",
                ".//span[contains(@class, 'time')]",
                ".//a[contains(@href, '/reel/')]/..//time",
                ".//*[contains(text(), 'd') or contains(text(), 'day') or contains(text(), 'week') or contains(text(), 'hour')]"
            ]
            
            cutoff_date = datetime.now() - timedelta(days=self.scraping_config.days_limit)
            
            for selector in date_selectors:
                try:
                    time_elements = reel_element.find_elements(By.XPATH, selector)
                    for time_elem in time_elements:
                        # Get the datetime attribute if available
                        datetime_attr = time_elem.get_attribute('datetime')
                        if datetime_attr:
                            try:
                                post_date = datetime.fromisoformat(datetime_attr.replace('Z', '+00:00'))
                                # Convert to local timezone for comparison
                                post_date = post_date.replace(tzinfo=None)
                                return post_date >= cutoff_date
                            except:
                                continue
                        
                        # Check text content for relative time indicators
                        time_text = time_elem.text.lower().strip()
                        if self.is_within_days_limit(time_text):
                            return True
                        
                except Exception:
                    continue
                    
            # If no specific date found, assume it's recent (could be enhanced)
            return True
            
        except Exception as e:
            self.logger.debug(f"Error checking reel date: {e}")
            return True  # Default to including the reel if date check fails
    
    def is_within_days_limit(self, time_text: str) -> bool:
        """Check if relative time text indicates the post is within the configured days limit."""
        try:
            time_text = time_text.lower()
            days_limit = self.scraping_config.days_limit
            
            # Recent posts (definitely within days limit)
            if any(keyword in time_text for keyword in ['second', 'minute', 'hour', 'just now', 'now']):
                return True
                
            # Days
            if 'd' in time_text or 'day' in time_text:
                numbers = re.findall(r'\d+', time_text)
                if numbers:
                    days = int(numbers[0])
                    return days <= days_limit
                    
            # Weeks
            if 'w' in time_text or 'week' in time_text:
                numbers = re.findall(r'\d+', time_text)
                if numbers:
                    weeks = int(numbers[0])
                    return weeks <= (days_limit // 7)  # Convert days to weeks
                    
            # Months (check if within the days limit)
            if 'month' in time_text or 'mo' in time_text:
                numbers = re.findall(r'\d+', time_text)
                if numbers:
                    months = int(numbers[0])
                    return months * 30 <= days_limit  # Rough conversion
                return False  # If it says "month" without number, assume > 1 month
                
            # Years (definitely too old)
            if 'year' in time_text or 'yr' in time_text:
                return False
                
            # If we can't determine, assume it's recent
            return True
            
        except Exception:
            return True
    
    def extract_username_from_url(self, url: str) -> str:
        """Extract Instagram username from URL."""
        try:
            # Extract username from URL pattern like https://www.instagram.com/username/
            if 'instagram.com/' in url:
                parts = url.split('instagram.com/')
                if len(parts) > 1:
                    username_part = parts[1].split('/')[0]
                    # Remove any query parameters
                    username = username_part.split('?')[0]
                    return f"@{username}" if username else "Unknown"
            return "Unknown"
        except Exception:
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

    def collect_visible_reel_links(self, use_detailed_date_check: bool = False) -> List[str]:
        """Collect ONLY reel links from currently visible elements (no posts with /p/).
        
        Args:
            use_detailed_date_check: If True, opens each reel to get precise date (slower but more accurate)
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
                
                for href in js_results:
                    if href and href not in seen:
                        # Clean URL
                        clean_url = href.split('?')[0] if '?' in href else href
                        if not clean_url.startswith('http'):
                            clean_url = f"https://instagram.com{clean_url}"
                        
                        # Ensure it's a reel, not a post
                        if '/reel/' not in clean_url:
                            continue
                        
                        # Check if within days limit
                        if use_detailed_date_check:
                            # Use detailed date checking (slower but more accurate)
                            if self.check_reel_date_detailed(clean_url):
                                recent_links.append(clean_url)
                                seen.add(href)
                                self.logger.debug(f"Added recent reel (detailed): {clean_url}")
                            else:
                                self.logger.debug(f"Skipped old reel (detailed): {clean_url}")
                        else:
                            # Use fast date checking with DOM elements
                            try:
                                link_element = self.driver.find_element(By.XPATH, f"//a[@href='{href}']")
                                parent_element = link_element.find_element(By.XPATH, "./ancestor::article | ./ancestor::div[contains(@class, 'reel')]")
                                
                                if self.check_reel_date(parent_element):
                                    recent_links.append(clean_url)
                                    seen.add(href)
                                    self.logger.debug(f"Added recent reel: {clean_url}")
                                else:
                                    self.logger.debug(f"Skipped old reel: {clean_url}")
                                    
                            except Exception as elem_error:
                                # If we can't find the element or check date, SKIP it to be conservative
                                self.logger.debug(f"Could not check date for {clean_url}, skipping for safety: {elem_error}")
                                continue
                
                filter_type = "detailed" if use_detailed_date_check else "fast"
                self.logger.info(f"Found {len(recent_links)} recent reels (within {self.scraping_config.days_limit} days) "
                               f"out of {len(js_results)} total using {filter_type} filtering")
                return recent_links
            
        except Exception as e:
            self.logger.warning(f"Error with JavaScript approach: {e}")
            
        # Fallback to Selenium method
        self.logger.info("Using Selenium fallback method")
        return self.collect_visible_reel_links_selenium(use_detailed_date_check)
    
    def collect_visible_reel_links_selenium(self, use_detailed_date_check: bool = False) -> List[str]:
        """Fallback method using pure Selenium to find ONLY reels (no posts).
        
        Args:
            use_detailed_date_check: If True, opens each reel to get precise date
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
                    for element in elements:
                        href = element.get_attribute('href')
                        if href and href not in seen and '/reel/' in href:
                            # Clean URL
                            clean_url = href.split('?')[0] if '?' in href else href
                            if not clean_url.startswith('http'):
                                clean_url = f"https://instagram.com{clean_url}"
                            
                            # Double-check it's a reel
                            if '/reel/' not in clean_url:
                                continue
                            
                            # Check date based on method
                            if use_detailed_date_check:
                                # Use detailed date checking
                                if self.check_reel_date_detailed(clean_url):
                                    recent_links.append(clean_url)
                                    seen.add(href)
                                    self.logger.debug(f"Added recent reel (detailed): {clean_url}")
                                else:
                                    self.logger.debug(f"Skipped old reel (detailed): {clean_url}")
                            else:
                                # Use fast DOM-based date checking
                                try:
                                    parent_element = element.find_element(By.XPATH, "./ancestor::article | ./ancestor::div[contains(@class, 'reel')]")
                                    
                                    if self.check_reel_date(parent_element):
                                        recent_links.append(clean_url)
                                        seen.add(href)
                                        self.logger.debug(f"Added recent reel: {clean_url}")
                                    else:
                                        self.logger.debug(f"Skipped old reel: {clean_url}")
                                        
                                except Exception:
                                    # If we can't find parent or check date, SKIP it to be conservative
                                    self.logger.debug(f"Could not check date for {clean_url}, skipping for safety")
                                    continue
                                
                except Exception as selector_error:
                    self.logger.debug(f"Error with selector {selector}: {selector_error}")
            
            filter_type = "detailed" if use_detailed_date_check else "fast"
            self.logger.info(f"Selenium method found {len(recent_links)} recent reels using {filter_type} filtering")
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
        
        # Ensure cache is loaded
        if not self.reel_id_cache_loaded:
            self.load_existing_reel_ids()
        
        for link in links:
            reel_id = self.extract_reel_id(link)
            
            if reel_id and reel_id in self.existing_reel_ids:
                duplicate_count += 1
                self.logger.debug(f"Skipping duplicate reel: {reel_id}")
            else:
                new_links.append(link)
                # Add to cache immediately to prevent duplicates within this batch
                if reel_id and 'unknown_' not in reel_id:
                    self.existing_reel_ids.add(reel_id)
        
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
    # PARALLEL PROCESSING FUNCTIONS
    # =============================================================================
    
    def process_links_parallel(self, links: List[str], max_workers: int = 4) -> List[str]:
        """Process links in parallel for ultra-fast duplicate checking and validation.
        
        Args:
            links: List of Instagram links to process
            max_workers: Number of parallel workers (default: 4)
            
        Returns:
            List of validated, non-duplicate links
        """
        if not links:
            return []
            
        self.logger.info(f"Processing {len(links)} links in parallel with {max_workers} workers")
        
        def process_single_link(link: str) -> Optional[str]:
            """Process a single link - extract reel ID and check for duplicates."""
            try:
                reel_id = self.extract_reel_id(link)
                if reel_id and not self.is_duplicate_reel(reel_id):
                    return link
                return None
            except Exception as e:
                self.logger.debug(f"Error processing link {link}: {e}")
                return None
        
        # Use ThreadPoolExecutor for parallel processing
        valid_links = []
        try:
            from concurrent.futures import ThreadPoolExecutor
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all links for processing
                future_to_link = {executor.submit(process_single_link, link): link for link in links}
                
                # Collect results
                for future in future_to_link:
                    result = future.result()
                    if result:
                        valid_links.append(result)
                        
        except Exception as e:
            self.logger.warning(f"Parallel processing failed, falling back to sequential: {e}")
            # Fallback to sequential processing
            for link in links:
                result = process_single_link(link)
                if result:
                    valid_links.append(result)
        
        self.logger.info(f"Parallel processing complete: {len(valid_links)} valid links from {len(links)} total")
        return valid_links

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
            self.logger.debug(f"Getting detailed date for: {reel_url}")
            
            # Store current URL to return to later
            current_url = self.driver.current_url
            
            # Navigate to the specific reel
            self.driver.get(reel_url)
            
            # Wait for the page to load
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.TAG_NAME, "time"))
            )
            
            # Look for time elements with datetime attributes
            time_elements = self.driver.find_elements(By.TAG_NAME, "time")
            
            for time_elem in time_elements:
                datetime_attr = time_elem.get_attribute('datetime')
                if datetime_attr:
                    try:
                        # Parse ISO format datetime
                        post_date = datetime.fromisoformat(datetime_attr.replace('Z', '+00:00'))
                        # Convert to local timezone for comparison
                        post_date = post_date.replace(tzinfo=None)
                        
                        # Return to previous page
                        self.driver.get(current_url)
                        time.sleep(0.5)  # Brief wait to load
                        
                        self.logger.debug(f"Found detailed date: {post_date}")
                        return post_date
                        
                    except Exception as parse_error:
                        self.logger.debug(f"Could not parse datetime {datetime_attr}: {parse_error}")
                        continue
            
            # Look for other date indicators
            date_selectors = [
                "span[title*='202']",  # Year in title
                "time",
                "*[datetime]",
                "span:contains('ago')",
                "*[title*='ago']"
            ]
            
            for selector in date_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elements:
                        title = elem.get_attribute('title')
                        text = elem.text
                        
                        # Try to parse various date formats
                        for date_text in [title, text]:
                            if date_text:
                                parsed_date = self.parse_date_text(date_text)
                                if parsed_date:
                                    # Return to previous page
                                    self.driver.get(current_url)
                                    time.sleep(0.5)
                                    return parsed_date
                                    
                except Exception:
                    continue
            
            # Return to previous page even if no date found
            self.driver.get(current_url)
            time.sleep(0.5)
            
            return None
            
        except Exception as e:
            self.logger.debug(f"Error getting detailed date for {reel_url}: {e}")
            # Try to return to previous page
            try:
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
            detailed_date = self.get_detailed_reel_date(reel_url)
            
            if detailed_date:
                cutoff_date = datetime.now() - timedelta(days=self.scraping_config.days_limit)
                is_recent = detailed_date >= cutoff_date
                
                age_days = (datetime.now() - detailed_date).days
                self.logger.debug(f"Detailed date check for {reel_url}: {detailed_date.strftime('%Y-%m-%d')} "
                                f"({age_days} days ago) -> {'✅ Recent' if is_recent else '❌ Too old'}")
                return is_recent
            else:
                # If we can't get detailed date, use strict filtering setting
                strict_filtering = getattr(config, 'STRICT_DATE_FILTERING', True)
                if strict_filtering:
                    self.logger.debug(f"Could not get detailed date for {reel_url}, skipping (strict mode)")
                    return False
                else:
                    self.logger.debug(f"Could not get detailed date for {reel_url}, assuming recent (permissive mode)")
                    return True
                
        except Exception as e:
            self.logger.debug(f"Error in detailed date check for {reel_url}: {e}")
            # Use strict filtering setting for error cases too
            strict_filtering = getattr(config, 'STRICT_DATE_FILTERING', True)
            return not strict_filtering  # Return False if strict, True if permissive
            
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
