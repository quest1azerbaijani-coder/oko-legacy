# server.py — простой healthcheck, чтобы хост видел открытый порт
import os, http.server, socketserver, threading, time

PORT = int(os.getenv("PORT", "10000"))

class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        return  # тише в логах

def run():
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        httpd.serve_forever()

if __name__ == "__main__":
    threading.Thread(target=run, daemon=True).start()
    while True:
        time.sleep(3600)  # держим процесс
