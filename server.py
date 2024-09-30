import os
from http.server import SimpleHTTPRequestHandler, HTTPServer
import urllib.parse

# Set the directory you want to serve files from
DIRECTORY = './imgs'

class CustomHandler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        # Serve files directly from the specified directory
        if path == '/':
            path = '/index.html'  # Default path when accessing root
        return os.path.join(DIRECTORY, urllib.parse.unquote(path.lstrip('/')))

    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(self.upload_form().encode('utf-8'))
        else:
            # Serve the file from the directory if the path is not root
            super().do_GET()

    def upload_form(self):
        files_list = self.list_files()
        return f'''<!DOCTYPE html>
<html>
<head>
    <title>Upload File</title>
</head>
<body>
    <h2>Upload File</h2>
    <form method="POST" enctype="multipart/form-data">
        <input type="file" name="file">
        <input type="submit" value="Upload">
    </form>
    <h2>Uploaded Files</h2>
    <ul>
        {files_list}
    </ul>
</body>
</html>
'''

    def list_files(self):
        files = os.listdir(DIRECTORY)
        file_links = ""
        for filename in files:
            file_links += f'<li><a href="{filename}">{filename}</a></li>'
        return file_links if file_links else '<li>No files uploaded yet.</li>'

    def do_POST(self):
        if self.path == '/':
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)

            # Parse the uploaded file
            boundary = self.headers['Content-Type'].split('=')[1].encode()
            parts = body.split(boundary)[1:-1]
            for part in parts:
                if b'filename' in part:
                    filename = self.get_filename(part)
                    file_data = self.get_file_data(part)
                    self.save_file(filename, file_data)

            self.send_response(303)
            self.send_header('Location', '/')
            self.end_headers()

    def get_filename(self, part):
        header, _ = part.split(b'\r\n\r\n', 1)
        for line in header.decode().splitlines():
            if 'filename' in line:
                return urllib.parse.unquote(line.split('filename=')[1].strip('"'))
        return None

    def get_file_data(self, part):
        _, data = part.split(b'\r\n\r\n', 1)
        return data.rsplit(b'\r\n', 1)[0]

    def save_file(self, filename, file_data):
        with open(os.path.join(DIRECTORY, filename), 'wb') as f:
            f.write(file_data)

def run(server_class=HTTPServer, handler_class=CustomHandler, port=8000):
    # Check if the directory exists and create it if it doesn't
    os.makedirs(DIRECTORY, exist_ok=True)
    
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Serving files from {DIRECTORY} at http://localhost:{port}')
    httpd.serve_forever()

if __name__ == "__main__":
    run()
