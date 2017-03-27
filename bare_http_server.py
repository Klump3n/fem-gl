#!/usr/bin/env python

from http.server import HTTPServer, BaseHTTPRequestHandler
import os
import sys

class MyHTTPServer():

    def __init__(
            self,
            address='',
            port=8000,
            path=os.getcwd()):

        self.address = address
        self.port = port
        self.server_path = path

        # Switch to html directory
        try:
            os.chdir(path)
        except FileNotFoundError:
            sys.exit('[FileNotFoundError] Initialisation of HTTP server ' \
                     'failed. Path does not exist.')

        self.start_server()

    def start_server(self):
        httpd = HTTPServer((self.address, self.port), self.My_request_handler)
        try:
            print('Path is {path_str}'.format(path_str=self.server_path))
            print('Serving HTTP on port {port_str}.'.format(port_str=self.port))
            httpd.serve_forever()
        except KeyboardInterrupt:
            print('\nHTTP server shutting down.')
            httpd.socket.close()

    class My_request_handler(BaseHTTPRequestHandler):

        def do_GET(self):
            if (self.path == '/'):
                self.path = '/index.html'

            file_path = os.path.join(os.getcwd(), * self.path.split('/'))  # Unpack the list
            try:
                if file_path.endswith('.html'):
                    f = open(file_path) #open requested file

                    #send code 200 response
                    self.send_response(200)

                    #send header first
                    self.send_header('Content-type','text-html'.encode())
                    self.end_headers()

                    #send file content to client
                    self.wfile.write(f.read().encode())
                    f.close()
                    return

                if file_path.endswith('.js'):
                    f = open(file_path) #open requested file

                    #send code 200 response
                    self.send_response(200)

                    #send header first
                    self.send_header('Content-type','javascript'.encode())
                    self.end_headers()

                    #send file content to client
                    self.wfile.write(f.read().encode())
                    f.close()
                    return

                if file_path.endswith('.css'):
                    f = open(file_path) #open requested file

                    #send code 200 response
                    self.send_response(200)

                    #send header first
                    self.send_header('Content-type','css'.encode())
                    self.end_headers()

                    #send file content to client
                    self.wfile.write(f.read().encode())
                    f.close()
                    return

                if file_path.endswith('.c'):
                    f = open(file_path) #open requested file

                    #send code 200 response
                    self.send_response(200)

                    #send header first
                    self.send_header('Content-type','c-source-file'.encode())
                    self.end_headers()

                    #send file content to client
                    self.wfile.write(f.read().encode())
                    f.close()
                    return

                if (
                        file_path.endswith('.triangles') or
                        file_path.endswith('.temperatures') or
                        file_path.endswith('.indices') or
                        file_path.endswith('.metafile')
                ):
                    f = open(file_path) #open requested file

                    #send code 200 response
                    self.send_response(200)

                    #send header first
                    self.send_header('Content-type','raw-data'.encode())
                    self.end_headers()

                    #send file content to client
                    self.wfile.write(f.read().encode())
                    f.close()
                    return

            except IOError:
                self.send_error(404, 'file not found')


if __name__ == '__main__':
    MyHTTPServer(
        port=8080,
        path='html/')
