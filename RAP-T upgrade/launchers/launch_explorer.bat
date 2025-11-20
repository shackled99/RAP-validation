@echo off
REM RAP Interactive Explorer Launcher
REM Double-click this file to start the explorer

echo ========================================
echo   RAP Interactive Explorer
echo ========================================
echo.
echo Starting Streamlit server...
echo.
echo The explorer will open in your browser automatically.
echo.
echo Press Ctrl+C to stop the server when done.
echo ========================================
echo.

cd /d "%~dp0"
streamlit run explore_rap.py

pause
