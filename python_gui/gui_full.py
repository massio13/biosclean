#!/usr/bin/env python3
import sys, os, subprocess, json
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFileDialog, QMessageBox, QSplitter, QTreeWidget, QTreeWidgetItem,
    QTextEdit, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QToolBar, QAction, QStatusBar, QTabWidget,
    QSizePolicy
)
from PySide6.QtCore import Qt, QByteArray
from PySide6.QtGui import QFont

RUST_BIN = os.environ.get("BIOS_CORE_BIN", os.path.join("..","target","release","bios_scanner_full_extended"))

def read_file_bytes(path, start=0, length=512):
    try:
        with open(path, "rb") as f:
            f.seek(start)
            return f.read(length)
    except Exception as e:
        return None

def bytes_to_hex_dump(b, base_offset=0):
    if not b:
        return ""
    lines = []
    for i in range(0, len(b), 16):
        chunk = b[i:i+16]
        hex_part = " ".join(f"{x:02X}" for x in chunk)
        asc_part = "".join(chr(x) if 32 <= x < 127 else "." for x in chunk)
        lines.append(f"{base_offset+i:08X}  {hex_part:<48}  {asc_part}")
    return "\n".join(lines)

class HexViewer(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setFont(QFont("Consolas", 10))
        self.setReadOnly(True)

    def display_bytes(self, b, base_offset=0):
        self.setPlainText(bytes_to_hex_dump(b, base_offset))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LBE-Lite Pro — BIOS Toolkit (Full UI)")
        self.resize(1150, 720)
        self.dump_path = ""
        self.scan_json_path = ""
        self.last_report = None

        self._build_ui()
        self._build_toolbar()
        self.setStatusBar(QStatusBar())

    def _build_ui(self):
        splitter = QSplitter(Qt.Horizontal, self)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        # file selector
        file_row = QHBoxLayout()
        self.path_edit = QLineEdit()
        btn_browse = QPushButton("Parcourir…")
        btn_browse.clicked.connect(self.on_browse)
        file_row.addWidget(QLabel("Dump BIOS:"))
        file_row.addWidget(self.path_edit)
        file_row.addWidget(btn_browse)
        left_layout.addLayout(file_row)

        # tree for FV list
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Section", "Offset", "Len", "GUID"])
        self.tree.itemSelectionChanged.connect(self.on_tree_select)
        left_layout.addWidget(self.tree)

        # actions row
        act_row = QHBoxLayout()
        self.btn_scan = QPushButton("Scan")
        self.btn_scan.clicked.connect(self.on_scan)
        self.btn_bg = QPushButton("BootGuard")
        self.btn_bg.clicked.connect(self.on_bootguard)
        self.btn_me = QPushButton("ME")
        self.btn_me.clicked.connect(self.on_me)
        self.btn_clean = QPushButton("Clean NVRAM")
        self.btn_clean.clicked.connect(self.on_clean)
        act_row.addWidget(self.btn_scan)
        act_row.addWidget(self.btn_bg)
        act_row.addWidget(self.btn_me)
        act_row.addWidget(self.btn_clean)
        left_layout.addLayout(act_row)

        # right panel tabs
        right_tabs = QTabWidget()
        self.hex_view = HexViewer()
        self.log_view = QTextEdit(); self.log_view.setReadOnly(True)
        self.json_view = QTextEdit(); self.json_view.setReadOnly(True)
        right_tabs.addTab(self.hex_view, "Hex Viewer")
        right_tabs.addTab(self.log_view, "Logs")
        right_tabs.addTab(self.json_view, "JSON Report")

        splitter.addWidget(left_panel)
        splitter.addWidget(right_tabs)
        splitter.setStretchFactor(1, 1)

        self.setCentralWidget(splitter)

    def _build_toolbar(self):
        tb = QToolBar("Actions")
        self.addToolBar(tb)
        a_open = QAction("Ouvrir dump", self); a_open.triggered.connect(self.on_browse); tb.addAction(a_open)
        a_scan = QAction("Scan", self); a_scan.triggered.connect(self.on_scan); tb.addAction(a_scan)
        a_bg = QAction("BootGuard", self); a_bg.triggered.connect(self.on_bootguard); tb.addAction(a_bg)
        a_me = QAction("ME", self); a_me.triggered.connect(self.on_me); tb.addAction(a_me)
        a_clean = QAction("Clean", self); a_clean.triggered.connect(self.on_clean); tb.addAction(a_clean)

    def log(self, msg):
        self.log_view.append(msg)
        self.statusBar().showMessage(msg, 4000)

    def on_browse(self):
        f, _ = QFileDialog.getOpenFileName(self, "Choisir un dump", "", "BIN files (*.bin);;All files (*)")
        if f:
            self.dump_path = f
            self.path_edit.setText(f)
            self.tree.clear()
            self.hex_view.clear()
            self.json_view.clear()
            self.last_report = None
            self.log(f"Fichier sélectionné: {f}")

    def run_core(self, args):
        try:
            self.log(f"$ {' '.join(args)}")
            p = subprocess.run(args, capture_output=True, text=True, check=False)
            out = p.stdout.strip()
            err = p.stderr.strip()
            if p.returncode != 0:
                self.log(f"ERREUR: {err or out}")
                QMessageBox.critical(self, "Erreur core", err or out or "Erreur inconnue")
                return None
            return out or err
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))
            return None

    def on_scan(self):
        p = self.path_edit.text().strip()
        if not p:
            QMessageBox.warning(self, "Dump manquant", "Sélectionne un dump d'abord")
            return
        outp = p + ".scan.json"
        args = [RUST_BIN, "Scan", "--input", p, "--out", outp]
        res = self.run_core(args)
        if res is None:
            return
        try:
            with open(outp, "r", encoding="utf-8") as f:
                report = json.load(f)
            self.last_report = report
            self.json_view.setPlainText(json.dumps(report, indent=2))
            self.populate_tree(report)
            self.log("Scan terminé.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur lecture report", str(e))

    def on_bootguard(self):
        p = self.path_edit.text().strip()
        if not p:
            QMessageBox.warning(self, "Dump manquant", "Sélectionne un dump d'abord")
            return
        outp = p + ".bg.json"
        args = [RUST_BIN, "Bootguard", "--input", p, "--out", outp]
        res = self.run_core(args)
        if res is None:
            return
        try:
            with open(outp, "r", encoding="utf-8") as f:
                self.json_view.setPlainText(f.read())
            self.log("BootGuard report généré.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur lecture report", str(e))

    def on_me(self):
        p = self.path_edit.text().strip()
        if not p:
            QMessageBox.warning(self, "Dump manquant", "Sélectionne un dump d'abord")
            return
        outp = p + ".me.json"
        args = [RUST_BIN, "Me", "--input", p, "--out", outp]
        res = self.run_core(args)
        if res is None:
            return
        try:
            with open(outp, "r", encoding="utf-8") as f:
                self.json_view.setPlainText(f.read())
            self.log("ME report généré.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur lecture report", str(e))

    def on_clean(self):
        p = self.path_edit.text().strip()
        if not p:
            QMessageBox.warning(self, "Dump manquant", "Sélectionne un dump d'abord")
            return
        outp = p + ".clean.bin"
        args = [RUST_BIN, "Clean", "--input", p, "--out", outp]
        res = self.run_core(args)
        if res is None:
            return
        self.log(f"Image nettoyée: {outp}")
        # show first bytes of cleaned
        b = read_file_bytes(outp, 0, 256)
        self.hex_view.display_bytes(b, 0)
        QMessageBox.information(self, "Clean", f"Fichier nettoyé créé:\n{outp}")

    def populate_tree(self, report):
        self.tree.clear()
        root_all = QTreeWidgetItem(["All FV", "", "", ""])
        root_nv = QTreeWidgetItem(["NvData candidates", "", "", ""])
        self.tree.addTopLevelItem(root_all)
        self.tree.addTopLevelItem(root_nv)
        # All FV
        for fv in report.get("all_fv", []):
            it = QTreeWidgetItem(root_all, ["FV", f"0x{fv['offset']:X}", f"0x{fv['len']:X}", fv['guid']])
            it.setData(0, Qt.UserRole, ("fv", fv['offset'], fv['len']))
        # Nv candidates
        for fv in report.get("nv_candidates", []):
            it = QTreeWidgetItem(root_nv, ["NV", f"0x{fv['offset']:X}", f"0x{fv['len']:X}", fv['guid']])
            it.setData(0, Qt.UserRole, ("nv", fv['offset'], fv['len']))
        self.tree.expandAll()

    def on_tree_select(self):
        items = self.tree.selectedItems()
        if not items or not self.dump_path:
            self.dump_path = self.path_edit.text().strip()
            if not self.dump_path:
                return
        if not items:
            return
        kind, off, ln = items[0].data(0, Qt.UserRole) or (None, None, None)
        if off is None or ln is None:
            return
        # show first 256 bytes at offset
        b = read_file_bytes(self.dump_path, off, min(512, ln))
        self.hex_view.display_bytes(b, base_offset=off)

def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
