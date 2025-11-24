# IG2mp3 – Batch Reels Audio Downloader

IG2mp3 is a tiny desktop tool (Windows, macOS, Linux) for people who just want to paste a bunch of Reels / Shorts links and grab the audio tracks. The app uses `yt-dlp` behind the scenes, exposes an easy Tkinter interface, and can optionally convert everything to MP3 when `ffmpeg` is present.

---

## 1. System requirements

- **Python 3.10+** – download from [python.org/downloads](https://www.python.org/downloads/).  
  - Windows installer tip: during setup, tick *"Add python.exe to PATH"* before clicking *Install Now*.
- **pip** – already bundled with modern Python; you can update it later with `python -m pip install --upgrade pip`.
- **ffmpeg** – converts audio to MP3. Without it you still get the original audio format (M4A/WEBM).
  - Windows (PowerShell or Command Prompt): `winget install --id=Gyan.FFmpeg.Full -e --source=winget`
  - macOS (Terminal with Homebrew): `brew install ffmpeg`
  - Linux: use your package manager, e.g. `sudo apt install ffmpeg`

You also need a working internet connection because the tool downloads media directly from Meta’s or YouTube’s servers.

---

## 2. Downloading the project

1. Open a terminal:
   - Windows: press `Win`, type **cmd** (or **PowerShell**) and hit Enter.
   - macOS: open **Terminal** from Spotlight.
   - Linux: any terminal emulator works.
2. Choose a folder where you want the project (for example `Documents`) and run:

```bash
git clone <repo-url> ig2mp3
cd ig2mp3
```

If you don’t have Git, download the ZIP from your repo hosting service, unzip it, and open the extracted folder in your terminal or file explorer.

---

## 2.5 Windows quick start (no execution-policy issues)

PowerShell may block the `Activate.ps1` script if your company PC enforces a strict policy. Two easy alternatives:

### Option A – Double-click helper

1. Open File Explorer inside the IG2mp3 folder.
2. Double-click `run_windows.bat` (or right-click → *Run as administrator* if required).
3. Wait while the script creates `.venv`, installs dependencies, and launches the GUI.  
   - The terminal window must stay open; close the GUI to stop the script.
4. Next time, just run `run_windows.bat` again; it reuses the same environment.

The `.bat` file uses only classic Command Prompt commands (`cmd.exe`), so PowerShell policies no longer apply.

### Option B – Manual commands without activating the venv

Run these in **Command Prompt** (not PowerShell) from the IG2mp3 folder:

```cmd
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe reels_audio_box.py
```

By calling `.venv\Scripts\python.exe` directly, you never have to run `activate.bat` or `Activate.ps1`, so no policy prompts appear.

---

## 3. Step-by-step installation (friendly version)

> The steps below use a Python virtual environment so that IG2mp3 stays isolated from your other tools. You can skip the venv if you know what you’re doing, but beginners should keep it.

1. **Create the virtual environment**
   - Windows:
     ```bash
     python -m venv .venv
     .\.venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```
   When the environment is active you should see `(.venv)` at the beginning of your terminal prompt.

2. **Install the required Python packages**
   ```bash
   pip install -r requirements.txt
   ```
   This will download `yt-dlp` (the downloader) and any of its dependencies.

3. **(Optional) update yt-dlp regularly**
   ```bash
   python -m pip install --upgrade yt-dlp
   ```
   Reels’ internal APIs change often; keeping yt-dlp up-to-date avoids many download errors.

4. **Launch the graphical app**
   ```bash
   python reels_audio_box.py
   ```
   A window titled “IG2mp3 – Batch Reels Audio Downloader” should appear. Keep the terminal open while the GUI runs.

Whenever you come back in the future:

```bash
cd ig2mp3
source .venv/bin/activate      # Windows: .\.venv\Scripts\activate
python reels_audio_box.py
```

---

## 4. Using the interface (slow and clear)

1. **Paste or import links**  
   - Type/paste each Reel URL on a separate line, or click **Import from file…** to load a `.txt` file (one link per line).

2. **Choose where the MP3s go**  
   - The app defaults to a `downloads` folder inside the project.  
   - Click **Choose output folder…** if you prefer Desktop, Documents, an external drive, etc.  
   - Click **Open folder** anytime to open the current directory in Explorer/Finder.

3. **Start**  
   - Press **Start download**. The button disables itself while the background worker processes each link to keep the window responsive.

4. **Watch the log**  
   - The log area shows timestamps, progress updates (e.g. `[2/5] Processing…`), success ticks, and error messages if a link fails.

5. **What to expect**  
   - Files are named `Uploader - Title [ID].mp3`. If `ffmpeg` is missing they will have the original extension (e.g. `.m4a`).  
   - When everything finishes, the status bar shows a summary like `Completed. Success: 4, failures: 1.` and the button re-enables.

---

## 5. Creating a single-file app (optional)

If you want an `.exe` or `.app` to give to friends without Python:

```bash
pip install pyinstaller
pyinstaller reels_audio_box.py --name IG2mp3 --noconsole --onefile
```

- The standalone file appears in `dist/IG2mp3` (Windows creates `IG2mp3.exe`).  
- Distribute `ffmpeg.exe` alongside it or tell users to install ffmpeg themselves.  
- On macOS you may need to notarize or right-click → Open the first time because of Gatekeeper.

---

## 6. Troubleshooting tips

- **“ERROR: … not available”** – The link may be private or requires login. Only public Reels/Shorts work out of the box.  
- **“ffmpeg not found” warning** – Install ffmpeg using the commands in section 1. The app still downloads audio, but in whatever format the platform served.  
- **The GUI seems frozen** – Large downloads can take time, but the log should continue updating. If it truly stops, close the window and relaunch; the partially-downloaded file is safe to delete.  
- **Antivirus blocks the download** – On Windows, allow Python/yt-dlp through your firewall if prompted.  
- **Want to reset everything** – Delete the `downloads` folder and the `.venv` directory, then repeat the setup steps above.

Need help? Open an issue or PR with a clear description of the problem and the exact message from the log output.