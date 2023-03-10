import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import pathlib
import mimetypes
import json
import socket
from threading import Thread
from datetime import datetime

HTTP_PORT = 3000
SOCKET_SERVER = '127.0.0.1'
SOCKET_PORT = 5000
MAIN_DIR = pathlib.Path()
BUFFER_SIZE = 1024

class MyApp(BaseHTTPRequestHandler):
    def do_POST(self):
        len = self.headers.get('Content-Length')
        data = self.rfile.read(int(len))
        info_save(data)
        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()



    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == '/':
            self.send_html_file('index.html')
        elif pr_url.path == '/message.html':
            self.send_html_file('message.html')
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static(MAIN_DIR)
            else:
                self.send_html_file('error.html', 404)

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())

    def send_static(self, filename, status_code = 200):
        self.send_response(status_code)
        mt = mimetypes.guess_type(filename)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", 'text/plain')
        self.end_headers()
        with open(filename, 'rb') as file:
            self.wfile.write(file.read())

def info_save(data):
    parse_data = urllib.parse.unquote_plus(data.decode())
    try:
        data_dict = {key: value for key, value in [el.split('=') for el in parse_data.split('&')]}
        data_save = {str(datetime.now()): data_dict}
        with open("storage/data.json", "a", encoding='utf-8') as fd:
            json.dump(data_save, fd, ensure_ascii=False, indent=4)
    except ValueError as err:
        logging.debug(f"In data {data_dict} error {err}")
    except OSError as err:
        logging.debug(f"In data {data_dict} error {err}")

def http_server_run():
    server_address = ('localhost', 3000)
    http = HTTPServer(server_address, MyApp)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        logging.info("Server spoted!")
        http.server_close()

def socket_server_run(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))
    try:
        while True:
            message, address = sock.recvfrom(1024).decode()
            info_save(message)
    except KeyboardInterrupt:
        print(f'Destroy server')
    finally:
        sock.close()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    thread_server = Thread(target=http_server_run)
    thread_server.start()

    thread_socket_server = Thread(target=socket_server_run, args = (SOCKET_SERVER, SOCKET_PORT))
    thread_socket_server.start()
