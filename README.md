# IG2mp3 – Batch Reels Audio Downloader

Applicazione desktop multipiattaforma (Windows, macOS e Linux) che permette di:

- incollare o importare un elenco di link di Reels/Shorts (uno per riga);
- scaricare automaticamente solo l'audio tramite `yt-dlp`;
- convertire in MP3 (se è disponibile `ffmpeg`);
- salvare tutto nella cartella scelta con un'interfaccia semplice costruita in Tkinter.

## Requisiti

- Python 3.10 o superiore.
- `pip` aggiornato.
- [ffmpeg](https://ffmpeg.org/download.html) per ottenere file MP3 (senza ffmpeg verrà salvato il formato audio originale).

Suggerimenti di installazione rapida di ffmpeg:

- **Windows**: `winget install --id=Gyan.FFmpeg.Full -e --source=winget`
- **macOS**: `brew install ffmpeg`

## Setup rapido

```bash
git clone <repo-url> ig2mp3
cd ig2mp3
python -m venv .venv
source .venv/bin/activate  # su Windows: .venv\Scripts\activate
pip install -r requirements.txt
python reels_audio_box.py
```

Se preferisci evitare ambienti virtuali, puoi anche usare `pipx run pip install -r requirements.txt`.

## Uso dell'interfaccia

1. Inserisci i link in textarea (uno per riga) oppure premi **Importa da file** per caricare un `.txt`.
2. (Opzionale) scegli la cartella di destinazione con **Scegli cartella output**.
3. Premi **Avvia download**: l'app mostrerà lo stato corrente e il log in tempo reale.
4. Al termine, utilizza **Apri cartella** per raggiungere rapidamente gli MP3 scaricati.

Il file di log riporta eventuali errori (link non valido, credenziali richieste, ecc.). I nomi dei file includono uploader, titolo e ID per evitare duplicati.

## Creare un eseguibile (opzionale)

Per avere un `.exe`/`.app` distribuitile senza dipendenze esterne puoi usare [PyInstaller](https://pyinstaller.org):

```bash
pip install pyinstaller
pyinstaller reels_audio_box.py --name IG2mp3 --noconsole --onefile
```

Troverai il binario dentro `dist/IG2mp3`. Ricorda di includere `ffmpeg.exe` (Windows) o installarlo sul sistema di destinazione.

## Risoluzione problemi

- **Il download fallisce**: assicurati che il link sia pubblico e di avere l'ultima versione di `yt-dlp` (`python -m pip install --upgrade yt-dlp`).
- **Manca ffmpeg**: l'app salva comunque l'audio originale, ma mostra un avviso nel log.
- **Blocchi o freeze**: la GUI rimane di base reattiva; se il download sembra fermo, controlla l'output nella sezione log.

Buon divertimento! Per richieste o miglioramenti, apri una issue o invia una pull request.