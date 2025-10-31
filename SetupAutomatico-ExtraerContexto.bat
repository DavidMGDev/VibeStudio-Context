@echo off
setlocal enabledelayedexpansion

REM ===============================================================
REM           VIBESTUDIO CONTEXT INSTALLER
REM ===============================================================

echo ===============================================================
echo           VIBESTUDIO CONTEXT INSTALLER v1.0
echo ===============================================================
echo.
echo This installer will set up VibeStudio Context tools for your project.
echo.

REM Check if Git is installed
where git >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Git is not installed or not in PATH!
    echo.
    echo Please install Git from: https://git-scm.com/download/win
    echo.
    pause
    exit /b 1
)

REM Check if Python is installed
where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH!
    echo.
    echo Please install Python from: https://python.org
    echo.
    pause
    exit /b 1
)

echo [CHECK] Git found
echo [CHECK] Python found
echo.

REM Check if VibeStudio folder already exists
if exist "VibeStudio" (
    echo [WARNING] VibeStudio folder already exists!
    echo.
    set /p OVERWRITE="Do you want to remove it and reinstall? (Y/N): "
    if /i not "!OVERWRITE!"=="Y" (
        echo.
        echo Installation cancelled.
        pause
        exit /b 0
    )
    echo.
    echo [STEP] Removing existing VibeStudio folder...
    rmdir /s /q "VibeStudio" 2>nul
    if exist "VibeStudio" (
        echo [ERROR] Failed to remove existing VibeStudio folder!
        echo Please remove it manually and try again.
        pause
        exit /b 1
    )
    echo [SUCCESS] Existing folder removed.
    echo.
)

REM Ask for project type BEFORE cloning
:ASK_PROJECT_TYPE
echo ===============================================================
echo           SELECT YOUR PROJECT TYPE
echo ===============================================================
echo.
echo Please choose your project type (this will download the appropriate tools):
echo.
echo   [1] Web Project (HTML, CSS, JS, TS, etc.)
echo   [2] Godot Game Engine (GD, TSCN)
echo   [3] Other (Specify custom file extensions)
echo.
set /p PROJECT_TYPE="Enter your choice (1, 2, or 3): "

if "%PROJECT_TYPE%"=="1" goto WEB_PROJECT
if "%PROJECT_TYPE%"=="2" goto GODOT_PROJECT
if "%PROJECT_TYPE%"=="3" goto OTHER_PROJECT

echo.
echo [ERROR] Invalid choice! Please enter 1, 2, or 3.
echo.
goto ASK_PROJECT_TYPE

:WEB_PROJECT
echo.
echo [SELECTED] Web Project
set SELECTED_BAT=Z - Extract Context (WEB).bat
set DELETE_BAT1=Z - Extract Context (GD).bat
set DELETE_BAT2=Z - Extract Context (Other).bat
set EXTENSIONS=
goto CLONE_REPO

:GODOT_PROJECT
echo.
echo [SELECTED] Godot Project
set SELECTED_BAT=Z - Extract Context (GD).bat
set DELETE_BAT1=Z - Extract Context (WEB).bat
set DELETE_BAT2=Z - Extract Context (Other).bat
set EXTENSIONS=
goto CLONE_REPO

:OTHER_PROJECT
echo.
echo [SELECTED] Custom Project
set SELECTED_BAT=Z - Extract Context (Other).bat
set DELETE_BAT1=Z - Extract Context (WEB).bat
set DELETE_BAT2=Z - Extract Context (GD).bat

REM Collect custom extensions BEFORE cloning
echo.
echo ---------------------------------------------------------------
echo           CUSTOM FILE EXTENSIONS
echo ---------------------------------------------------------------
echo.
echo Enter the file extensions you want to process.
echo Enter extensions one at a time (with or without dots).
echo Type 'done' when finished.
echo.
echo Examples: .py  or  py
echo           .cpp or  cpp
echo.

set EXTENSIONS=
set COUNT=0

:EXTENSION_LOOP
set /p EXT="Extension #!COUNT!: "

REM Check if user is done
if /i "!EXT!"=="done" (
    if !COUNT! EQU 0 (
        echo.
        echo [ERROR] You must specify at least one extension!
        echo.
        goto EXTENSION_LOOP
    )
    goto CLONE_REPO
)

REM Validate extension
if "!EXT!"=="" (
    echo [WARNING] Empty input, please enter a valid extension or 'done'
    goto EXTENSION_LOOP
)

REM Add dot if not present
set FIRST_CHAR=!EXT:~0,1!
if not "!FIRST_CHAR!"=="." (
    set EXT=.!EXT!
)

REM Add to extensions list
if "!EXTENSIONS!"=="" (
    set EXTENSIONS=!EXT!
) else (
    set EXTENSIONS=!EXTENSIONS! !EXT!
)

set /a COUNT+=1
echo [ADDED] !EXT!
goto EXTENSION_LOOP

:CLONE_REPO
echo.
echo [STEP] Cloning VibeStudio Context repository based on your selection...
echo.
git clone https://github.com/DavidMGDev/VibeStudio-Context.git VibeStudio
if errorlevel 1 (
    echo.
    echo [ERROR] Failed to clone repository!
    echo Please check your internet connection and try again.
    pause
    exit /b 1
)
echo.
echo [SUCCESS] Repository cloned successfully.

REM Delete the installer from the cloned repo folder if it exists (safe, no error if not present)
del "VibeStudio\VibeStudio-Context (Installer).bat" 2>nul

REM Remove .git folder to clean up
if exist "VibeStudio\.git" (
    rmdir /s /q "VibeStudio\.git" 2>nul
)

:PROCESS_INSTALLATION
echo.
echo ===============================================================
echo           PROCESSING INSTALLATION
echo ===============================================================
echo.

REM Check if selected batch file exists
if not exist "VibeStudio\!SELECTED_BAT!" (
    echo [ERROR] Selected batch file not found: !SELECTED_BAT!
    echo The repository structure may have changed.
    pause
    exit /b 1
)

REM Step 1: Move selected batch file to current directory
echo [STEP 1/5] Moving selected batch file...
copy "VibeStudio\!SELECTED_BAT!" "Z - Extract Context.bat" >nul
if errorlevel 1 (
    echo [ERROR] Failed to copy batch file!
    pause
    exit /b 1
)
echo [SUCCESS] Batch file moved: Z - Extract Context.bat

REM Step 2: Delete unselected batch files
echo.
echo [STEP 2/5] Removing unselected batch files...
del "VibeStudio\!DELETE_BAT1!" 2>nul
del "VibeStudio\!DELETE_BAT2!" 2>nul
del "VibeStudio\!SELECTED_BAT!" 2>nul
echo [SUCCESS] Unselected files removed

REM Step 3: If custom extensions, update the batch file
if not "!EXTENSIONS!"=="" (
    echo.
    echo [STEP 3/5] Configuring custom extensions...
    
    REM Create a temporary batch file with custom extensions
    (
        echo @echo off
        echo REM Code Textify - Custom Project Mode
        echo REM Place this file in the project root directory
        echo.
        echo echo ===============================================================
        echo echo           Z - EXTRACT CONTEXT
        echo echo ===============================================================
        echo echo.
        echo echo This tool will extract and merge code files into
        echo echo consolidated text files.
        echo echo.
        echo echo File extensions: !EXTENSIONS!
        echo echo.
        echo.
        echo REM Set the script path relative to project root
        echo set SCRIPT_PATH=VibeStudio\CodeTextify.py
        echo.
        echo REM Check if Python is available
        echo python --version ^>nul 2^>^&1
        echo if errorlevel 1 ^(
        echo     echo ERROR: Python is not installed or not in PATH
        echo     echo Please install Python from https://python.org
        echo     pause
        echo     exit /b 1
        echo ^)
        echo.
        echo REM Check if the Python script exists
        echo if not exist "%%SCRIPT_PATH%%" ^(
        echo     echo ERROR: Python script '%%SCRIPT_PATH%%' not found
        echo     echo Please make sure the script is located at VibeStudio/CodeTextify.py
        echo     echo and this batch file is in the project root
        echo     pause
        echo     exit /b 1
        echo ^)
        echo.
        echo REM Ensure we're in the project root directory
        echo cd /d "%%~dp0"
        echo.
        echo REM Run the Python script with configured extensions
        echo echo Starting Code Processor...
        echo echo Script location: %%SCRIPT_PATH%%
        echo echo Working directory: %%CD%%
        echo echo.
        echo python "%%SCRIPT_PATH%%" !EXTENSIONS!
        echo.
        echo REM Check if the script ran successfully
        echo if errorlevel 1 ^(
        echo     echo.
        echo     echo Script execution failed. Check the error messages above.
        echo     pause
        echo     exit /b 1
        echo ^)
        echo.
        echo REM Success message
        echo echo.
        echo echo Batch file execution completed.
        echo pause
    ) > "Z - Extract Context.bat"
    
    echo [SUCCESS] Custom extensions configured: !EXTENSIONS!
) else (
    echo.
    echo [STEP 3/5] No custom configuration needed
)

REM Step 4: Keep only CodeTextify.py in VibeStudio folder
echo.
echo [STEP 4/5] Cleaning up VibeStudio folder...
for %%F in ("VibeStudio\*.*") do (
    if /i not "%%~nxF"=="CodeTextify.py" (
        del "%%F" 2>nul
    )
)
echo [SUCCESS] VibeStudio folder cleaned

REM Step 5: Delete installer (this script)
echo.
echo [STEP 5/5] Finalizing installation...
echo [SUCCESS] Installation complete!

REM Display summary
echo.
echo ===============================================================
echo           INSTALLATION SUCCESSFUL!
echo ===============================================================
echo.
echo Your project has been set up with VibeStudio Context tools.
echo.
echo What was installed:
echo   - VibeStudio\CodeTextify.py (main processor script)
echo   - Z - Extract Context.bat (launcher for your project type)
echo.
if not "!EXTENSIONS!"=="" (
    echo Configured extensions: !EXTENSIONS!
    echo.
)
echo To use:
echo   1. Run "Z - Extract Context.bat" in your project root
echo   2. Files will be processed and saved to "VibeStudio\Merged"
echo.
echo ===============================================================
echo.
echo This installer will now self-destruct...
pause

REM Self-delete using a helper script (deletes the installer from current directory)
(
    echo @echo off
    echo timeout /t 1 /nobreak ^>nul
    echo del "%~f0" ^>nul 2^>^&1
    echo del "VibeStudio-Context (Installer).bat" ^>nul 2^>^&1
) > "%TEMP%\delete_installer.bat"

start /b cmd /c "%TEMP%\delete_installer.bat"
exit