# IG to YouTube Automation

A comprehensive automation tool that scrapes Instagram reels from multiple accounts, stores them in Google Sheets with proper data validation, and integrates seamlessly with n8n workflows for YouTube uploading and other processing tasks.

## 🚀 Features

- **Multi-Account Support**: Scrape reels from multiple Instagram accounts simultaneously
- **Smart Date Filtering**: Filter reels by last N days with configurable date ranges
- **Google Sheets Integration**: Automatic data storage with dropdown validation and proper formatting
- **Fast Mode**: Headless browser operation for efficient scraping
- **Batch Processing**: Process multiple URLs with optimized performance
- **Robust Error Handling**: Comprehensive logging and error recovery
- **n8n Ready**: Pre-built workflow for seamless automation
- **Backup System**: Automatic local JSON backup for data safety
- **Chrome Profile Support**: Persistent login sessions and user preferences

## 📋 Requirements

- **Python 3.8+**
- **Chrome/Chromium browser** (latest version recommended)
- **Google Sheets API credentials**
- **Instagram account** (for authentication)
- **Internet connection** (for scraping and API calls)

## 🔧 Quick Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Google Sheets API
1. Follow the detailed guide in [`docs/google_sheets_setup.md`](docs/google_sheets_setup.md)
2. Download your `credentials.json` file
3. Place it in the project root directory

### 3. Setup Configuration
```bash
copy config_template.py config.py
```
Edit `config.py` with your specific settings:
- Instagram URLs to scrape
- Google Sheets ID
- Date filtering preferences
- Chrome profile settings

### 4. Initial Browser Setup
Run the login helper to set up your Chrome profile:
```bash
login_to_instagram.bat
```
Log into Instagram manually and close the browser when done.

### 5. Run the Scraper
```bash
python run_scraper.py
```

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [**Quick Start Guide**](docs/quick_start.md) | Fast setup and basic usage |
| [**Configuration Guide**](docs/configuration.md) | Detailed configuration options |
| [**Google Sheets Setup**](docs/google_sheets_setup.md) | Complete API setup guide |
| [**n8n Integration**](docs/n8n_integration.md) | Workflow automation setup |
| [**Troubleshooting**](docs/troubleshooting.md) | Common issues and solutions |
| [**Advanced Usage**](docs/advanced_usage.md) | Power user features |
| [**Developer Guide**](docs/developer_guide.md) | Code structure and contribution |

## 🏗️ Project Structure

```
instagram-youtube-automation/
├── 📄 instagram_reel_scraper.py     # Core scraper logic
├── 📄 run_scraper.py                # CLI interface
├── 📄 config_template.py            # Configuration template
├── 📄 config.py                     # User configuration (created)
├── 📁 docs/                         # Documentation
│   ├── quick_start.md
│   ├── configuration.md
│   ├── google_sheets_setup.md
│   ├── n8n_integration.md
│   ├── troubleshooting.md
│   ├── advanced_usage.md
│   └── developer_guide.md
├── 📁 tests/                        # Test files
│   ├── test_google_api.py
│   ├── test_sheets.py
│   └── demo.py
├── 📁 .github/workflows/            # CI/CD workflows
│   └── download.yml
├── 📄 login_to_instagram.bat        # Browser login helper
├── 📄 start_chrome_debug.bat        # Chrome debug helper
├── 📄 requirements.txt              # Python dependencies
├── 📄 setup.py                      # Package configuration
├── 📄 insta to yt.json             # n8n workflow template
└── 📄 README.md                     # This file
```

## 🎯 Usage Examples

### Basic Scraping
```bash
# Run with default settings
python run_scraper.py

# Run in fast mode (headless)
python run_scraper.py --fast

# Scrape last 7 days only
python run_scraper.py --days 7

# Limit to 10 reels per account
python run_scraper.py --limit 10
```

### Advanced Usage
```bash
# Custom configuration file
python run_scraper.py --config my_config.py

# Verbose logging
python run_scraper.py --verbose

# Skip Google Sheets upload
python run_scraper.py --no-upload

# Batch mode for multiple configurations
python run_scraper.py --batch configs/
```

## 📊 Google Sheets Integration

The tool automatically creates and manages a Google Sheet with the following structure:

| Column | Description | Type |
|--------|-------------|------|
| Date | Reel posting date | Date |
| Instagram Username | Account handle | Text |
| Link | Direct reel URL | URL |
| Reel ID | Unique identifier | Text |
| Status | Processing status | Dropdown |
| YT Posted Date | YouTube upload date | Date |

**Status Options**: `Not Processed`, `Downloaded`, `Uploaded to YT`, `Failed`, `Skipped`

## 🔄 n8n Workflow Integration

1. Import the provided `insta to yt.json` workflow
2. Configure your Google Sheets connection
3. Set up YouTube API credentials
4. Enable webhook triggers for automation

See [n8n Integration Guide](docs/n8n_integration.md) for detailed setup instructions.

## 🛠️ Configuration Options

Key configuration parameters in `config.py`:

```python
# Instagram accounts to scrape
INSTAGRAM_URLS = [
    "https://www.instagram.com/account1/",
    "https://www.instagram.com/account2/"
]

# Google Sheets settings
SPREADSHEET_ID = "your_sheet_id_here"
WORKSHEET_NAME = "Instagram Reels"

# Scraping preferences
DAYS_TO_SCRAPE = 30
MAX_REELS_PER_ACCOUNT = 50
USE_FAST_MODE = True

# Chrome settings
CHROME_PROFILE_PATH = "./instagram_profile"
HEADLESS_MODE = False
```

## 🔍 Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Chrome won't start | Check Chrome installation and profile path |
| Login fails | Clear profile and re-login manually |
| Sheets API errors | Verify credentials and permissions |
| No reels found | Check account privacy and date range |

See the [Troubleshooting Guide](docs/troubleshooting.md) for detailed solutions.

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

See [Developer Guide](docs/developer_guide.md) for development setup and coding standards.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Selenium WebDriver** for browser automation
- **Google Sheets API** for data storage
- **n8n** for workflow automation
- **yt-dlp** for video processing capabilities

## 📞 Support

- 📖 **Documentation**: Check the [docs/](docs/) directory
- 🐛 **Issues**: Create an issue on GitHub
- 💬 **Discussions**: Use GitHub Discussions for questions
- 📧 **Contact**: Create an issue for direct support

---

**Made with ❤️ for content creators and automation enthusiasts**