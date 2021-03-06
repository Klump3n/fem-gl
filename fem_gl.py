#!/usr/bin/env python3

# fem-gl -- Display fem data in a modern browser via web gl
#
# Copyright (C) 2017 Matthias Plock <matthias.plock@bam.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Start a web server for fem-gl. Direct your browser to [HOST_IP]:[PORT]
with PORT being either 8008 or the supplied value.
"""

import os
import argparse
import modules.backend as fem_web
# import modules.web_service as fem_web


def parse_commandline():
    """Parse the command line and return the parsed arguments.
    """

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '-p', '--port', default=8008,
        help='The port for the web server.')
    parser.add_argument(
        '-m', '--mesh-dir', required=True,
        help='The directory in which we want to look for mesh files.')
    args = parser.parse_args()

    return args

def start_web_instance(args):
    """Start the web server.
    """

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
        html_directory=html_dir,
        mesh_directory=mesh_dir,
        port=port)
    web_instance.start()


# Start the program.
ARGS = parse_commandline()
start_web_instance(ARGS)
