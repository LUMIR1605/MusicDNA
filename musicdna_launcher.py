"""Small Windows-first desktop launcher for the existing MusicDNA pipeline."""

from __future__ import annotations

import os
import queue
import sys
import threading
import traceback
import webbrowser
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.ingestion import IngestionError, IngestionResult
from core.launcher_service import run_add, validate_add_url
from core.paths import data_root, ensure_directory
from core.publication import PublicationError, publication_status_label, publish_pending_results
from core.runtime import RuntimeCapabilityError

try:
    import tkinter as tk
    from tkinter import messagebox, scrolledtext
except ImportError:  # pragma: no cover - covered by the Windows startup fallback.
    tk = None
    messagebox = None
    scrolledtext = None


def open_report(report_path: Path) -> None:
    """Open a completed local report with the operating system default handler."""

    path = Path(report_path).resolve()
    if sys.platform == "win32" and hasattr(os, "startfile"):
        os.startfile(str(path))
        return
    webbrowser.open(path.as_uri())


def copy_report_path(root: tk.Misc, report_path: Path) -> None:
    """Put a completed report-workspace path on the desktop clipboard."""

    root.clipboard_clear()
    root.clipboard_append(str(Path(report_path).resolve()))
    root.update()


def can_close_launcher(job_running: bool, cancellation_confirmed: bool = False) -> bool:
    """Return whether the launcher can close without silently interrupting a job."""

    return not job_running or cancellation_confirmed


def diagnostic_log_path() -> Path:
    """Return the local, cross-platform path for launcher diagnostic logs."""

    return data_root() / "logs" / "launcher-errors.log"


def _root_cause(error: BaseException) -> BaseException:
    cause = error
    while cause.__cause__ is not None:
        cause = cause.__cause__
    return cause


def write_failure_log(error: BaseException) -> Path:
    """Append a complete exception chain without changing the user-facing error."""

    root = _root_cause(error)
    frames = traceback.extract_tb(root.__traceback__)
    failing_frame = frames[-1] if frames else None
    log_path = diagnostic_log_path()
    ensure_directory(log_path.parent)

    lines = [
        "MusicDNA launcher diagnostic",
        f"Timestamp (UTC): {datetime.now(timezone.utc).isoformat()}",
        f"Exception type: {type(root).__name__}",
        f"Exception message: {root}",
    ]
    if failing_frame is not None:
        lines.extend(
            [
                f"Failing module: {failing_frame.filename}",
                f"Failing function: {failing_frame.name}",
                f"Failing line number: {failing_frame.lineno}",
            ]
        )
    else:
        lines.append("Failing location: unavailable")

    lines.extend(["", "Full traceback:", "".join(traceback.format_exception(error)), "=" * 80, ""])
    with log_path.open("a", encoding="utf-8") as log_file:
        log_file.write("\n".join(lines))
    return log_path


if tk is not None:

    class MusicDNALauncher(tk.Tk):
        """Tkinter shell that keeps all ingestion work off the UI thread."""

        def __init__(self) -> None:
            super().__init__()
            self.title("MusicDNA")
            self.geometry("640x480")
            self.minsize(560, 410)
            self.configure(padx=24, pady=22, bg="#101820")

            self._events: queue.Queue[tuple[str, Any]] = queue.Queue()
            self._running = False
            self._closing = False
            self._workspace_path: Path | None = None
            self.url = tk.StringVar()
            self.status = tk.StringVar(value="Paste one YouTube video link to begin.")
            self.result = tk.StringVar(value="")
            self.publication = tk.StringVar(value=publication_status_label())

            self._build_ui()
            self.protocol("WM_DELETE_WINDOW", self._on_close_request)
            self.after(100, self._process_events)

        def _build_ui(self) -> None:
            title = tk.Label(
                self,
                text="MusicDNA",
                font=("Segoe UI", 22, "bold"),
                fg="#e8f4ff",
                bg="#101820",
            )
            title.pack(anchor="w")
            subtitle = tk.Label(
                self,
                text="Paste a YouTube video link. MusicDNA will save the sample and report locally.",
                font=("Segoe UI", 10),
                fg="#b7c9d8",
                bg="#101820",
                wraplength=570,
                justify="left",
            )
            subtitle.pack(anchor="w", pady=(4, 16))

            self.url_entry = tk.Entry(self, textvariable=self.url, font=("Segoe UI", 11))
            self.url_entry.pack(fill="x", ipady=7)
            self.url_entry.focus_set()

            self.start_button = tk.Button(
                self,
                text="START",
                command=self.start,
                font=("Segoe UI", 11, "bold"),
                bg="#1f9dce",
                fg="#ffffff",
                activebackground="#167aa2",
                activeforeground="#ffffff",
                relief="flat",
                padx=24,
                pady=9,
            )
            self.start_button.pack(anchor="w", pady=(14, 10))

            self.publish_button = tk.Button(
                self,
                text="PUBLISH PENDING RESULTS",
                command=self.publish_pending,
                font=("Segoe UI", 9, "bold"),
                bg="#27485a",
                fg="#e8f4ff",
                activebackground="#315d72",
                activeforeground="#ffffff",
                relief="flat",
                padx=14,
                pady=6,
            )
            self.publish_button.pack(anchor="w")
            tk.Label(
                self,
                textvariable=self.publication,
                font=("Segoe UI", 9),
                fg="#83d8a8",
                bg="#101820",
            ).pack(anchor="w", pady=(4, 10))

            tk.Label(
                self,
                textvariable=self.status,
                font=("Segoe UI", 10, "bold"),
                fg="#d9e8f2",
                bg="#101820",
                wraplength=570,
                justify="left",
            ).pack(anchor="w")
            tk.Label(
                self,
                textvariable=self.result,
                font=("Segoe UI", 9),
                fg="#83d8a8",
                bg="#101820",
                wraplength=570,
                justify="left",
            ).pack(anchor="w", pady=(4, 8))

            self.report_folder_button = tk.Button(
                self,
                text="OPEN REPORT FOLDER",
                command=self.open_report_folder,
                state="disabled",
                font=("Segoe UI", 9, "bold"),
                bg="#27485a",
                fg="#e8f4ff",
                relief="flat",
                padx=12,
                pady=5,
            )
            self.report_folder_button.pack(anchor="w")
            self.report_button = tk.Button(
                self,
                text="OPEN REPORT",
                command=self.open_workspace_report,
                state="disabled",
                font=("Segoe UI", 9, "bold"),
                bg="#27485a",
                fg="#e8f4ff",
                relief="flat",
                padx=12,
                pady=5,
            )
            self.report_button.pack(anchor="w", pady=(4, 0))
            self.copy_report_path_button = tk.Button(
                self,
                text="COPY REPORT PATH",
                command=self.copy_workspace_path,
                state="disabled",
                font=("Segoe UI", 9, "bold"),
                bg="#27485a",
                fg="#e8f4ff",
                relief="flat",
                padx=12,
                pady=5,
            )
            self.copy_report_path_button.pack(anchor="w", pady=(4, 10))

            self.progress = scrolledtext.ScrolledText(
                self,
                height=10,
                font=("Consolas", 9),
                bg="#071018",
                fg="#c9d9e6",
                insertbackground="#c9d9e6",
                relief="flat",
                state="disabled",
            )
            self.progress.pack(fill="both", expand=True)

        def _append_progress(self, message: str) -> None:
            self.progress.configure(state="normal")
            self.progress.insert("end", f"{message}\n")
            self.progress.see("end")
            self.progress.configure(state="disabled")

        def start(self) -> None:
            if self._running:
                return
            url = self.url.get().strip()
            try:
                validate_add_url(url)
            except IngestionError as error:
                self.status.set("The YouTube link needs attention.")
                messagebox.showerror("MusicDNA", str(error), parent=self)
                return

            self._running = True
            self.start_button.configure(state="disabled")
            self.publish_button.configure(state="disabled")
            self._set_workspace_controls(None)
            self.result.set("")
            self.status.set("Starting MusicDNA...")
            self._append_progress("Starting MusicDNA...")
            threading.Thread(target=self._run_pipeline, args=(url,), daemon=True).start()

        def publish_pending(self) -> None:
            if self._running:
                return
            self._running = True
            self.start_button.configure(state="disabled")
            self.publish_button.configure(state="disabled")
            self.result.set("")
            self.status.set("Publishing completed MusicDNA results...")
            self._append_progress("Publishing completed MusicDNA results...")
            threading.Thread(target=self._run_publication, daemon=True).start()

        def _run_pipeline(self, url: str) -> None:
            try:
                result = run_add(url, lambda message: self._events.put(("progress", message)))
            except (IngestionError, RuntimeCapabilityError) as error:
                self._events.put(("error", (str(error), write_failure_log(error))))
            except Exception as error:
                self._events.put(
                    (
                        "error",
                        (
                            "MusicDNA could not finish this job. Please try again.",
                            write_failure_log(error),
                        ),
                    )
                )
            else:
                self._events.put(("success", result))

        def _run_publication(self) -> None:
            try:
                result = publish_pending_results(
                    lambda message: self._events.put(("progress", message))
                )
            except (PublicationError, RuntimeCapabilityError) as error:
                self._events.put(("error", (str(error), write_failure_log(error))))
            except Exception as error:
                self._events.put(
                    (
                        "error",
                        (
                            "MusicDNA could not publish pending results. Please try again.",
                            write_failure_log(error),
                        ),
                    )
                )
            else:
                self._events.put(("publication_success", result))

        def _on_close_request(self) -> None:
            if can_close_launcher(self._running):
                self.destroy()
                return

            close_now = messagebox.askyesno(
                "MusicDNA",
                "MusicDNA is still processing this job. Closing now will interrupt the "
                "download, analysis, or report save.\n\nClose anyway?",
                default="no",
                parent=self,
            )
            if can_close_launcher(self._running, close_now):
                self._closing = True
                self.destroy()

        def _process_events(self) -> None:
            if self._closing:
                return
            try:
                while True:
                    event, value = self._events.get_nowait()
                    if event == "progress":
                        self.status.set(str(value))
                        self._append_progress(str(value))
                    elif event == "error":
                        self._finish_with_error(*value)
                    elif event == "success":
                        self._finish_with_success(value)
                    elif event == "publication_success":
                        self._finish_with_publication(value)
            except queue.Empty:
                pass
            self.after(100, self._process_events)

        def _finish_with_error(self, message: str, log_path: Path) -> None:
            self._running = False
            self.start_button.configure(state="normal")
            self.publish_button.configure(state="normal")
            self.status.set("MusicDNA could not finish the job.")
            self._append_progress(f"Error: {message}")
            log_message = f"Diagnostic log: {log_path}"
            self.result.set(log_message)
            self._append_progress(log_message)
            self._refresh_publication_status()
            messagebox.showerror("MusicDNA", f"{message}\n\n{log_message}", parent=self)

        def _set_workspace_controls(self, workspace_path: Path | None) -> None:
            self._workspace_path = workspace_path
            state = "normal" if workspace_path is not None else "disabled"
            self.report_folder_button.configure(state=state)
            self.report_button.configure(state=state)
            self.copy_report_path_button.configure(state=state)

        def open_report_folder(self) -> None:
            if self._workspace_path is not None:
                open_report(self._workspace_path)

        def open_workspace_report(self) -> None:
            if self._workspace_path is not None:
                open_report(self._workspace_path / "summary.md")

        def copy_workspace_path(self) -> None:
            if self._workspace_path is not None:
                copy_report_path(self, self._workspace_path)
                self.status.set("Report path copied.")

        def _finish_with_success(self, result: IngestionResult) -> None:
            self._running = False
            self.start_button.configure(state="normal")
            self.publish_button.configure(state="normal")
            self.status.set("Analysis complete")
            self._refresh_publication_status()
            self._set_workspace_controls(result.workspace_path)
            if result.report_path is None:
                self.result.set("No new report was created because this item is already known.")
                self._append_progress(self.result.get())
                return

            if result.workspace_path is not None:
                self.result.set(f"Report workspace: {result.workspace_path}")
            else:
                self.result.set(f"Report saved to: {result.report_path}")
            self._append_progress(self.result.get())
            try:
                open_report(result.workspace_path / "summary.md" if result.workspace_path else result.report_path)
            except OSError:
                self._append_progress("The report was saved, but Windows could not open it automatically.")
            messagebox.showinfo("MusicDNA", self.result.get(), parent=self)

        def _finish_with_publication(self, result: Any) -> None:
            self._running = False
            self.start_button.configure(state="normal")
            self.publish_button.configure(state="normal")
            self._refresh_publication_status()
            self.result.set(
                f"Published: {len(result.published)}. Already published: {len(result.already_published)}."
            )
            self.status.set("Publication completed." if not result.has_failures else "Publication needs attention.")
            self._append_progress(self.result.get())

        def _refresh_publication_status(self) -> None:
            self.publication.set(publication_status_label())

else:

    class MusicDNALauncher:  # pragma: no cover - only used without Tkinter.
        def __init__(self) -> None:
            raise RuntimeError("Tkinter is unavailable in this Python installation.")


def _show_tkinter_error() -> None:
    try:
        import ctypes

        ctypes.windll.user32.MessageBoxW(
            0,
            "MusicDNA needs the standard Tkinter component of Python. Reinstall Python with Tcl/Tk enabled.",
            "MusicDNA",
            0x10,
        )
    except Exception:
        pass


def main() -> int:
    if tk is None:
        _show_tkinter_error()
        return 2
    app = MusicDNALauncher()
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
