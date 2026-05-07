# updater.py
import requests
import subprocess
import sys
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


def _mostra_download(app, current: str, latest: str):
    """Finestra di download con progress bar e border radius."""
    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar
    )
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QPixmap, QPainter, QColor, QPainterPath

    class _RoundedWidget(QWidget):
        def paintEvent(self_, event):
            painter = QPainter(self_)
            painter.setRenderHint(QPainter.Antialiasing)
            for i in range(10, 0, -1):
                painter.setBrush(QColor(0, 0, 0, 5 * i))
                painter.setPen(Qt.NoPen)
                painter.drawRoundedRect(self_.rect().adjusted(i, i, -i, -i), 14, 14)
            path = QPainterPath()
            path.addRoundedRect(float(10), float(10),
                                float(self_.width() - 20), float(self_.height() - 20),
                                12.0, 12.0)
            painter.setBrush(QColor("#FFFFFF"))
            painter.setPen(Qt.NoPen)
            painter.drawPath(path)

    win = _RoundedWidget()
    win.setWindowTitle("MyWay Tools — Aggiornamento")
    win.setFixedSize(460, 230)
    win.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
    win.setAttribute(Qt.WA_TranslucentBackground)
    win.setStyleSheet("""
        QLabel       { background: transparent; }
        QProgressBar {
            border: none; border-radius: 4px;
            background-color: #EDEDED; color: transparent;
        }
        QProgressBar::chunk { background-color: #E60000; border-radius: 4px; }
    """)

    lay = QVBoxLayout(win)
    lay.setContentsMargins(40, 36, 40, 32)
    lay.setSpacing(10)

    barra = QWidget(win)
    barra.setGeometry(10, 10, 440, 6)
    barra.setStyleSheet("""
        background: #E60000;
        border-top-left-radius: 12px;
        border-top-right-radius: 12px;
    """)

    logo_row = QHBoxLayout()
    logo_row.setSpacing(12)
    icon_path = get_asset('logo.ico')
    lbl_logo = QLabel()
    if icon_path.exists():
        px = QPixmap(str(icon_path)).scaled(38, 38, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        lbl_logo.setPixmap(px)
    else:
        lbl_logo.setText("●")
        lbl_logo.setStyleSheet("color:#E60000; font-size:28px; font-weight:bold;")
    logo_row.addWidget(lbl_logo)
    lbl_app = QLabel("MyWay Tools")
    lbl_app.setStyleSheet("color:#1A1A1A; font-size:18px; font-weight:bold;")
    logo_row.addWidget(lbl_app)
    logo_row.addStretch()
    lay.addLayout(logo_row)

    lbl_info = QLabel(f"Aggiornamento in corso:  {current}  →  {latest}")
    lbl_info.setStyleSheet("color:#555555; font-size:13px;")
    lay.addWidget(lbl_info)
    lay.addSpacing(4)

    progress = QProgressBar()
    progress.setRange(0, 100)
    progress.setValue(0)
    progress.setFixedHeight(8)
    lay.addWidget(progress)

    lbl_status = QLabel("Scaricamento in corso...")
    lbl_status.setStyleSheet("color:#999999; font-size:12px;")
    lay.addWidget(lbl_status)

    screen = app.primaryScreen().geometry()
    win.move(
        (screen.width()  - win.width())  // 2,
        (screen.height() - win.height()) // 2,
    )
    win.show()
    app.processEvents()
    return win, progress, lbl_status


def _mostra_notifica(app, current: str, latest: str) -> bool:
    """
    Popup che chiede all'utente se vuole aggiornare ora o più tardi.
    Restituisce True se l'utente clicca 'Aggiorna', False se 'Più tardi'.
    """
    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
    )
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QPixmap, QPainter, QColor, QPainterPath

    class _RoundedWidget(QWidget):
        def paintEvent(self_, event):
            painter = QPainter(self_)
            painter.setRenderHint(QPainter.Antialiasing)
            for i in range(10, 0, -1):
                painter.setBrush(QColor(0, 0, 0, 5 * i))
                painter.setPen(Qt.NoPen)
                painter.drawRoundedRect(self_.rect().adjusted(i, i, -i, -i), 14, 14)
            path = QPainterPath()
            path.addRoundedRect(float(10), float(10),
                                float(self_.width() - 20), float(self_.height() - 20),
                                12.0, 12.0)
            painter.setBrush(QColor("#FFFFFF"))
            painter.setPen(Qt.NoPen)
            painter.drawPath(path)

    scelta = {"valore": False}

    win = _RoundedWidget()
    win.setWindowTitle("MyWay Tools — Aggiornamento disponibile")
    win.setFixedSize(460, 260)
    win.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
    win.setAttribute(Qt.WA_TranslucentBackground)
    win.setStyleSheet("""
        QLabel  { background: transparent; }
        QPushButton {
            border-radius: 8px; font-size: 14px;
            font-weight: bold; padding: 10px 20px;
        }
    """)

    lay = QVBoxLayout(win)
    lay.setContentsMargins(40, 36, 40, 32)
    lay.setSpacing(12)

    # Barra rossa in cima
    barra = QWidget(win)
    barra.setGeometry(10, 10, 440, 6)
    barra.setStyleSheet("""
        background: #E60000;
        border-top-left-radius: 12px;
        border-top-right-radius: 12px;
    """)

    # Logo + titolo
    logo_row = QHBoxLayout()
    logo_row.setSpacing(12)
    icon_path = get_asset('logo.ico')
    lbl_logo = QLabel()
    if icon_path.exists():
        px = QPixmap(str(icon_path)).scaled(38, 38, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        lbl_logo.setPixmap(px)
    else:
        lbl_logo.setText("●")
        lbl_logo.setStyleSheet("color:#E60000; font-size:28px; font-weight:bold;")
    logo_row.addWidget(lbl_logo)
    lbl_app = QLabel("MyWay Tools")
    lbl_app.setStyleSheet("color:#1A1A1A; font-size:18px; font-weight:bold;")
    logo_row.addWidget(lbl_app)
    logo_row.addStretch()
    lay.addLayout(logo_row)

    # Testo
    lbl_titolo = QLabel("🎉  Nuova versione disponibile!")
    lbl_titolo.setStyleSheet("color:#1A1A1A; font-size:15px; font-weight:bold;")
    lay.addWidget(lbl_titolo)

    lbl_info = QLabel(f"Versione attuale:  <b>{current}</b>   →   Nuova versione:  <b>{latest}</b>")
    lbl_info.setStyleSheet("color:#555555; font-size:13px;")
    lay.addWidget(lbl_info)

    lbl_desc = QLabel("L'aggiornamento verrà installato automaticamente.\nL'app si chiuderà e si riaprirà una volta completato.")
    lbl_desc.setStyleSheet("color:#999999; font-size:12px;")
    lbl_desc.setWordWrap(True)
    lay.addWidget(lbl_desc)

    lay.addSpacing(6)

    # Bottoni
    btn_row = QHBoxLayout()
    btn_row.setSpacing(12)

    btn_dopo = QPushButton("Più tardi")
    btn_dopo.setStyleSheet("""
        QPushButton {
            background: #F5F5F5; color: #555555;
            border: 1px solid #E0E0E0;
        }
        QPushButton:hover { background: #EBEBEB; }
    """)
    btn_dopo.clicked.connect(lambda: win.close())

    btn_aggiorna = QPushButton("🔄  Aggiorna ora")
    btn_aggiorna.setStyleSheet("""
        QPushButton {
            background: #E60000; color: white; border: none;
        }
        QPushButton:hover { background: #CC0000; }
    """)
    btn_aggiorna.clicked.connect(lambda: (setattr(scelta, 'valore', True), win.close()))

    btn_row.addWidget(btn_dopo)
    btn_row.addWidget(btn_aggiorna)
    lay.addLayout(btn_row)

    screen = app.primaryScreen().geometry()
    win.move(
        (screen.width()  - win.width())  // 2,
        (screen.height() - win.height()) // 2,
    )
    win.show()

    # Aspetta che l'utente scelga
    from PySide6.QtCore import QEventLoop
    loop = QEventLoop()
    win.destroyed.connect(loop.quit)
    loop.exec()

    return scelta["valore"]


def check_and_update(app) -> bool:
    log_path = Path(sys.executable).parent / 'updater_debug.txt'

    try:
        response = requests.get(VERSION_URL, timeout=5)
        latest   = response.text.strip()
        current  = get_current_version()
        log_path.write_text(f"locale: {current}\ngithub: {latest}\n")

        if version.parse(latest) <= version.parse(current):
            return False

        if not _mostra_notifica(app, current, latest):
            return False

        win, progress, lbl_status = _mostra_download(app, current, latest)

        tmp_path  = Path(tempfile.gettempdir()) / "myway_update.exe"
        risultato = {"ok": False, "errore": None}

        def _download():
            try:
                r = requests.get(SETUP_URL, timeout=120, stream=True)
                # ← NUOVO: controlla che sia davvero un exe
                content_type = r.headers.get('content-type', '')
                if 'html' in content_type:
                    risultato["errore"] = f"GitHub ha restituito HTML invece di un exe. URL: {SETUP_URL}"
                    return
                total      = int(r.headers.get('content-length', 0))
                downloaded = 0
                with open(tmp_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total:
                            pct = int(downloaded / total * 100)
                            from PySide6.QtCore import QTimer
                            QTimer.singleShot(0, lambda p=pct: (
                                progress.setValue(p),
                                lbl_status.setText(f"Scaricamento...  {p}%")
                            ))
                # ← NUOVO: verifica dimensione minima (un exe valido > 100KB)
                if tmp_path.stat().st_size < 100_000:
                    risultato["errore"] = f"File scaricato troppo piccolo: {tmp_path.stat().st_size} bytes"
                    return
                risultato["ok"] = True
            except Exception as e:
                risultato["errore"] = str(e)

        thread = threading.Thread(target=_download, daemon=True)
        thread.start()

        while thread.is_alive():
            app.processEvents()
            thread.join(timeout=0.05)

        # ← NUOVO: mostra errore all'utente invece di fallire silenziosamente
        if not risultato["ok"]:
            errore_msg = risultato.get("errore", "Errore sconosciuto")
            log_path.write_text(log_path.read_text() + f"\nErrore download: {errore_msg}\n")
            lbl_status.setText(f"❌  Errore: {errore_msg}")
            progress.setValue(0)
            app.processEvents()
            import time; time.sleep(3)
            win.close()
            return False

        size_mb = tmp_path.stat().st_size / 1024 / 1024
        log_path.write_text(
            log_path.read_text() +
            f"File: {tmp_path}\nDimensione: {size_mb:.2f} MB\n"
        )

        lbl_status.setText("✅  Installazione in corso...")
        progress.setValue(100)
        app.processEvents()

        def _installa():
            try:
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
                        log_path.write_text(log_path.read_text() + f"Avviato: {new_exe}\n")
                    else:
                        log_path.write_text(log_path.read_text() + f"Exe non trovato in: {install_path}\n")
                except Exception as e:
                    log_path.write_text(log_path.read_text() + f"Errore avvio post-install: {e}\n")
            except Exception as e:
                log_path.write_text(log_path.read_text() + f"Errore installer: {e}\n")

        threading.Thread(target=_installa, daemon=False).start()
        import time; time.sleep(1)  # ← dai tempo al thread di partire prima di sys.exit
        sys.exit(0)

    except requests.exceptions.ConnectionError:
        log_path.write_text("Nessuna connessione\n")
    except Exception as e:
        import traceback
        log_path.write_text(f"Errore generale: {e}\n{traceback.format_exc()}\n")

    return False