import socket
from threading import Thread
from typing import Callable
import re


class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.handlers = {}
    
    def bind_handlers(self, handlers: dict[tuple[str, str], Callable]):
        self.handlers = handlers

    def _parse_body(self, data: str) -> dict:
        body_match = re.search(r"\r?\n\r?\n(.*)$", data, re.DOTALL)
        res = {}
        if body_match:
            body = body_match.group(1)
            params = body.split("&")
            for param in params:
                if "=" in param:
                    key, value = param.split("=", 1)
                    res[key] = value

        return res

    def _request_handler(self, conn, addr):
        with conn:
            print(f"Connected by {addr}\n")
            data: str = conn.recv(1024).decode('utf-8')

            match = re.match(r"^(GET|POST|PUT|DELETE|HEAD|OPTIONS|PATCH)\s+([^?\s]+)", data)

            if match:
                http_method = match.group(1)
                path = match.group(2)
                body = self._parse_body(data)
                print(f"Method: {http_method}, Path: {path}\n")
                print(f"Body: {body}\n")
            else:
                print("Invalid HTTP request")
                

            print(f"Received data:\n{data}")

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


class Request:
    body: dict
    headers: dict
    
    def __init__(self, headers: dict, body: dict = {}):
        self.headers = headers
        self.body = body

