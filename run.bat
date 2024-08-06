@echo off
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Please install Python and try again.
    exit /b 1
)

pip show numpy >nul 2>&1
if %errorlevel% neq 0 (
    echo Required packages are not installed. Installing now...
    pip install -r requirements.txt
)

python main.py
