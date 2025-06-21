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
from datetime import datetime
from typing import List, Dict, Optional
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

# Configuration
@dataclass
class Config:
    instagram_url: str
    google_sheets_id: str
    instagram_urls: List[str] = None  # List of URLs to scrape
    target_links: int = 0  # Target number of links to collect (0 = unlimited)
    credentials_file: str = "credentials.json"
    max_scrolls: int = 10
    scroll_delay: float = 0.5  # Reduced from 2.0 to 0.5 seconds
    batch_size: int = 25  # Number of links to collect before saving to sheets
    implicit_wait: int = 5  # Reduced from 10 to 5 seconds
    page_load_timeout: int = 20  # Reduced from 30 to 20 seconds
    headless: bool = False
    fast_mode: bool = True  # New parameter for fast mode
    
class InstagramReelScraper:
    def __init__(self, config: Config):
        self.config = config
        self.driver = None
        self.sheet = None
        self.collected_links = set()
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[                
                logging.FileHandler('instagram_scraper.log'),                
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    def setup_driver(self) -> webdriver.Chrome:
        """Setup Chrome WebDriver with a dedicated profile directory that preserves cookies."""
        self.logger.info("Starting Chrome with a dedicated profile for Instagram scraping...")
        
        try:
            chrome_options = Options()
            
            # Create a dedicated profile directory in the project folder
            profile_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "instagram_profile")
            os.makedirs(profile_dir, exist_ok=True)
            
            self.logger.info(f"Using profile directory: {profile_dir}")
            
            # Set up Chrome options for faster loading
            chrome_options.add_argument(f"--user-data-dir={profile_dir}")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            
            # Performance optimizations
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-notifications")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-infobars")
            
            # Disable images for faster loading if fast_mode is enabled
            if hasattr(self.config, 'fast_mode') and self.config.fast_mode:
                self.logger.info("Fast mode enabled: disabling images and CSS animations")
                prefs = {
                    "profile.managed_default_content_settings.images": 2,  # 2 = block images
                    "profile.default_content_setting_values.notifications": 2,  # 2 = block notifications
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
                driver.execute_script("""
                var style = document.createElement('style');
                style.type = 'text/css';
                style.innerHTML = '* { animation-duration: 0.001s !important; transition-duration: 0.001s !important; }';
                document.getElementsByTagName('head')[0].appendChild(style);
                """)
            
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
                if not headers or headers != ['Timestamp', 'Reel URL', 'Reel ID', 'Status']:
                    self.sheet.clear()
                    self.sheet.append_row(['Timestamp', 'Reel URL', 'Reel ID', 'Status'])
                    self.logger.info("Headers added to Google Sheet")
                else:
                    self.logger.info("Headers already exist and are correct")
            except Exception as header_error:
                self.logger.warning(f"Could not set headers, trying to add them: {header_error}")
                try:
                    self.sheet.append_row(['Timestamp', 'Reel URL', 'Reel ID', 'Status'])
                    self.logger.info("Headers added successfully")
                except Exception as add_error:
                    self.logger.error(f"Failed to add headers: {add_error}")
                
            self.logger.info("Google Sheets connection established successfully")
            
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
        """Collect reel links from currently visible elements with optimized performance."""
        try:
            # Faster approach: Use JavaScript to extract all links in one go
            links_js = """
            return Array.from(document.querySelectorAll('a[href*="/reel/"], a[href*="/p/"]'))
                .map(a => a.href)
                .filter(href => href.includes('/reel/') || href.includes('/p/'));
            """
            js_links = self.driver.execute_script(links_js)
            
            # Process the links
            unique_links = []
            seen = set()
            
            for href in js_links:
                if href and href not in seen:
                    # Ensure it's a full URL
                    if not href.startswith('http'):
                        href = f"https://instagram.com{href}"
                    unique_links.append(href)
                    seen.add(href)
                    
            return unique_links
            
        except Exception as e:
            self.logger.warning(f"Error collecting links with JavaScript: {e}")
            self.logger.info("Falling back to Selenium method")
            
            # Fallback to the original method if JavaScript approach fails
            links = []
            selectors = [
                "a[href*='/reel/']",
                "a[href*='/p/']",
                "[href*='instagram.com/reel/']",
                "[href*='instagram.com/p/']"
            ]
            
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        href = element.get_attribute('href')
                        if href and ('/reel/' in href or '/p/' in href):
                            if not href.startswith('http'):
                                href = f"https://instagram.com{href}"
                            links.append(href)
                except Exception as selector_error:
                    self.logger.debug(f"Error with selector {selector}: {selector_error}")
                    
            # Remove duplicates while preserving order
            unique_links = []
            seen = set()
            for link in links:
                if link not in seen:
                    unique_links.append(link)
                    seen.add(link)
                    
            return unique_links
        
    def save_to_google_sheets(self, links: List[str]):
        """Save collected links to Google Sheets."""
        if not self.sheet:
            self.logger.error("Google Sheets not initialized")
            return
            
        self.logger.info(f"Saving {len(links)} links to Google Sheets...")
        
        # Get existing URLs to avoid duplicates
        try:
            existing_data = self.sheet.get_all_records()
            existing_urls = {row.get('Reel URL', '') for row in existing_data}
        except:
            existing_urls = set()
            
        new_links = []
        for link in links:
            if link not in existing_urls:                
                reel_id = self.extract_reel_id(link)
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                new_links.append([timestamp, link, reel_id or 'N/A', 'Pending'])
                
        if new_links:
            try:
                self.sheet.append_rows(new_links)
                self.logger.info(f"Successfully saved {len(new_links)} new links to Google Sheets")
            except Exception as e:
                self.logger.error(f"Error saving to Google Sheets: {e}")
                # Save to local file as backup
                self.save_to_local_backup(new_links)
        else:
            self.logger.info("No new links to save (all were duplicates)")
            
    def save_to_local_backup(self, data: List[List[str]]):
        """Save data to local JSON file as backup."""
        try:
            filename = f"reel_links_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            backup_data = []
            for row in data:                backup_data.append({
                    'timestamp': row[0],
                    'url': row[1],
                    'reel_id': row[2],
                    'status': row[3]
                })
                
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Backup saved to {filename}")
            
        except Exception as e:
            self.logger.error(f"Error saving backup: {e}")
            
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
                            self.logger.info(f"🎯 Target of {self.config.target_links} links reached!")
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
