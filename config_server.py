# Import necessary modules.
import http.server  # For creating the HTTP server.
import socketserver  # Handling socket-level operations for the server.
import configparser  # To read and write configuration settings.
from urllib.parse import parse_qs  # To parse POST data.

# Define constants.
PORT = 8080  # Port on which the server will listen.
CONFIG_FILE = "IceColdSettings.conf"  # The configuration file we'll update.

# CustomHandler inherits from SimpleHTTPRequestHandler and lets us define our own GET and POST behavior.
class CustomHandler(http.server.SimpleHTTPRequestHandler):
    # This method handles GET requests.
    def do_GET(self):
        # If the path is the root, we'll display the configuration form.
        if self.path == "/":
            # Open the configuration file and read its content.
            with open(CONFIG_FILE, 'r') as f:
                config = configparser.ConfigParser()
                config.read_file(f)
                settings = dict(config['General'])  # Convert the 'General' section to a dictionary.

            # Open our HTML file and format it using the settings.
            with open('config.html', 'r') as f:
                html = f.read().format(**settings)
                # Send a 200 OK response with the formatted HTML.
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(html.encode())
        else:
            # If the path isn't root, send a 404 not found response.
            self.send_response(404)
            self.end_headers()

    # This method handles POST requests.
    def do_POST(self):
        # The update path is used to update the configuration.
        if self.path == "/update":
            # Parse the POST data.
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            settings = parse_qs(post_data)

            # Update our configuration file with the new settings.
            config = configparser.ConfigParser()
            config['General'] = {k: v[0] for k, v in settings.items()}  # Transform settings into a suitable format.

            # Save the updated settings to the configuration file.
            with open(CONFIG_FILE, 'w') as f:
                config.write(f)

            # Redirect the user back to the root (so they see the form again).
            self.send_response(302)
            self.send_header('Location', '/')
            self.end_headers()
        else:
            # If the path isn't "/update", send a 404 not found response.
            self.send_response(404)
            self.end_headers()

# Create and start the HTTP server.
# '0.0.0.0' means it will listen on all available network interfaces, making it accessible from other devices on the same network.
with socketserver.TCPServer(("0.0.0.0", PORT), CustomHandler) as httpd:
    print(f"Serving at http://0.0.0.0:{PORT}")
    httpd.serve_forever()  # Run the server indefinitely.
