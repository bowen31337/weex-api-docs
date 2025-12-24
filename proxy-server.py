#!/usr/bin/env python3
"""
WEEX API Documentation Server with CORS Proxy and Authentication.

This server:
1. Serves the static documentation files
2. Proxies API requests to WEEX with HMAC-SHA256 signature generation
3. Bypasses CORS restrictions for browser testing

Usage:
    python proxy-server.py [port]
    
Default port: 8888
Access documentation at: http://localhost:8888
"""

import http.server
import socketserver
import os
import sys
import json
import hmac
import hashlib
import base64
import time
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from urllib.parse import urlparse

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8888
WEEX_API_BASE = "https://api-contract.weex.com"


def generate_signature(secret: str, timestamp: str, method: str, path: str, body: str = "") -> str:
    """Generate HMAC-SHA256 signature for WEEX API."""
    message = timestamp + method.upper() + path + body
    signature = base64.b64encode(
        hmac.new(secret.encode(), message.encode(), hashlib.sha256).digest()
    ).decode()
    return signature


class CORSProxyHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler with CORS support and API proxy with authentication."""

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

    def do_GET(self):
        """Handle GET requests - proxy API calls or serve static files."""
        if self.path.startswith('/capi/'):
            self._proxy_request('GET')
        else:
            super().do_GET()

    def do_POST(self):
        """Handle POST requests - proxy to WEEX API."""
        if self.path.startswith('/capi/'):
            self._proxy_request('POST')
        else:
            self.send_error(404, "Not Found")

    def _proxy_request(self, method):
        """Proxy request to WEEX API with authentication."""
        try:
            # Parse the path (may include query string)
            path_parts = self.path.split('?')
            base_path = path_parts[0]
            query_string = path_parts[1] if len(path_parts) > 1 else ""
            
            # Build target URL
            target_url = WEEX_API_BASE + self.path
            
            # Read request body for POST
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else ""
            
            # Get authentication headers from request
            api_key = self.headers.get('ACCESS-KEY', '')
            api_secret = self.headers.get('ACCESS-SIGN', '')  # Secret is passed as ACCESS-SIGN
            passphrase = self.headers.get('ACCESS-PASSPHRASE', '')
            
            # Build headers to forward
            forward_headers = {
                'Content-Type': 'application/json',
                'locale': self.headers.get('locale', 'en-US')
            }
            
            # Check if this is an authenticated request
            if api_key and api_secret and passphrase:
                # Generate timestamp
                timestamp = str(int(time.time() * 1000))
                
                # Build sign path (include query string for GET)
                if method.upper() == "GET" and query_string:
                    sign_path = base_path + "?" + query_string
                else:
                    sign_path = base_path
                
                # Generate signature
                sign_body = body if method.upper() == "POST" else ""
                signature = generate_signature(api_secret, timestamp, method, sign_path, sign_body)
                
                # Add auth headers
                forward_headers['ACCESS-KEY'] = api_key
                forward_headers['ACCESS-SIGN'] = signature
                forward_headers['ACCESS-PASSPHRASE'] = passphrase
                forward_headers['ACCESS-TIMESTAMP'] = timestamp
                
                print(f"🔐 Authenticated request: {method} {base_path}")
                print(f"   Timestamp: {timestamp}")
                print(f"   Sign path: {sign_path}")
            else:
                print(f"📊 Public request: {method} {base_path}")
            
            # Make request to WEEX API
            req = Request(
                target_url, 
                data=body.encode('utf-8') if body else None, 
                headers=forward_headers, 
                method=method
            )
            
            with urlopen(req, timeout=30) as response:
                response_body = response.read()
                
                self.send_response(response.status)
                self.send_header('Content-Type', response.getheader('Content-Type', 'application/json'))
                
                # Forward rate limit headers if present
                for header in ['X-RateLimit-Limit', 'X-RateLimit-Remaining', 'X-RateLimit-Reset']:
                    value = response.getheader(header)
                    if value:
                        self.send_header(header, value)
                
                self.end_headers()
                self.wfile.write(response_body)
                
                # Log successful request
                print(f"   ✅ Response: {response.status}")
                
        except HTTPError as e:
            error_body = e.read().decode('utf-8', errors='replace')
            self.send_response(e.code)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(error_body.encode())
            print(f"   ⚠️ API Error: {e.code} - {error_body[:100]}")
            
        except URLError as e:
            self.send_response(502)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            error_response = json.dumps({
                "code": "502",
                "msg": f"Failed to connect to WEEX API: {str(e.reason)}",
                "requestTime": None,
                "data": None
            })
            self.wfile.write(error_response.encode())
            print(f"   ❌ Connection Error: {e.reason}")
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            error_response = json.dumps({
                "code": "500",
                "msg": f"Proxy error: {str(e)}",
                "requestTime": None,
                "data": None
            })
            self.wfile.write(error_response.encode())
            print(f"   ❌ Proxy Error: {str(e)}")

    def log_message(self, format, *args):
        """Custom logging - suppress static file logs."""
        pass  # Suppress default logging, we handle it manually


def run_server():
    """Start the HTTP server with CORS proxy."""
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Allow socket reuse
    socketserver.TCPServer.allow_reuse_address = True
    
    with socketserver.TCPServer(("", PORT), CORSProxyHandler) as httpd:
        print(f"""
╔══════════════════════════════════════════════════════════════════════╗
║       WEEX Futures Trading API Documentation + Auth Proxy           ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  🚀 Server running at: http://localhost:{PORT:<25}║
║                                                                      ║
║  📖 Open the URL above in your browser to view the docs              ║
║  🔐 Authentication: Proxy generates HMAC-SHA256 signatures           ║
║  📡 API requests: /capi/* -> {WEEX_API_BASE}/capi/*                  ║
║                                                                      ║
║  💡 How to use:                                                      ║
║     1. Click "Authorize" in Swagger UI                               ║
║     2. Enter your API Key in WeexApiKey                              ║
║     3. Enter your API Secret in WeexApiSecret (ACCESS-SIGN field)    ║
║     4. Enter your Passphrase in WeexPassphrase                       ║
║     5. Click "Authorize" then "Close"                                ║
║     6. Use "Try it out" on any endpoint                              ║
║                                                                      ║
║  ⚠️  This proxy is for TESTING only.                                 ║
║                                                                      ║
║  Press Ctrl+C to stop the server                                     ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
        """)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n👋 Server stopped. Goodbye!")
            sys.exit(0)


if __name__ == "__main__":
    run_server()
