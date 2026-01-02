# 🚀 Step-by-Step Deployment Guide to Streamlit Cloud

## **Step 1: Create a New GitHub Repository**

1. Go to https://github.com/new
2. **Repository name**: `stock-market-app` (or any name you like)
3. **Description**: "AI-powered Indian stock market analysis tool"
4. Select **Public** (required for free tier)
5. Check ✓ "Add a README file"
6. Click **Create repository**

---

## **Step 2: Prepare Your Files**

Your project needs these files in GitHub:

### Required Files:
- `ui_app.py` - Main Streamlit app
- `requirements.txt` - All dependencies
- `data_fetcher.py`
- `sentiment_analysis.py`
- `predictor.py`
- `visualizer.py`
- `utils.py`
- `.gitignore` - To ignore unnecessary files
- `README.md` - Documentation

### Files to SKIP (don't upload):
- `.venv/` folder (virtual environment)
- `models/` folder (too large)
- `__pycache__/`
- `.pyc` files

---

## **Step 3: Create .gitignore File**

Create a file named `.gitignore` in D:\Groww with:

```
.venv/
models/
__pycache__/
*.pyc
*.egg-info/
.DS_Store
.streamlit/
*.json
```

---

## **Step 4: Update requirements.txt**

Make sure your `requirements.txt` has (without version numbers for compatibility):

```
beautifulsoup4
requests
lxml
nltk
joblib
scikit-learn
matplotlib
pandas
yfinance
streamlit
numpy
```

---

## **Step 5: Push Code to GitHub**

### Option A: Using Git Commands (Windows)

```powershell
# Go to your project folder
cd D:\Groww

# Initialize git
git init

# Add all files
git add .

# Create first commit
git commit -m "Initial commit: Stock market analysis app"

# Add remote (replace YOUR_USERNAME and stock-market-app with your GitHub username and repo name)
git remote add origin https://github.com/YOUR_USERNAME/stock-market-app.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### Option B: Using GitHub Desktop (Easier)
1. Download GitHub Desktop: https://desktop.github.com
2. Clone your new repository
3. Copy all your files into the cloned folder
4. Commit and push from the app

---

## **Step 6: Deploy to Streamlit Cloud**

1. Go to https://streamlit.io/cloud
2. Click **"Sign in with GitHub"** and authorize
3. Click **"New app"** button
4. Select:
   - **Repository**: `stock-market-app`
   - **Branch**: `main`
   - **Main file path**: `ui_app.py`
5. Click **"Deploy"**

**Wait 2-3 minutes for deployment...**

---

## **Step 7: Access Your App**

✅ Your app will get a public URL like:
```
https://stock-market-app-YOUR_USERNAME.streamlit.app
```

**Access on iPhone:**
1. Open Safari on your iPhone
2. Paste the URL
3. Bookmark it for quick access!

---

## **Common Issues & Fixes**

### ❌ "ModuleNotFoundError: No module named..."
- **Fix**: Make sure all imports are in `requirements.txt`

### ❌ "App keeps crashing"
- **Fix**: Check the Logs in Streamlit Cloud dashboard
- Make sure `data_fetcher.py` has proper error handling

### ❌ "Yfinance not working"
- **Fix**: Add timeout handling for API calls

---

## **To Update Your App Later**

Just edit files in your GitHub repository or use:

```powershell
cd D:\Groww
git add .
git commit -m "Update: Add new features"
git push origin main
```

Streamlit Cloud will **auto-deploy** within seconds!

---

## **Monitoring & Logs**

After deployment, view logs at:
```
https://share.streamlit.io/YOUR_USERNAME/stock-market-app
```

---

## **Free Tier Limits**

- ✅ Unlimited apps
- ✅ 3 concurrent users
- ✅ 1GB storage
- ✅ Public repositories

Perfect for your use case! 🎉

