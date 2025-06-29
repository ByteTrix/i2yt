#!/usr/bin/env python3
"""
Description Extractor Module
Handles extraction of video descriptions using yt-dlp
"""

import os
import logging
import subprocess
import json
from typing import Dict, Optional, List
from datetime import datetime
import tempfile
import config

# Setup logging - use the parent logger configuration
logger = logging.getLogger(__name__)

class DescriptionExtractor:
    """Handles extraction of descriptions from Instagram reels using yt-dlp"""
    
    def __init__(self):
        self.logger = logger
        self.ensure_ytdlp_installed()
    
    def ensure_ytdlp_installed(self):
        """Ensure yt-dlp is installed"""
        try:
            subprocess.run(['yt-dlp', '--version'], capture_output=True, check=True)
            self.logger.info("yt-dlp is available")
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.logger.info("Installing yt-dlp...")
            subprocess.run(['pip', 'install', 'yt-dlp'], check=True)
    
    def extract_description(self, url: str) -> Optional[str]:
        """
        Extract description from a single Instagram reel URL
        
        Args:
            url: Instagram reel URL
            
        Returns:
            Description text or None if extraction fails
        """
        try:
            self.logger.info(f"Extracting description from: {url}")
            
            # Use yt-dlp to get description only with browser cookies
            cmd = [
                'yt-dlp',
                '--get-description',
                '--no-warnings'
            ]
            
            # Use cookies.txt for authentication if it exists
            cookies_file = os.path.join(os.path.dirname(__file__), 'cookies.txt')
            if os.path.exists(cookies_file):
                cmd.extend(['--cookies', cookies_file])
                self.logger.debug(f"Using cookies from {cookies_file} for authentication")
            else:
                self.logger.warning("cookies.txt not found, authentication may fail")
            
            cmd.append(url)
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                description = result.stdout.strip()
                # Convert multi-line description to single line by replacing newlines with spaces
                description_single_line = ' '.join(description.split())
                self.logger.info(f"Successfully extracted description: {description_single_line[:100]}...")
                return description_single_line
            else:
                self.logger.error(f"Failed to extract description: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            self.logger.error(f"Timeout while extracting description from: {url}")
            return None
        except Exception as e:
            self.logger.error(f"Error extracting description from {url}: {str(e)}")
            return None
    
    def extract_descriptions_batch(self, urls: List[str]) -> Dict[str, Optional[str]]:
        """
        Extract descriptions from multiple URLs
        
        Args:
            urls: List of Instagram reel URLs
            
        Returns:
            Dictionary mapping URLs to their descriptions
        """
        results = {}
        
        for url in urls:
            description = self.extract_description(url)
            results[url] = description
            
        return results
    
    def get_video_metadata(self, url: str) -> Optional[Dict]:
        """
        Get full metadata for a video including description, title, etc.
        
        Args:
            url: Instagram reel URL
            
        Returns:
            Dictionary with video metadata or None if extraction fails
        """
        try:
            self.logger.info(f"Getting metadata from: {url}")
            
            cmd = [
                'yt-dlp',
                '--dump-json',
                '--no-warnings'
            ]
            
            # Use cookies.txt for authentication if it exists
            cookies_file = os.path.join(os.path.dirname(__file__), 'cookies.txt')
            if os.path.exists(cookies_file):
                cmd.extend(['--cookies', cookies_file])
                self.logger.debug(f"Using cookies from {cookies_file} for metadata extraction")
            else:
                self.logger.warning("cookies.txt not found, metadata extraction may fail")
            
            cmd.append(url)
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                metadata = json.loads(result.stdout)
                self.logger.info(f"Successfully extracted metadata for: {metadata.get('title', 'Unknown')}")
                return metadata
            else:
                self.logger.error(f"Failed to extract metadata: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            self.logger.error(f"Timeout while extracting metadata from: {url}")
            return None
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON metadata: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"Error extracting metadata from {url}: {str(e)}")
            return None


if __name__ == "__main__":
    # Allow running this module standalone for testing
    logger.info("This module should be used via main_processor.py")
    logger.info("For description extraction, use: python main_processor.py descriptions")
