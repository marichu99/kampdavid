#!/usr/bin/env python3
"""
Static file server for the KampDavid Mall frontend.

Serves index.html and the photos/ directory from the project root.
Default: http://localhost:8000

Usage:
    python server.py           # port 8000
    python server.py 3000      # custom port
"""

import http.server
import socketserver
import sys
import os

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
ROOT = os.path.dirname(os.path.abspath(__file__))


class Handler(http.server.SimpleHTTPRequestHandler):
    """Serve files from the project root and return index.html for unknown paths."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def do_GET(self):
        # Serve index.html for the bare root path
        if self.path == "/":
            self.path = "/index.html"
        super().do_GET()

    def log_message(self, fmt, *args):
        # Cleaner log output
        print(f"  {self.address_string()}  {fmt % args}")


class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


if __name__ == "__main__":
    os.chdir(ROOT)
    with ReusableTCPServer(("", PORT), Handler) as httpd:
        print(f"Static server running at  http://localhost:{PORT}")
        print(f"Serving files from        {ROOT}")
        print("Press Ctrl+C to stop.\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")
