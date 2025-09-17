# biosclean
# biosclean

Outil de nettoyage NVRAM/Variables UEFI (HP/Lenovo/Dell, etc.) avec détection BootGuard.
- GUI : `bios_nvram_toolkit_gui.py`
- CLI : `bios_nvram_toolkit.py`

## Installation (Windows)
1. Installer Python 3.10+.
2. `pip install -r requirements.txt`

## Lancer
- **GUI** : `python bios_nvram_toolkit_gui.py`
- **CLI (auto)** :
  ```bash
  python bios_nvram_toolkit.py --clean "C:\path\dump.bin" -o clean.bin

CLI (offsets manuels) :

python bios_nvram_toolkit.py --clean "dump.bin" -o clean.bin --offsets 0x10 0x40000 0x84018

Scan seulement :

python bios_nvram_toolkit.py --scan "dump.bin"


Résultats

Image nettoyée : *_clean*.bin

Rapport : *_report.txt

Exports (si activé) : dossier exports_YYYY-MM-DD_hhmmss/


BootGuard

Disabled/Not enforced/Measured : nettoyage possible (boot non garanti).

Verified : nettoyage UEFI seul ne suffit pas → reconstruire ME+BIOS OEM complet.
