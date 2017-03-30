#!/usr/bin/env python

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
