#!/usr/bin/env python3
"""
IG2mp3 - Scarica gli audio dei Reels in batch con un'interfaccia semplice.
Funziona sia su Windows che su macOS (e Linux) grazie a Python + Tkinter + yt-dlp.
"""

from __future__ import annotations

import os
import queue
import shutil
import subprocess
import sys
import threading
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, ttk
from typing import List

import yt_dlp


APP_TITLE = "IG2mp3 – Batch Reels Audio Downloader"
DOWNLOAD_SUBDIR = "downloads"
QUEUE_POLL_MS = 120


class ReelsDownloaderApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title(APP_TITLE)
        self.root.minsize(720, 520)

        self.messages: queue.Queue = queue.Queue()
        self.worker: threading.Thread | None = None
        self.is_downloading = False

        default_dir = self._default_download_dir()
        self.output_dir = tk.StringVar(value=str(default_dir))

        self._build_ui()
        self.root.after(QUEUE_POLL_MS, self._drain_queue)

    # ------------------------------------------------------------------ UI
    def _build_ui(self) -> None:
        pad = {"padx": 12, "pady": 8}

        header = ttk.Label(
            self.root,
            text="Incolla uno o più link di Reels e ottieni gli MP3 in locale.",
            font=("Segoe UI", 12, "bold"),
        )
        header.pack(anchor="w", **pad)

        desc = ttk.Label(
            self.root,
            text=("Ogni link va su una riga separata. Puoi importare un file .txt "
                  "con i link oppure incollarli manualmente."),
            wraplength=660,
        )
        desc.pack(anchor="w", padx=12, pady=(0, 10))

        urls_label = ttk.Label(self.root, text="Link dei Reels:")
        urls_label.pack(anchor="w", padx=12)

        self.urls_box = scrolledtext.ScrolledText(self.root, height=8, wrap="word")
        self.urls_box.pack(fill="both", expand=False, padx=12, pady=(0, 10))

        actions_frame = ttk.Frame(self.root)
        actions_frame.pack(fill="x", padx=12)

        import_btn = ttk.Button(actions_frame, text="Importa da file…", command=self._import_urls)
        import_btn.pack(side="left")

        choose_btn = ttk.Button(actions_frame, text="Scegli cartella output…", command=self._choose_output_dir)
        choose_btn.pack(side="left", padx=(8, 0))

        open_btn = ttk.Button(actions_frame, text="Apri cartella", command=self._open_output_dir)
        open_btn.pack(side="left", padx=(8, 0))

        ttk.Label(actions_frame, text="Cartella attuale:").pack(side="left", padx=(16, 4))
        self.output_entry = ttk.Entry(actions_frame, textvariable=self.output_dir)
        self.output_entry.pack(side="left", fill="x", expand=True)

        self.start_btn = ttk.Button(
            self.root, text="Avvia download", command=self._start_downloads
        )
        self.start_btn.pack(pady=(12, 6))

        self.status_label = ttk.Label(self.root, text="In attesa di input…")
        self.status_label.pack(anchor="w", padx=12)

        log_label = ttk.Label(self.root, text="Log operazioni:")
        log_label.pack(anchor="w", padx=12, pady=(12, 0))

        self.log_box = scrolledtext.ScrolledText(self.root, state="disabled", height=12, wrap="word")
        self.log_box.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    # ------------------------------------------------------------------ actions
    def _import_urls(self) -> None:
        filepath = filedialog.askopenfilename(
            title="Seleziona un file con i link",
            filetypes=(("File di testo", "*.txt"), ("Tutti i file", "*.*")),
        )
        if not filepath:
            return

        try:
            content = Path(filepath).read_text(encoding="utf-8")
        except Exception as exc:  # pragma: no cover - UI feedback
            messagebox.showerror("Errore", f"Impossibile leggere il file:\n{exc}")
            return

        if content:
            current = self.urls_box.get("1.0", "end").strip()
            merged = f"{current}\n{content}".strip() if current else content.strip()
            self.urls_box.delete("1.0", "end")
            self.urls_box.insert("1.0", merged)
            self._log(f"Importati {len(content.splitlines())} link dal file selezionato.")

    def _choose_output_dir(self) -> None:
        chosen = filedialog.askdirectory(title="Seleziona la cartella di destinazione")
        if chosen:
            self.output_dir.set(chosen)
            Path(chosen).mkdir(parents=True, exist_ok=True)
            self._log(f"Cartella impostata su: {chosen}")

    def _open_output_dir(self) -> None:
        target = Path(self.output_dir.get()).expanduser()
        target.mkdir(parents=True, exist_ok=True)
        try:
            if os.name == "nt":
                os.startfile(str(target))  # type: ignore[attr-defined]
            elif sys.platform == "darwin":  # pragma: no cover - platform specific
                subprocess.run(["open", str(target)], check=False)
            else:
                subprocess.run(["xdg-open", str(target)], check=False)
        except Exception as exc:  # pragma: no cover - UI feedback
            messagebox.showwarning("Attenzione", f"Impossibile aprire la cartella:\n{exc}")

    def _start_downloads(self) -> None:
        if self.is_downloading:
            messagebox.showinfo("In corso", "Un download è già attivo, attendi il termine.")
            return

        urls = self._collect_urls(self.urls_box.get("1.0", "end"))
        if not urls:
            messagebox.showinfo("Nessun link", "Inserisci almeno un link valido.")
            return

        out_dir = Path(self.output_dir.get()).expanduser()
        out_dir.mkdir(parents=True, exist_ok=True)

        self.is_downloading = True
        self.start_btn.config(state="disabled")
        self.status_label.config(text="Download in corso…")
        self._log(f"Avvio download per {len(urls)} link.")

        self.worker = threading.Thread(
            target=self._download_batch, args=(urls, out_dir), daemon=True
        )
        self.worker.start()

    # ------------------------------------------------------------------ download logic
    def _download_batch(self, urls: List[str], out_dir: Path) -> None:
        ffmpeg_ready = self._ffmpeg_available()
        if not ffmpeg_ready:
            self.messages.put(("log", "⚠️ FFmpeg non rilevato: verrà scaricato l'audio originale senza conversione in MP3."))

        success, failures = 0, 0
        total = len(urls)

        for idx, url in enumerate(urls, start=1):
            self.messages.put(("status", f"[{idx}/{total}] Elaborazione in corso…"))
            try:
                ydl_opts = self._build_ydl_opts(out_dir, ffmpeg_ready)
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                success += 1
                self.messages.put(("log", f"✅ Audio salvato per: {url}"))
            except Exception as exc:  # pragma: no cover - network errors
                failures += 1
                self.messages.put(("log", f"❌ Errore con {url}: {exc}"))

        self.messages.put(("done", (success, failures)))

    def _build_ydl_opts(self, out_dir: Path, ffmpeg_ready: bool) -> dict:
        filename_template = out_dir / "%(uploader)s - %(title).80s [%(id)s].%(ext)s"
        postprocessors = []
        if ffmpeg_ready:
            postprocessors.append(
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            )

        return {
            "format": "bestaudio/best",
            "outtmpl": str(filename_template),
            "quiet": True,
            "noprogress": True,
            "nocheckcertificate": True,
            "concurrent_fragment_downloads": 1,
            "postprocessors": postprocessors,
            "cachedir": False,
            "restrictfilenames": True,
            "windowsfilenames": True,
        }

    # ------------------------------------------------------------------ helpers
    def _collect_urls(self, raw: str) -> List[str]:
        rows = [line.strip() for line in raw.splitlines()]
        return [row for row in rows if row.startswith("http")]

    def _default_download_dir(self) -> Path:
        base = Path.cwd() / DOWNLOAD_SUBDIR
        base.mkdir(exist_ok=True)
        return base

    def _ffmpeg_available(self) -> bool:
        return shutil.which("ffmpeg") is not None

    def _log(self, message: str) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.messages.put(("log", f"[{timestamp}] {message}"))

    def _drain_queue(self) -> None:
        try:
            while True:
                event, payload = self.messages.get_nowait()
                if event == "log":
                    self._append_log(payload)
                elif event == "status":
                    self.status_label.config(text=payload)
                elif event == "done":
                    success, failures = payload
                    summary = f"Completato. Successi: {success}, errori: {failures}."
                    self.status_label.config(text=summary)
                    self._append_log(summary)
                    self.start_btn.config(state="normal")
                    self.is_downloading = False
        except queue.Empty:
            pass
        finally:
            self.root.after(QUEUE_POLL_MS, self._drain_queue)

    def _append_log(self, message: str) -> None:
        self.log_box.configure(state="normal")
        self.log_box.insert("end", f"{message}\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")


def main() -> None:
    root = tk.Tk()
    app = ReelsDownloaderApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
