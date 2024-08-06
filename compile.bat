@echo off
pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo PyInstaller not found, installing...
    pip install pyinstaller
)
pyinstaller --onefile --noconsole --name LatencyApp2 --hidden-import "PyQt5.sip" --hidden-import "PyQt5.QtCore" --hidden-import "PyQt5.QtGui" --hidden-import "PyQt5.QtWidgets" --hidden-import "pynput.mouse" --hidden-import "numpy" --hidden-import "mss" --hidden-import "time" --hidden-import "collections" --hidden-import "threading" --strip --noupx main.py

echo Compilation finished successfully
