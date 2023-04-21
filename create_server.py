import threading
import http.server
import socketserver

def serve_on_port(port):
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), Handler) as httpd:
        httpd.serve_forever()

ports = [21,85,25565,8080, 8081, 8082, 8083] # List of ports to create servers on

print("Starting servers... on ")
for port in ports:
    thread = threading.Thread(target=serve_on_port, args=[port])
    thread.start()

print("Servers started")