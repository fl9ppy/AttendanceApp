import http.server
import socketserver
import webbrowser
import os

# Set the directory to the path where your HTML file is located
directory = r'C:\Users\Alex\Documents\GitHub\AttendanceApp\site'

# Set the port for the server
port = 8000

# Change the working directory to the specified directory
os.chdir(directory)

# Define the handler to use, in this case, the SimpleHTTPRequestHandler
handler = http.server.SimpleHTTPRequestHandler

# Create the server
httpd = socketserver.TCPServer(("", port), handler)

# Print a message indicating the server is running
print(f"Serving on port {port}...")

# Open the default web browser to the specified URL
webbrowser.open(f"http://localhost:{port}/site_unihack.html")

# Start the server
httpd.serve_forever()
