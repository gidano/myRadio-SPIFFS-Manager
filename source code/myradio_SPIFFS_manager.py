#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import base64
import sys
import threading
import time
import zipfile
from dataclasses import dataclass
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

try:
    import serial
    from serial.tools import list_ports
except Exception:
    serial = None
    list_ports = None

APP_VERSION = "1.1"
CHUNK_SIZE = 96



def set_windows_app_id():
    try:
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("gidano.myRadio.SPIFFS.Kezelo")
    except Exception:
        pass


def get_app_icon_path() -> str | None:
    candidates = []

    # PyInstaller one-file temp extraction directory
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        candidates.append(Path(meipass) / "icon.ico")

    # Next to the running script / executable
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
                ctypes.windll.dwmapi.DwmSetWindowAttribute(
                    hwnd,
                    attr,
                    ctypes.byref(value),
                    ctypes.sizeof(value)
                )
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
        style.configure("TLabel", background=bg, foreground=fg)
        style.configure("TButton", background=panel, foreground=fg, bordercolor=edge, focusthickness=1, focuscolor=edge)
        style.map(
            "TButton",
            background=[("active", "#2f3136"), ("pressed", "#2a2d31")],
            foreground=[("disabled", "#8a8a8a")]
        )

        style.configure(
            "TCombobox",
            fieldbackground=panel,
            background=panel,
            foreground=fg,
            arrowcolor=fg,
            bordercolor=edge,
            lightcolor=edge,
            darkcolor=edge
        )
        style.map(
            "TCombobox",
            fieldbackground=[("readonly", panel)],
            selectbackground=[("readonly", select)],
            selectforeground=[("readonly", fg)]
        )

        style.configure(
            "Treeview",
            background=panel,
            fieldbackground=panel,
            foreground=fg,
            bordercolor=edge,
            lightcolor=edge,
            darkcolor=edge
        )
        style.configure(
            "Treeview.Heading",
            background="#2d2d30",
            foreground=fg,
            bordercolor=edge,
            lightcolor=edge,
            darkcolor=edge
        )
        style.map(
            "Treeview",
            background=[("selected", select)],
            foreground=[("selected", fg)]
        )
        style.map(
            "Treeview.Heading",
            background=[("active", "#383b40")]
        )

        style.configure(
            "Horizontal.TProgressbar",
            troughcolor=panel,
            background="#6aa2ff",
            bordercolor=edge,
            lightcolor=edge,
            darkcolor=edge
        )

        style.configure(
            "Vertical.TScrollbar",
            background=panel,
            troughcolor=bg,
            arrowcolor=fg,
            bordercolor=edge,
            lightcolor=edge,
            darkcolor=edge
        )
        style.configure(
            "Horizontal.TScrollbar",
            background=panel,
            troughcolor=bg,
            arrowcolor=fg,
            bordercolor=edge,
            lightcolor=edge,
            darkcolor=edge
        )

        try:
            root.option_add("*Background", bg)
            root.option_add("*Foreground", fg)
            root.option_add("*Entry.Background", panel)
            root.option_add("*Entry.Foreground", fg)
            root.option_add("*Text.Background", panel)
            root.option_add("*Text.Foreground", fg)
            root.option_add("*Listbox.Background", panel)
            root.option_add("*Listbox.Foreground", fg)
            root.option_add("*selectBackground", select)
            root.option_add("*selectForeground", fg)
        except Exception:
            pass
    else:
        try:
            style.theme_use("vista")
        except Exception:
            try:
                style.theme_use(style.theme_use())
            except Exception:
                pass

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
        "upload_files": "Fájlok feltöltése",
        "upload_folder": "Mappa feltöltése",
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
        "target_folder": "célmappa",
        "status_deleting": "Törlés folyamatban...",
        "status_downloading": "Mentés a számítógépre...",
        "status_rebooting": "Újraindítás kérése...",
        "pyserial_missing": "A pyserial nincs telepítve.\nParancs: python -m pip install pyserial",
        "connect_first": "Előbb csatlakozz a rádióhoz.",
        "confirm_restore": "Biztosan visszaállítod a kiválasztott mentést?\n\nA rádió teljes SPIFFS tartalma előtte törlésre kerül.",
        "confirm_delete": "Biztosan törlöd a kijelölt elemet vagy elemeket a rádióról?",
        "saved": "Mentve",
        "done": "Kész",
        "error": "Hiba",
        "warning": "Figyelmeztetés",
        "maintenance_ok": "Karbantartó mód aktív.",
        "ports_none": "Nincs találat",
        "select_item": "Jelölj ki egy fájlt vagy mappát.",
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
        "verify_ok": "Az ellenőrzés rendben van.",
        "verify_failed": "Az ellenőrzés hibát talált.",
        "last_step": "Utolsó művelet",
        "restore_mismatch": "Eltérés a visszaállítás után",
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
        "upload_files": "Upload files",
        "upload_folder": "Upload folder",
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
        "target_folder": "target folder",
        "status_deleting": "Deleting...",
        "status_downloading": "Saving to computer...",
        "status_rebooting": "Requesting reboot...",
        "pyserial_missing": "pyserial is not installed.\nCommand: python -m pip install pyserial",
        "connect_first": "Connect to the radio first.",
        "confirm_restore": "Restore the selected backup?\n\nThe current SPIFFS contents on the radio will be deleted first.",
        "confirm_delete": "Delete the selected item(s) from the radio?",
        "saved": "Saved",
        "done": "Done",
        "error": "Error",
        "warning": "Warning",
        "maintenance_ok": "Maintenance mode is active.",
        "ports_none": "No ports found",
        "select_item": "Select a file or folder.",
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
        "verify_ok": "Verification completed successfully.",
        "verify_failed": "Verification found problems.",
        "last_step": "Last step",
        "restore_mismatch": "Mismatch after restore",
        "save_selected_title": "Save file",
        "save_backup_title": "Save backup ZIP",
        "open_backup_title": "Choose backup ZIP",
        "footer": "© 2026 gidano",
    },
}


class ProtoError(RuntimeError):
    pass


@dataclass
class RemoteFile:
    path: str
    size: int


def normalize_remote_path(path: str) -> str:
    path = (path or "").replace("\\", "/")
    while "//" in path:
        path = path.replace("//", "/")
    if not path.startswith("/"):
        path = "/" + path
    return path


class SerialSpiFFSClient:
    def __init__(self):
        self.ser = None

    def connect(self, port: str, baudrate: int = 115200, timeout: float = 0.6):
        if serial is None:
            raise ProtoError("pyserial not installed")
        self.ser = serial.Serial(port=port, baudrate=baudrate, timeout=timeout, write_timeout=20)
        time.sleep(1.2)
        self.clear_input()

    def disconnect(self):
        if self.ser:
            try:
                self.ser.close()
            finally:
                self.ser = None

    def clear_input(self):
        if not self.ser:
            return
        try:
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()
        except Exception:
            pass
        end = time.time() + 0.3
        while time.time() < end:
            line = self.ser.readline()
            if not line:
                break

    def _write_line(self, line: str):
        if not self.ser:
            raise ProtoError("not connected")
        self.ser.write((line + "\n").encode("utf-8"))
        self.ser.flush()

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
            if not line.startswith("MRSPIFS|"):
                last_noise = line
                continue
            return line[len("MRSPIFS|"):]
        if last_noise:
            raise ProtoError(f"protocol timeout (last serial: {last_noise[:120]})")
        raise ProtoError("protocol timeout")

    def begin_maintenance(self):
        self.clear_input()
        for _ in range(8):
            self._write_line("MRSPIFS:BEGIN")
            try:
                line = self._read_proto_line(timeout=2.0)
            except ProtoError:
                continue
            parts = line.split("|")
            if len(parts) >= 2 and parts[0] == "OK" and parts[1] == "BEGIN":
                return True
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
                for idx, i in enumerate(range(0, len(data), CHUNK_SIZE), 1):
                    chunk = data[i:i + CHUNK_SIZE]
                    b64 = base64.b64encode(chunk).decode("ascii")
                    self._write_line(f"WRITE_DATA|B64|{b64}")
                    parts = self._read_proto_line(timeout=25.0).split("|")
                    if not (len(parts) >= 2 and parts[0] == "OK" and parts[1] == "WRITE_DATA"):
                        raise ProtoError(f"bad WRITE_DATA reply at chunk {idx}/{total_chunks} for {path}: " + "|".join(parts))
                    yield idx, total_chunks
                    time.sleep(0.005)

                self._write_line("WRITE_END")
                parts = self._read_proto_line(timeout=25.0).split("|")
                if not (len(parts) >= 2 and parts[0] == "OK" and parts[1] == "WRITE_END"):
                    raise ProtoError("bad WRITE_END reply: " + "|".join(parts))
                time.sleep(0.02)
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

        self.title(f"{self.tr('title')} v{APP_VERSION}")
        self.geometry("1220x800")
        self.minsize(1000, 650)

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
        self.port_combo = ttk.Combobox(top, textvariable=self.port_var, width=42, state="readonly")
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
        self.btn_upload_files = ttk.Button(actions, text=self.tr("upload_files"), command=self.upload_files)
        self.btn_upload_files.pack(side="left", padx=3)
        self.btn_upload_folder = ttk.Button(actions, text=self.tr("upload_folder"), command=self.upload_folder)
        self.btn_upload_folder.pack(side="left", padx=3)
        self.btn_download = ttk.Button(actions, text=self.tr("download"), command=self.download_selected)
        self.btn_download.pack(side="left", padx=3)
        self.btn_delete = ttk.Button(actions, text=self.tr("delete"), command=self.delete_selected)
        self.btn_delete.pack(side="left", padx=3)
        self.btn_reboot = ttk.Button(actions, text=self.tr("reboot"), command=self.reboot_radio)
        self.btn_reboot.pack(side="left", padx=3)

        progress_wrap = ttk.Frame(self, padding=(8, 0, 8, 8))
        progress_wrap.pack(fill="x")
        self.progress = ttk.Progressbar(progress_wrap, variable=self.progress_var, maximum=100.0)
        self.progress.pack(fill="x")

        center = ttk.Frame(self, padding=8)
        center.pack(fill="both", expand=True)
        self.tree = ttk.Treeview(center, columns=("type", "size"), show="tree headings")
        self.tree.heading("#0", text=self.tr("tree"))
        self.tree.heading("type", text=self.tr("type"))
        self.tree.heading("size", text=self.tr("size"))
        self.tree.column("#0", width=760, anchor="w")
        self.tree.column("type", width=120, anchor="w")
        self.tree.column("size", width=120, anchor="e")
        self.tree_ys = ttk.Scrollbar(center, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self._on_tree_yview)
        self.tree.pack(side="left", fill="both", expand=True)

        bottom = ttk.Frame(self, padding=(8, 0, 8, 8))
        bottom.pack(fill="x")
        ttk.Label(bottom, textvariable=self.status_var).pack(side="left")
        ttk.Label(bottom, text=self.tr("footer")).pack(side="right")

        self.tree.bind("<<TreeviewOpen>>", lambda event: self.after_idle(self._refresh_tree_scrollbar))
        self.tree.bind("<<TreeviewClose>>", lambda event: self.after_idle(self._refresh_tree_scrollbar))

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
        self.tree.heading("#0", text=self.tr("tree"))
        self.tree.heading("type", text=self.tr("type"))
        self.tree.heading("size", text=self.tr("size"))
        self.status_var.set(self.tr("status_ready"))
        apply_theme(self, self._dark_mode)
        if self._dark_mode:
            self.after(10, lambda: apply_dark_title_bar(self))

    def set_status(self, text: str):
        self.after(0, lambda: self.status_var.set(text))

    def set_progress(self, value: float):
        value = max(0.0, min(100.0, value))
        self.after(0, lambda: self.progress_var.set(value))

    def reset_progress(self):
        self.set_progress(0.0)

    def run_job(self, fn, done=None):
        if self.worker and self.worker.is_alive():
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
            finally:
                self.set_progress(0.0)

        self.worker = threading.Thread(target=wrap, daemon=True)
        self.worker.start()

    def _localize_error(self, text: str) -> str:
        if self.lang != "HU":
            return text
        replacements = {
            "could not enter maintenance mode": "Nem sikerült belépni a karbantartó módba",
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

    def refresh_ports(self):
        if list_ports is None:
            return
        ports = []
        for p in list_ports.comports():
            label = f"{p.device} - {p.description}"
            ports.append(label)
        self.port_combo["values"] = ports or [self.tr("ports_none")]
        if ports:
            self.port_var.set(ports[0])
        else:
            self.port_var.set(self.tr("ports_none"))

    def _selected_port(self) -> str:
        value = self.port_var.get().strip()
        if not value or value == self.tr("ports_none"):
            raise ProtoError(self.tr("ports_none"))
        return value.split(" - ", 1)[0].strip()

    def connect(self):
        def job():
            self.set_progress(0)
            self.set_status(self.tr("status_connecting"))
            self.client.connect(self._selected_port())
            self.set_progress(20)
            self.set_status(self.tr("status_maintenance"))
            self.client.begin_maintenance()
            self.client.ping()
            self.set_progress(60)
            self.set_status(self.tr("status_listing"))
            files = self.client.list_files()
            self.set_progress(100)
            return files

        def done(files):
            self.files = files
            self.populate_tree()
            self.set_status(self.tr("maintenance_ok"))

        self.run_job(job, done)

    def disconnect(self):
        self.client.disconnect()
        self.set_status(self.tr("status_ready"))
        self.reset_progress()

    def enter_maintenance(self):
        def job():
            self.set_status(self.tr("status_maintenance"))
            self.client.begin_maintenance()
            self.client.ping()
            return True

        def done(_):
            self.set_status(self.tr("maintenance_ok"))

        self.run_job(job, done)

    def ensure_connected(self):
        if not self.client.ser:
            raise ProtoError(self.tr("connect_first"))

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
                        node = self.tree.insert(parent_id, "end", text=part, values=(self.tr("file"), self._fmt_size(rf.size)))
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

    def backup_zip(self):
        out = filedialog.asksaveasfilename(
            title=self.tr("save_backup_title"),
            defaultextension=".zip",
            filetypes=[("ZIP", "*.zip")],
            initialfile="myradio_spiffs_mentes.zip" if self.lang == "HU" else "myradio_spiffs_backup.zip",
        )
        if not out:
            return
        out_path = Path(out)

        def job():
            self.ensure_connected()
            files = self.client.list_files()
            if not files:
                raise ProtoError(self.tr("no_files"))
            self.set_status(self.tr("status_saving"))
            total = len(files)
            with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
                dirs = set()
                for rf in files:
                    p = Path(rf.path.lstrip("/"))
                    parents = list(p.parents)[:-1]
                    for d in reversed(parents):
                        if str(d) != ".":
                            dirs.add(str(d).replace("\\", "/") + "/")
                for d in sorted(dirs):
                    zf.writestr(d, b"")
                for idx, rf in enumerate(files, 1):
                    self.set_status(f"{self.tr('status_saving')} {idx} / {total} - {rf.path}")
                    self.set_progress((idx - 1) / total * 100.0)
                    data = self.client.read_file(rf.path)
                    zf.writestr(rf.path.lstrip("/"), data)
                    self.set_progress(idx / total * 100.0)
            return True

        def done(_):
            self.set_status(self.tr("backup_done"))
            messagebox.showinfo(self.tr("done"), self.tr("backup_done"))

        self.run_job(job, done)

    def _verify_restore(self, expected: dict[str, int]):
        remote = {rf.path: rf.size for rf in self.client.list_files()}
        problems = []
        for path, size in expected.items():
            actual = remote.get(path)
            if actual != size:
                problems.append((path, size, actual))
        return problems

    def restore_zip(self):
        zpath = filedialog.askopenfilename(
            title=self.tr("open_backup_title"),
            filetypes=[("ZIP", "*.zip")],
        )
        if not zpath:
            return
        if not messagebox.askyesno(self.tr("restore"), self.tr("confirm_restore")):
            return
        zp = Path(zpath)

        def job():
            self.ensure_connected()
            self.set_status(self.tr("status_restoring"))

            current = self.client.list_files()
            targets = sorted((rf.path for rf in current), key=lambda p: (p.count("/"), p.lower()), reverse=True)
            delete_total = max(1, len(targets))
            for idx, path in enumerate(targets, 1):
                self.set_status(f"{self.tr('status_deleting')} {idx} / {delete_total} - {path}")
                self.set_progress((idx / delete_total) * 15.0)
                last_err = None
                for attempt in range(3):
                    try:
                        self.client.delete_file(path)
                        last_err = None
                        break
                    except Exception as e:
                        last_err = e
                        time.sleep(0.10 * (attempt + 1))
                if last_err is not None:
                    raise last_err
                time.sleep(0.01)

            expected_sizes: dict[str, int] = {}
            with zipfile.ZipFile(zp, "r") as zf:
                names = [n for n in zf.namelist() if not n.endswith("/")]
                if not names:
                    return {"problems": [], "count": 0}

                parts0 = [Path(n).parts for n in names]
                top = {p[0] for p in parts0 if len(p) > 1}
                strip_first = len(top) == 1

                normalized = []
                for n in names:
                    parts = Path(n).parts
                    if strip_first and len(parts) > 1:
                        parts = parts[1:]
                    rel = "/".join(parts).replace("\\", "/").strip("/")
                    if rel:
                        normalized.append((n, rel))

                made = set()
                for _, rel in normalized:
                    parent = str(Path(rel).parent).replace("\\", "/")
                    if parent and parent != ".":
                        current_path = ""
                        for part in [x for x in parent.split("/") if x]:
                            current_path += "/" + part
                            if current_path not in made:
                                self.client.mkdir(current_path)
                                made.add(current_path)
                                time.sleep(0.005)

                total = len(normalized)
                for idx, (zip_name, rel) in enumerate(normalized, 1):
                    data = zf.read(zip_name)
                    remote_path = normalize_remote_path("/" + rel)
                    expected_sizes[remote_path] = len(data)
                    base_progress = 15.0 + ((idx - 1) / total) * 75.0
                    self.set_status(f"{self.tr('status_restoring')} {idx} / {total} - {remote_path}")
                    for chunk_idx, chunk_total in self.client.write_file(remote_path, data):
                        local_progress = base_progress + (chunk_idx / chunk_total) * (75.0 / total)
                        self.set_progress(local_progress)
                    time.sleep(0.02)

            self.set_status(self.tr("status_verifying"))
            self.set_progress(95.0)
            problems = self._verify_restore(expected_sizes)
            self.set_progress(100.0)
            return {"problems": problems, "count": len(expected_sizes)}

        def done(result):
            self.refresh_list()
            problems = result["problems"]
            if problems:
                lines = [self.tr("verify_failed") + ":", ""]
                for path, exp, got in problems[:25]:
                    lines.append(f"{path}  várt: {exp}  kapott: {got}")
                if len(problems) > 25:
                    lines.append("...")
                messagebox.showwarning(self.tr("restore_mismatch"), "\n".join(lines))
                self.set_status(self.tr("verify_failed"))
            else:
                messagebox.showinfo(self.tr("done"), f"{self.tr('restore_done')}\n{self.tr('verify_ok')}")
                self.set_status(self.tr("restore_done"))

        self.run_job(job, done)

    def _selected_upload_target_root(self) -> str:
        selection = self.tree.selection()
        if not selection:
            return "/"

        selected_remote, selected_is_file = self._item_remote_path(selection[0])
        if selected_is_file:
            return normalize_remote_path("/".join(selected_remote.split("/")[:-1]) or "/")
        return normalize_remote_path(selected_remote)

    def upload_files(self):
        paths = filedialog.askopenfilenames()
        if not paths:
            return

        target_root = self._selected_upload_target_root()

        def job():
            self.ensure_connected()
            total = len(paths)
            for idx, file_path in enumerate(paths, 1):
                p = Path(file_path)
                remote_path = normalize_remote_path(f"{target_root}/{p.name}")
                self.set_status(
                    f"{self.tr('status_uploading')} {idx} / {total} - {remote_path} "
                    f"[{self.tr('target_folder')}: {target_root}]"
                )
                base_progress = ((idx - 1) / total) * 100.0
                data = p.read_bytes()
                for chunk_idx, chunk_total in self.client.write_file(remote_path, data):
                    local_progress = base_progress + (chunk_idx / chunk_total) * (100.0 / total)
                    self.set_progress(local_progress)
            return True

        def done(_):
            self.refresh_list()
            messagebox.showinfo(self.tr("done"), self.tr("upload_done"))

        self.run_job(job, done)


    def upload_folder(self):
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

        def mkdir_p(remote_dir: str):
            remote_dir = normalize_remote_path(remote_dir)
            if remote_dir == "/":
                return
            current_path = ""
            for part in [p for p in remote_dir.strip("/").split("/") if p]:
                current_path += "/" + part
                self.client.mkdir(current_path)

        def job():
            self.ensure_connected()
            if preserve_local_folder_name:
                mkdir_p("/" + root.name)

            total = len(files)
            for idx, p in enumerate(files, 1):
                rel = p.relative_to(root).as_posix()
                if preserve_local_folder_name:
                    remote_path = normalize_remote_path(f"/{root.name}/{rel}")
                else:
                    remote_path = normalize_remote_path(f"{target_root}/{rel}")

                parent = "/".join(remote_path.split("/")[:-1]) or "/"
                mkdir_p(parent)

                self.set_status(f"{self.tr('status_uploading')} {idx} / {total} - {remote_path}")
                base_progress = ((idx - 1) / total) * 100.0
                data = p.read_bytes()
                for chunk_idx, chunk_total in self.client.write_file(remote_path, data):
                    local_progress = base_progress + (chunk_idx / chunk_total) * (100.0 / total)
                    self.set_progress(local_progress)
            return True

        def done(_):
            self.refresh_list()
            messagebox.showinfo(self.tr("done"), self.tr("upload_done"))

        self.run_job(job, done)

    def download_selected(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning(self.tr("warning"), self.tr("select_item"))
            return
        path, is_file = self._item_remote_path(selection[0])
        if not is_file:
            messagebox.showwarning(self.tr("warning"), self.tr("select_item"))
            return

        out = filedialog.asksaveasfilename(
            title=self.tr("save_selected_title"),
            initialfile=Path(path).name,
        )
        if not out:
            return
        out_path = Path(out)

        def job():
            self.ensure_connected()
            self.set_status(self.tr("status_downloading"))
            data = self.client.read_file(path)
            out_path.write_bytes(data)
            self.set_progress(100.0)
            return True

        def done(_):
            messagebox.showinfo(self.tr("done"), self.tr("download_done"))

        self.run_job(job, done)

    def delete_selected(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning(self.tr("warning"), self.tr("select_item"))
            return
        if not messagebox.askyesno(self.tr("delete"), self.tr("confirm_delete")):
            return
        path, is_file = self._item_remote_path(selection[0])

        def job():
            self.ensure_connected()
            files = self.client.list_files()
            targets = [path] if is_file else [f.path for f in files if f.path == path or f.path.startswith(path.rstrip("/") + "/")]
            total = max(1, len(targets))
            for idx, target in enumerate(sorted(targets, reverse=True), 1):
                self.set_status(f"{self.tr('status_deleting')} {idx} / {total} - {target}")
                self.client.delete_file(target)
                self.set_progress(idx / total * 100.0)
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
            self.set_progress(100.0)
            return True

        def done(_):
            messagebox.showinfo(self.tr("done"), self.tr("reboot_done"))

        self.run_job(job, done)

    @staticmethod
    def _fmt_size(size: int) -> str:
        value = float(size)
        for unit in ("B", "KB", "MB"):
            if value < 1024 or unit == "MB":
                if unit == "B":
                    return f"{int(value)} {unit}"
                return f"{value:.1f} {unit}"
            value /= 1024
        return f"{size} B"


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
