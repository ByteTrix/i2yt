#!/usr/bin/env python3
"""
Instagram Reel Scraper
Automation script that opens browser, navigates to Instagram, 
collects reel links and stores them in Google Sheets.
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

# Selenium imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Google Sheets imports
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# Configuration
@dataclass
class Config:
    instagram_url: str
    google_sheets_id: str
    instagram_urls: List[str] = None  # List of URLs to scrape
    target_links: int = 0  # Target number of links to collect (0 = unlimited)    
    days_limit: int = 30  # Only collect reels from last N days
    credentials_file: str = "credentials.json"
    max_scrolls: int = 15  # Will be overridden by config.py
    scroll_delay: float = 0.5  # Will be overridden by config.py
    batch_size: int = 25  # Will be overridden by config.py
    implicit_wait: int = 5  # Will be overridden by config.py
    page_load_timeout: int = 20  # Will be overridden by config.py
    headless: bool = False  # Will be overridden by config.py
    fast_mode: bool = True  # Will be overridden by config.py
    
class InstagramReelScraper:
    def __init__(self, config: Config):
        self.config = config
        self.driver = None
        self.sheet = None
        self.collected_links = set()
        self.existing_reel_ids = set()  # Cache for existing reel IDs
        self.reel_id_cache_loaded = False  # Track if cache is loaded
          # Setup logging with UTF-8 encoding support
        import sys
        
        # Configure file handler with UTF-8 encoding
        file_handler = logging.FileHandler('instagram_scraper.log', encoding='utf-8')
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        
        # Configure console handler with UTF-8 encoding for Windows compatibility
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        
        # Try to set UTF-8 encoding for console on Windows
        try:
            if hasattr(sys.stdout, 'reconfigure'):
                sys.stdout.reconfigure(encoding='utf-8')
        except:
            pass  # Fallback for older Python versions or systems
        
        logging.basicConfig(
            level=logging.INFO,
            handlers=[file_handler, console_handler],
            force=True  # Override existing configuration
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_driver(self) -> webdriver.Chrome:
        """Setup Chrome WebDriver with a dedicated profile directory that preserves cookies."""
        self.logger.info("Starting Chrome with a dedicated profile for Instagram scraping...")
        
        try:
            chrome_options = Options()
            # Create a dedicated profile directory in the project folder
            profile_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "instagram_profile")
            
            # Create profile directory if it doesn't exist (preserve existing login)
            os.makedirs(profile_dir, exist_ok=True)
            
            self.logger.info(f"Using profile directory: {profile_dir}")
            
            # Set up Chrome options for faster loading
            chrome_options.add_argument(f"--user-data-dir={profile_dir}")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
              # Performance optimizations for maximum speed
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-notifications")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-infobars")
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
            
            # Security bypasses for TrustedHTML issues
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--disable-features=VizDisplayCompositor")
            chrome_options.add_argument("--disable-features=TrustedWebActivity")
            chrome_options.add_argument("--allow-running-insecure-content")
            chrome_options.add_argument("--disable-security-policy")
            chrome_options.add_argument("--disable-features=TrustTokens")
            chrome_options.add_argument("--disable-features=TrustedDOMTypes")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--allow-running-insecure-content")
            chrome_options.add_argument("--ignore-certificate-errors")
            chrome_options.add_argument("--ignore-ssl-errors")
            chrome_options.add_argument("--ignore-certificate-errors-spki-list")
            chrome_options.add_argument("--ignore-certificate-errors-ssl")
            chrome_options.add_argument("--disable-site-isolation-trials")
            chrome_options.add_argument("--disable-blink-features=TrustedDOMTypes,RequireTrustedTypesForDOM")
            chrome_options.add_argument("--use-fake-ui-for-media-stream")
            chrome_options.add_argument("--enable-unsafe-swiftshader")
        
              # Disable images and other content for maximum speed if fast_mode is enabled
            if hasattr(self.config, 'fast_mode') and self.config.fast_mode:
                self.logger.info("Fast mode enabled: disabling images, CSS animations, and other content")
                prefs = {
                    "profile.managed_default_content_settings.images": 2,  # 2 = block images
                    "profile.default_content_setting_values.notifications": 2,  # 2 = block notifications
                    "profile.managed_default_content_settings.stylesheets": 2,  # Block CSS
                    "profile.managed_default_content_setting_values.cookies": 1,  # Allow cookies
                    "profile.managed_default_content_settings.javascript": 1,  # Allow JS (needed for Instagram)
                    "profile.managed_default_content_settings.plugins": 2,  # Block plugins
                    "profile.managed_default_content_settings.popups": 2,  # Block popups
                    "profile.managed_default_content_settings.geolocation": 2,  # Block location
                    "profile.managed_default_content_settings.media_stream": 2,  # Block media
                }
                chrome_options.add_experimental_option("prefs", prefs)
            
            # Set a realistic user agent
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            if self.config.headless:
                self.logger.warning("Running in headless mode. Note that Instagram may detect this.")
                chrome_options.add_argument("--headless")
            
            driver = webdriver.Chrome(options=chrome_options)
            driver.implicitly_wait(self.config.implicit_wait)
            driver.set_page_load_timeout(self.config.page_load_timeout)
            
            # Attempt to hide automation
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
              # Inject CSS to hide animations for faster performance if fast_mode is enabled
            if hasattr(self.config, 'fast_mode') and self.config.fast_mode:
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
            
            self.logger.info("Chrome browser started successfully with dedicated profile")
            return driver
            
        except Exception as e:
            self.logger.error(f"Failed to start Chrome: {e}")
            raise
            
    def setup_google_sheets(self):
        """Setup Google Sheets connection."""
        try:
            self.logger.info("Setting up Google Sheets connection...")
            
            # Check if credentials file exists
            if not os.path.exists(self.config.credentials_file):
                raise FileNotFoundError(f"Credentials file not found: {self.config.credentials_file}")
            
            # Define the scope
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            
            self.logger.info("Loading Google Service Account credentials...")
            # Load credentials
            creds = Credentials.from_service_account_file(
                self.config.credentials_file, 
                scopes=scope
            )
            
            self.logger.info("Authorizing Google Sheets client...")
            # Initialize the client
            client = gspread.authorize(creds)
            
            self.logger.info(f"Opening Google Sheet with ID: {self.config.google_sheets_id}")
            # Open the spreadsheet
            spreadsheet = client.open_by_key(self.config.google_sheets_id)
            self.sheet = spreadsheet.sheet1  # Use the first sheet
            
            self.logger.info(f"Successfully connected to sheet: {spreadsheet.title}")
            
            # Setup headers if they don't exist
            try:
                self.logger.info("Checking/setting up sheet headers...")                
                headers = self.sheet.row_values(1)
                if not headers or headers != ['Date', 'Insta Username', 'Link', 'Reel ID', 'Status', 'YT Posted Date','Shorts ID']:
                    self.sheet.clear()
                    self.sheet.append_row(['Date', 'Insta Username', 'Link', 'Reel ID', 'Status', 'YT Posted Date','Shorts ID'])
                    self.logger.info("Headers added to Google Sheet")
                    
                    # Setup dropdown validation for Status column (column E)
                    try:
                        self.setup_status_dropdown()
                    except Exception as dropdown_error:
                        self.logger.warning(f"Could not setup status dropdown: {dropdown_error}")
                        
                else:
                    self.logger.info("Headers already exist and are correct")
            except Exception as header_error:
                self.logger.warning(f"Could not set headers, trying to add them: {header_error}")
                try:
                    self.sheet.append_row(['Date', 'Insta Username', 'Link', 'Reel ID', 'Status', 'YT Posted Date','Shorts ID'])
                    self.logger.info("Headers added successfully")
                except Exception as add_error:
                    self.logger.error(f"Failed to add headers: {add_error}")
                
            self.logger.info("Google Sheets connection established successfully")
            
            # Load existing reel IDs for fast duplicate checking
            self.load_existing_reel_ids()
            
        except FileNotFoundError as e:
            self.logger.error(f"Credentials file error: {e}")
            raise
        except gspread.exceptions.SpreadsheetNotFound:
            self.logger.error(f"Google Sheet not found with ID: {self.config.google_sheets_id}")
            self.logger.error("Please check:")
            self.logger.error("1. The Sheet ID is correct")
            self.logger.error("2. The sheet is shared with the service account email")
            self.logger.error(f"3. Service account email: {creds.service_account_email if 'creds' in locals() else 'Unable to determine'}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to setup Google Sheets: {str(e)}")
            self.logger.error(f"Error type: {type(e).__name__}")
            import traceback
            self.logger.error(f"Full traceback: {traceback.format_exc()}")
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
            time.sleep(1)  # Reduced from 3 to 1 second
            
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
                    time.sleep(1)
                    
            # Handle cookie banner
            accept_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Accept')]")
            for button in accept_buttons:
                if button.is_displayed():
                    button.click()
                    time.sleep(1)
                    
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
                time.sleep(3)
            else:
                self.logger.warning("Could not find reels section, proceeding with current page")
        except Exception as e:
            self.logger.warning(f"Could not navigate to reels section: {e}")
            
    def extract_reel_id(self, url: str) -> Optional[str]:
        """Extract reel ID from Instagram URL."""
        try:
            # Match patterns like /reel/ABC123/ or /p/ABC123/
            match = re.search(r'/(?:reel|p)/([A-Za-z0-9_-]+)/', url)
            if match:
                return match.group(1)
            return None
        except Exception:
            return None
            
    def check_reel_date(self, reel_element) -> bool:
        """Check if a reel was posted within the configured days limit."""
        try:
            # Look for time elements or date indicators near the reel
            date_selectors = [
                ".//time",
                ".//span[contains(@class, 'time')]",
                ".//a[contains(@href, '/p/')]/..//time",
                ".//a[contains(@href, '/reel/')]/..//time",
                ".//*[contains(text(), 'd') or contains(text(), 'day') or contains(text(), 'week') or contains(text(), 'hour')]"
            ]
            
            cutoff_date = datetime.now() - timedelta(days=self.config.days_limit)
            
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
            days_limit = self.config.days_limit
            
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
    def scroll_and_collect_links(self, target_limit: int = 0) -> List[str]:
        """Scroll through the page and collect reel links with optimized speed.
        
        Args:
            target_limit: Stop collecting when this many links are found (0 = no limit)
        """
        links = set()
        scroll_count = 0
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        consecutive_no_new_links = 0
        last_link_count = 0
        
        self.logger.info("Starting to scroll and collect reel links...")
        if target_limit > 0:
            self.logger.info(f"Will stop after collecting {target_limit} links")
        
        # Preload the page to ensure the DOM is ready
        time.sleep(1)
        
        # First batch collection (without scrolling)
        current_links = self.collect_visible_reel_links()
        links.update(current_links)
        self.logger.info(f"Initial collection: Found {len(current_links)} links")
        
        # Start batch saving process if enabled
        if hasattr(self.config, 'batch_size') and self.config.batch_size > 0:
            batch_size = self.config.batch_size
            self.logger.info(f"Batch processing enabled: Will save every {batch_size} new links")
        else:
            batch_size = 0
            
        # Check if we've already reached the target
        if target_limit > 0 and len(links) >= target_limit:
            self.logger.info(f"Already collected enough links ({len(links)}/{target_limit}) without scrolling")
            return list(links)[:target_limit]
            
        while scroll_count < self.config.max_scrolls:
            # Determine scroll speed based on performance
            current_delay = self.config.scroll_delay
            if consecutive_no_new_links > 0:
                # If we're not finding new links, slow down a bit
                current_delay = min(2.0, current_delay * 1.5)
            
            # Scroll down with dynamic scrolling
            for i in range(1, 4):  # Do multiple small scrolls instead of one big one
                scroll_height = last_height / 4 * i
                self.driver.execute_script(f"window.scrollTo(0, {scroll_height});")
                time.sleep(current_delay / 3)  # Distribute the delay across small scrolls
            
            # Final scroll to bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(current_delay / 3)
            
            # Collect links
            current_links = self.collect_visible_reel_links()
            old_count = len(links)
            links.update(current_links)
            new_count = len(links)
            new_links_found = new_count - old_count
            
            self.logger.info(f"Scroll {scroll_count + 1}: Found {new_links_found} new links, "
                          f"total unique: {new_count}")
            
            # Check if we've reached the target number of links
            if target_limit > 0 and new_count >= target_limit:
                self.logger.info(f"Reached target of {target_limit} links, stopping scroll")
                break
            
            # Check if we should save the batch
            if batch_size > 0 and new_count >= last_link_count + batch_size:
                self.logger.info(f"Reached batch size of {batch_size} new links, saving intermediate results...")
                self.save_to_google_sheets(list(links))
                last_link_count = new_count
            
            # Check if new content loaded
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            
            # Track if we're finding new content
            if new_links_found == 0:
                consecutive_no_new_links += 1
            else:
                consecutive_no_new_links = 0
                
            # Stop conditions:
            # 1. No new height (end of page)
            # 2. No new links found for 3 consecutive scrolls
            if new_height == last_height or consecutive_no_new_links >= 3:
                if new_height == last_height:
                    self.logger.info("No new content loaded, stopping scroll")
                else:
                    self.logger.info("No new links found in 3 consecutive scrolls, stopping")
                break
                
            last_height = new_height
            scroll_count += 1
            
        self.logger.info(f"Scrolling complete. Collected {len(links)} unique reel links")
        
        # Return all links, or just up to the target limit if specified
        if target_limit > 0 and len(links) > target_limit:
            return list(links)[:target_limit]
        return list(links)
        
    def collect_visible_reel_links(self) -> List[str]:
        """Collect reel links from currently visible elements with date filtering for last 30 days."""
        try:
            # First try JavaScript approach for speed
            links_js = """
            try {
                return Array.from(document.querySelectorAll('a[href*="/reel/"], a[href*="/p/"]'))
                    .map(a => ({
                        href: a.href,
                        element: a
                    }))
                    .filter(item => item.href && (item.href.includes('/reel/') || item.href.includes('/p/')));
            } catch(e) {
                console.log('Link collection failed:', e);
                return [];
            }
            """
            js_results = self.driver.execute_script(links_js)
            
            if js_results:
                # Use Selenium to check dates for each link
                recent_links = []
                seen = set()
                
                for item in js_results:
                    href = item.get('href') if isinstance(item, dict) else item
                    if href and href not in seen:
                        # Find the element again for date checking
                        try:
                            link_element = self.driver.find_element(By.XPATH, f"//a[@href='{href}']")
                            parent_element = link_element.find_element(By.XPATH, "./ancestor::article | ./ancestor::div[contains(@class, 'reel') or contains(@class, 'post')]")
                            
                            # Check if this reel is within 30 days
                            if self.check_reel_date(parent_element):
                                if not href.startswith('http'):
                                    href = f"https://instagram.com{href}"
                                recent_links.append(href)
                                seen.add(href)
                                self.logger.debug(f"Added recent reel: {href}")
                            else:
                                self.logger.debug(f"Skipped old reel: {href}")
                                
                        except Exception as elem_error:
                            # If we can't find the element or check date, include it
                            self.logger.debug(f"Could not check date for {href}, including anyway: {elem_error}")
                            if not href.startswith('http'):
                                href = f"https://instagram.com{href}"
                            recent_links.append(href)
                            seen.add(href)
                
                self.logger.info(f"Found {len(recent_links)} recent reels (within 30 days) out of {len(js_results)} total")
                return recent_links
            
        except Exception as e:
            self.logger.warning(f"Error with JavaScript date filtering approach: {e}")
            
        # Fallback to Selenium method with date checking
        self.logger.info("Using Selenium fallback method with date filtering")
        return self.collect_visible_reel_links_selenium()
    
    def collect_visible_reel_links_selenium(self) -> List[str]:
        """Fallback method using pure Selenium with date filtering."""
        recent_links = []
        seen = set()
        
        try:
            # Find all reel/post links
            selectors = [
                "a[href*='/reel/']",
                "a[href*='/p/']"
            ]
            
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        href = element.get_attribute('href')
                        if href and href not in seen and ('/reel/' in href or '/p/' in href):
                            # Find parent container for date checking
                            try:
                                parent_element = element.find_element(By.XPATH, "./ancestor::article | ./ancestor::div[contains(@class, 'reel') or contains(@class, 'post')]")
                                
                                # Check if this reel is within 30 days
                                if self.check_reel_date(parent_element):
                                    if not href.startswith('http'):
                                        href = f"https://instagram.com{href}"
                                    recent_links.append(href)
                                    seen.add(href)
                                    self.logger.debug(f"Added recent reel: {href}")
                                else:
                                    self.logger.debug(f"Skipped old reel: {href}")
                                    
                            except Exception:
                                # If we can't find parent or check date, include it
                                if not href.startswith('http'):
                                    href = f"https://instagram.com{href}"
                                recent_links.append(href)
                                seen.add(href)
                                
                except Exception as selector_error:
                    self.logger.debug(f"Error with selector {selector}: {selector_error}")
            
            self.logger.info(f"Selenium method found {len(recent_links)} recent reels")
            return recent_links
            
        except Exception as e:
            self.logger.error(f"Error in Selenium fallback method: {e}")
            return []        
    def save_to_google_sheets(self, links: List[str]):
        """Save collected links to Google Sheets."""
        if not self.sheet:
            self.logger.error("Google Sheets not initialized")
            return        
        self.logger.info(f"Checking {len(links)} links for duplicates...")
        
        # Fast batch duplicate filtering
        filtered_links, duplicate_count = self.filter_duplicate_reels(links)
        
        if duplicate_count > 0:
            self.logger.info(f"Found {duplicate_count} duplicate reels, processing {len(filtered_links)} new reels")
        
        # Process only new links
        new_links = []
        for link in filtered_links:
            reel_id = self.extract_reel_id(link)            # Format date as dd-JAN-yy (e.g., 21-JUN-25)
            date_formatted = datetime.now().strftime('%d-%b-%y').upper()
            # Extract username from URL
            username = self.extract_username_from_url(link)
            new_links.append([date_formatted, username, link, reel_id or 'N/A', 'Pending', '', ''])
                
        if new_links:
            try:
                self.sheet.append_rows(new_links)
                self.logger.info(f"Successfully saved {len(new_links)} new links to Google Sheets")
                if duplicate_count > 0:
                    self.logger.info(f"Skipped {duplicate_count} duplicate reels (already in sheet)")
            except Exception as e:
                self.logger.error(f"Error saving to Google Sheets: {e}")
                # Save to local file as backup
                self.save_to_local_backup(new_links)
        else:
            if duplicate_count > 0:
                self.logger.info(f"No new links to save - all {duplicate_count} reels were duplicates")
            else:
                self.logger.info("No new links to save")
            
    def save_to_local_backup(self, data: List[List[str]]):
        """Save data to local JSON file as backup."""
        try:
            filename = f"reel_links_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            backup_data = []
            for row in data:                
                backup_data.append({
                    'date': row[0],
                    'username': row[1],
                    'url': row[2],
                    'reel_id': row[3],
                    'status': row[4],
                    'yt_posted_date': row[5] if len(row) > 5 else ''
                })
                
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Backup saved to {filename}")
            
        except Exception as e:
            self.logger.error(f"Error saving backup: {e}")
            
    def extract_username_from_url(self, url: str) -> str:
        """Extract Instagram username from URL."""
        try:
            # Extract username from URL pattern like https://www.instagram.com/username/
            if 'instagram.com/' in url:
                parts = url.split('instagram.com/')
                if len(parts) > 1:
                    username_part = parts[1].split('/')[0]                    # Remove any query parameters
                    username = username_part.split('?')[0]
                    return f"@{username}" if username else "Unknown"
            return "Unknown"
        except Exception:
            return "Unknown"
    
    def setup_status_dropdown(self):
        """Setup dropdown validation for Status column with Pending/Processing/Completed options.
        
        This method uses Google Sheets API v4 to create data validation rules for the Status column.
        The dropdown will be available in the Google Sheets interface for rows 2-1000.
        
        To test: After running the scraper, go to your Google Sheet and click on any cell 
        in the Status column. You should see a dropdown arrow with the three options.
        """
        try:
            # Use Google Sheets API v4 to set up data validation
            from google.oauth2.service_account import Credentials
            from googleapiclient.discovery import build
            
            # Setup credentials for Sheets API v4
            credentials = Credentials.from_service_account_file(
                self.config.credentials_file,
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
            
            # Build the service
            service = build('sheets', 'v4', credentials=credentials)
            
            # Get sheet properties to find the sheet ID
            spreadsheet = service.spreadsheets().get(spreadsheetId=self.config.google_sheets_id).execute()
            sheet_id = spreadsheet['sheets'][0]['properties']['sheetId']  # Use first sheet
            
            # Define the dropdown validation rule for the Status column (column E = index 4)
            validation_rule = {
                'setDataValidation': {
                    'range': {
                        'sheetId': sheet_id,
                        'startRowIndex': 1,  # Start from row 2 (after header)
                        'endRowIndex': 1000,  # Apply to first 1000 rows
                        'startColumnIndex': 4,  # Column E (Status)
                        'endColumnIndex': 5  # End at column F
                    },
                    'rule': {
                        'condition': {
                            'type': 'ONE_OF_LIST',
                            'values': [
                                {'userEnteredValue': 'Pending'},
                                {'userEnteredValue': 'Completed'}
                            ]
                        },
                        'showCustomUi': True,
                        'strict': True
                    }
                }
            }
            
            # Execute the batch update
            requests = [validation_rule]
            body = {
                'requests': requests
            }
            
            service.spreadsheets().batchUpdate(
                spreadsheetId=self.config.google_sheets_id,
                body=body
            ).execute()
            
            self.logger.info("Successfully set up dropdown validation for Status column with options: Pending, Processing, Completed")
            
        except Exception as e:
            self.logger.warning(f"Could not setup dropdown validation: {e}")
            # Fallback: just log the expected values
            self.logger.info("Status column should use dropdown values: Pending, Processing, Completed")
    
    def load_existing_reel_ids(self):
        """Load existing reel IDs from Google Sheets for fast duplicate checking."""
        if self.reel_id_cache_loaded or not self.sheet:
            return
            
        try:
            self.logger.info("Loading existing reel IDs for duplicate checking...")
            
            # Get only the Reel ID column (column D) to minimize data transfer
            reel_id_column = self.sheet.col_values(4)  # Column D (Reel ID)
            
            # Skip header row and add non-empty reel IDs to cache
            for reel_id in reel_id_column[1:]:  # Skip header
                if reel_id and reel_id != 'N/A':
                    self.existing_reel_ids.add(reel_id)
            
            self.reel_id_cache_loaded = True
            self.logger.info(f"Loaded {len(self.existing_reel_ids)} existing reel IDs for duplicate checking")
            
        except Exception as e:
            self.logger.warning(f"Could not load existing reel IDs: {e}")
            # Continue without cache - will still work but slower
            self.reel_id_cache_loaded = False

    def is_duplicate_reel(self, reel_id: str) -> bool:
        """Fast check if a reel ID already exists in the sheet."""
        if not reel_id or reel_id == 'N/A':
            return False
            
        # Ensure cache is loaded
        if not self.reel_id_cache_loaded:
            self.load_existing_reel_ids()
            
        return reel_id in self.existing_reel_ids

    def add_reel_to_cache(self, reel_id: str):
        """Add a new reel ID to the cache when it's successfully saved."""
        if reel_id and reel_id != 'N/A':
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
                if reel_id and reel_id != 'N/A':
                    self.existing_reel_ids.add(reel_id)
        
        return new_links, duplicate_count

    def refresh_reel_id_cache(self):
        """Refresh the reel ID cache from Google Sheets."""
        self.existing_reel_ids.clear()
        self.reel_id_cache_loaded = False
        self.load_existing_reel_ids()
        self.logger.info("Reel ID cache refreshed")

    def get_cache_stats(self) -> Dict[str, int]:
        """Get statistics about the reel ID cache."""
        return {
            'cached_reel_ids': len(self.existing_reel_ids),
            'cache_loaded': self.reel_id_cache_loaded
        }

    def run(self):
        """Main execution method."""
        all_links = []
        urls_to_scrape = []
        
        # Determine which URLs to scrape
        if self.config.instagram_urls and len(self.config.instagram_urls) > 0:
            urls_to_scrape = self.config.instagram_urls
            self.logger.info(f"Using {len(urls_to_scrape)} URLs from instagram_urls list")
        else:
            urls_to_scrape = [self.config.instagram_url]
            self.logger.info("Using single URL from instagram_url")
            
        try:
            self.logger.info("Starting Instagram Reel Scraper...")
            
            # Setup common resources
            self.setup_google_sheets()
            self.driver = self.setup_driver()
            
            # Track progress toward target
            target_reached = False
            total_collected = 0
            
            # Process each URL
            for idx, url in enumerate(urls_to_scrape):
                if target_reached:
                    break
                    
                self.logger.info(f"Processing URL {idx+1}/{len(urls_to_scrape)}: {url}")
                
                try:
                    # Navigate and scrape this URL
                    self.navigate_to_instagram(url)
                    self.navigate_to_reels()
                    
                    # Determine how many more links we need if we have a target
                    remaining_target = 0
                    if self.config.target_links > 0:
                        remaining_target = self.config.target_links - total_collected
                        if remaining_target <= 0:
                            target_reached = True
                            break
                        self.logger.info(f"Need {remaining_target} more links to reach target of {self.config.target_links}")
                      # Collect links from this URL
                    self.logger.info(f"Collecting reels URL: {url}")
                    url_links = self.scroll_and_collect_links(remaining_target)
                    
                    if url_links:
                        # Save the links from this URL
                        self.save_to_google_sheets(url_links)
                        total_collected += len(url_links)
                        all_links.extend(url_links)
                        
                        self.logger.info(f"URL {url} completed. Collected {len(url_links)} links.")
                        self.logger.info(f"Total links collected so far: {total_collected}")
                          # Check if we've reached our target
                        if self.config.target_links > 0 and total_collected >= self.config.target_links:
                            self.logger.info(f"TARGET REACHED: {self.config.target_links} links collected!")
                            target_reached = True
                            break
                    else:
                        self.logger.warning(f"No reel links found at URL: {url}")
                        
                except Exception as url_error:
                    self.logger.error(f"Error processing URL {url}: {url_error}")
                    # Continue with next URL despite error
                
            # Final summary
            self.logger.info(f"Scraping completed! Processed {len(urls_to_scrape)} URLs and collected {total_collected} links total.")
            
        except Exception as e:
            self.logger.error(f"Error during scraping: {e}")
            raise
        finally:
            if self.driver:
                self.driver.quit()
                self.logger.info("Browser closed")
                
        return all_links
                
def main():
    """Main function to run the scraper."""
    # Configuration - Update these values
    config = Config(
        instagram_url="https://www.instagram.com/your_target_account/",  # Replace with target Instagram URL
        instagram_urls=["https://www.instagram.com/your_target_account/"],  # List of URLs to scrape
        target_links=100,  # Target number of links to collect (0 = unlimited)
        days_limit=30,  # Only collect reels from last 30 days
        google_sheets_id="your_google_sheets_id_here",  # Replace with your Google Sheets ID
        credentials_file="credentials.json",  # Path to your Google Service Account credentials
        max_scrolls=15,  # Number of scrolls to perform
        scroll_delay=0.5,  # Delay between scrolls in seconds (reduced from 2.0)
        batch_size=25,  # Save to Google Sheets every 25 new links
        headless=False,  # Set to True to run without browser window
        fast_mode=True  # Enable fast mode with image blocking for better performance
    )
    
    scraper = InstagramReelScraper(config)
    collected_links = scraper.run()
    print(f"Total links collected: {len(collected_links)}")
    return collected_links

if __name__ == "__main__":
    main()
