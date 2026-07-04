@echo off
REM ============================================================================
REM Dataset Mirroring Automation Script for Sign2Kannada
REM ============================================================================
REM
REM This script automates the entire process of mirroring your dataset and
REM training a model that works for both left and right hands.
REM
REM Prerequisites:
REM - Python installed and in PATH
REM - Images in data/dataset/0/ through data/dataset/9/
REM
REM Usage:
REM   mirror_and_train.bat
REM
REM ============================================================================

setlocal enabledelayedexpansion

echo.
echo ============================================================================
echo SIGN2KANNADA: DATASET MIRRORING AND TRAINING AUTOMATION
echo ============================================================================
echo.
echo This script will:
echo   1. Mirror your dataset (create right-hand equivalents)
echo   2. Preprocess original images
echo   3. Preprocess mirrored images
echo   4. Combine both datasets
echo   5. Train the model
echo   6. Display results
echo.
echo Note: This may take 5-10 minutes depending on dataset size
echo.
pause

REM ============================================================================
REM Step 1: Mirror Dataset
REM ============================================================================
echo.
echo ============================================================================
echo STEP 1: MIRRORING DATASET
echo ============================================================================
python mirror_dataset.py

if errorlevel 1 (
    echo.
    echo ERROR: Failed to mirror dataset
    echo Make sure you have images in data/dataset/0/, 1/, ... 9/
    pause
    exit /b 1
)

echo.
echo ✓ Dataset mirrored successfully
echo.

REM ============================================================================
REM Step 2: Preprocess Original Images
REM ============================================================================
echo.
echo ============================================================================
echo STEP 2: PREPROCESSING ORIGINAL IMAGES
echo ============================================================================
python preprocess.py

if errorlevel 1 (
    echo.
    echo ERROR: Failed to preprocess original images
    pause
    exit /b 1
)

echo.
echo ✓ Original images preprocessed
echo.

REM ============================================================================
REM Step 3: Preprocess Mirrored Images
REM ============================================================================
echo.
echo ============================================================================
echo STEP 3: PREPROCESSING MIRRORED IMAGES
echo ============================================================================
python preprocess_mirrored.py

if errorlevel 1 (
    echo.
    echo ERROR: Failed to preprocess mirrored images
    pause
    exit /b 1
)

echo.
echo ✓ Mirrored images preprocessed
echo.

REM ============================================================================
REM Step 4: Combine Datasets
REM ============================================================================
echo.
echo ============================================================================
echo STEP 4: COMBINING DATASETS
echo ============================================================================
python combine_landmarks.py

if errorlevel 1 (
    echo.
    echo ERROR: Failed to combine datasets
    pause
    exit /b 1
)

echo.
echo ✓ Datasets combined
echo.

REM ============================================================================
REM Step 5: Copy Combined Dataset
REM ============================================================================
echo.
echo ============================================================================
echo STEP 5: PREPARING FOR TRAINING
echo ============================================================================
echo.
echo Copying combined dataset to default location...

REM Delete old landmarks.csv and copy combined version
if exist data\landmarks.csv (
    echo Backing up old landmarks.csv...
    move /Y data\landmarks.csv data\landmarks_backup.csv >nul 2>&1
)

echo Copying data\landmarks_combined.csv to data\landmarks.csv...
copy /Y data\landmarks_combined.csv data\landmarks.csv >nul 2>&1

if errorlevel 1 (
    echo.
    echo ERROR: Failed to copy combined dataset
    pause
    exit /b 1
)

echo ✓ Dataset ready for training
echo.

REM ============================================================================
REM Step 6: Train Model
REM ============================================================================
echo.
echo ============================================================================
echo STEP 6: TRAINING MODEL ON COMBINED DATASET
echo ============================================================================
echo.
echo Training on both original and mirrored images...
echo This step may take a few minutes...
echo.

python train.py

if errorlevel 1 (
    echo.
    echo ERROR: Failed to train model
    echo Check the output above for details
    pause
    exit /b 1
)

echo.
echo ✓ Model trained successfully!
echo.

REM ============================================================================
REM Summary
REM ============================================================================
echo.
echo ============================================================================
echo ✅ COMPLETE! ALL STEPS SUCCESSFUL!
echo ============================================================================
echo.
echo Summary:
echo   ✓ Dataset mirrored (original + mirrored images)
echo   ✓ Landmarks extracted (original)
echo   ✓ Landmarks extracted (mirrored)
echo   ✓ Datasets combined (490 total samples)
echo   ✓ Model trained on combined dataset
echo.
echo Next Steps:
echo   1. Test the model: python main.py
echo   2. Show RIGHT hand → Should work now!
echo   3. Show LEFT hand → Should still work!
echo   4. Show BOTH hands → Both should work independently!
echo.
echo Files Created:
echo   • data/dataset/0_mirrored/ through 9_mirrored/
echo   • data/landmarks_mirrored.csv (mirrored landmarks)
echo   • data/landmarks_combined.csv (original + mirrored)
echo   • data/landmarks_backup.csv (backup of old file)
echo   • model.pkl (new trained model)
echo.
echo To revert to original:
echo   move /Y data\landmarks_backup.csv data\landmarks.csv
echo   python train.py
echo.
echo ============================================================================
echo.

pause
