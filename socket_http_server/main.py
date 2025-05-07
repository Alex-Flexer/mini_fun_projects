import socket
from threading import Thread
from typing import Callable
import re


class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
    
    def bind_handlers(self, handlers: dict[tuple[str, str], Callable]):
        self.handlers = handlers

    def _request_handler(self, conn, addr):
        with conn:
            print(f"Connected by {addr}")
            data: str = conn.recv(1024).decode('utf-8')

            match = re.match(r"^(GET|POST|PUT|DELETE|HEAD|OPTIONS|PATCH)\s+([^?\s]+)", data)

            if match:
                http_method = match.group(1)
                path = match.group(2)
                print(f"Method: {http_method}, Path: {path}")
            else:
                print("Invalid HTTP request")
                

            print(f"Received data: {path}")

            response = b"HTTP/1.1 200 OK\r\n"
            response += b"Content-Type: text/html; charset=utf-8\r\n"
            response += b"Connection: close\r\n"
            response += b"\r\n"
            response += self.handlers.get((http_method, path), lambda: "404 Not Found")().encode('utf-8')
            conn.sendall(response)

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen()
            while True:
                conn, addr = s.accept()
                thr = Thread(target=self._request_handler, args=(conn, addr))
                thr.start()


server = Server("localhost", 8080)
server.bind_handlers({
    ("GET", "/"): lambda: "<h1>Welcome to the main page</h1>",
    ("GET", "/about"): lambda: "<h1>About us</h1>",
    ("GET", "/contact"): lambda: "<h1>Contact us</h1>"
})
server.run()
