#!/usr/bin/env python3
"""
Lightweight Web Console Server for ParaGravity.
Serves the React dashboard and provides a REST API using only the Python standard library.
"""

import os
import sys
import json
import mimetypes
import webbrowser
import subprocess
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, unquote

REPO_ROOT = Path(__file__).resolve().parent.parent
DASHBOARD_DIST = REPO_ROOT / "dashboard" / "dist"
CLI_PATH = REPO_ROOT / "bin" / "paragravity"

class ParaGravityHandler(BaseHTTPRequestHandler):
    def end_headers(self):
        # Disable caching for dynamic dev API
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/profiles":
            self.handle_get_profiles()
            return
        elif path == "/api/system":
            self.send_json({
                "version": "1.0.0",
                "theme": "dawn-iris",
                "themeName": "晨曦紫霞白 (Dawn Iris & Violet)",
                "platform": sys.platform,
            })
            return

        # Static file serving
        self.serve_static(path)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/profiles":
            self.handle_create_profile()
            return

        # POST /api/batch/launch
        if path == "/api/batch/launch":
            self.handle_batch_launch()
            return

        # POST /api/batch/stop
        if path == "/api/batch/stop":
            self.handle_batch_stop()
            return

        # POST /api/tile
        if path == "/api/tile":
            self.handle_tile_windows()
            return

        # POST /api/profiles/<name>/launch
        parts = [p for p in path.split("/") if p]
        if len(parts) == 4 and parts[0] == "api" and parts[1] == "profiles" and parts[3] == "launch":
            name = unquote(parts[2])
            self.handle_launch_profile(name)
            return

        # POST /api/profiles/<name>/stop
        if len(parts) == 4 and parts[0] == "api" and parts[1] == "profiles" and parts[3] == "stop":
            name = unquote(parts[2])
            self.handle_stop_profile(name)
            return

        self.send_error(404, "Endpoint not found")

    def do_DELETE(self):
        parsed = urlparse(self.path)
        parts = [p for p in parsed.path.split("/") if p]
        if len(parts) == 3 and parts[0] == "api" and parts[1] == "profiles":
            name = unquote(parts[2])
            self.handle_delete_profile(name)
            return

        self.send_error(404, "Endpoint not found")

    def handle_get_profiles(self):
        try:
            out = subprocess.check_output([sys.executable, str(CLI_PATH), "list", "--json"], text=True)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(out.strip().encode("utf-8"))
        except Exception as e:
            self.send_json({"error": str(e)}, status=500)

    def handle_create_profile(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8")
            data = json.loads(body or "{}")
            name = data.get("name", "").strip()
            desc = data.get("description", "")
            launch = data.get("launch", False)

            if not name:
                self.send_json({"error": "Profile name is required"}, status=400)
                return

            cmd = [sys.executable, str(CLI_PATH), "create", name]
            if desc:
                cmd.extend(["-d", desc])
            if launch:
                cmd.append("-l")

            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode == 0:
                self.send_json({"success": True, "output": res.stdout})
            else:
                self.send_json({"error": res.stderr or res.stdout or "Failed to create profile"}, status=400)
        except Exception as e:
            self.send_json({"error": str(e)}, status=500)

    def handle_launch_profile(self, name: str):
        try:
            res = subprocess.run([sys.executable, str(CLI_PATH), "launch", name], capture_output=True, text=True)
            if res.returncode == 0:
                self.send_json({"success": True, "output": res.stdout})
            else:
                self.send_json({"error": res.stderr or res.stdout or "Failed to launch"}, status=400)
        except Exception as e:
            self.send_json({"error": str(e)}, status=500)

    def handle_stop_profile(self, name: str):
        try:
            res = subprocess.run([sys.executable, str(CLI_PATH), "stop", name, "--force"], capture_output=True, text=True)
            if res.returncode == 0:
                self.send_json({"success": True, "output": res.stdout})
            else:
                self.send_json({"error": res.stderr or res.stdout or "Failed to stop"}, status=400)
        except Exception as e:
            self.send_json({"error": str(e)}, status=500)

    def handle_delete_profile(self, name: str):
        try:
            res = subprocess.run([sys.executable, str(CLI_PATH), "delete", name, "-f"], capture_output=True, text=True)
            if res.returncode == 0:
                self.send_json({"success": True, "output": res.stdout})
            else:
                self.send_json({"error": res.stderr or res.stdout or "Failed to delete"}, status=400)
        except Exception as e:
            self.send_json({"error": str(e)}, status=500)

    def handle_batch_launch(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8")
            data = json.loads(body or "{}")
            names = data.get("names", [])
            results = []
            for name in names:
                res = subprocess.run([sys.executable, str(CLI_PATH), "launch", name], capture_output=True, text=True)
                results.append({
                    "name": name,
                    "success": res.returncode == 0,
                    "output": (res.stdout or res.stderr or "").strip()
                })
            self.send_json({"success": True, "results": results})
        except Exception as e:
            self.send_json({"error": str(e)}, status=500)

    def handle_batch_stop(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8")
            data = json.loads(body or "{}")
            names = data.get("names", [])
            results = []
            for name in names:
                res = subprocess.run([sys.executable, str(CLI_PATH), "stop", name, "--force"], capture_output=True, text=True)
                results.append({
                    "name": name,
                    "success": res.returncode == 0,
                    "output": (res.stdout or res.stderr or "").strip()
                })
            self.send_json({"success": True, "results": results})
        except Exception as e:
            self.send_json({"error": str(e)}, status=500)

    def handle_tile_windows(self):
        if sys.platform != "darwin":
            self.send_json({"success": False, "message": "Window tiling is supported on macOS only."}, status=400)
            return

        script = """
        tell application "Finder"
            set b to bounds of window of desktop
            set screenW to item 3 of b
            set screenH to item 4 of b
        end tell

        tell application "System Events"
            set appProcs to (every application process whose name contains "Antigravity")
            set allWins to {}
            repeat with p in appProcs
                try
                    set winList to every window of p
                    repeat with w in winList
                        set end of allWins to {proc:p, win:w}
                    end repeat
                end try
            end repeat
            
            set winCount to count of allWins
            if winCount is 0 then return "no_windows"
            
            if winCount is 1 then
                set wObj to item 1 of allWins
                set position of (win of wObj) to {60, 60}
                set size of (win of wObj) to {screenW - 120, screenH - 120}
            else if winCount is 2 then
                set halfW to (screenW / 2) as integer
                set w1 to item 1 of allWins
                set w2 to item 2 of allWins
                set position of (win of w1) to {0, 30}
                set size of (win of w1) to {halfW, screenH - 30}
                set position of (win of w2) to {halfW, 30}
                set size of (win of w2) to {halfW, screenH - 30}
            else if winCount is 3 then
                set thirdW to (screenW / 3) as integer
                repeat with i from 1 to 3
                    set wObj to item i of allWins
                    set position of (win of wObj) to {((i - 1) * thirdW), 30}
                    set size of (win of wObj) to {thirdW, screenH - 30}
                end repeat
            else
                set halfW to (screenW / 2) as integer
                set halfH to ((screenH - 30) / 2) as integer
                set coords to {{0, 30}, {halfW, 30}, {0, 30 + halfH}, {halfW, 30 + halfH}}
                repeat with i from 1 to 4
                    if i <= winCount then
                        set wObj to item i of allWins
                        set c to item i of coords
                        set position of (win of wObj) to c
                        set size of (win of wObj) to {halfW, halfH}
                    end if
                end repeat
            end if
            return "ok"
        end tell
        """
        try:
            res = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=5)
            if res.returncode == 0:
                self.send_json({"success": True, "output": res.stdout.strip()})
            else:
                self.send_json({"success": False, "error": res.stderr.strip() or "Window tiling requires Accessibility permission."})
        except Exception as e:
            self.send_json({"success": False, "error": str(e)})

    def serve_static(self, path: str):
        if not DASHBOARD_DIST.exists():
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            html = """
            <html>
            <body style="font-family:sans-serif;padding:40px;background:#F8F9FD;color:#1E1B4B;">
                <h2>🌌 ParaGravity Web Console</h2>
                <p>前端静态资源未构建。请在 <code>dashboard/</code> 目录运行以下命令进行构建：</p>
                <pre style="background:#EEF2FF;padding:15px;border-radius:8px;">cd dashboard && npm install && npm run build</pre>
                <p>或在开发时运行 <code>npm run dev</code> 开启实时热重载模式。</p>
            </body>
            </html>
            """
            self.wfile.write(html.encode("utf-8"))
            return

        rel_path = path.lstrip("/")
        target = DASHBOARD_DIST / rel_path

        # SPA fallback to index.html if file doesn't exist
        if not target.is_file():
            target = DASHBOARD_DIST / "index.html"

        content_type, _ = mimetypes.guess_type(str(target))
        content_type = content_type or "application/octet-stream"

        try:
            data = target.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        except Exception as e:
            self.send_error(500, f"Error reading file: {e}")

    def send_json(self, data: dict, status: int = 200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        # Clean terminal logging
        pass

def start_server(port: int = 3888, open_browser: bool = True):
    server_address = ("127.0.0.1", port)
    httpd = HTTPServer(server_address, ParaGravityHandler)
    url = f"http://127.0.0.1:{port}"
    print(f"\033[36m🌌 ParaGravity Web Console 已启动：\033[0m \033[1m{url}\033[0m")
    print("  • 主题风格: \033[35m晨曦紫霞白 (Dawn Iris & Violet)\033[0m")
    print("  • 退出服务: 按 \033[1mCtrl + C\033[0m\n")

    if open_browser:
        webbrowser.open(url)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\033[33mWeb Console 已停止。\033[0m")
        httpd.server_close()

if __name__ == "__main__":
    port = 3888
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        port = int(sys.argv[1])
    start_server(port)
