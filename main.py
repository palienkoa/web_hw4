from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import json
import datetime
import logging
import socket
from threading import Thread


class HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        # print(pr_url)
        if pr_url.path == '/':
            self.send_html_file('index.html')
        elif pr_url.path == '/message.html':
            self.send_html_file('message.html')
        elif pr_url.path == '/style.css':
            self.send_html_file('style.css')
        elif pr_url.path == '/logo.png':
            self.send_html_file('logo.png')
        else:
            self.send_html_file('error.html', 404)

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())
    
    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        # sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # sock.sendto(data, ('localhost', 5000))
        # sock.close()
        save_data(data)

        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()

def save_data(data):
    data_parse = urllib.parse.unquote_plus(data.decode())
    try:
        time = datetime.datetime.now()
        # print(time)
        # data_dict = {str(time): {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}}
        #зчитуємо попередній вміст файлу
        storage_file = 'storage/data.json'
        try:
            data_dict = json.load(open(storage_file))
        except:
            data_dict = {}
        
        #додаємо новий запис
        data_dict.update({str(time): {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}})
        
        #записуємо назад, перезаписуючи повністю 
        with open(storage_file, 'w') as json_file:
            json.dump(data_dict, json_file)
            json_file.write('\n')
    except ValueError as err:
        logging.error(err)
    except OSError as err:
        logging.error(err)

def start_http_server(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ('', 3000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()
        
def start_socket_server(host, port):
    with socket.socket() as s:
        # s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.listen(1)
        conn, addr = s.accept()
        logging.DEBUG(f"Connected by {addr}")
        with conn:
            while True:
                data = conn.recv(1024)
                save_data(data)
                if not data:
                    break
                # conn.send(data.upper())


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(threadName)s %(message)s')
    
    http_server = Thread(target=start_http_server)
    http_server.start()

    socket_server = Thread(target=start_socket_server, args=("localhost", 5000))
    socket_server.start()

