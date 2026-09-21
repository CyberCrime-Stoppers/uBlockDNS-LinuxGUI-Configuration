import tkinter as tk
from tkinter import ttk
from ui.panels import OutputPanel, ToolbarPanel, StatusBar


class uBdnsUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("uBlockDNS Configure CLI — Linux")
        self.geometry("1000x650")
        self.minsize(700, 450)

        # Dark-ish theme
        self.configure(bg="#1e1e2e")
        self._apply_theme()

        # Layout
        self.toolbar = ToolbarPanel(self, self.on_action)
        self.toolbar.pack(fill="x", padx=6, pady=(6, 2))

        self.output = OutputPanel(self)
        self.output.pack(fill="both", expand=True, padx=6, pady=2)

        self.status = StatusBar(self)
        self.status.pack(fill="x", padx=6, pady=(2, 6))
        self.status.set("Ready.")

    def _apply_theme(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background="#1e1e2e")
        style.configure("TButton", background="#313244", foreground="#cdd6f4")
        style.map("TButton",
                  background=[("active", "#45475a")],
                  foreground=[("active", "#cdd6f4")])
        style.configure("TLabel", background="#1e1e2e", foreground="#cdd6f4")
        style.configure("Vertical.TScrollbar",
                         background="#313244", troughcolor="#1e1e2e")

    def on_action(self, action_name, **kwargs):
        """Central dispatcher for toolbar actions."""
        handlers = {
            "ublockdns_upgrade": self.output.run_command,
            "ublockdns_stop": self.output.run_command,
            "ublockdns_start": self.output.run_command,
            "export": self.output.export_log,
            "clear": self.output.clear,
    }

        cmd_map = {
            "ublockdns_upgrade": ["pkexec", "ublockdns", "upgrade"],
            "ublockdns_stop": ["pkexec", "ublockdns", "stop"],
            "ublockdns_start": ["pkexec", "ublockdns", "start"],
    }

        handler = handlers.get(action_name)
        if not handler:
            return

        if action_name in cmd_map:
            self.status.set(f"Running: {' '.join(cmd_map[action_name])}")
            handler(cmd_map[action_name], on_done=lambda: self.status.set("Done."))
        else:
            handler()
            self.status.set("Ready.")
