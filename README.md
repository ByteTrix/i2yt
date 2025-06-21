# IG to YT

Simple tool to collect links from IG and process them with n8n for YT uploads.

## What it does

- Collects reel links from multiple IG accounts
- Saves links to Google Sheets with metadata
- Integrates with n8n workflow for automated processing
- Supports target limits and batch processing

## Quick Setup

1. Install requirements:
   ```
   pip install -r requirements.txt
   ```

2. Set up Chrome profile:
   ```
   login_to_instagram.bat
   ```
   Log in to IG, then close the window to save your session.

3. Configure `config.py`:
   ```python
   # IG URLs to scrape
   INSTAGRAM_URLS = [
       "https://www.instagram.com/account1/",
       "https://www.instagram.com/account2/"
   ]

   # Collection settings
   TARGET_LINKS = 100  # 0 = unlimited
   
   # Google Sheets settings
   GOOGLE_SHEETS_ID = "your_sheet_id_here"
   CREDENTIALS_FILE = "credentials.json"
   ```

4. Run the tool:
   ```
   python run_scraper.py
   ```

## n8n Integration

The tool saves to Google Sheets with these columns:

| Column         | Description                    |
|----------------|--------------------------------|
| Date           | Collection date (dd-MMM-yy)    |
| Insta Username | Instagram account (@username)  |
| Link           | Full reel URL                  |
| Reel ID        | Unique ID from URL            |
| Status         | Processing status (dropdown)   |
| YT Posted Date | YouTube upload date           |

The `Status` column automatically has a dropdown with these options:
- "Pending" = Ready for processing
- "Processing" = Being handled by n8n  
- "Completed" = Successfully processed

**Note**: The dropdown validation is automatically set up when headers are created.

See `sample_n8n_workflow.json` for a ready-to-import workflow.

## Options

- Set `HEADLESS = True` to run without browser window
- Set `FAST_MODE = True` to speed up collection (blocks images)
- Set `BATCH_SIZE = 25` to save every 25 new links
- Set `MAX_SCROLLS = 15` to limit scrolling per account

## Workflow Integration

This tool is designed to work with n8n for end-to-end automation:

1. This tool collects links from IG
2. Google Sheets stores the links
3. n8n monitors for new links
4. n8n downloads content and uploads to YT
5. n8n updates status in Google Sheets

For detailed n8n setup, see `google_sheets_n8n_integration.md`

## Monitoring

- Check GitHub Actions tab for workflow runs
- Monitor Airtable for processed reels
- Review n8n execution logs for processing status
- YouTube Studio for uploaded videos

## Troubleshooting

### Common Issues

1. **Cookie Expiration**: Update Instagram cookies in GitHub secrets
2. **API Rate Limits**: Adjust check frequency if hitting limits
3. **Airtable Permissions**: Ensure token has read/write access
4. **N8N Webhook**: Verify webhook URL is accessible

### Debug Mode

Enable debug logging by setting workflow environment variables:
```yaml
env:
  DEBUG: true
```

## Customization

### Adjust Check Frequency
Modify the cron schedule in `check-instagram.yml`:
```yaml
schedule:
  - cron: '0 */3 * * *'  # Every 3 hours instead of 2
```

### Change Recent Reel Timeframe
Update the `is_recent_reel` function to check different time periods:
```python
def is_recent_reel(upload_date, hours=48):  # 48 hours instead of 24
```

### Add More Accounts
Extend the checker script to support additional backup accounts by adding more cookie files and account environment variables.

# Instagram Reel Scraper

This project automates scraping Instagram reel links and saves them to a Google Sheet.

## How It Works

The script uses Selenium to control Chrome, navigate to Instagram, scroll through the target page, and collect all reel links. It then saves these links to a specified Google Sheet, avoiding duplicates.

## Setup Instructions

### 1. Prerequisites
- Python 3.x installed.
- Google Chrome installed.
- A Google Cloud project with the Google Sheets API and Google Drive API enabled.
- A Google Service Account with credentials.

### 2. Initial Setup
1.  **Clone the repository or download the files.**
2.  **Install Dependencies**: Open a terminal in the project directory and run:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Configure Google Credentials**:
    - Place your Google Service Account `credentials.json` file in the root of the project directory.
    - Open your Google Sheet and share it with the `client_email` found in your `credentials.json` file, giving it "Editor" permissions.
4.  **Configure the Scraper**:
    - Rename `config_template.py` to `config.py`.
    - Open `config.py` and fill in the required values:
        - `instagram_url`: The full URL of the Instagram profile or page you want to scrape.
        - `google_sheets_id`: The ID of your Google Sheet (from its URL).

### 3. Log in to Instagram

The scraper uses a dedicated Chrome profile to store your Instagram login. To set this up:

1. **Run the Login Helper**: 
   - Run `login_to_instagram.bat` by double-clicking it.
   - A Chrome window will open.
   - Log in to your Instagram account.
   - After logging in, you can close the browser.

2. **Run the Scraper**:
   - Now you can run the scraper:
     ```bash
     python run_scraper.py
     ```
   - The script will use the saved login session, navigate to the target account, and collect reel links.

Your login session will be saved in the dedicated profile, so you only need to do this once. The scraper will use this profile automatically in future runs.

## Files

- `instagram_reel_scraper.py`: The main Python script for scraping.
- `run_scraper.py`: A simple launcher for the main script.
- `login_to_instagram.bat`: Helper script to log in to Instagram and save the session.
- `config.py`: Your configuration file (you create this from the template).
- `config_template.py`: A template for the configuration.
- `requirements.txt`: A list of required Python packages.
- `credentials.json`: Your Google Service Account credentials (you provide this).
- `.gitignore`: Prevents sensitive files from being committed to Git.
- `README.md`: This file.