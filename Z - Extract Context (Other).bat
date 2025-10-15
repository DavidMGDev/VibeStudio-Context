@echo off
REM Z - Extract Context - Custom Extensions Mode
REM Place this file in the project root directory

echo ===============================================================
echo           Z - EXTRACT CONTEXT - CUSTOM EXTENSIONS MODE
echo ===============================================================
echo.
echo This tool will extract and merge code files with extensions
echo you specify into consolidated text files.
echo.
echo Instructions:
echo   - Enter file extensions separated by spaces
echo   - Extensions can be with or without the dot (e.g., .py or py)
echo   - Example: .py .js .html .css
echo   - Example: ts tsx jsx
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

REM Ask user for file extensions
set /p EXTENSIONS=Enter file extensions (separated by spaces):

REM Check if user provided any extensions
if "%EXTENSIONS%"=="" (
    echo.
    echo ERROR: No extensions provided!
    pause
    exit /b 1
)

REM Run the Python script with user-provided extensions
echo.
echo Starting Code Textify with extensions: %EXTENSIONS%
echo Script location: %SCRIPT_PATH%
echo Working directory: %CD%
echo.
python "%SCRIPT_PATH%" %EXTENSIONS%

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