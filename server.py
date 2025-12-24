#!/usr/bin/env python3
"""
Simple HTTP server for WEEX API Documentation with CORS support.

Usage:
    python server.py [port]
    
Default port: 8080
Access documentation at: http://localhost:8080
"""

import http.server
import socketserver
import os
import sys

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8080

class CORSRequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP request handler with CORS headers."""
    
    def end_headers(self):
        """Add CORS headers to all responses."""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Access-Control-Expose-Headers', '*')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        super().end_headers()
    
    def do_OPTIONS(self):
        """Handle preflight CORS requests."""
        self.send_response(200)
        self.end_headers()
    
    def log_message(self, format, *args):
        """Custom logging format."""
        print(f"[{self.log_date_time_string()}] {format % args}")

def run_server():
    """Start the HTTP server."""
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    with socketserver.TCPServer(("", PORT), CORSRequestHandler) as httpd:
        print(f"""
╔══════════════════════════════════════════════════════════════════╗
║          WEEX Futures Trading API Documentation Server          ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  🚀 Server running at: http://localhost:{PORT:<22}║
║                                                                  ║
║  📖 Open the URL above in your browser to view the docs          ║
║  🔧 CORS headers enabled for API testing                         ║
║                                                                  ║
║  Press Ctrl+C to stop the server                                 ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
        """)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n👋 Server stopped. Goodbye!")
            sys.exit(0)

if __name__ == "__main__":
    run_server()

