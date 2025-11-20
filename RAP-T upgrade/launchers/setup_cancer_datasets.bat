@echo off
REM Cancer Dataset Setup - Automated
REM Downloads and prepares cancer cell line growth data

title Cancer Dataset Setup

echo ========================================
echo   CANCER DATASET SETUP
echo ========================================
echo.
echo This will:
echo   1. Download cancer cell growth datasets
echo   2. Prepare data for RAP analysis
echo   3. Validate files are ready
echo.
echo Datasets to download:
echo   - HL-60 Leukemia growth curves
echo   - DepMap cancer cell doubling times
echo   - NCI-60 cancer panel data
echo.

set /p confirm="Continue? (y/n): "
if /i not "%confirm%"=="y" goto end

echo.
echo ========================================
echo STEP 1: Downloading datasets...
echo ========================================
echo.

python download_cancer_datasets.py

echo.
echo ========================================
echo STEP 2: Preparing data for RAP...
echo ========================================
echo.

python prepare_cancer_data.py

echo.
echo ========================================
echo STEP 3: Validation
echo ========================================
echo.

if exist "datasets\cancer\hl60_processed.xlsx" (
    echo ✅ HL-60 dataset ready
) else (
    echo ⚠️  HL-60 dataset not found
)

if exist "datasets\cancer\depmap_processed.csv" (
    echo ✅ DepMap dataset ready
) else (
    echo ⚠️  DepMap dataset not found
)

if exist "datasets\cancer\nci60_extracted" (
    echo ✅ NCI-60 dataset extracted
) else (
    echo ⚠️  NCI-60 dataset not found
)

echo.
echo ========================================
echo SETUP COMPLETE
echo ========================================
echo.
echo Next steps:
echo   1. Launch RAP Explorer:
echo      streamlit run explore_rap.py
echo.
echo   2. Select cancer dataset:
echo      - hl60_leukemia
echo      - depmap_cancer  
echo      - nci60_cancer
echo.
echo   3. Fit curves and compare to E. coli baseline
echo.
echo See CANCER_DATASETS_GUIDE.md for details
echo ========================================
echo.

:end
pause
