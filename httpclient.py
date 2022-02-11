#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# Copyright 2022 Kaixuan H.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
from urllib.parse import urlparse, urlencode

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_hostname(self, url):
        url_list = url.split("/")
        if ":" in url_list[2]:
            return url_list[2].split(":")[0]
        else:
            return url_list[2]

    def get_port(self, url):
        url_list = url.split("/")
        if ":" in url_list[2]:
            return int(url_list[2].split(":")[1])
        else:
            return 80

    def get_path(self, url):
        url_list = url.split("/")
        path = '/'
        path += '/'.join(url_list[3:])
        return path

    def get_header_GET(self, path, host):
        header = 'GET '
        header += path
        header += ' HTTP/1.1\r\nHost: '
        header += host
        header += '\r\nConnection: close\r\n\r\n'
        return header

    def get_header_POST(self, path, host, length, encode_args = None):
        header = 'POST '
        header += path
        header += ' HTTP/1.1\r\nHost: '
        header += host
        header += '\r\n'
        header += 'Content-Type: application/x-www-form-urlencoded\r\nContent-Length: '
        header += length
        header += '\r\n\r\n'
        if encode_args:
            header += encode_args
        return header

    def get_code(self, data):
        data_list = data.split('\r\n')
        code = data_list[0].split(" ")[1]
        return int(code)

    def get_body(self, data):
        return data.split('\r\n\r\n')[1]

    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))

    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        code = 500
        body = ""

        host = self.get_hostname(url)
        port = self.get_port(url)
        path = self.get_path(url)
        header = self.get_header_GET(path, host)

        self.connect(host, port)
        self.sendall(header)

        response = self.recvall(self.socket)
        code = self.get_code(response)
        body = self.get_body(response)
        self.close()

        print(body)
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""

        host = self.get_hostname(url)
        port = self.get_port(url)
        path = self.get_path(url)

        if args:
            length = str(len(urlencode(args)))
            header = self.get_header_POST(path, host, length, urlencode(args))
        else:
            header = self.get_header_POST(path, host, str(0))

        self.connect(host, port)
        self.sendall(header)

        response = self.recvall(self.socket)
        code = self.get_code(response)
        body = self.get_body(response)
        self.close()

        print(body)
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )

if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
