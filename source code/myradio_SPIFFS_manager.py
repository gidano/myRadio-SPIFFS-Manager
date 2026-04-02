#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import base64
import sys
import threading
import time
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

try:
    import serial
    from serial.tools import list_ports
except Exception:
    serial = None
    list_ports = None

APP_VERSION = "1.2"
DEFAULT_BAUDRATE = 460800
CHUNK_SIZE = 512
MAX_AUTO_RETRIES = 2


TEXT = {
    "HU": {
        "title": "myRadio SPIFFS Manager",
        "port": "COM port",
        "refresh_ports": "Portok frissítése",
        "connect": "Kapcsolódás",
        "disconnect": "Kapcsolat bontása",
        "maintenance": "Karbantartó mód indítása",
        "backup": "Teljes mentés (ZIP)",
        "restore": "Mentés visszaállítása",
        "list": "Fájllista frissítése",
        "delete": "Kijelölt törlése",
        "upload_files": "Fájlok queue-ba",
        "upload_folder": "Mappa queue-ba",
        "download": "Kijelölt mentése",
        "reboot": "Rádió újraindítása",
        "lang": "Nyelv: HU / EN",
        "tree": "A rádió SPIFFS tartalma",
        "type": "Típus",
        "size": "Méret",
        "status_ready": "Készen.",
        "status_connecting": "Kapcsolódás folyamatban...",
        "status_maintenance": "Karbantartó mód indítása...",
        "status_listing": "Fájllista frissítése...",
        "status_saving": "Mentés folyamatban...",
        "status_restoring": "Visszaállítás folyamatban...",
        "status_verifying": "Ellenőrzés folyamatban...",
        "status_uploading": "Feltöltés folyamatban...",
        "status_deleting": "Törlés folyamatban...",
        "status_downloading": "Mentés a számítógépre...",
        "status_rebooting": "Újraindítás kérése...",
        "target_folder": "célmappa",
        "connect_first": "Előbb csatlakozz a rádióhoz.",
        "error": "Hiba",
        "warning": "Figyelmeztetés",
        "done": "Kész",
        "saved": "Mentve",
        "maintenance_ok": "Karbantartó mód aktív.",
        "ports_none": "Nincs találat",
        "pyserial_missing": "A pyserial nincs telepítve.\nParancs: python -m pip install pyserial",
        "tree_no_selection": "Jelölj ki egy fájlt vagy mappát.",
        "backup_done": "A teljes mentés elkészült.",
        "restore_done": "A visszaállítás elkészült.",
        "download_done": "A kijelölt fájl mentése elkészült.",
        "upload_done": "A feltöltés elkészült.",
        "delete_done": "A törlés elkészült.",
        "reboot_done": "Az újraindítás kérése elküldve.",
        "no_files": "Nincs fájl a rádión.",
        "empty_folder": "A kiválasztott mappa üres.",
        "folder": "mappa",
        "file": "fájl",
        "queue": "Feltöltési queue",
        "queue_name": "Név",
        "queue_target": "Cél",
        "queue_status": "Állapot",
        "queue_progress": "Folyamat",
        "queue_size": "Méret",
        "queue_add_files": "Fájlok hozzáadása",
        "queue_add_folder": "Mappa hozzáadása",
        "queue_start": "Queue indítása",
        "queue_cancel": "Megszakítás",
        "queue_retry": "Hibásak újra",
        "queue_remove": "Kijelölt eltávolítása",
        "queue_clear_done": "Készek törlése",
        "queue_idle": "A queue üres.",
        "queue_waiting": "Várakozik",
        "queue_uploading": "Feltöltés",
        "queue_done": "Kész",
        "queue_failed": "Hibás",
        "queue_cancelled": "Megszakítva",
        "queue_retrying": "Újrapróba",
        "queue_running": "A queue fut.",
        "queue_added": "A fájlok bekerültek a queue-ba.",
        "queue_cancel_requested": "Megszakítás kérve...",
        "queue_finished": "Queue kész.",
        "queue_empty_start": "Nincs feltöltendő elem a queue-ban.",
        "queue_file": "Aktuális fájl",
        "queue_overall": "Összesen",
        "queue_speed": "Sebesség",
        "queue_eta": "Hátralévő idő",
        "queue_index": "Fájl",
        "queue_failures": "Hibák",
        "queue_cancelled_done": "A queue megszakadt.",
        "last_step": "Utolsó művelet",
        "save_selected_title": "Fájl mentése",
        "save_backup_title": "Mentés mentése ZIP fájlba",
        "open_backup_title": "Mentés kiválasztása",
        "footer": "© 2026 gidano",
    },
    "EN": {
        "title": "myRadio SPIFFS Manager",
        "port": "COM port",
        "refresh_ports": "Refresh ports",
        "connect": "Connect",
        "disconnect": "Disconnect",
        "maintenance": "Start maintenance mode",
        "backup": "Full backup (ZIP)",
        "restore": "Restore backup",
        "list": "Refresh file list",
        "delete": "Delete selected",
        "upload_files": "Add files to queue",
        "upload_folder": "Add folder to queue",
        "download": "Save selected",
        "reboot": "Reboot radio",
        "lang": "Language: HU / EN",
        "tree": "Radio SPIFFS contents",
        "type": "Type",
        "size": "Size",
        "status_ready": "Ready.",
        "status_connecting": "Connecting...",
        "status_maintenance": "Starting maintenance mode...",
        "status_listing": "Refreshing file list...",
        "status_saving": "Saving backup...",
        "status_restoring": "Restoring backup...",
        "status_verifying": "Verifying...",
        "status_uploading": "Uploading...",
        "status_deleting": "Deleting...",
        "status_downloading": "Saving to computer...",
        "status_rebooting": "Requesting reboot...",
        "target_folder": "target folder",
        "connect_first": "Connect to the radio first.",
        "error": "Error",
        "warning": "Warning",
        "done": "Done",
        "saved": "Saved",
        "maintenance_ok": "Maintenance mode is active.",
        "ports_none": "No ports found",
        "pyserial_missing": "pyserial is not installed.\nCommand: python -m pip install pyserial",
        "tree_no_selection": "Select a file or folder.",
        "backup_done": "Full backup completed.",
        "restore_done": "Restore completed.",
        "download_done": "Selected file saved.",
        "upload_done": "Upload completed.",
        "delete_done": "Delete completed.",
        "reboot_done": "Reboot requested.",
        "no_files": "There are no files on the radio.",
        "empty_folder": "The selected folder is empty.",
        "folder": "folder",
        "file": "file",
        "queue": "Upload queue",
        "queue_name": "Name",
        "queue_target": "Target",
        "queue_status": "Status",
        "queue_progress": "Progress",
        "queue_size": "Size",
        "queue_add_files": "Add files",
        "queue_add_folder": "Add folder",
        "queue_start": "Start queue",
        "queue_cancel": "Cancel",
        "queue_retry": "Retry failed",
        "queue_remove": "Remove selected",
        "queue_clear_done": "Clear completed",
        "queue_idle": "The queue is empty.",
        "queue_waiting": "Waiting",
        "queue_uploading": "Uploading",
        "queue_done": "Done",
        "queue_failed": "Failed",
        "queue_cancelled": "Cancelled",
        "queue_retrying": "Retrying",
        "queue_running": "The queue is running.",
        "queue_added": "Files added to queue.",
        "queue_cancel_requested": "Cancel requested...",
        "queue_finished": "Queue finished.",
        "queue_empty_start": "There is nothing in the upload queue.",
        "queue_file": "Current file",
        "queue_overall": "Overall",
        "queue_speed": "Speed",
        "queue_eta": "ETA",
        "queue_index": "File",
        "queue_failures": "Failures",
        "queue_cancelled_done": "Queue cancelled.",
        "last_step": "Last step",
        "save_selected_title": "Save file",
        "save_backup_title": "Save backup ZIP",
        "open_backup_title": "Choose backup ZIP",
        "footer": "© 2026 gidano",
    },
}


def normalize_remote_path(path: str) -> str:
    path = (path or "").replace("\\", "/")
    while "//" in path:
        path = path.replace("//", "/")
    if not path.startswith("/"):
        path = "/" + path
    return path


def format_eta(seconds: float | None) -> str:
    if seconds is None or seconds < 0 or seconds == float("inf"):
        return "--:--"
    sec = int(seconds)
    m, s = divmod(sec, 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h:d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def human_speed(bytes_per_sec: float) -> str:
    if bytes_per_sec <= 0:
        return "0 KB/s"
    kb = bytes_per_sec / 1024.0
    if kb < 1024:
        return f"{kb:.1f} KB/s"
    return f"{kb / 1024.0:.2f} MB/s"


def fmt_size(size: int) -> str:
    value = float(size)
    for unit in ("B", "KB", "MB"):
        if value < 1024 or unit == "MB":
            if unit == "B":
                return f"{int(value)} {unit}"
            return f"{value:.1f} {unit}"
        value /= 1024
    return f"{size} B"


def set_windows_app_id():
    try:
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("gidano.myRadio.SPIFFS.Kezelo")
    except Exception:
        pass


def get_app_icon_path() -> str | None:
    candidates = []
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        candidates.append(Path(meipass) / "icon.ico")
    try:
        candidates.append(Path(sys.executable).resolve().parent / "icon.ico")
    except Exception:
        pass
    try:
        candidates.append(Path(__file__).resolve().parent / "icon.ico")
    except Exception:
        pass
    for p in candidates:
        if p.exists():
            return str(p)
    return None


def is_windows_dark_mode():
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
        )
        value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
        return value == 0
    except Exception:
        return False


def apply_dark_title_bar(window):
    try:
        import ctypes
        hwnd = ctypes.windll.user32.GetParent(window.winfo_id())
        value = ctypes.c_int(1)
        for attr in (20, 19):
            try:
                ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, attr, ctypes.byref(value), ctypes.sizeof(value))
            except Exception:
                pass
    except Exception:
        pass


def apply_theme(root: tk.Tk, dark: bool):
    style = ttk.Style(root)
    if dark:
        try:
            style.theme_use("clam")
        except Exception:
            pass
        bg = "#1e1e1e"
        panel = "#252526"
        fg = "#ffffff"
        edge = "#6f6f6f"
        select = "#3a3d41"
        root.configure(bg=bg)
        style.configure(".", background=bg, foreground=fg)
        style.configure("TFrame", background=bg)
        style.configure("TLabelframe", background=bg, foreground=fg)
        style.configure("TLabelframe.Label", background=bg, foreground=fg)
        style.configure("TLabel", background=bg, foreground=fg)
        style.configure("TButton", background=panel, foreground=fg, bordercolor=edge, focusthickness=1, focuscolor=edge)
        style.map("TButton", background=[("active", "#2f3136"), ("pressed", "#2a2d31")], foreground=[("disabled", "#8a8a8a")])
        style.configure("TCombobox", fieldbackground=panel, background=panel, foreground=fg, arrowcolor=fg, bordercolor=edge, lightcolor=edge, darkcolor=edge)
        style.map("TCombobox", fieldbackground=[("readonly", panel)], selectbackground=[("readonly", select)], selectforeground=[("readonly", fg)])
        style.configure("Treeview", background=panel, fieldbackground=panel, foreground=fg, bordercolor=edge, lightcolor=edge, darkcolor=edge)
        style.configure("Treeview.Heading", background="#2d2d30", foreground=fg, bordercolor=edge, lightcolor=edge, darkcolor=edge)
        style.map("Treeview", background=[("selected", select)], foreground=[("selected", fg)])
        style.map("Treeview.Heading", background=[("active", "#383b40")])
        style.configure("Horizontal.TProgressbar", troughcolor=panel, background="#6aa2ff", bordercolor=edge, lightcolor=edge, darkcolor=edge)
        style.configure("Vertical.TScrollbar", background=panel, troughcolor=bg, arrowcolor=fg, bordercolor=edge, lightcolor=edge, darkcolor=edge)
        style.configure("Horizontal.TScrollbar", background=panel, troughcolor=bg, arrowcolor=fg, bordercolor=edge, lightcolor=edge, darkcolor=edge)
    else:
        try:
            style.theme_use("vista")
        except Exception:
            pass


class ProtoError(RuntimeError):
    pass


@dataclass
class RemoteFile:
    path: str
    size: int


@dataclass
class UploadTask:
    local_path: Path
    remote_path: str
    size: int
    status: str = "waiting"
    progress_pct: float = 0.0
    uploaded_bytes: int = 0
    retries_done: int = 0
    max_retries: int = MAX_AUTO_RETRIES
    error: str = ""
    task_id: str = field(default_factory=lambda: f"task-{time.time_ns()}")


class SerialSpiFFSClient:
    def __init__(self):
        self.ser = None
        self.debug_lines: list[str] = []

    def connect(self, port: str, baudrate: int = DEFAULT_BAUDRATE, timeout: float = 0.8):
        if serial is None:
            raise ProtoError("pyserial not installed")

        tmp = serial.Serial()
        tmp.port = port
        tmp.baudrate = baudrate
        tmp.timeout = timeout
        tmp.write_timeout = 20
        try:
            tmp.dtr = False
            tmp.rts = False
        except Exception:
            pass
        tmp.open()
        self.ser = tmp

        time.sleep(1.7)
        self.light_drain(0.6)

    def disconnect(self):
        if self.ser:
            try:
                self.ser.close()
            finally:
                self.ser = None

    def light_drain(self, duration: float = 0.25):
        if not self.ser:
            return
        end = time.time() + duration
        while time.time() < end:
            raw = self.ser.readline()
            if not raw:
                continue
            line = raw.decode("utf-8", errors="ignore").strip()
            if line:
                self.debug_lines.append(line)
                self.debug_lines = self.debug_lines[-20:]

    def clear_input(self):
        if not self.ser:
            return
        try:
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()
        except Exception:
            pass
        self.light_drain(0.15)

    def _write_line(self, line: str):
        if not self.ser:
            raise ProtoError("not connected")
        self.ser.write((line + "\n").encode("utf-8"))
        self.ser.flush()
        self.debug_lines.append(f">>> {line}")
        self.debug_lines = self.debug_lines[-20:]

    def _read_proto_line(self, timeout: float = 15.0) -> str:
        if not self.ser:
            raise ProtoError("not connected")
        end = time.time() + timeout
        last_noise = ""
        while time.time() < end:
            raw = self.ser.readline()
            if not raw:
                continue
            line = raw.decode("utf-8", errors="ignore").strip()
            if not line:
                continue
            self.debug_lines.append(line)
            self.debug_lines = self.debug_lines[-20:]
            if not line.startswith("MRSPIFS|"):
                last_noise = line
                continue
            return line[len("MRSPIFS|"):]
        if last_noise:
            raise ProtoError(f"protocol timeout (last serial: {last_noise[:120]})")
        raise ProtoError("protocol timeout")

    def begin_maintenance(self):
        for _ in range(14):
            self._write_line("MRSPIFS:BEGIN")
            try:
                line = self._read_proto_line(timeout=2.8)
            except ProtoError:
                time.sleep(0.25)
                continue
            parts = line.split("|")
            if len(parts) >= 2 and parts[0] == "OK" and parts[1] == "BEGIN":
                return True
            raise ProtoError("unexpected BEGIN reply: " + line)
        raise ProtoError("could not enter maintenance mode")

    def ping(self):
        self._write_line("PING")
        parts = self._read_proto_line(timeout=5.0).split("|")
        if len(parts) >= 2 and parts[0] == "OK" and parts[1] == "PING":
            return True
        raise ProtoError("bad PING reply")

    def abort_write(self):
        self._write_line("WRITE_ABORT")
        parts = self._read_proto_line(timeout=5.0).split("|")
        if not (len(parts) >= 2 and parts[0] == "OK" and parts[1] == "WRITE_ABORT"):
            raise ProtoError("bad WRITE_ABORT reply: " + "|".join(parts))

    def ensure_idle(self):
        try:
            self.abort_write()
        except Exception:
            self.clear_input()

    def list_files(self) -> list[RemoteFile]:
        self._write_line("LIST")
        files = []
        while True:
            parts = self._read_proto_line(timeout=20.0).split("|")
            if not parts:
                continue
            if parts[0] == "FILE" and len(parts) >= 3:
                try:
                    files.append(RemoteFile(parts[1], int(parts[2])))
                except ValueError:
                    pass
            elif parts[0] == "OK" and len(parts) >= 2 and parts[1] == "LIST":
                break
            elif parts[0] == "ERR":
                raise ProtoError("|".join(parts))
        return sorted(files, key=lambda x: x.path.lower())

    def read_file(self, path: str) -> bytes:
        path = normalize_remote_path(path)
        self._write_line(f"READ|PATH|{path}")
        out = bytearray()
        while True:
            parts = self._read_proto_line(timeout=20.0).split("|")
            if not parts:
                continue
            if parts[0] == "READ_BEGIN":
                continue
            if parts[0] == "DATA" and len(parts) >= 2:
                out.extend(base64.b64decode(parts[1]))
                continue
            if parts[0] == "OK" and len(parts) >= 2 and parts[1] == "READ_END":
                return bytes(out)
            if parts[0] == "ERR":
                raise ProtoError("|".join(parts))

    def write_file(self, path: str, data: bytes):
        path = normalize_remote_path(path)
        last_err = None
        for attempt in range(1, 4):
            try:
                self.ensure_idle()
                self._write_line(f"WRITE_BEGIN|PATH|{path}|{len(data)}")
                parts = self._read_proto_line(timeout=25.0).split("|")
                if not (len(parts) >= 2 and parts[0] == "OK" and parts[1] == "WRITE_BEGIN"):
                    raise ProtoError("bad WRITE_BEGIN reply: " + "|".join(parts))

                total_chunks = max(1, (len(data) + CHUNK_SIZE - 1) // CHUNK_SIZE)
                uploaded = 0
                if not data:
                    total_chunks = 1
                for idx, i in enumerate(range(0, len(data), CHUNK_SIZE), 1):
                    chunk = data[i:i + CHUNK_SIZE]
                    b64 = base64.b64encode(chunk).decode("ascii")
                    self._write_line(f"WRITE_DATA|B64|{b64}")
                    parts = self._read_proto_line(timeout=25.0).split("|")
                    if not (len(parts) >= 2 and parts[0] == "OK" and parts[1] == "WRITE_DATA"):
                        raise ProtoError(f"bad WRITE_DATA reply at chunk {idx}/{total_chunks} for {path}: " + "|".join(parts))
                    uploaded += len(chunk)
                    yield idx, total_chunks, uploaded
                if len(data) == 0:
                    yield 1, 1, 0
                self._write_line("WRITE_END")
                parts = self._read_proto_line(timeout=25.0).split("|")
                if not (len(parts) >= 2 and parts[0] == "OK" and parts[1] == "WRITE_END"):
                    raise ProtoError("bad WRITE_END reply: " + "|".join(parts))
                return
            except Exception as e:
                last_err = e
                try:
                    self.abort_write()
                except Exception:
                    self.clear_input()
                time.sleep(0.10 * attempt)
        raise ProtoError(f"write failed after retries for {path}: {last_err}")

    def delete_file(self, path: str):
        path = normalize_remote_path(path)
        self._write_line(f"DELETE|PATH|{path}")
        parts = self._read_proto_line(timeout=15.0).split("|")
        if not (len(parts) >= 2 and parts[0] == "OK" and parts[1] == "DELETE"):
            raise ProtoError("bad DELETE reply: " + "|".join(parts))

    def mkdir(self, path: str):
        path = normalize_remote_path(path)
        self._write_line(f"MKDIR|PATH|{path}")
        parts = self._read_proto_line(timeout=15.0).split("|")
        if not (len(parts) >= 2 and parts[0] == "OK" and parts[1] == "MKDIR"):
            raise ProtoError("bad MKDIR reply: " + "|".join(parts))

    def reboot(self):
        self._write_line("REBOOT")
        parts = self._read_proto_line(timeout=5.0).split("|")
        if not (len(parts) >= 2 and parts[0] == "OK" and parts[1] == "REBOOT"):
            raise ProtoError("bad REBOOT reply: " + "|".join(parts))


class App(tk.Tk):
    def __init__(self):
        set_windows_app_id()
        super().__init__()
        self.lang = "HU"
        self.client = SerialSpiFFSClient()
        self.files: list[RemoteFile] = []
        self.worker = None
        self.cancel_event = threading.Event()
        self.queue_lock = threading.Lock()
        self.upload_queue: list[UploadTask] = []
        self.queue_running = False
        self.current_queue_task_id: str | None = None

        self.title(f"{self.tr('title')} v{APP_VERSION}")
        self.geometry("1180x860")
        self.minsize(1180, 720)
        self._dark_mode = is_windows_dark_mode()
        apply_theme(self, self._dark_mode)
        icon_path = get_app_icon_path()
        if icon_path:
            try:
                self.iconbitmap(default=icon_path)
            except Exception:
                try:
                    self.iconbitmap(icon_path)
                except Exception:
                    pass

        self.port_var = tk.StringVar()
        self.status_var = tk.StringVar(value=self.tr("status_ready"))
        self.progress_var = tk.DoubleVar(value=0.0)
        self.overall_progress_var = tk.DoubleVar(value=0.0)
        self.current_file_var = tk.StringVar(value="-")
        self.overall_var = tk.StringVar(value="0 / 0")
        self.speed_var = tk.StringVar(value="0 KB/s")
        self.eta_var = tk.StringVar(value="--:--")
        self.failures_var = tk.StringVar(value="0")

        self._build_ui()
        self.refresh_ports()
        self.after(100, self._refresh_tree_scrollbar)
        self.bind("<Configure>", lambda event: self.after_idle(self._refresh_tree_scrollbar))
        if self._dark_mode:
            self.after(50, lambda: apply_dark_title_bar(self))
        if serial is None:
            messagebox.showwarning(self.tr("error"), self.tr("pyserial_missing"))

    def tr(self, key: str) -> str:
        return TEXT[self.lang][key]

    def _build_ui(self):
        top = ttk.Frame(self, padding=8)
        top.pack(fill="x")
        self.lbl_port = ttk.Label(top, text=self.tr("port"))
        self.lbl_port.grid(row=0, column=0, sticky="w")
        self.port_combo = ttk.Combobox(top, textvariable=self.port_var, width=22, state="readonly")
        self.port_combo.grid(row=0, column=1, sticky="ew", padx=6)
        self.btn_ports = ttk.Button(top, text=self.tr("refresh_ports"), command=self.refresh_ports)
        self.btn_ports.grid(row=0, column=2, padx=4)
        self.btn_connect = ttk.Button(top, text=self.tr("connect"), command=self.connect)
        self.btn_connect.grid(row=0, column=3, padx=4)
        self.btn_disconnect = ttk.Button(top, text=self.tr("disconnect"), command=self.disconnect)
        self.btn_disconnect.grid(row=0, column=4, padx=4)
        self.btn_maint = ttk.Button(top, text=self.tr("maintenance"), command=self.enter_maintenance)
        self.btn_maint.grid(row=0, column=5, padx=4)
        self.btn_lang = ttk.Button(top, text=self.tr("lang"), command=self.toggle_lang)
        self.btn_lang.grid(row=0, column=6, padx=4)
        top.columnconfigure(1, weight=1)

        actions = ttk.Frame(self, padding=(8, 0, 8, 8))
        actions.pack(fill="x")
        self.btn_list = ttk.Button(actions, text=self.tr("list"), command=self.refresh_list)
        self.btn_list.pack(side="left", padx=3)
        self.btn_backup = ttk.Button(actions, text=self.tr("backup"), command=self.backup_zip)
        self.btn_backup.pack(side="left", padx=3)
        self.btn_restore = ttk.Button(actions, text=self.tr("restore"), command=self.restore_zip)
        self.btn_restore.pack(side="left", padx=3)
        self.btn_upload_files = ttk.Button(actions, text=self.tr("upload_files"), command=self.queue_add_files)
        self.btn_upload_files.pack(side="left", padx=3)
        self.btn_upload_folder = ttk.Button(actions, text=self.tr("upload_folder"), command=self.queue_add_folder)
        self.btn_upload_folder.pack(side="left", padx=3)
        self.btn_download = ttk.Button(actions, text=self.tr("download"), command=self.download_selected)
        self.btn_download.pack(side="left", padx=3)
        self.btn_delete = ttk.Button(actions, text=self.tr("delete"), command=self.delete_selected)
        self.btn_delete.pack(side="left", padx=3)
        self.btn_reboot = ttk.Button(actions, text=self.tr("reboot"), command=self.reboot_radio)
        self.btn_reboot.pack(side="left", padx=3)

        self.main_pane = ttk.Panedwindow(self, orient="horizontal")
        self.main_pane.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        left = ttk.Frame(self.main_pane)
        right = ttk.Frame(self.main_pane)
        self.main_pane.add(left, weight=11)
        self.main_pane.add(right, weight=9)

        self.left_panel = ttk.LabelFrame(left, text=self.tr("tree"), padding=8)
        self.left_panel.pack(fill="both", expand=True)
        self.tree = ttk.Treeview(self.left_panel, columns=("type", "size"), show="tree headings")
        self.tree.heading("#0", text=self.tr("tree"))
        self.tree.heading("type", text=self.tr("type"))
        self.tree.heading("size", text=self.tr("size"))
        self.tree.column("#0", width=430, anchor="w")
        self.tree.column("type", width=95, anchor="w")
        self.tree.column("size", width=85, anchor="w")
        self.tree_ys = ttk.Scrollbar(self.left_panel, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self._on_tree_yview)
        self.tree.pack(side="left", fill="both", expand=True)
        self.tree.bind("<<TreeviewOpen>>", lambda event: self.after_idle(self._refresh_tree_scrollbar))
        self.tree.bind("<<TreeviewClose>>", lambda event: self.after_idle(self._refresh_tree_scrollbar))

        self.queue_panel = ttk.LabelFrame(right, text=self.tr("queue"), padding=8)
        self.queue_panel.pack(fill="both", expand=True)

        queue_buttons = ttk.Frame(self.queue_panel)
        queue_buttons.pack(fill="x", pady=(0, 8))
        self.btn_queue_add_files = ttk.Button(queue_buttons, text=self.tr("queue_add_files"), command=self.queue_add_files)
        self.btn_queue_add_files.pack(side="left", padx=2)
        self.btn_queue_add_folder = ttk.Button(queue_buttons, text=self.tr("queue_add_folder"), command=self.queue_add_folder)
        self.btn_queue_add_folder.pack(side="left", padx=2)
        self.btn_queue_start = ttk.Button(queue_buttons, text=self.tr("queue_start"), command=self.start_queue)
        self.btn_queue_start.pack(side="left", padx=2)
        self.btn_queue_cancel = ttk.Button(queue_buttons, text=self.tr("queue_cancel"), command=self.cancel_queue)
        self.btn_queue_cancel.pack(side="left", padx=2)

        self.queue_tree = ttk.Treeview(self.queue_panel, columns=("target", "status", "progress", "size"), show="tree headings", height=18)
        self.queue_tree.heading("#0", text=self.tr("queue_name"))
        self.queue_tree.heading("target", text=self.tr("queue_target"))
        self.queue_tree.heading("status", text=self.tr("queue_status"))
        self.queue_tree.heading("progress", text=self.tr("queue_progress"))
        self.queue_tree.heading("size", text=self.tr("queue_size"))
        self.queue_tree.column("#0", width=150, anchor="w")
        self.queue_tree.column("target", width=130, anchor="w")
        self.queue_tree.column("status", width=70, anchor="w")
        self.queue_tree.column("progress", width=60, anchor="w")
        self.queue_tree.column("size", width=60, anchor="w")
        self.queue_tree.pack(fill="both", expand=True)

        self.progress_box = ttk.LabelFrame(self.queue_panel, text=self.tr("queue_progress"), padding=8)
        self.progress_box.pack(fill="x", pady=(8, 0))
        self.progress = ttk.Progressbar(self.progress_box, variable=self.progress_var, maximum=100.0)
        self.progress.pack(fill="x")
        self.progress_overall = ttk.Progressbar(self.progress_box, variable=self.overall_progress_var, maximum=100.0)
        self.progress_overall.pack(fill="x", pady=(6, 0))

        grid = ttk.Frame(self.progress_box)
        grid.pack(fill="x", pady=(8, 0))
        for idx in range(0, 4):
            grid.columnconfigure(idx, weight=1)
        self.lbl_queue_file = ttk.Label(grid, text=self.tr("queue_file"))
        self.lbl_queue_file.grid(row=0, column=0, sticky="w")
        ttk.Label(grid, textvariable=self.current_file_var).grid(row=0, column=1, sticky="w")
        self.lbl_queue_index = ttk.Label(grid, text=self.tr("queue_index"))
        self.lbl_queue_index.grid(row=0, column=2, sticky="w")
        ttk.Label(grid, textvariable=self.overall_var).grid(row=0, column=3, sticky="w")
        self.lbl_queue_speed = ttk.Label(grid, text=self.tr("queue_speed"))
        self.lbl_queue_speed.grid(row=1, column=0, sticky="w", pady=(4, 0))
        ttk.Label(grid, textvariable=self.speed_var).grid(row=1, column=1, sticky="w", pady=(4, 0))
        self.lbl_queue_eta = ttk.Label(grid, text=self.tr("queue_eta"))
        self.lbl_queue_eta.grid(row=1, column=2, sticky="w", pady=(4, 0))
        ttk.Label(grid, textvariable=self.eta_var).grid(row=1, column=3, sticky="w", pady=(4, 0))
        self.lbl_queue_failures = ttk.Label(grid, text=self.tr("queue_failures"))
        self.lbl_queue_failures.grid(row=2, column=0, sticky="w", pady=(4, 0))
        ttk.Label(grid, textvariable=self.failures_var).grid(row=2, column=1, sticky="w", pady=(4, 0))
        self.lbl_queue_overall = ttk.Label(grid, text=self.tr("queue_overall"))
        self.lbl_queue_overall.grid(row=2, column=2, sticky="w", pady=(4, 0))
        ttk.Label(grid, textvariable=self.status_var).grid(row=2, column=3, sticky="w", pady=(4, 0))

        self.after(100, self._apply_initial_layout)

        bottom = ttk.Frame(self, padding=(8, 0, 8, 8))
        bottom.pack(fill="x")
        ttk.Label(bottom, text=self.tr("footer")).pack(side="right")

    def _set_tree_scrollbar_visible(self, visible: bool):
        if visible:
            if not self.tree_ys.winfo_ismapped():
                self.tree_ys.pack(side="right", fill="y")
        else:
            if self.tree_ys.winfo_ismapped():
                self.tree_ys.pack_forget()

    def _on_tree_yview(self, first, last):
        self.tree_ys.set(first, last)
        try:
            self._set_tree_scrollbar_visible(not (float(first) <= 0.0 and float(last) >= 1.0))
        except Exception:
            self._set_tree_scrollbar_visible(True)

    def _refresh_tree_scrollbar(self):
        self.update_idletasks()
        try:
            first, last = self.tree.yview()
            self._set_tree_scrollbar_visible(not (float(first) <= 0.0 and float(last) >= 1.0))
        except Exception:
            self._set_tree_scrollbar_visible(False)

    def _apply_initial_layout(self):
        try:
            total = self.main_pane.winfo_width()
            if total > 0:
                self.main_pane.sashpos(0, int(total * 0.56))
        except Exception:
            pass

    def toggle_lang(self):
        self.lang = "EN" if self.lang == "HU" else "HU"
        self.title(f"{self.tr('title')} v{APP_VERSION}")
        self.lbl_port.config(text=self.tr("port"))
        self.btn_ports.config(text=self.tr("refresh_ports"))
        self.btn_connect.config(text=self.tr("connect"))
        self.btn_disconnect.config(text=self.tr("disconnect"))
        self.btn_maint.config(text=self.tr("maintenance"))
        self.btn_lang.config(text=self.tr("lang"))
        self.btn_list.config(text=self.tr("list"))
        self.btn_backup.config(text=self.tr("backup"))
        self.btn_restore.config(text=self.tr("restore"))
        self.btn_upload_files.config(text=self.tr("upload_files"))
        self.btn_upload_folder.config(text=self.tr("upload_folder"))
        self.btn_download.config(text=self.tr("download"))
        self.btn_delete.config(text=self.tr("delete"))
        self.btn_reboot.config(text=self.tr("reboot"))
        self.btn_queue_add_files.config(text=self.tr("queue_add_files"))
        self.btn_queue_add_folder.config(text=self.tr("queue_add_folder"))
        self.btn_queue_start.config(text=self.tr("queue_start"))
        self.btn_queue_cancel.config(text=self.tr("queue_cancel"))
        self.tree.heading("#0", text=self.tr("tree"))
        self.tree.heading("type", text=self.tr("type"))
        self.tree.heading("size", text=self.tr("size"))
        self.left_panel.config(text=self.tr("tree"))
        self.queue_panel.config(text=self.tr("queue"))
        self.progress_box.config(text=self.tr("queue_progress"))
        self.lbl_queue_file.config(text=self.tr("queue_file"))
        self.lbl_queue_index.config(text=self.tr("queue_index"))
        self.lbl_queue_speed.config(text=self.tr("queue_speed"))
        self.lbl_queue_eta.config(text=self.tr("queue_eta"))
        self.lbl_queue_failures.config(text=self.tr("queue_failures"))
        self.lbl_queue_overall.config(text=self.tr("queue_overall"))
        self.queue_tree.heading("#0", text=self.tr("queue_name"))
        self.queue_tree.heading("target", text=self.tr("queue_target"))
        self.queue_tree.heading("status", text=self.tr("queue_status"))
        self.queue_tree.heading("progress", text=self.tr("queue_progress"))
        self.queue_tree.heading("size", text=self.tr("queue_size"))
        current_status = self.status_var.get()
        for key in ("status_ready", "maintenance_ok", "queue_idle", "queue_running", "queue_finished", "queue_cancelled_done"):
            other = TEXT["EN" if self.lang == "HU" else "HU"][key]
            if current_status == other or current_status == TEXT[self.lang][key]:
                self.status_var.set(self.tr(key))
                break
        apply_theme(self, self._dark_mode)
        self.refresh_queue_tree()

    def set_status(self, text: str):
        self.after(0, lambda: self.status_var.set(text))

    def _localize_error(self, text: str) -> str:
        if self.lang != "HU":
            return text
        replacements = {
            "could not enter maintenance mode": "Nem sikerült belépni a karbantartó módba",
            "unexpected BEGIN reply": "Váratlan BEGIN válasz",
            "protocol timeout": "Kommunikációs időtúllépés",
            "not connected": "Nincs kapcsolat",
            "bad DELETE reply": "Hibás törlési válasz",
            "bad MKDIR reply": "Hibás mappalétrehozási válasz",
            "bad WRITE_BEGIN reply": "Hibás íráskezdési válasz",
            "bad WRITE_DATA reply": "Hibás írási adatválasz",
            "bad WRITE_END reply": "Hibás írászárási válasz",
            "bad READ_END reply": "Hibás olvasási záróválasz",
            "bad REBOOT reply": "Hibás újraindítási válasz",
            "pyserial not installed": "A pyserial nincs telepítve",
            "write failed after retries for": "Az írás többszöri próbálkozás után is sikertelen ennél:",
        }
        out = text
        for src, dst in replacements.items():
            out = out.replace(src, dst)
        return out

    def run_job(self, fn, done=None):
        if self.worker and self.worker.is_alive():
            messagebox.showwarning(self.tr("warning"), self.tr("queue_running"))
            return

        def wrap():
            try:
                result = fn()
                if done:
                    self.after(0, lambda: done(result))
            except Exception as e:
                last_step = self.status_var.get()
                self.after(0, lambda: messagebox.showerror(self.tr("error"), f"{self._localize_error(str(e))}\n\n{self.tr('last_step')}: {last_step}"))
                self.set_status(self.tr("error"))
                self.after(0, self._reset_queue_runtime_labels)
            finally:
                pass

        self.worker = threading.Thread(target=wrap, daemon=True)
        self.worker.start()

    def refresh_ports(self):
        if list_ports is None:
            return
        ports = []
        for p in list_ports.comports():
            ports.append(f"{p.device} - {p.description}")
        self.port_combo["values"] = ports or [self.tr("ports_none")]
        self.port_var.set(ports[0] if ports else self.tr("ports_none"))

    def _selected_port(self) -> str:
        value = self.port_var.get().strip()
        if not value or value == self.tr("ports_none"):
            raise ProtoError(self.tr("ports_none"))
        return value.split(" - ", 1)[0].strip()

    def ensure_connected(self):
        if not self.client.ser:
            raise ProtoError(self.tr("connect_first"))

    def connect(self):
        def job():
            self.set_status(self.tr("status_connecting"))
            self.client.connect(self._selected_port())
            self.set_status(self.tr("status_maintenance"))
            self.client.begin_maintenance()
            self.client.ping()
            self.set_status(self.tr("status_listing"))
            return self.client.list_files()

        def done(files):
            self.files = files
            self.populate_tree()
            self.set_status(self.tr("maintenance_ok"))

        self.run_job(job, done)

    def disconnect(self):
        if self.queue_running:
            self.cancel_queue()
        self.client.disconnect()
        self.set_status(self.tr("status_ready"))
        self._reset_queue_runtime_labels()

    def enter_maintenance(self):
        def job():
            self.set_status(self.tr("status_maintenance"))
            self.client.begin_maintenance()
            self.client.ping()
            return True

        def done(_):
            self.set_status(self.tr("maintenance_ok"))

        self.run_job(job, done)

    def refresh_list(self):
        def job():
            self.ensure_connected()
            self.set_status(self.tr("status_listing"))
            return self.client.list_files()

        def done(files):
            self.files = files
            self.populate_tree()
            self.set_status(f"{len(files)} {self.tr('file')}")

        self.run_job(job, done)

    def populate_tree(self):
        self.tree.delete(*self.tree.get_children())
        nodes = {"/": ""}
        for rf in self.files:
            parts = [p for p in rf.path.strip("/").split("/") if p]
            current_path = "/"
            parent_id = ""
            for idx, part in enumerate(parts):
                full = (current_path.rstrip("/") + "/" + part) if current_path != "/" else "/" + part
                is_last = idx == len(parts) - 1
                if full not in nodes:
                    if is_last:
                        node = self.tree.insert(parent_id, "end", text=part, values=(self.tr("file"), fmt_size(rf.size)))
                    else:
                        node = self.tree.insert(parent_id, "end", text=part, values=(self.tr("folder"), ""))
                    nodes[full] = node
                parent_id = nodes[full]
                current_path = full
        self.after_idle(self._refresh_tree_scrollbar)

    def _item_remote_path(self, item_id: str) -> tuple[str, bool]:
        parts = []
        current = item_id
        while current:
            parts.append(self.tree.item(current, "text"))
            current = self.tree.parent(current)
        parts.reverse()
        path = "/" + "/".join(parts)
        is_file = self.tree.set(item_id, "type") == self.tr("file")
        return path, is_file

    def _selected_upload_target_root(self) -> str:
        selection = self.tree.selection()
        if not selection:
            return "/"
        selected_remote, selected_is_file = self._item_remote_path(selection[0])
        if selected_is_file:
            return normalize_remote_path("/".join(selected_remote.split("/")[:-1]) or "/")
        return normalize_remote_path(selected_remote)

    def _queue_append(self, task: UploadTask):
        with self.queue_lock:
            self.upload_queue.append(task)
        self.after(0, self.refresh_queue_tree)

    def queue_add_files(self):
        paths = filedialog.askopenfilenames()
        if not paths:
            return
        target_root = self._selected_upload_target_root()
        for file_path in paths:
            p = Path(file_path)
            task = UploadTask(local_path=p, remote_path=normalize_remote_path(f"{target_root}/{p.name}"), size=p.stat().st_size)
            self._queue_append(task)
        self.set_status(self.tr("queue_added"))

    def queue_add_folder(self):
        folder = filedialog.askdirectory()
        if not folder:
            return
        root = Path(folder)
        files = [p for p in root.rglob("*") if p.is_file()]
        if not files:
            messagebox.showwarning(self.tr("warning"), self.tr("empty_folder"))
            return
        selection = self.tree.selection()
        selected_remote = None
        selected_is_file = False
        if selection:
            selected_remote, selected_is_file = self._item_remote_path(selection[0])
        if selected_remote:
            if selected_is_file:
                target_root = normalize_remote_path("/".join(selected_remote.split("/")[:-1]) or "/")
            else:
                target_root = normalize_remote_path(selected_remote)
            preserve_local_folder_name = False
        else:
            target_root = "/"
            preserve_local_folder_name = True
        for p in files:
            rel = p.relative_to(root).as_posix()
            remote_path = normalize_remote_path(f"/{root.name}/{rel}" if preserve_local_folder_name else f"{target_root}/{rel}")
            task = UploadTask(local_path=p, remote_path=remote_path, size=p.stat().st_size)
            self._queue_append(task)
        self.set_status(self.tr("queue_added"))

    def refresh_queue_tree(self):
        selected = set(self.queue_tree.selection())
        self.queue_tree.delete(*self.queue_tree.get_children())
        failures = 0
        with self.queue_lock:
            tasks = list(self.upload_queue)
        for task in tasks:
            if task.status == "failed":
                failures += 1
            item = self.queue_tree.insert(
                "",
                "end",
                iid=task.task_id,
                text=task.local_path.name,
                values=(task.remote_path, self._task_status_label(task.status), f"{task.progress_pct:.0f}%", fmt_size(task.size)),
            )
            if item in selected:
                self.queue_tree.selection_add(item)
        self.failures_var.set(str(failures))
        if not tasks:
            self.current_file_var.set("-")
            self.overall_var.set("0 / 0")
            if not self.queue_running:
                self.set_status(self.tr("queue_idle"))

    def _task_status_label(self, status: str) -> str:
        mapping = {
            "waiting": self.tr("queue_waiting"),
            "uploading": self.tr("queue_uploading"),
            "done": self.tr("queue_done"),
            "failed": self.tr("queue_failed"),
            "cancelled": self.tr("queue_cancelled"),
            "retrying": self.tr("queue_retrying"),
        }
        return mapping.get(status, status)

    def remove_selected_tasks(self):
        if self.queue_running:
            messagebox.showwarning(self.tr("warning"), self.tr("queue_running"))
            return
        selected = set(self.queue_tree.selection())
        if not selected:
            return
        with self.queue_lock:
            self.upload_queue = [t for t in self.upload_queue if t.task_id not in selected]
        self.refresh_queue_tree()

    def clear_completed_tasks(self):
        if self.queue_running:
            messagebox.showwarning(self.tr("warning"), self.tr("queue_running"))
            return
        with self.queue_lock:
            self.upload_queue = [t for t in self.upload_queue if t.status not in {"done", "cancelled"}]
        self.refresh_queue_tree()

    def retry_failed_tasks(self):
        if self.queue_running:
            messagebox.showwarning(self.tr("warning"), self.tr("queue_running"))
            return
        changed = False
        with self.queue_lock:
            for task in self.upload_queue:
                if task.status == "failed":
                    task.status = "waiting"
                    task.progress_pct = 0.0
                    task.uploaded_bytes = 0
                    task.error = ""
                    changed = True
        if changed:
            self.refresh_queue_tree()
            self.set_status(self.tr("queue_added"))

    def cancel_queue(self):
        if not self.queue_running:
            return
        self.cancel_event.set()
        self.set_status(self.tr("queue_cancel_requested"))

    def start_queue(self):
        if self.queue_running:
            messagebox.showwarning(self.tr("warning"), self.tr("queue_running"))
            return
        with self.queue_lock:
            pending = [t for t in self.upload_queue if t.status in {"waiting", "retrying"}]
        if not pending:
            messagebox.showwarning(self.tr("warning"), self.tr("queue_empty_start"))
            return

        def job():
            self.ensure_connected()
            self.queue_running = True
            self.cancel_event.clear()
            self._set_queue_controls_enabled(False)
            self._run_upload_queue()
            return True

        def done(_):
            self.queue_running = False
            self._set_queue_controls_enabled(True)
            self.refresh_queue_tree()
            if self.cancel_event.is_set():
                self.set_status(self.tr("queue_cancelled_done"))
            else:
                self.set_status(self.tr("queue_finished"))
            self.cancel_event.clear()
            self.refresh_list()
            self._reset_queue_runtime_labels(keep_status=True)

        self.run_job(job, done)

    def _set_queue_controls_enabled(self, enabled: bool):
        state = tk.NORMAL if enabled else tk.DISABLED
        self.after(0, lambda: self.btn_queue_add_files.config(state=state))
        self.after(0, lambda: self.btn_queue_add_folder.config(state=state))
        self.after(0, lambda: self.btn_queue_start.config(state=state))
        self.after(0, lambda: self.btn_upload_files.config(state=state))
        self.after(0, lambda: self.btn_upload_folder.config(state=state))
        self.after(0, lambda: self.btn_queue_cancel.config(state=tk.NORMAL if not enabled else tk.DISABLED))

    def _reset_queue_runtime_labels(self, keep_status: bool = False):
        self.progress_var.set(0.0)
        self.overall_progress_var.set(0.0)
        self.current_file_var.set("-")
        self.overall_var.set("0 / 0")
        self.speed_var.set("0 KB/s")
        self.eta_var.set("--:--")
        if not keep_status:
            self.set_status(self.tr("status_ready"))

    def _ensure_remote_parent_dirs(self, remote_path: str):
        parent = "/".join(normalize_remote_path(remote_path).split("/")[:-1]) or "/"
        if parent == "/":
            return
        current_path = ""
        for part in [p for p in parent.strip("/").split("/") if p]:
            current_path += "/" + part
            self.client.mkdir(current_path)

    def _run_upload_queue(self):
        with self.queue_lock:
            tasks = [t for t in self.upload_queue if t.status in {"waiting", "retrying"}]
            total_bytes = sum(t.size for t in tasks)
        sent_before = 0
        queue_start = time.time()
        total_count = len(tasks)
        current_index = 0
        for task in tasks:
            current_index += 1
            if self.cancel_event.is_set():
                self._mark_waiting_as_cancelled()
                break
            self.current_queue_task_id = task.task_id
            self.after(0, lambda n=task.local_path.name: self.current_file_var.set(n))
            self.after(0, lambda i=current_index, tc=total_count: self.overall_var.set(f"{i} / {tc}"))
            ok = self._upload_single_task(task, current_index, total_count, sent_before, total_bytes, queue_start)
            sent_before += task.size if ok else task.uploaded_bytes
        self.current_queue_task_id = None

    def _mark_waiting_as_cancelled(self):
        with self.queue_lock:
            for task in self.upload_queue:
                if task.status in {"waiting", "retrying"}:
                    task.status = "cancelled"
        self.after(0, self.refresh_queue_tree)

    def _set_transfer_metrics(self, current_name: str, current_index: int, total_count: int, bytes_done: int, bytes_total: int, start_time: float):
        elapsed = max(0.001, time.time() - start_time)
        speed = bytes_done / elapsed if bytes_done > 0 else 0.0
        eta = (max(0, bytes_total - bytes_done) / speed) if speed > 0 else None
        pct = 100.0 if bytes_total == 0 else (bytes_done / bytes_total) * 100.0
        self.after(0, lambda n=current_name: self.current_file_var.set(n))
        self.after(0, lambda i=current_index, tc=total_count: self.overall_var.set(f"{i} / {tc}"))
        self.after(0, lambda p=pct: self.progress_var.set(p))
        self.after(0, lambda p=pct: self.overall_progress_var.set(p))
        self.after(0, lambda s=human_speed(speed): self.speed_var.set(s))
        self.after(0, lambda e=format_eta(eta): self.eta_var.set(e))

    def _reset_transfer_metrics(self):
        self.progress_var.set(0.0)
        self.overall_progress_var.set(0.0)
        self.current_file_var.set("-")
        self.overall_var.set("0 / 0")
        self.speed_var.set("0 KB/s")
        self.eta_var.set("--:--")

    def _upload_single_task(self, task: UploadTask, current_index: int, total_count: int, sent_before: int, total_bytes: int, queue_start: float) -> bool:
        local_bytes = task.local_path.read_bytes()
        last_error = None
        for attempt in range(task.retries_done, task.max_retries + 1):
            if self.cancel_event.is_set():
                task.status = "cancelled"
                self.after(0, self.refresh_queue_tree)
                return False
            task.status = "uploading" if attempt == 0 else "retrying"
            task.error = ""
            task.progress_pct = 0.0
            task.uploaded_bytes = 0
            self.after(0, self.refresh_queue_tree)
            try:
                self._ensure_remote_parent_dirs(task.remote_path)
                file_start = time.time()
                for chunk_idx, chunk_total, uploaded in self.client.write_file(task.remote_path, local_bytes):
                    if self.cancel_event.is_set():
                        try:
                            self.client.abort_write()
                        except Exception:
                            pass
                        task.status = "cancelled"
                        self.after(0, self.refresh_queue_tree)
                        return False
                    task.uploaded_bytes = uploaded
                    task.progress_pct = 100.0 if task.size == 0 else (uploaded / max(1, task.size)) * 100.0
                    elapsed = max(0.001, time.time() - queue_start)
                    total_sent_now = sent_before + uploaded
                    speed = total_sent_now / elapsed
                    remaining = max(0, total_bytes - total_sent_now)
                    eta = remaining / speed if speed > 0 else None
                    self.after(0, lambda p=task.progress_pct: self.progress_var.set(p))
                    overall_pct = 100.0 if total_bytes == 0 else (total_sent_now / total_bytes) * 100.0
                    self.after(0, lambda p=overall_pct: self.overall_progress_var.set(p))
                    self.after(0, lambda s=human_speed(speed): self.speed_var.set(s))
                    self.after(0, lambda e=format_eta(eta): self.eta_var.set(e))
                    self.set_status(f"{self.tr('status_uploading')} {current_index}/{total_count} - {task.remote_path}")
                    self.after(0, self.refresh_queue_tree)
                task.status = "done"
                task.progress_pct = 100.0
                task.uploaded_bytes = task.size
                self.after(0, self.refresh_queue_tree)
                return True
            except Exception as e:
                task.retries_done = attempt + 1
                task.error = str(e)
                last_error = e
                if attempt < task.max_retries and not self.cancel_event.is_set():
                    task.status = "retrying"
                    self.after(0, self.refresh_queue_tree)
                    time.sleep(0.3 * (attempt + 1))
                    continue
                task.status = "failed"
                self.after(0, self.refresh_queue_tree)
                return False
        if last_error:
            task.error = str(last_error)
        task.status = "failed"
        self.after(0, self.refresh_queue_tree)
        return False

    def backup_zip(self):
        out = filedialog.asksaveasfilename(title=self.tr("save_backup_title"), defaultextension=".zip", filetypes=[("ZIP", "*.zip")], initialfile="myradio_spiffs_mentes.zip" if self.lang == "HU" else "myradio_spiffs_backup.zip")
        if not out:
            return
        out_path = Path(out)

        def job():
            self.ensure_connected()
            files = self.client.list_files()
            if not files:
                raise ProtoError(self.tr("no_files"))
            self.set_status(self.tr("status_saving"))
            total_files = len(files)
            total_bytes = sum(rf.size for rf in files)
            transferred = 0
            start = time.time()
            self.after(0, self._reset_transfer_metrics)
            with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
                for idx, rf in enumerate(files, 1):
                    data = self.client.read_file(rf.path)
                    zf.writestr(rf.path.lstrip("/"), data)
                    transferred += len(data)
                    self._set_transfer_metrics(Path(rf.path).name, idx, total_files, transferred, total_bytes, start)
                    self.set_status(f"{self.tr('status_saving')} {idx}/{total_files} - {rf.path}")
            return True

        def done(_):
            self._reset_transfer_metrics()
            self.set_status(self.tr("backup_done"))
            messagebox.showinfo(self.tr("done"), self.tr("backup_done"))

        self.run_job(job, done)

    def restore_zip(self):
        zpath = filedialog.askopenfilename(title=self.tr("open_backup_title"), filetypes=[("ZIP", "*.zip")])
        if not zpath:
            return
        zp = Path(zpath)

        def job():
            self.ensure_connected()
            self.set_status(self.tr("status_restoring"))
            current = self.client.list_files()
            for rf in sorted(current, key=lambda x: (x.path.count("/"), x.path.lower()), reverse=True):
                self.client.delete_file(rf.path)
            with zipfile.ZipFile(zp, "r") as zf:
                names = [n for n in zf.namelist() if not n.endswith("/")]
                total_files = max(1, len(names))
                total_bytes = sum(len(zf.read(name)) for name in names) if names else 0
                transferred = 0
                start = time.time()
                self.after(0, self._reset_transfer_metrics)
                for idx, name in enumerate(names, 1):
                    data = zf.read(name)
                    remote_path = normalize_remote_path("/" + name)
                    self._ensure_remote_parent_dirs(remote_path)
                    for _, _, uploaded in self.client.write_file(remote_path, data):
                        self._set_transfer_metrics(Path(name).name, idx, total_files, transferred + uploaded, total_bytes, start)
                        self.set_status(f"{self.tr('status_restoring')} {idx}/{total_files} - {remote_path}")
                    transferred += len(data)
            return True

        def done(_):
            self._reset_transfer_metrics()
            self.refresh_list()
            messagebox.showinfo(self.tr("done"), self.tr("restore_done"))

        self.run_job(job, done)

    def download_selected(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning(self.tr("warning"), self.tr("tree_no_selection"))
            return
        path, is_file = self._item_remote_path(selection[0])
        if not is_file:
            messagebox.showwarning(self.tr("warning"), self.tr("tree_no_selection"))
            return
        out = filedialog.asksaveasfilename(title=self.tr("save_selected_title"), initialfile=Path(path).name)
        if not out:
            return
        out_path = Path(out)

        def job():
            self.ensure_connected()
            self.set_status(self.tr("status_downloading"))
            data = self.client.read_file(path)
            out_path.write_bytes(data)
            return True

        def done(_):
            messagebox.showinfo(self.tr("done"), self.tr("download_done"))

        self.run_job(job, done)

    def delete_selected(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning(self.tr("warning"), self.tr("tree_no_selection"))
            return
        path, is_file = self._item_remote_path(selection[0])

        def job():
            self.ensure_connected()
            files = self.client.list_files()
            targets = [path] if is_file else [f.path for f in files if f.path == path or f.path.startswith(path.rstrip("/") + "/")]
            for target in sorted(targets, reverse=True):
                self.client.delete_file(target)
            return True

        def done(_):
            self.refresh_list()
            messagebox.showinfo(self.tr("done"), self.tr("delete_done"))

        self.run_job(job, done)

    def reboot_radio(self):
        def job():
            self.ensure_connected()
            self.set_status(self.tr("status_rebooting"))
            self.client.reboot()
            return True

        def done(_):
            messagebox.showinfo(self.tr("done"), self.tr("reboot_done"))

        self.run_job(job, done)


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
