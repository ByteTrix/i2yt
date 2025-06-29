"""
===============================================================================
                INSTAGRAM REELS SCRAPER - CONFIGURATION TEMPLATE
===============================================================================

🎯 Professional Instagram Reels Scraping & Processing Workflow Template
📋 Copy this file to 'config.py' and customize with your specific values

⚡ QUICK START CHECKLIST:
1. Copy this file to 'config.py'
2. Add your Instagram URLs to INSTAGRAM_URLS
3. Set your Google Sheets ID in GOOGLE_SHEETS_ID
4. Configure Google Drive folder ID (if using uploads)
5. Run the scraper!

📊 WORKFLOW FEATURES:
• Smart username/reel ID extraction from all Instagram URL formats
• Single-line description formatting for clean data presentation
• Colored status tags in Google Sheets for visual workflow tracking
• Selective processing (only handles 'pending' status items)
• Standardized DD-MMM-YY date format for international compatibility
• Clean data policy (Google Drive file IDs not stored in sheets)
• Enhanced duplicate detection with efficient batch operations

Version: 2.0.0 | Template Updated: June 2025
===============================================================================
"""

# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                        🎯 PRIMARY CONFIGURATION                          ║
# ╚═══════════════════════════════════════════════════════════════════════════╝
# → These are the main settings you'll need to customize

# ┌─────────────────────────────────────────────────────────────────────────┐
# │ 📱 Instagram Data Sources                                               │
# └─────────────────────────────────────────────────────────────────────────┘
# Replace with your target Instagram accounts
INSTAGRAM_URLS = [
    "https://www.instagram.com/your_account_1/",
    "https://www.instagram.com/your_account_2/",
    "https://www.instagram.com/your_account_3/"
    # 💡 Add more URLs as needed - no limit!
]

# ┌─────────────────────────────────────────────────────────────────────────┐
# │ 📊 Google Services Integration                                          │
# └─────────────────────────────────────────────────────────────────────────┘
GOOGLE_SHEETS_ID = "your_google_sheets_id_here"    # 📋 From your Google Sheets URL
CREDENTIALS_FILE = "credentials.json"              # 🔑 Service account credentials

# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                        ⚙️  SCRAPING PARAMETERS                           ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

# ┌─────────────────────────────────────────────────────────────────────────┐
# │ 🎯 Collection Settings                                                  │
# └─────────────────────────────────────────────────────────────────────────┘
TARGET_LINKS = 50                    # Number of reels per URL (0 = unlimited)
DAYS_LIMIT = 30                      # Only collect reels from last N days
MAX_SCROLLS = 15                     # Maximum page scrolls per Instagram URL
BATCH_SIZE = 25                      # Save to Google Sheets every N links

# ┌─────────────────────────────────────────────────────────────────────────┐
# │ ⚡ Performance & Timing                                                 │
# └─────────────────────────────────────────────────────────────────────────┘
SCROLL_DELAY = 0.5                   # Delay between scrolls (lower = faster)
IMPLICIT_WAIT = 5                    # Browser element wait time (seconds)
PAGE_LOAD_TIMEOUT = 20               # Maximum page load time (seconds)
HEADLESS = False                     # False = visible browser, True = hidden
FAST_MODE = True                     # Enable performance optimizations

# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                     📊 GOOGLE SHEETS STRUCTURE                           ║
# ╚═══════════════════════════════════════════════════════════════════════════╝
"""
🏗️  AUTOMATIC COLUMN LAYOUT:
┌─────────────────────────────────────────────────────────────────────────┐
│ A │ B        │ C           │ D       │ E           │ F         │ G  │ H  │
│   │          │             │         │             │           │    │    │
│📅 │ @username │ Insta URL   │ Reel ID │ Description │ Status    │YT  │YT  │
│   │          │             │         │             │           │Date│ID  │
└─────────────────────────────────────────────────────────────────────────┘

🎨 STATUS COLOR CODING (Applied Automatically):
• 🟠 pending    → Orange background (awaiting processing)
• 🔵 processing → Blue background (currently being processed)
• 🟢 completed  → Green background (successfully completed)
• 🔴 failed     → Red background (processing failed)

📅 DATE FORMAT: DD-MMM-YY (e.g., 28-JUN-25)
👤 USERNAME FORMAT: @username (e.g., @composedmindset)
📝 DESCRIPTION: Single-line format (no line breaks)
"""

# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                      🔄 PROCESSING WORKFLOW                              ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

# ┌─────────────────────────────────────────────────────────────────────────┐
# │ 📝 Content Processing                                                   │
# └─────────────────────────────────────────────────────────────────────────┘
EXTRACT_DESCRIPTIONS = True          # Extract and format reel descriptions
                                     # ⚠️ Requires: cookies.txt for authentication

# ┌─────────────────────────────────────────────────────────────────────────┐
# │ ☁️  Google Drive Integration                                            │
# └─────────────────────────────────────────────────────────────────────────┘
UPLOAD_TO_GOOGLE_DRIVE = False       # 🔄 Set to True to enable video uploads
DRIVE_FOLDER_ID = ""                 # 📁 Google Drive folder ID (empty = root)
DRIVE_CREDENTIALS_FILE = "credentials.json"  # 🔑 Service account credentials
DELETE_LOCAL_AFTER_UPLOAD = True     # 🗑️  Clean up local files post-upload

# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                       🔧 ADVANCED CONFIGURATION                          ║
# ╚═══════════════════════════════════════════════════════════════════════════╝
# → These settings usually work well as-is, but can be fine-tuned

# ┌─────────────────────────────────────────────────────────────────────────┐
# │ 🌐 Browser Configuration                                                │
# └─────────────────────────────────────────────────────────────────────────┘
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
BROWSER_DEBUG_PORT = 9222            # Chrome debug port for troubleshooting

# ┌─────────────────────────────────────────────────────────────────────────┐
# │ 🚀 Performance Optimization                                             │
# └─────────────────────────────────────────────────────────────────────────┘
ENABLE_CONCURRENT_PROCESSING = True  # Enable parallel processing where possible
USE_AGGRESSIVE_CACHING = True        # Cache results for faster subsequent runs
SKIP_DUPLICATE_CHECKS = False        # ⚠️ Set True only if certain no duplicates

# Advanced Parallel Processing Settings
MAX_SCRAPING_WORKERS = 4             # Concurrent threads for link processing
MAX_DOWNLOAD_WORKERS = 3             # Concurrent download threads  
MAX_UPLOAD_WORKERS = 2               # Concurrent upload threads (be conservative)
MAX_DESCRIPTION_WORKERS = 5          # Concurrent description extraction threads
BATCH_PROCESSING_SIZE = 20           # Items per batch for parallel operations
WORKER_TIMEOUT = 60                  # Timeout per worker task (seconds)

# ┌─────────────────────────────────────────────────────────────────────────┐
# │ 📥 Download Configuration                                               │
# └─────────────────────────────────────────────────────────────────────────┘
DOWNLOAD_DIRECTORY = "downloaded_reels"  # Local storage directory
MAX_DOWNLOAD_WORKERS = 3             # Concurrent download threads
DOWNLOAD_TIMEOUT = 30                # Download timeout per file (seconds)
RETRY_FAILED_DOWNLOADS = 2           # Number of retry attempts for failures

# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                    🏷️  WORKFLOW STATUS DEFINITIONS                       ║
# ╚═══════════════════════════════════════════════════════════════════════════╝
# ⚠️  DO NOT MODIFY - These constants are used throughout the application

STATUS_PENDING = "pending"           # 🟡 Awaiting processing
STATUS_PROCESSING = "processing"     # 🔵 Currently being processed  
STATUS_COMPLETED = "completed"       # 🟢 Successfully completed
STATUS_FAILED = "failed"             # 🔴 Processing failed

# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                           📚 SETUP GUIDE                                 ║
# ╚═══════════════════════════════════════════════════════════════════════════╝
"""
🚀 GETTING STARTED:

1️⃣  COPY CONFIGURATION:
   • Copy this file to 'config.py'
   • Update INSTAGRAM_URLS with your target accounts
   • Set GOOGLE_SHEETS_ID from your Google Sheets URL

2️⃣  GOOGLE SHEETS SETUP:
   • Create a new Google Sheet
   • Get the Sheet ID from the URL
   • Set up Google Service Account credentials
   • Save credentials as 'credentials.json'

3️⃣  GOOGLE DRIVE SETUP (Optional):
   • Set UPLOAD_TO_GOOGLE_DRIVE = True
   • Create a folder in Google Drive
   • Set DRIVE_FOLDER_ID to the folder ID

4️⃣  INSTAGRAM AUTHENTICATION:
   • Export your Instagram cookies to 'cookies.txt'
   • Use browser extension or manual export
   • Required for description extraction

5️⃣  RUN THE SCRAPER:
   • Execute: python run_scraper.py
   • Monitor progress in terminal and Google Sheets
   • Check logs in 'instagram_scraper.log'

📖 For detailed setup instructions, see docs/quick_start.md
🔧 For troubleshooting, see docs/troubleshooting.md
"""