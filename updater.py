# updater.py

import requests
import subprocess
import sys
import os
import tempfile
from packaging import version

# URL del tuo repo — modifica con il tuo username e nome repo
GITHUB_USER = "MyWay-stage"
GITHUB_REPO = "MyWay-Tools"

VERSION_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/main/version.txt"
SETUP_URL   = f"https://github.com/{GITHUB_USER}/{GITHUB_REPO}/releases/latest/download/setup.exe"

def get_current_version():
    """Legge la versione dal file locale version.txt accanto all'exe."""
    try:
        # Quando compilato con PyInstaller, i file sono accanto all'exe
        base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(base, 'version.txt')
        with open(path, 'r') as f:
            return f.read().strip()
    except Exception:
        return "0.0.0"

def check_and_update(parent_window=None):
    """
    Controlla se esiste una versione più nuova su GitHub.
    Se sì, scarica e avvia il nuovo setup.exe in modo silenzioso.
    parent_window: finestra tkinter da nascondere durante l'update (opzionale).
    """
    try:
        response = requests.get(VERSION_URL, timeout=5)
        latest   = response.text.strip()
        current  = get_current_version()

        if version.parse(latest) <= version.parse(current):
            return False  # nessun aggiornamento

        print(f"Aggiornamento disponibile: {current} → {latest}")

        # Scarica il nuovo installer nella cartella temp
        r = requests.get(SETUP_URL, timeout=60, stream=True)
        tmp_path = os.path.join(tempfile.gettempdir(), "myway_update.exe")

        with open(tmp_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

        # Nascondi la finestra se è stata passata
        if parent_window:
            parent_window.withdraw()

        # Avvia installer silenzioso e chiudi il programma
        subprocess.Popen([
            tmp_path,
            "/VERYSILENT",
            "/SUPPRESSMSGBOXES",
            "/NORESTART",
            "/CLOSEAPPLICATIONS",
        ])

        sys.exit(0)  # chiude l'app attuale, l'installer fa il resto

    except requests.exceptions.ConnectionError:
        pass  # nessuna connessione, va bene — continua normalmente
    except Exception as e:
        print(f"Errore update: {e}")

    return False