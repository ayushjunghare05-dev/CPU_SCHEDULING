"""CPU Scheduling Simulator - local, dependency-free web server."""
from __future__ import annotations

import os
import json
import mimetypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

from scheduler import _normalise_processes, fcfs, sjf_non_preemptive, round_robin

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", "5000"))


class SimulatorHandler(BaseHTTPRequestHandler):
    server_version = "SchedLab/1.0"

    def _send_bytes(self, status: int, content: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(content)

    def _send_json(self, status: int, payload: dict) -> None:
        content = json.dumps(payload).encode("utf-8")
        self._send_bytes(status, content, "application/json; charset=utf-8")

    def do_GET(self) -> None:  # noqa: N802 - stdlib handler method name
        path = urlparse(self.path).path
        if path == "/" or path == "/index.html":
            target = STATIC_DIR / "index.html"
        elif path.startswith("/static/"):
            relative = unquote(path[len("/static/"):])
            target = (STATIC_DIR / relative).resolve()
            if not target.is_relative_to(STATIC_DIR.resolve()):
                self._send_json(403, {"error": "Path is not allowed."})
                return
        else:
            self._send_json(404, {"error": "Page not found."})
            return

        if not target.is_file():
            self._send_json(404, {"error": "File not found."})
            return
        content_type = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
        if content_type.startswith("text/") or content_type in ("application/javascript", "application/json"):
            content_type += "; charset=utf-8"
        self._send_bytes(200, target.read_bytes(), content_type)

    def do_POST(self) -> None:  # noqa: N802 - stdlib handler method name
        if urlparse(self.path).path != "/api/simulate":
            self._send_json(404, {"error": "API endpoint not found."})
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > 1_000_000:
                raise ValueError("Request must contain a small JSON body.")
            body = json.loads(self.rfile.read(length).decode("utf-8"))
            if not isinstance(body, dict):
                raise ValueError("Request body must be a JSON object.")
            processes = _normalise_processes(body.get("processes"))
            try:
                quantum = int(body.get("time_quantum", 2))
            except (TypeError, ValueError):
                raise ValueError("Time quantum must be a positive whole number.")
            if quantum <= 0 or quantum > 10000:
                raise ValueError("Time quantum must be a whole number from 1 to 10,000.")

            results = [fcfs(processes), sjf_non_preemptive(processes), round_robin(processes, quantum)]
            waiting_winner = min(results, key=lambda r: r["metrics"]["average_waiting_time"])
            turnaround_winner = min(results, key=lambda r: r["metrics"]["average_turnaround_time"])
            self._send_json(200, {
                "results": results,
                "time_quantum": quantum,
                "insights": {
                    "best_average_waiting_time": waiting_winner["algorithm"],
                    "best_average_turnaround_time": turnaround_winner["algorithm"],
                    "note": "The best result depends on the selected processes and Round Robin time quantum.",
                },
            })
        except (ValueError, json.JSONDecodeError, UnicodeDecodeError) as exc:
            self._send_json(400, {"error": str(exc) or "Invalid request body."})
        except Exception as exc:
            self.log_error("Unexpected simulation error: %s", repr(exc))
            self._send_json(500, {"error": "An unexpected error occurred. Check the input and try again."})

    def log_message(self, format_string: str, *args) -> None:
        # Keep the local console output short and avoid noisy per-file logs.
        print(f"[{self.log_date_time_string()}] {format_string % args}")


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), SimulatorHandler)
    print("\nSchedLab CPU Scheduling Simulator")
    print(f"Open http://{HOST}:{PORT} in your browser.")
    print("Press Ctrl+C to stop the server.\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping SchedLab…")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
