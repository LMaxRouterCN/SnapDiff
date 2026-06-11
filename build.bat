@echo off
echo ========================================
echo   SnapDiff Build Script
echo ========================================

echo [1/3] Checking and installing dependencies...
pip install -r requirements.txt
pip install pyinstaller

echo [2/3] Compiling core executable (this may take a few minutes)...
pyinstaller --noconfirm --onedir --windowed --name "SnapDiff" main.py

echo [3/3] Deploying config files...
xcopy /E /I /Y "config" "dist\SnapDiff\config"

echo ========================================
echo Build Success!
echo Please go to dist\SnapDiff directory to find your release package.
echo ========================================
pause