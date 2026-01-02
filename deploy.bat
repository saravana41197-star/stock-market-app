@echo off
REM Step-by-step deployment to GitHub and Streamlit Cloud
REM Run this file from D:\Groww folder

echo.
echo ========================================
echo GITHUB DEPLOYMENT SETUP
echo ========================================
echo.

REM Replace YOUR_USERNAME with your actual GitHub username
set GITHUB_USERNAME=YOUR_USERNAME
set REPO_NAME=stock-market-app

echo Please enter your GitHub username (or just press Enter to use: %GITHUB_USERNAME%):
set /p GITHUB_USERNAME=

echo.
echo Repository will be: https://github.com/%GITHUB_USERNAME%/%REPO_NAME%
echo.

REM Initialize git
echo [Step 1] Initializing git repository...
git init

echo [Step 2] Adding all files...
git add .

echo [Step 3] Creating initial commit...
git commit -m "Initial commit: Stock market analysis app"

echo [Step 4] Adding remote repository...
git remote add origin https://github.com/%GITHUB_USERNAME%/%REPO_NAME%.git

echo [Step 5] Renaming branch to main...
git branch -M main

echo [Step 6] Pushing to GitHub...
git push -u origin main

echo.
echo ========================================
echo DEPLOYMENT COMPLETE!
echo ========================================
echo.
echo Next steps:
echo 1. Go to https://streamlit.io/cloud
echo 2. Sign in with GitHub
echo 3. Click "New app"
echo 4. Select:
echo    - Repository: %REPO_NAME%
echo    - Branch: main
echo    - Main file path: ui_app.py
echo 5. Click "Deploy"
echo.
echo Your app will be available at:
echo https://%REPO_NAME%-%GITHUB_USERNAME%.streamlit.app
echo.
pause
