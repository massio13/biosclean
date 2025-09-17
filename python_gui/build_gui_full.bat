@echo off
setlocal
REM Build the full GUI into one EXE, bundling the Rust core next to it.
if not exist "..\target\release\bios_scanner_full_extended.exe" (
    echo [!] Rust core not found. Build it first: cargo build --release
    exit /b 1
)
py -3 -m pip install --upgrade pip
py -3 -m pip install PySide6 pyinstaller
py -3 -m PyInstaller --noconfirm --onefile --add-data "..\target\release\bios_scanner_full_extended.exe;." gui_full.py
echo [OK] GUI EXE in python_gui\dist\gui_full.exe
endlocal
