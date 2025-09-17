# Build script for Windows (PowerShell)
# Usage: .\build_release.ps1
Set-StrictMode -Version Latest
Write-Host "Building Rust release..."
cargo build --release
if ($LASTEXITCODE -ne 0) { Write-Error "Cargo build failed"; exit 1 }
Write-Host "Building GUI executable with PyInstaller..."
pushd python_gui
py -3 -m pip install --upgrade pip
py -3 -m pip install PySide6 pyinstaller
py -3 -m PyInstaller --noconfirm --onefile --add-data "..\target\release\bios_scanner_full_extended.exe;." gui.py
popd
Write-Host "Build finished. Binaries in target\\release and python_gui\\dist"
