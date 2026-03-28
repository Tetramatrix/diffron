@echo off
REM ============================================================
REM Diffron - Commit and Push to GitHub
REM ============================================================
REM Use this in the Public Repo to commit and push changes
REM ============================================================

setlocal enabledelayedexpansion

set "REPO_DIR=%~dp0"

echo.
echo ============================================================
echo  Diffron - Commit and Push to GitHub
echo ============================================================
echo.

cd /d "%REPO_DIR%"

REM Show current status
echo Current branch:
git branch
echo.

REM Show changes
echo Changes to commit:
git status --short
echo.

REM Ask for commit message
set /p "MSG=Enter commit message: "

if "!MSG!"=="" (
    echo ERROR: Commit message cannot be empty!
    pause
    exit /b 1
)

REM Add, commit, push
echo.
echo Adding files...
git add .

echo Committing: !MSG!
git commit -m "!MSG!"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Pushing to GitHub...
    git push origin master
    
    if %ERRORLEVEL% EQU 0 (
        echo.
        echo ============================================================
        echo  Successfully pushed to GitHub!
        echo  https://github.com/Tetramatrix/diffron
        echo ============================================================
    ) else (
        echo.
        echo ERROR: Push failed!
    )
) else (
    echo.
    echo Nothing to commit or commit failed.
)

echo.
endlocal
pause
