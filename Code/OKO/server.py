import os, http.server, socketserver, threading, time
PORT = int(os.getenv("PORT", "10000"))

class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args, **kwargs):  # тише логи
        pass

def run():
    import socketserver
socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        httpd.serve_forever()

if __name__ == "__main__":
    threading.Thread(target=run, daemon=True).start()
    while True:
        time.sleep(3600)
