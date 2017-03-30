#!/usr/bin/env python
"""Start a http server for fem-gl and start serving the html directory.
"""

import modules.web_service as fem_web
import argparse
import os

parser = argparse.ArgumentParser(description='Start a web server for fem-gl. '\
                                 'Direct your browser to [HOST_IP]:[PORT] '\
                                 'with PORT being either 8008 or the '\
                                 'supplied value.')
parser.add_argument('-p', '--port', default=8008,
                    help='The port for the web server. Defaults to 8008.')
parser.add_argument('-m', '--mesh-dir', required=True,
                    help='The directory in which we want '\
                    'to look for mesh files.')
args = parser.parse_args()

cwd = os.getcwd()

html_dir = os.path.abspath('html')
mesh_dir = os.path.abspath(args.mesh_dir)

port = args.port

start_msg = 'Starting fem-gl http server on port {port_text}\n\n'\
            'Serving html from directory {html_dir_text}\n'\
            'Will search for fem data in directory {mesh_dir_text}'\
            '\n'.format(
                port_text=port,
                html_dir_text=html_dir,
                mesh_dir_text=mesh_dir)
print(start_msg)
web_instance = fem_web.WebServer(
    directory=html_dir,
    port=port)
web_instance.start()