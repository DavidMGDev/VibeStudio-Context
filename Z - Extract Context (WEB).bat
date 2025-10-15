@echo off
REM Z - Extract Context - Web Project Mode
REM Place this file in the project root directory

echo ===============================================================
echo           Z - EXTRACT CONTEXT - WEB PROJECT MODE
echo ===============================================================
echo.
echo This tool will extract and merge web development files into
echo consolidated text files.
echo.
echo File types included:
echo   - HTML files (.html, .htm)
echo   - CSS files (.css, .scss, .sass, .less)
echo   - JavaScript files (.js, .jsx, .mjs)
echo   - TypeScript files (.ts, .tsx)
echo   - Vue files (.vue)
echo   - PHP files (.php)
echo   - JSON files (.json)
echo.

REM Set the script path relative to project root
set SCRIPT_PATH=VibeStudio\CodeTextify.py

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

REM Check if the Python script exists
if not exist "%SCRIPT_PATH%" (
    echo ERROR: Python script '%SCRIPT_PATH%' not found
    echo Please make sure the script is located at VibeStudio/CodeTextify.py
    echo and this batch file is in the project root
    pause
    exit /b 1
)

REM Ensure we're in the project root directory (where this batch file is located)
cd /d "%~dp0"

REM Run the Python script with web extensions
echo Starting Web Project Processor...
echo Script location: %SCRIPT_PATH%
echo Working directory: %CD%
echo.
python "%SCRIPT_PATH%" .html .htm .css .scss .sass .less .js .jsx .mjs .ts .tsx .vue .php .json

REM Check if the script ran successfully
if errorlevel 1 (
    echo.
    echo Script execution failed. Check the error messages above.
    pause
    exit /b 1
)

REM Success message
echo.
echo Batch file execution completed.
pause