from http.server import BaseHTTPRequestHandler, HTTPServer

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        print(self.requestline)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Hello, world!')

    def do_POST(self):
        print("AAYAYAYAYAYA")
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        print(self.requestline)
        print(body.decode('utf-8'))
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Hello, world!')

def run(server_class=HTTPServer, handler_class=RequestHandler):
    server_address = ('', 8000)
    httpd = server_class(server_address, handler_class)
    print('Starting httpd...')
    httpd.serve_forever()

run()