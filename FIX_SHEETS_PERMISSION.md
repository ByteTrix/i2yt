# 🔧 FIX: Google Sheets Permission Error

## ❌ Problem Identified
Your Google Sheet is not shared with the service account email: `infdjksahssfds.iam.gserviceaccount.com`

## ✅ Solution (2 minutes to fix)

### Step 1: Open Your Google Sheet
1. Go to: https://docs.google.com/spreadsheets/d/jh1dsjkah2ujs
2. This will open your Google Sheet

### Step 2: Share the Sheet
1. Click the **"Share"** button (top-right corner)
2. In the "Add people and groups" field, enter this email:
   ```
   kfdsajknjdksafd.iam.gserviceaccount.com
   ```
3. Set permission to **"Editor"** (not just Viewer)
4. Click **"Send"**

### Step 3: Test the Fix
Run this command to test:
```bash
python test_sheets.py
```

You should now see: ✅ All Google Sheets tests passed!

## 🎯 Quick Alternative: Create New Sheet

If you prefer to create a new sheet:

1. **Create New Google Sheet**: https://sheets.google.com
2. **Share it** with: `jkdshafjkdhsjkahfjdsa.iam.gserviceaccount.com` (Editor)
3. **Copy the Sheet ID** from the URL (the long string between `/d/` and `/edit`)
4. **Update config.py** with the new Sheet ID

## 🚀 After Fixing

Once the sheet is shared properly, run:
```bash
python run_scraper.py
```

The scraper will now work perfectly and start collecting Instagram reel links!

---
**The issue is simply that Google doesn't know your automation script is allowed to access the sheet. Sharing it with the service account email fixes this immediately.**
