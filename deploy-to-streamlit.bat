@echo off
REM ========================================
REM QUICK DEPLOYMENT TO STREAMLIT CLOUD
REM Run this from D:\Groww folder
REM ========================================

echo.
echo ========================================
echo STREAMLIT CLOUD DEPLOYMENT HELPER
echo ========================================
echo.
echo This script will help you deploy to Streamlit Cloud
echo.

REM Check if git is installed
git --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git is not installed!
    echo Please install Git from: https://git-scm.com/download/win
    echo Then restart this script.
    pause
    exit /b 1
)

echo [✓] Git is installed
echo.

REM Get GitHub username
set /p GITHUB_USERNAME="Enter your GitHub username: "

if "%GITHUB_USERNAME%"=="" (
    echo ERROR: GitHub username required!
    pause
    exit /b 1
)

set REPO_NAME=stock-market-app
set REPO_URL=https://github.com/%GITHUB_USERNAME%/%REPO_NAME%.git

echo.
echo ========================================
echo DEPLOYMENT INFORMATION
echo ========================================
echo GitHub Username: %GITHUB_USERNAME%
echo Repository: %REPO_NAME%
echo URL: %REPO_URL%
echo App URL (after deploy): https://%REPO_NAME%-%GITHUB_USERNAME%.streamlit.app
echo.

pause

echo.
echo [Step 1] Initializing git...
git init

echo [Step 2] Adding all files...
git add .

echo [Step 3] Creating initial commit...
git commit -m "Initial commit: Stock market analysis app for beginners"

echo [Step 4] Adding remote repository...
git remote add origin %REPO_URL%

echo [Step 5] Setting main branch...
git branch -M main

echo [Step 6] Pushing to GitHub...
echo Please wait, this may take a moment...
git push -u origin main

if errorlevel 1 (
    echo.
    echo ERROR: Failed to push to GitHub!
    echo Possible reasons:
    echo - Repository already exists (delete it and recreate)
    echo - Wrong GitHub username
    echo - Network issue
    echo.
    echo Please try again or visit https://github.com/new to create repository manually
    pause
    exit /b 1
)

echo.
echo ========================================
echo ✓ FILES UPLOADED TO GITHUB SUCCESSFULLY!
echo ========================================
echo.
echo Next steps:
echo.
echo 1. Go to https://streamlit.io/cloud
echo 2. Click "Sign in with GitHub"
echo 3. Click "New app"
echo 4. Fill in:
echo    - Repository: %REPO_NAME%
echo    - Branch: main
echo    - Main file path: ui_app.py
echo 5. Click "Deploy"
echo.
echo 6. Wait 2-3 minutes for deployment
echo.
echo 7. Your app will be available at:
echo    https://%REPO_NAME%-%GITHUB_USERNAME%.streamlit.app
echo.
echo 8. Open in Safari on iPhone and bookmark!
echo.
echo ========================================
echo Questions?
echo - Read: QUICK_DEPLOY.md
echo - Read: DEPLOYMENT_GUIDE.md
echo - Check: README.md
echo ========================================
echo.

pause
