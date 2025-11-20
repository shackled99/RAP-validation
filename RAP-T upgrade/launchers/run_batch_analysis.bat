@echo off
REM RAP Batch Analysis Launcher
REM Process datasets automatically

echo ========================================
echo   RAP Batch Analysis Pipeline
echo ========================================
echo.
echo Available commands:
echo   1. List datasets
echo   2. Test on ecoli_round5 (50 curves)
echo   3. Process 1000 curves from ecoli_full
echo   4. Process ALL ecoli_full (13,608 curves)
echo   5. Custom command
echo   0. Exit
echo.

:menu
set /p choice="Enter your choice (0-5): "

if "%choice%"=="0" goto end
if "%choice%"=="1" goto list
if "%choice%"=="2" goto test
if "%choice%"=="3" goto thousand
if "%choice%"=="4" goto full
if "%choice%"=="5" goto custom

echo Invalid choice. Try again.
goto menu

:list
echo.
echo ========================================
python run_rap.py --list
echo ========================================
echo.
goto menu

:test
echo.
echo ========================================
echo Running test analysis on ecoli_round5...
echo ========================================
echo.
python run_rap.py ecoli_round5
echo.
echo Test complete! Check results/automated/ecoli_round5/
echo.
pause
goto menu

:thousand
echo.
echo ========================================
echo Processing 1000 curves from ecoli_full...
echo ========================================
echo.
python run_rap.py ecoli_full --limit 1000 --workers 8
echo.
echo Analysis complete! Check results/automated/ecoli_full/
echo.
pause
goto menu

:full
echo.
echo ========================================
echo Processing ALL 13,608 curves from ecoli_full
echo This will take 2-3 hours!
echo ========================================
echo.
set /p confirm="Are you sure? (y/n): "
if /i not "%confirm%"=="y" goto menu

echo.
echo Starting full analysis...
echo.
python run_rap.py ecoli_full --workers 8
echo.
echo Full analysis complete! Check results/automated/ecoli_full/
echo.
pause
goto menu

:custom
echo.
set /p dataset="Enter dataset ID: "
set /p limit="Enter limit (or 0 for all): "
set /p workers="Enter number of workers (default 8): "

if "%workers%"=="" set workers=8

if "%limit%"=="0" (
    python run_rap.py %dataset% --workers %workers%
) else (
    python run_rap.py %dataset% --limit %limit% --workers %workers%
)

echo.
echo Analysis complete!
echo.
pause
goto menu

:end
echo.
echo Exiting...
