# updater.py
import requests
import subprocess
import sys
import os
import tempfile
import threading
from packaging import version
from pathlib import Path

GITHUB_USER = "MyWay-stage"
GITHUB_REPO = "MyWay-Tools"

VERSION_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/main/version.txt"
SETUP_URL   = f"https://github.com/{GITHUB_USER}/{GITHUB_REPO}/releases/latest/download/setup.exe"


def get_asset(filename: str) -> Path:
    if getattr(sys, 'frozen', False):
        exe_dir = Path(sys.executable).parent
        for candidate in [exe_dir, exe_dir / '_internal']:
            path = candidate / filename
            if path.exists():
                return path
    return Path(__file__).parent / filename


def get_current_version() -> str:
    try:
        return get_asset('version.txt').read_text().strip()
    except Exception:
        return "0.0.0"


class UpdateWindow:
    """Finestra di aggiornamento con border radius e ombra."""

    def __init__(self, app, current: str, latest: str):
        from PySide6.QtWidgets import (
            QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar
        )
        from PySide6.QtCore import Qt
        from PySide6.QtGui import QPixmap, QPainter, QColor, QPainterPath

        class _RoundedWidget(QWidget):
            def paintEvent(self_, event):
                painter = QPainter(self_)
                painter.setRenderHint(QPainter.Antialiasing)
                # Ombra
                for i in range(10, 0, -1):
                    painter.setBrush(QColor(0, 0, 0, 5 * i))
                    painter.setPen(Qt.NoPen)
                    painter.drawRoundedRect(
                        self_.rect().adjusted(i, i, -i, -i), 14, 14
                    )
                # Background bianco
                path = QPainterPath()
                path.addRoundedRect(
                    float(10), float(10),
                    float(self_.width() - 20), float(self_.height() - 20),
                    12.0, 12.0
                )
                painter.setBrush(QColor("#FFFFFF"))
                painter.setPen(Qt.NoPen)
                painter.drawPath(path)

        self._app = app
        self.win = _RoundedWidget()
        self.win.setWindowTitle("MyWay Tools — Aggiornamento")
        self.win.setFixedSize(460, 230)
        self.win.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.win.setAttribute(Qt.WA_TranslucentBackground)
        self.win.setStyleSheet("""
            QLabel       { background: transparent; }
            QProgressBar {
                border: none; border-radius: 4px;
                background-color: #EDEDED; color: transparent;
            }
            QProgressBar::chunk { background-color: #E60000; border-radius: 4px; }
        """)

        # Layout con margini extra per lasciare spazio all'ombra
        lay = QVBoxLayout(self.win)
        lay.setContentsMargins(40, 36, 40, 32)
        lay.setSpacing(10)

        # Barra rossa in cima (posizionata sopra il layout)
        barra = QWidget(self.win)
        barra.setGeometry(10, 10, 440, 6)
        barra.setStyleSheet("""
            background: #E60000;
            border-top-left-radius: 12px;
            border-top-right-radius: 12px;
        """)

        # Logo + nome app
        logo_row = QHBoxLayout()
        logo_row.setSpacing(12)

        icon_path = get_asset('logo.ico')
        lbl_logo = QLabel()
        if icon_path.exists():
            px = QPixmap(str(icon_path)).scaled(
                38, 38, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            lbl_logo.setPixmap(px)
        else:
            lbl_logo.setText("●")
            lbl_logo.setStyleSheet(
                "color:#E60000; font-size:28px; font-weight:bold;"
            )
        logo_row.addWidget(lbl_logo)

        lbl_app = QLabel("MyWay Tools")
        lbl_app.setStyleSheet(
            "color:#1A1A1A; font-size:18px; font-weight:bold;"
        )
        logo_row.addWidget(lbl_app)
        logo_row.addStretch()
        lay.addLayout(logo_row)

        lbl_info = QLabel(f"Aggiornamento disponibile:  {current}  →  {latest}")
        lbl_info.setStyleSheet("color:#555555; font-size:13px;")
        lay.addWidget(lbl_info)

        lay.addSpacing(4)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setFixedHeight(8)
        lay.addWidget(self.progress)

        self.lbl_status = QLabel("Scaricamento in corso...")
        self.lbl_status.setStyleSheet("color:#999999; font-size:12px;")
        lay.addWidget(self.lbl_status)

        # Centra sullo schermo
        screen = app.primaryScreen().geometry()
        self.win.move(
            (screen.width()  - self.win.width())  // 2,
            (screen.height() - self.win.height()) // 2,
        )
        self.win.show()
        app.processEvents()

    def set_progress(self, pct: int):
        from PySide6.QtCore import QTimer
        QTimer.singleShot(0, lambda: (
            self.progress.setValue(pct),
            self.lbl_status.setText(f"Scaricamento...  {pct}%")
        ))

    def set_installing(self):
        self.lbl_status.setText("✅  Installazione in corso...")
        self.progress.setValue(100)
        self._app.processEvents()


def check_and_update(app) -> bool:
    log_path = Path(sys.executable).parent / 'updater_debug.txt'

    try:
        response = requests.get(VERSION_URL, timeout=5)
        latest   = response.text.strip()
        current  = get_current_version()
        log_path.write_text(f"locale: {current}\ngithub: {latest}\n")

        if version.parse(latest) <= version.parse(current):
            return False

        # Mostra finestra
        ui = UpdateWindow(app, current, latest)

        # Download in thread separato
        tmp_path  = Path(tempfile.gettempdir()) / "myway_update.exe"
        risultato = {"ok": False, "errore": None}

        def _download():
            try:
                r = requests.get(SETUP_URL, timeout=60, stream=True)
                total      = int(r.headers.get('content-length', 0))
                downloaded = 0
                with open(tmp_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total:
                            pct = int(downloaded / total * 100)
                            ui.set_progress(pct)
                risultato["ok"] = True
            except Exception as e:
                risultato["errore"] = str(e)

        thread = threading.Thread(target=_download, daemon=True)
        thread.start()

        # Tieni la GUI responsiva mentre scarica
        while thread.is_alive():
            app.processEvents()
            thread.join(timeout=0.05)

        if not risultato["ok"]:
            log_path.write_text(f"Errore download: {risultato['errore']}\n")
            return False

        size_mb = tmp_path.stat().st_size / 1024 / 1024
        log_path.write_text(
            f"locale: {current}\ngithub: {latest}\n"
            f"File: {tmp_path}\nDimensione: {size_mb:.2f} MB\n"
        )

        ui.set_installing()

        # Installa e riavvia in thread separato (daemon=False → sopravvive a sys.exit)
        def _installa():
            processo = subprocess.Popen([
                str(tmp_path),
                "/VERYSILENT",
                "/SUPPRESSMSGBOXES",
                "/NORESTART",
                "/CLOSEAPPLICATIONS",
            ])
            processo.wait()

            try:
                import winreg
                key = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\MyWay Tools_is1"
                )
                install_path, _ = winreg.QueryValueEx(key, "InstallLocation")
                new_exe = Path(install_path) / "MyWayTools.exe"
                if new_exe.exists():
                    subprocess.Popen([str(new_exe)])
                    log_path.write_text(
                        log_path.read_text() + f"Avviato: {new_exe}\n"
                    )
            except Exception as e:
                log_path.write_text(
                    log_path.read_text() + f"Errore avvio: {e}\n"
                )

        threading.Thread(target=_installa, daemon=False).start()
        sys.exit(0)

    except requests.exceptions.ConnectionError:
        log_path.write_text("Nessuna connessione\n")
    except Exception as e:
        log_path.write_text(f"Errore: {e}\n")

    return False