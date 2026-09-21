import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog
import threading
import subprocess
from datetime import datetime


class ToolbarPanel(ttk.Frame):
    """Top toolbar with action buttons."""

    def __init__(self, parent, callback):
        super().__init__(parent)
        self.callback = callback

        ttk.Button(self, text="Upgrade your uBlockDNS Version",
                   command=lambda: callback("ublockdns_upgrade")).pack(side="left", padx=3)
        ttk.Button(self, text="Stop your uBlockDNS Service",
                   command=lambda: callback("ublockdns_stop")).pack(side="left", padx=3)
        ttk.Button(self, text="Start your uBlockDNS Service",
                   command=lambda: callback("ublockdns_start")).pack(side="left", padx=3)
        ttk.Button(self, text="Export",
                   command=lambda: callback("export")).pack(side="left", padx=3)
        ttk.Button(self, text="Clear",
                   command=lambda: callback("clear")).pack(side="left", padx=3)
        ttk.Button(self, text="Quit",
                   command=parent.quit).pack(side="right", padx=3)


class OutputPanel(ttk.Frame):
    """Scrollable text output with threaded command execution."""

    def __init__(self, parent):
        super().__init__(parent)

        self.text = scrolledtext.ScrolledText(
            self, wrap="word", state="disabled",
            bg="#11111b", fg="#cdd6f4",
            insertbackground="#cdd6f4",
            font=("Monospace", 11),
            padx=8, pady=8,
        )
        self.text.pack(fill="both", expand=True)

        # Tag styles
        self.text.tag_config("info", foreground="#89b4fa")
        self.text.tag_config("warn", foreground="#fab387")
        self.text.tag_config("error", foreground="#f38ba8")
        self.text.tag_config("success", foreground="#a6e3a1")

    def _write(self, msg, tag=None):
        self.text.config(state="normal")
        ts = datetime.now().strftime("%H:%M:%S")
        if tag:
            self.text.insert("end", f"[{ts}] {msg}\n", tag)
        else:
            self.text.insert("end", f"[{ts}] {msg}\n")
        self.text.see("end")
        self.text.config(state="disabled")

    def run_command(self, cmd_list, on_done=None, password=None):
        """Run a subprocess in a background thread."""
        self._write(f"$ {' '.join(cmd_list)}", "info")

        def _worker():
            try:
                result = subprocess.run(
                    cmd_list, capture_output=True, text=True, timeout=120
                )
                lines = result.stdout.strip().splitlines()
                for line in lines:
                    self._write(line)
                if result.returncode != 0 and result.stderr:
                    self._write(result.stderr.strip(), "error")
            except subprocess.TimeoutExpired:
                self._write("Command timed out after 120s", "warn")
            except Exception as e:
                self._write(f"Error: {e}", "error")
            finally:
                if on_done:
                    self.after(0, on_done)

        t = threading.Thread(target=_worker, daemon=True)
        t.start()

    def clear(self):
        self.text.config(state="normal")
        self.text.delete("1.0", "end")
        self.text.config(state="disabled")

    def export_log(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".log",
            filetypes=[("Log files", "*.log"), ("Text files", "*.txt"), ("All", "*.*")],
        )
        if not path:
            return

        content = self.text.get("1.0", "end")
        with open(path, "w") as f:
            f.write(content)
        self._write(f"Log exported to {path}", "success")

class StatusBar(ttk.Frame):
    """Bottom status bar."""

    def __init__(self, parent):
        super().__init__(parent)
        self.label = ttk.Label(self, text="", anchor="w")
        self.label.pack(fill="x")

    def set(self, message):
        self.label.config(text=f"  {message}")
