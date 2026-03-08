#!/usr/bin/env python3
"""Agent local simple pour gérer un PC via commandes en langage naturel.

Fonctionnalités (MVP):
- infos système
- statut CPU/RAM/disque
- lister les processus actifs
- lancer une application/commande autorisée
- arrêter un processus par PID (avec confirmation)

Dépendance optionnelle: psutil
    pip install psutil
"""

from __future__ import annotations

import platform
import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path

try:
    import psutil  # type: ignore
except ImportError:  # pragma: no cover
    psutil = None

ALLOWED_APPS = {
    "notepad": ["notepad"],
    "calc": ["calc"],
    "explorer": ["explorer"],
    "terminal": ["cmd"],
    "vscode": ["code"],
}


@dataclass
class AgentResult:
    ok: bool
    message: str


class PCManagerAgent:
    def __init__(self, workspace: str | Path = ".") -> None:
        self.workspace = Path(workspace).resolve()

    def run(self) -> None:
        print("🤖 Agent PC prêt. Tape 'aide' pour les commandes, 'quit' pour sortir.")
        while True:
            user_input = input("\n> ").strip()
            if not user_input:
                continue
            if user_input.lower() in {"quit", "exit"}:
                print("👋 Fin de session.")
                break

            result = self.handle(user_input)
            prefix = "✅" if result.ok else "❌"
            print(f"{prefix} {result.message}")

    def handle(self, query: str) -> AgentResult:
        q = query.lower().strip()

        if q in {"aide", "help", "?"}:
            return AgentResult(True, self.help_text())
        if "infos" in q or "système" in q or "system" in q:
            return self.system_info()
        if "statut" in q or "cpu" in q or "ram" in q or "disque" in q:
            return self.system_status()
        if "process" in q or "tâches" in q or "taches" in q:
            return self.list_processes()
        if q.startswith("lance ") or q.startswith("ouvrir "):
            app = q.split(maxsplit=1)[1]
            return self.launch_app(app)
        if q.startswith("tue ") or q.startswith("kill "):
            pid_text = q.split(maxsplit=1)[1]
            return self.kill_process(pid_text)

        return AgentResult(False, "Commande inconnue. Tape 'aide' pour voir les options.")

    @staticmethod
    def help_text() -> str:
        return (
            "Commandes:\n"
            "- infos système\n"
            "- statut\n"
            "- processus\n"
            "- lance <notepad|calc|explorer|terminal|vscode>\n"
            "- tue <pid>\n"
            "- quit"
        )

    def system_info(self) -> AgentResult:
        uname = platform.uname()
        msg = (
            f"OS: {uname.system} {uname.release} | "
            f"Machine: {uname.machine} | "
            f"Processeur: {uname.processor or 'N/A'}"
        )
        return AgentResult(True, msg)

    def system_status(self) -> AgentResult:
        if psutil is None:
            return AgentResult(
                False,
                "Le module 'psutil' manque. Installe-le avec: pip install psutil",
            )
        cpu = psutil.cpu_percent(interval=0.3)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage(str(self.workspace.anchor))
        msg = (
            f"CPU: {cpu:.1f}% | RAM: {ram.percent:.1f}% "
            f"({ram.used // (1024**3)} / {ram.total // (1024**3)} Go) | "
            f"Disque: {disk.percent:.1f}%"
        )
        return AgentResult(True, msg)

    def list_processes(self) -> AgentResult:
        if psutil is None:
            return AgentResult(
                False,
                "Le module 'psutil' manque. Installe-le avec: pip install psutil",
            )

        processes = []
        for proc in psutil.process_iter(["pid", "name", "cpu_percent"]):
            info = proc.info
            processes.append((info.get("cpu_percent") or 0.0, info.get("pid"), info.get("name") or "?"))

        processes.sort(reverse=True)
        top = processes[:8]
        lines = [f"{pid:>6}  {cpu:>5.1f}%  {name}" for cpu, pid, name in top]
        return AgentResult(True, "Top processus CPU:\n" + "\n".join(lines))

    def launch_app(self, app_name: str) -> AgentResult:
        app = app_name.strip().lower()
        if app not in ALLOWED_APPS:
            allowed = ", ".join(sorted(ALLOWED_APPS))
            return AgentResult(False, f"Application non autorisée. Choix: {allowed}")

        cmd = ALLOWED_APPS[app]
        try:
            subprocess.Popen(cmd, cwd=str(self.workspace))
        except FileNotFoundError:
            quoted = shlex.join(cmd)
            return AgentResult(False, f"Commande introuvable sur ce système: {quoted}")

        return AgentResult(True, f"Application lancée: {app}")

    def kill_process(self, pid_text: str) -> AgentResult:
        if psutil is None:
            return AgentResult(False, "Le module 'psutil' manque. Installe-le avec: pip install psutil")
        if not pid_text.isdigit():
            return AgentResult(False, "PID invalide. Utilise: tue <pid>")

        pid = int(pid_text)
        try:
            proc = psutil.Process(pid)
        except psutil.NoSuchProcess:
            return AgentResult(False, f"Aucun processus avec PID {pid}")

        confirm = input(f"Confirmer arrêt de '{proc.name()}' (PID {pid}) ? [o/N]: ").strip().lower()
        if confirm not in {"o", "oui", "y", "yes"}:
            return AgentResult(False, "Action annulée.")

        proc.terminate()
        return AgentResult(True, f"Processus {pid} arrêté.")


if __name__ == "__main__":
    PCManagerAgent().run()
