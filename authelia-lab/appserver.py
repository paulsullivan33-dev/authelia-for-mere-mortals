#!/usr/bin/env python3
"""The lab's pretend applications: one tiny server behind nginx for every site.
It answers with the name of the site, the path, and the identity headers
nginx passed on after asking Authelia - exactly what a real app would read."""
from http.server import BaseHTTPRequestHandler, HTTPServer

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        user = self.headers.get('Remote-User') or '(nobody - anonymous)'
        groups = self.headers.get('Remote-Groups') or '(none)'
        body = (f"APP PAGE\n"
                f"site: {self.headers.get('Host')}\n"
                f"path: {self.path}\n"
                f"user: {user}\n"
                f"groups: {groups}\n").encode()
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    def log_message(self, *args):
        pass

HTTPServer(('127.0.0.1', 8000), Handler).serve_forever()
