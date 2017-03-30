#!/usr/bin/env python

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


# conda install cherrypy
import cherrypy
import modules.mesh_parser

class WebServer:
    """Host a web server on a given port and hand out the files in the path.
    """

    def __init__(self, directory, port=8008):
        """Initialise the webserver.
        """
        self.conf = {
            '/': {
                'tools.gzip.on': True,
                'tools.staticdir.on': True,
                'tools.staticdir.dir': directory,
                'tools.staticdir.index': 'index.html'
            }
        }
        self.port = port

    def start(self):
        """Start the web server on the given port with the given config.
        """
        cherrypy.config.update(
            {'server.socket_port': self.port}
        )
        cherrypy.tree.mount(self.FemGL(), '/', self.conf)
        cherrypy.engine.start()
        cherrypy.engine.block()

    class FemGL:
        """Handle the data for fem-gl.
        """

        @cherrypy.expose
        def index(self):
            """Just serve the static dir.
            """
            pass

        @cherrypy.expose
        def list_files(self):
            print('LIST ALL FILES')


if __name__ == '__main__':
    web_server = WebServer(directory='/home/mplock/coding/dev/fem-gl/html/', port=8008)
    web_server.start()
