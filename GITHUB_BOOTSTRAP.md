# GitHub Bootstrap Guide (Repo + Actions + EXE)

## 1) Create repo & push
```bash
# in Windows PowerShell or Git Bash inside rust_bios_scanner_full_extended
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/<your-user>/<your-repo>.git
git push -u origin main
```

## 2) Enable Actions
- Go to GitHub → Actions → enable workflows if asked.
- The workflow `.github/workflows/build_windows.yml` will appear.
- Click "Run workflow" (or push to main).

## 3) Download artifacts
- After the job finishes, open the run → **Artifacts**:
  - `bios_scanner_windows` → contains `bios_scanner_full_extended.exe`
  - `bios_scanner_gui_windows` → contains `gui.exe`

## 4) Optional Release
- Use `.github/workflows/release_build.yml` → "Run workflow" to create a Release with attached binaries.

## 5) Add collaborator (me)
- Settings → Collaborators → Add a collaborator → invite my GitHub handle (paste it in chat and I’ll confirm).
- Once added, I can push changes, trigger builds, and publish releases for you.
```

## 6) Local EXE build (alternative without GitHub)
- Run PowerShell script:
```powershell
.\build_release.ps1
```
- Binaries will be at:
  - `target\release\bios_scanner_full_extended.exe`
  - `python_gui\dist\gui.exe` (PyInstaller)

## 7) Installer (optional)
- Install **Inno Setup**.
- Open `installer.iss` and compile → produces `bios_scanner_setup.exe`.
