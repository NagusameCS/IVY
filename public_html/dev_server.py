#!/usr/bin/env python3
"""
IVYSTUDY Development Server
Serves static files and handles the view counter API locally
"""

import http.server
import socketserver
import urllib.parse
import os
import sys

# Import the WSGI application
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))
try:
    from application import application as wsgi_app
except ImportError:
    print("Warning: Could not import WSGI application. API endpoints will not work.")
    wsgi_app = None

class IVYSTUDYRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Set the directory to serve files from
        super().__init__(*args, directory='/Users/user/Downloads/public_html', **kwargs)
    
    def do_GET(self):
        # Handle API requests
        if self.path.startswith('/api/') and wsgi_app:
            self.handle_wsgi()
            return
        
        # Handle root path - serve the resources/search page
        if self.path == '/':
            self.path = '/index.html'
        # Handle clean URLs - try .shtml then .html
        elif self.path == '/home':
            self.path = '/home/index.html'
        elif self.path == '/timer':
            self.path = '/timer/index.html'
        elif self.path == '/teachers':
            self.path = '/teachers/index.html'
        elif self.path == '/exemplars':
            self.path = '/exemplars/index.html'
        elif self.path == '/overview':
            self.path = '/overview/index.html'
        elif self.path == '/info':
            self.path = '/info/index.html'
        
        # Handle other directory paths
        parsed_path = urllib.parse.urlparse(self.path)
        clean_path = parsed_path.path
        
        # Check if it's a directory request that should serve index.html
        local_path = os.path.join('/Users/user/Downloads/public_html', clean_path.lstrip('/'))
        if os.path.isdir(local_path):
            index_file = os.path.join(local_path, 'index.html')
            if os.path.exists(index_file):
                self.path = clean_path.rstrip('/') + '/index.html'
        
        # Serve static files
        return super().do_GET()
    
    def do_OPTIONS(self):
        # Handle preflight requests for API
        if self.path.startswith('/api/'):
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            return
        
        return super().do_GET()
    
    def handle_wsgi(self):
        """Handle WSGI application requests"""
        try:
            # Parse the request
            parsed_path = urllib.parse.urlparse(self.path)
            
            # Create WSGI environ
            environ = {
                'REQUEST_METHOD': self.command,
                'PATH_INFO': parsed_path.path,
                'QUERY_STRING': parsed_path.query,
                'CONTENT_TYPE': self.headers.get('content-type', ''),
                'CONTENT_LENGTH': self.headers.get('content-length', ''),
                'SERVER_NAME': self.server.server_address[0],
                'SERVER_PORT': str(self.server.server_address[1]),
                'REMOTE_ADDR': self.client_address[0],
                'HTTP_X_FORWARDED_FOR': self.headers.get('x-forwarded-for', ''),
                'wsgi.version': (1, 0),
                'wsgi.url_scheme': 'http',
                'wsgi.input': self.rfile,
                'wsgi.errors': sys.stderr,
                'wsgi.multithread': True,
                'wsgi.multiprocess': False,
                'wsgi.run_once': False,
            }
            
            # Add all HTTP headers to environ
            for header, value in self.headers.items():
                header = header.upper().replace('-', '_')
                if header not in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
                    environ[f'HTTP_{header}'] = value
            
            # Response data
            response_data = []
            response_status = '500 Internal Server Error'
            response_headers = []
            
            def start_response(status, headers, exc_info=None):
                nonlocal response_status, response_headers
                response_status = status
                response_headers = headers
            
            # Call WSGI application
            app_iter = wsgi_app(environ, start_response)
            try:
                for data in app_iter:
                    response_data.append(data)
            finally:
                if hasattr(app_iter, 'close'):
                    app_iter.close()
            
            # Send response
            status_code = int(response_status.split(' ', 1)[0])
            self.send_response(status_code)
            
            for header_name, header_value in response_headers:
                self.send_header(header_name, header_value)
            
            self.end_headers()
            
            for data in response_data:
                self.wfile.write(data)
                
        except Exception as e:
            print(f"WSGI Error: {e}")
            self.send_error(500, f"WSGI Error: {e}")
    
    def log_message(self, format, *args):
        """Custom log format"""
        print(f"[{self.log_date_time_string()}] {format % args}")

def main():
    PORT = 8080
    
    print("IVYSTUDY Development Server")
    print("=" * 50)
    print(f"Starting server on http://localhost:{PORT}")
    print(f"Serving files from: /Users/user/Downloads/public_html")
    print("")
    print("Available URLs:")
    print(f"  Home page:      http://localhost:{PORT}/")
    print(f"  Main lessons:   http://localhost:{PORT}/index.html")
    print(f"  Timer:          http://localhost:{PORT}/timer/")
    print(f"  Class Overview: http://localhost:{PORT}/overview/")
    print(f"  Exemplars:      http://localhost:{PORT}/exemplars/")
    print(f"  For Educators:  http://localhost:{PORT}/teachers/")
    print(f"  Stats:          http://localhost:{PORT}/info/")
    print(f"  View Counter:   http://localhost:{PORT}/api/")
    print("")
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        with socketserver.TCPServer(("", PORT), IVYSTUDYRequestHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"Error: Port {PORT} is already in use.")
            print("Try a different port or stop the existing server.")
        else:
            print(f"Error starting server: {e}")

if __name__ == "__main__":
    main()