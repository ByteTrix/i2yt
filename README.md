# 🚀 i2yt: Instagram to YouTube/Google Drive Automation

**i2yt** is a powerful and highly customizable automation tool designed to streamline your content workflow. It scrapes Instagram Reels, intelligently organizes the data in Google Sheets, and can automatically upload the videos to Google Drive, preparing them for your YouTube channel or other content pipelines.

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

---

## ✨ Features

*   **Multi-Account Scraping**: Effortlessly scrape Reels from multiple Instagram accounts with parallel processing
*   **Smart Data Management**: Automatically saves data to Google Sheets with duplicate checks, status tracking, and clean formatting
*   **Google Drive Integration**: Seamlessly download and upload Reels to Google Drive with automated file management
*   **Professional Parallel Processing**: Leverages concurrent processing for maximum speed in scraping, description extraction, and uploads
*   **Multiple Execution Methods**: Run via Python CLI, PowerShell interactive menu, or Windows batch launcher
*   **Highly Customizable**: Fine-tune the entire workflow through a comprehensive `config.py` file with 50+ settings
*   **Resilient & Robust**: Built-in error handling, retry mechanisms, and intelligent rate limiting
*   **Workflow Automation Ready**: Designed for integration with n8n, Task Scheduler, or other automation platforms
*   **Advanced Browser Management**: Headless mode, session persistence, and optimized Chrome profile handling
*   **Comprehensive Logging**: Detailed logging system with multiple verbosity levels and structured output
*   **Modular Architecture**: Separate modules for scraping, description extraction, and Google Drive uploads
*   **Professional Status Tracking**: Color-coded status system in Google Sheets with workflow state management

---

## ⚙️ How It Works

The automation process follows these steps:

1.  **Scrape Reels**: The tool scrapes the latest Reels from the specified Instagram accounts.
2.  **Populate Google Sheets**: New Reel URLs, along with metadata like username and Reel ID, are added to a Google Sheet. Duplicates are automatically skipped.
3.  **Extract Descriptions**: (Optional) The description for each Reel is extracted and added to the sheet.
4.  **Upload to Google Drive**: (Optional) The videos are downloaded and uploaded to your Google Drive.
5.  **Update Status**: The status of each Reel is updated in the Google Sheet, giving you a clear overview of the workflow (`pending`, `processing`, `completed`, `failed`).

---

## 🏁 Getting Started

### Prerequisites

*   Python 3.8+
*   Google Chrome or Chromium
*   A Google Cloud project with the Google Sheets and Google Drive APIs enabled.
*   An Instagram account (for authentication to extract descriptions).

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/i2yt.git
cd i2yt
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Automated Setup (Recommended)

**For quick setup, use the automated setup script:**

```bash
python setup.py
```

This script will:
- Install all Python dependencies
- Create `config.py` from the template
- Check Chrome WebDriver availability
- Display next steps with clear instructions

### 4. Configure Google API Access (Manual Setup)

If you prefer manual setup or need to understand each step:

You'''ll need to set up a Google Service Account to allow the application to access your Google Sheet and Google Drive.

1.  Follow the official Google Cloud documentation to create a service account and download the `credentials.json` file.
    *   [Enable Google Sheets API](https://console.cloud.google.com/apis/library/sheets.googleapis.com)
    *   [Enable Google Drive API](https://console.cloud.google.com/apis/library/drive.googleapis.com)
2.  Place the `credentials.json` file in the root directory of the project.
3.  Share your Google Sheet with the service account email address (Editor permissions).

**⚠️ Google Drive Important Note**: Service accounts cannot upload to their own Google Drive due to storage quota limitations. For Google Drive uploads, you need to either:
- Use a Google Workspace Shared Drive (add service account as Content Manager)
- Share a personal folder with the service account (Editor permissions)
- See [detailed setup guide](docs/google_sheets_setup.md#phase-5-google-drive-setup-optional) for complete instructions

### 5. Create Your Configuration

Copy the template to create your own configuration file:

```bash
copy config_template.py config.py
```

Now, open `config.py` and customize it with your details:

*   `INSTAGRAM_URLS`: A list of Instagram accounts to scrape.
*   `GOOGLE_SHEETS_ID`: The ID of your Google Sheet (from its URL).
*   `UPLOAD_TO_GOOGLE_DRIVE`: Set to `True` to enable uploads.
*   `DRIVE_FOLDER_ID`: The ID of the Google Drive folder for uploads.

### 6. Run the Scraper

You can run the scraper in multiple ways:

#### Option A: Direct Python Execution
```bash
python run_scraper.py
```

#### Option B: PowerShell Script
```powershell
.\run_scraper.ps1
```

#### Option C: Windows Batch Launcher (Recommended for Windows)

For Windows users, a convenient batch file launcher is provided:

**⚠️ IMPORTANT: You must update the path in the batch file before first use!**

1. Open `Launch_Instagram_Scraper.bat` in a text editor
2. Find this line:
   ```batch
   start wt -p "PowerShell" --title "Instagram Reel Scraper" pwsh -NoExit -ExecutionPolicy Bypass -File "d:\Kodo\i2yt\run_scraper.ps1"
   ```
3. Replace `"d:\Kodo\i2yt\run_scraper.ps1"` with the full path to your project directory
   
   **Example:** If your project is in `C:\Users\YourName\Documents\i2yt\`, change it to:
   ```batch
   start wt -p "PowerShell" --title "Instagram Reel Scraper" pwsh -NoExit -ExecutionPolicy Bypass -File "C:\Users\YourName\Documents\i2yt\run_scraper.ps1"
   ```

4. Save the file and double-click to run

**Features of the Batch Launcher:**
- Opens a new Windows Terminal with PowerShell
- Sets the correct working directory automatically
- Runs with bypass execution policy
- Can be launched from anywhere (desktop, taskbar, etc.)
- Keeps the terminal open so you can see the results
- Provides an interactive menu for different operations

**📖 For detailed information on all execution methods, see [Running Guide](docs/running_guide.md)**

---

## 🔧 Configuration

All settings are managed in the `config.py` file. Here are some of the key options:

### Essential Configuration

| Setting | Description | Example |
|---|---|---|
| `INSTAGRAM_URLS` | List of Instagram profile URLs to scrape | `["https://www.instagram.com/account/"]` |
| `GOOGLE_SHEETS_ID` | The ID of the target Google Sheet | `"1abcd1234efgh5678..."` |
| `CREDENTIALS_FILE` | Path to Google API credentials | `"credentials.json"` |
| `TARGET_LINKS` | Number of Reels to scrape per account | `50` (0 = unlimited) |
| `DAYS_LIMIT` | Only scrape Reels from the last N days | `30` (0 = all time) |

### Performance & Processing

| Setting | Description | Default |
|---|---|---|
| `HEADLESS` | Run browser in headless mode | `False` |
| `FAST_MODE` | Enable performance optimizations | `True` |
| `ENABLE_CONCURRENT_PROCESSING` | Use parallel processing | `True` |
| `MAX_SCRAPING_WORKERS` | Concurrent threads for scraping | `4` |
| `BATCH_SIZE` | Save to sheets every N new reels | `25` |

### Content Processing

| Setting | Description | Default |
|---|---|---|
| `EXTRACT_DESCRIPTIONS` | Extract Reel descriptions | `True` |
| `UPLOAD_TO_GOOGLE_DRIVE` | Enable Google Drive uploads | `False` |
| `DRIVE_FOLDER_ID` | Google Drive destination folder | `""` |
| `DELETE_LOCAL_AFTER_UPLOAD` | Clean up local files | `True` |

For complete configuration options, see [Configuration Guide](docs/configuration.md).

---

## 📂 Project Structure

```
i2yt/
├── .gitignore
├── config.py                     # Your configuration (created from template)
├── config_template.py            # Configuration template with examples
├── Launch_Instagram_Scraper.bat  # Windows launcher (requires path customization)
├── login_to_instagram.bat        # Instagram login helper for Windows
├── run_scraper.ps1               # PowerShell script for Windows
├── credentials.json              # Google API credentials (you create this)
├── requirements.txt              # Python dependencies
├── description_extractor.py      # Extract descriptions using yt-dlp
├── google_drive_manager.py       # Handles Google Drive video uploads
├── google_sheets_manager.py      # Manages Google Sheets interactions
├── instagram_scraper.py          # Main Instagram scraping engine
├── instagram_scraper_clean.py    # Alternative clean scraper implementation
├── main_processor.py             # Orchestrates the complete workflow
├── parallel_processor.py         # Handles concurrent processing for performance
├── run_scraper.py                # Python entry point with CLI options
├── setup.py                      # Automated setup and configuration helper
├── n8n_workflow.json            # n8n workflow template for automation
├── docs/                         # Comprehensive documentation
│   ├── quick_start.md            # Get started in 10 minutes
│   ├── running_guide.md          # Complete guide to execution methods
│   ├── configuration.md          # Complete configuration guide
│   ├── google_sheets_setup.md    # Step-by-step Google API setup
│   ├── n8n_integration.md       # YouTube automation with n8n
│   ├── advanced_usage.md         # Power user features
│   ├── developer_guide.md        # For developers and contributors
│   ├── troubleshooting.md        # Common issues and solutions
│   └── technical_sheets_permissions.md  # Google Sheets permissions fix
├── tests/                        # Testing and validation tools
│   ├── test_google_api.py        # Test Google API connectivity
│   ├── test_sheets.py           # Test Google Sheets integration
│   └── demo.py                  # Quick demo and setup verification
├── downloaded_reels/             # Local video storage (auto-created)
├── instagram_profile/            # Chrome profile for Instagram login
└── __pycache__/                 # Python bytecode cache
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a pull request.

1.  Fork the repository.
2.  Create your feature branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes (`git commit -m '''Add some AmazingFeature'''`).
4.  Push to the branch (`git push origin feature/AmazingFeature`).
5.  Open a pull request.

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## ⚠️ Disclaimer

This tool is for educational purposes only. Please be responsible and respect Instagram'''s terms of service. The developers are not responsible for any misuse of this tool.
