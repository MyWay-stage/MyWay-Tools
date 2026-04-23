# 📦 Applicazione Interna – README

## 🧩 Struttura della Repository

Questa repository contiene tutto il necessario per eseguire l’applicazione senza dover installare manualmente Python o dipendenze su ogni macchina.

### 📁 `runtime/`

Contiene:

* Interprete Python
* Librerie necessarie all’esecuzione

👉 Serve a rendere l’app completamente **portabile e indipendente dall’ambiente esterno**.

---

### 📁 `dist/`

Contiene:

* File `.exe` generato
* Tutti i file necessari all’esecuzione dell’applicazione

👉 È la cartella da utilizzare per avviare il programma.

---

### 📄 File `.spec`

Utilizzato da PyInstaller per definire:

* Configurazione del build
* Inclusione file e dipendenze
* Parametri di compilazione

---

## ▶️ Esecuzione dell’applicazione

Per avviare l’app:

1. Accedere alla cartella `dist/`
2. Eseguire il file `.exe`

Non è richiesta alcuna installazione aggiuntiva.

---

## 🔗 Funzionamento del Pannello di Controllo

Il pannello di controllo non contiene localmente tutti gli script, ma li recupera dinamicamente da:

👉 **Repository “MyWay Tools” su Teams**

Questo permette di:

* Aggiornare gli script centralmente
* Evitare ridistribuzioni dell’eseguibile
* Mantenere il sistema sempre aggiornato

---

## ⚙️ Note

* L’applicazione è destinata ad uso interno
* Richiede accesso alla repository su Teams per il corretto funzionamento degli script
* Eventuali modifiche agli script vengono riflesse automaticamente al successivo utilizzo

---

## 🛠️ Build

La build dell’eseguibile è effettuata tramite PyInstaller utilizzando il file `.spec`.

---
