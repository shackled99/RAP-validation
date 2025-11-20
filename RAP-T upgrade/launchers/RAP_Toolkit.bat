@echo off
REM RAP Analysis Toolkit - Main Launcher
REM Your one-stop shop for all RAP analysis

title RAP Analysis Toolkit

:menu
cls
echo ========================================
echo   RAP ANALYSIS TOOLKIT
echo ========================================
echo.
echo What would you like to do?
echo.
echo   1. Launch Interactive Explorer
echo   2. Run Batch Analysis
echo   3. Install/Update Dependencies
echo   4. View Documentation
echo   0. Exit
echo.
echo ========================================

set /p choice="Enter your choice (0-4): "

if "%choice%"=="0" goto end
if "%choice%"=="1" goto explorer
if "%choice%"=="2" goto batch
if "%choice%"=="3" goto install
if "%choice%"=="4" goto docs

echo Invalid choice. Try again.
timeout /t 2 >nul
goto menu

:explorer
echo.
echo ========================================
echo Launching RAP Interactive Explorer...
echo ========================================
echo.
streamlit run explore_rap.py
goto menu

:batch
echo.
call run_batch_analysis.bat
goto menu

:install
echo.
echo ========================================
echo Installing/Updating Python Dependencies
echo ========================================
echo.
pip install -r requirements.txt
echo.
echo Installation complete!
echo.
pause
goto menu

:docs
echo.
echo ========================================
echo Available Documentation:
echo ========================================
echo.
echo   START_HERE.md          - Quick start guide
echo   EXPLORER_GUIDE.md      - Interactive explorer docs
echo   AUTOMATION_GUIDE.md    - Batch processing docs
echo   TOOLS_OVERVIEW.md      - Complete toolkit overview
echo.
echo Opening START_HERE.md...
echo.
start START_HERE.md
echo.
pause
goto menu

:end
echo.
echo Thanks for using RAP Analysis Toolkit!
echo.
timeout /t 2 >nul
