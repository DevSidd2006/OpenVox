#!/usr/bin/env python3
from __future__ import annotations

import os
import signal
import subprocess
import threading
import time
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path
import tkinter as tk
from tkinter import messagebox

ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT / ".env"


class DesktopApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("OpenVox Desktop")
        self.root.geometry("640x500")
        self.root.minsize(640, 500)

        self.api_proc: subprocess.Popen | None = None
        self.hotkey_proc: subprocess.Popen | None = None

        self.vars: dict[str, tk.StringVar] = {}

        self.status_var = tk.StringVar(value="Idle")
        self.health_var = tk.StringVar(value="API: unknown")

        self._build_ui()
        self._load_env()

        self._poll_thread = threading.Thread(target=self._health_poller, daemon=True)
        self._poll_thread.start()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self) -> None:
        frame = tk.Frame(self.root, padx=14, pady=12)
        frame.pack(fill="both", expand=True)

        title = tk.Label(frame, text="OpenVox Desktop Controller", font=("TkDefaultFont", 13, "bold"))
        title.pack(anchor="w")

        status = tk.Label(frame, textvariable=self.status_var)
        status.pack(anchor="w", pady=(6, 2))

        health = tk.Label(frame, textvariable=self.health_var, fg="#1f5f1f")
        health.pack(anchor="w", pady=(0, 10))

        btn_row = tk.Frame(frame)
        btn_row.pack(fill="x", pady=(0, 8))

        tk.Button(btn_row, text="Start Local Stack", command=self.start_local).pack(side="left", padx=4)
        tk.Button(btn_row, text="Stop Local Stack", command=self.stop_local).pack(side="left", padx=4)
        tk.Button(btn_row, text="Open Web UI", command=self.open_web).pack(side="left", padx=4)

        svc_row = tk.Frame(frame)
        svc_row.pack(fill="x", pady=(0, 14))
        tk.Button(svc_row, text="Install/Restart Services", command=self.install_services).pack(side="left", padx=4)
        tk.Button(svc_row, text="Start Services", command=self.start_services).pack(side="left", padx=4)
        tk.Button(svc_row, text="Stop Services", command=self.stop_services).pack(side="left", padx=4)

        form = tk.LabelFrame(frame, text="Core Settings (.env)", padx=10, pady=10)
        form.pack(fill="x", pady=(0, 10))

        keys = [
            "GROQ_API_KEY",
            "HOST",
            "PORT",
            "OPENVOX_API_URL",
            "OPENVOX_HOTKEY",
            "OPENVOX_AUTO_PASTE",
            "OPENVOX_INSERT_MODE",
            "OPENVOX_OVERLAY",
            "OPENVOX_STYLE",
            "OPENVOX_CONTEXT",
            "OPENVOX_LANGUAGE",
            "OPENVOX_AUDIO_FEEDBACK",
            "OPENVOX_OVERLAY_POSITION",
            "OPENVOX_VAD_ENABLED",
            "OPENVOX_VAD_SILENCE_TIMEOUT",
            "OPENVOX_VAD_AGGRESSIVENESS",
        ]

        for i, key in enumerate(keys):
            tk.Label(form, text=key, width=18, anchor="w").grid(row=i, column=0, sticky="w", pady=2)
            var = tk.StringVar(value="")
            self.vars[key] = var
            show = "*" if key == "GROQ_API_KEY" else ""
            tk.Entry(form, textvariable=var, width=56, show=show).grid(row=i, column=1, sticky="we", pady=2)

        form.grid_columnconfigure(1, weight=1)

        save_row = tk.Frame(frame)
        save_row.pack(fill="x")
        tk.Button(save_row, text="Save .env", command=self.save_env).pack(side="left", padx=4)
        tk.Button(save_row, text="Reload .env", command=self._load_env).pack(side="left", padx=4)

        note = tk.Label(
            frame,
            text="Tip: For global hotkeys in service mode, ensure pynput is installed in .venv (requirements-hotkey.txt).",
            fg="#4b5563",
            wraplength=600,
            justify="left",
        )
        note.pack(anchor="w", pady=(10, 0))

    def _load_env(self) -> None:
        env = {}
        if ENV_PATH.exists():
            for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()

        defaults = {
            "HOST": "127.0.0.1",
            "PORT": "18080",
            "OPENVOX_API_URL": "http://127.0.0.1:18080",
            "OPENVOX_HOTKEY": "ctrl+space",
            "OPENVOX_AUTO_PASTE": "true",
            "OPENVOX_INSERT_MODE": "paste",
            "OPENVOX_OVERLAY": "true",
            "OPENVOX_STYLE": "professional",
            "OPENVOX_CONTEXT": "email",
            "OPENVOX_LANGUAGE": "en",
            "OPENVOX_AUDIO_FEEDBACK": "true",
            "OPENVOX_OVERLAY_POSITION": "top-right",
            "OPENVOX_VAD_ENABLED": "true",
            "OPENVOX_VAD_SILENCE_TIMEOUT": "3",
            "OPENVOX_VAD_AGGRESSIVENESS": "2",
        }

        for key, var in self.vars.items():
            var.set(env.get(key, defaults.get(key, "")))

        self.status_var.set("Loaded .env")

    def save_env(self) -> None:
        if not ENV_PATH.exists():
            messagebox.showerror("Error", f"Missing {ENV_PATH}")
            return

        lines: list[str] = []
        existing_keys = set()

        for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.strip().startswith("#"):
                key = line.split("=", 1)[0].strip()
                if key in self.vars:
                    lines.append(f"{key}={self.vars[key].get().strip()}")
                    existing_keys.add(key)
                else:
                    lines.append(line)
            else:
                lines.append(line)

        for key, var in self.vars.items():
            if key not in existing_keys:
                lines.append(f"{key}={var.get().strip()}")

        ENV_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
        self.status_var.set("Saved .env")

    def _env_for_process(self) -> dict[str, str]:
        env = os.environ.copy()
        for key, var in self.vars.items():
            env[key] = var.get().strip()
        return env

    def start_local(self) -> None:
        env = self._env_for_process()
        if self.api_proc and self.api_proc.poll() is None:
            self.status_var.set("Local API already running")
        else:
            self.api_proc = subprocess.Popen(
                [str(ROOT / "scripts/start_prod.sh")],
                cwd=str(ROOT),
                env=env,
            )
            self.status_var.set("Started local API")

        venv_py = ROOT / ".venv/bin/python"
        if not venv_py.exists():
            messagebox.showwarning("Hotkey", "Missing .venv Python. Run scripts/bootstrap.sh first.")
            return

        hotkey_script = ROOT / "scripts/hotkey_push_to_talk.py"
        if self.hotkey_proc and self.hotkey_proc.poll() is None:
            return

        self.hotkey_proc = subprocess.Popen(
            [str(venv_py), str(hotkey_script)],
            cwd=str(ROOT),
            env=env,
        )
        self.status_var.set("Started local API + hotkey daemon")

    def stop_local(self) -> None:
        self._terminate_proc(self.hotkey_proc)
        self.hotkey_proc = None
        self._terminate_proc(self.api_proc)
        self.api_proc = None
        self.status_var.set("Stopped local processes")

    def _terminate_proc(self, proc: subprocess.Popen | None) -> None:
        if proc is None or proc.poll() is not None:
            return
        proc.terminate()
        try:
            proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            proc.send_signal(signal.SIGKILL)

    def open_web(self) -> None:
        port = self.vars.get("PORT", tk.StringVar(value="18080")).get().strip() or "18080"
        webbrowser.open(f"http://127.0.0.1:{port}")

    def _run_cmd(self, args: list[str]) -> tuple[int, str]:
        try:
            proc = subprocess.run(args, cwd=str(ROOT), capture_output=True, text=True)
            return proc.returncode, (proc.stdout + "\n" + proc.stderr).strip()
        except Exception as exc:
            return 1, str(exc)

    def install_services(self) -> None:
        code, out = self._run_cmd([str(ROOT / "scripts/install_user_service.sh")])
        if code == 0:
            self.status_var.set("Services installed/restarted")
        else:
            self.status_var.set("Service install failed")
            messagebox.showerror("Service Error", out)

    def start_services(self) -> None:
        code1, out1 = self._run_cmd(["systemctl", "--user", "start", "openvox-api.service"])
        code2, out2 = self._run_cmd(["systemctl", "--user", "start", "openvox-hotkey.service"])
        if code1 == 0:
            self.status_var.set("Requested service start")
        else:
            messagebox.showerror("Service Error", f"API start failed:\n{out1}\n\nHotkey output:\n{out2}")

    def stop_services(self) -> None:
        self._run_cmd(["systemctl", "--user", "stop", "openvox-hotkey.service"])
        self._run_cmd(["systemctl", "--user", "stop", "openvox-api.service"])
        self.status_var.set("Requested service stop")

    def _health_poller(self) -> None:
        while True:
            port = self.vars.get("PORT", tk.StringVar(value="18080")).get().strip() or "18080"
            url = f"http://127.0.0.1:{port}/api/health"
            ok = False
            try:
                with urllib.request.urlopen(url, timeout=1.2) as resp:
                    ok = resp.status == 200
            except Exception:
                ok = False

            def apply() -> None:
                self.health_var.set("API: healthy" if ok else "API: offline")

            self.root.after(0, apply)
            time.sleep(3)

    def _on_close(self) -> None:
        self.stop_local()
        self.root.destroy()


def main() -> None:
    root = tk.Tk()
    DesktopApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
