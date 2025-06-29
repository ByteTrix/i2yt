# 🚀 i2yt: Instagram to YouTube/Google Drive Automation

**i2yt** is a powerful and highly customizable automation tool designed to streamline your content workflow. It scrapes Instagram Reels, intelligently organizes the data in Google Sheets, and can automatically upload the videos to Google Drive, preparing them for your YouTube channel or other content pipelines.

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

---

## ✨ Features

*   **Multi-Account Scraping**: Effortlessly scrape Reels from multiple Instagram accounts.
*   **Smart Data Management**: Automatically saves data to Google Sheets with duplicate checks and clean formatting.
*   **Google Drive Integration**: Seamlessly upload Reels to a specified Google Drive folder.
*   **Parallel Processing**: Leverages concurrent processing for faster scraping, description extraction, and uploads.
*   **Highly Customizable**: Fine-tune the entire workflow through a simple `config.py` file.
*   **Resilient & Robust**: Built-in error handling and retry mechanisms.
*   **Workflow Automation Ready**: Designed to be integrated with tools like n8n or other automation platforms.
*   **Headless Mode**: Run the scraper in the background for efficient server-based operation.
*   **Detailed Logging**: Keep track of the entire process with comprehensive logs.

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

### 3. Configure Google API Access

You'''ll need to set up a Google Service Account to allow the application to access your Google Sheet and Google Drive.

1.  Follow the official Google Cloud documentation to create a service account and download the `credentials.json` file.
    *   [Enable Google Sheets API](https://console.cloud.google.com/apis/library/sheets.googleapis.com)
    *   [Enable Google Drive API](https://console.cloud.google.com/apis/library/drive.googleapis.com)
2.  Place the `credentials.json` file in the root directory of the project.
3.  Share your Google Sheet and Google Drive folder with the service account'''s email address.

### 4. Create Your Configuration

Copy the template to create your own configuration file:

```bash
copy config_template.py config.py
```

Now, open `config.py` and customize it with your details:

*   `INSTAGRAM_URLS`: A list of Instagram accounts to scrape.
*   `GOOGLE_SHEETS_ID`: The ID of your Google Sheet (from its URL).
*   `UPLOAD_TO_GOOGLE_DRIVE`: Set to `True` to enable uploads.
*   `DRIVE_FOLDER_ID`: The ID of the Google Drive folder for uploads.

### 5. Run the Scraper

Execute the main script to start the process:

```bash
python run_scraper.py
```

---

## 🔧 Configuration

All settings are managed in the `config.py` file. Here are some of the key options:

| Setting | Description |
|---|---|
| `INSTAGRAM_URLS` | List of Instagram profile URLs to scrape. |
| `GOOGLE_SHEETS_ID` | The ID of the target Google Sheet. |
| `TARGET_LINKS` | Number of Reels to scrape per account. |
| `DAYS_LIMIT` | Only scrape Reels from the last N days. |
| `HEADLESS` | Run the browser in headless mode (`True`/`False`). |
| `UPLOAD_TO_GOOGLE_DRIVE` | Enable or disable Google Drive uploads. |
| `DRIVE_FOLDER_ID` | The destination folder ID in Google Drive. |
| `ENABLE_CONCURRENT_PROCESSING` | Use parallel processing for speed. |

---

## 📂 Project Structure

```
i2yt/
├── .gitignore
├── config.py                 # Your configuration (created from template)
├── config_template.py        # Configuration template
├── description_extractor.py  # Logic for extracting Reel descriptions
├── google_drive_manager.py   # Handles Google Drive uploads
├── google_sheets_manager.py  # Manages Google Sheets interactions
├── instagram_scraper.py      # Core Instagram scraping logic
├── main_processor.py         # Orchestrates the entire workflow
├── parallel_processor.py     # Handles concurrent processing
├── run_scraper.py            # Main entry point to run the application
├── requirements.txt          # Python dependencies
├── docs/                     # Documentation files
└── tests/                    # Test suite
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
