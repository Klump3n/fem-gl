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


import os

import json

import numpy as np

# conda install cherrypy
import cherrypy

import modules.mesh_parser as fem_mesh


class WebServer:
    """Host a web server on a given port and hand out the files in the path.
    """

    def __init__(self, html_directory, mesh_directory, port=8008):
        """Initialise the webserver.
        """
        self.conf = {
            '/': {
                'tools.gzip.on': True,
                'tools.staticdir.on': True,
                'tools.staticdir.dir': html_directory,
                'tools.staticdir.index': 'index.html'
            }
        }
        self.port = port
        self.mesh_directory = mesh_directory

    def start(self):
        """Start the web server on the given port with the given config.
        """

        # Set the port
        cherrypy.config.update(
            {'server.socket_port': self.port}
        )

        # Load the server class for displaying fem data
        cherrypy.tree.mount(
            self.FemGL(mesh_directory=self.mesh_directory), '/', self.conf)

        # Start the server
        cherrypy.engine.start()
        cherrypy.engine.block()

    class FemGL:
        """Handle the data for fem-gl.
        """

        def __init__(self, mesh_directory):
            self.mesh_directory = mesh_directory

        @cherrypy.expose
        def index(self):
            """Just serve the static dir.
            """
            pass

        @cherrypy.expose
        def get_object_list(self):
            """Return a list of folders that potentially hold FEM data.

            On catching 'get_object_list'

            Check all the files we find in self.mesh_directory, check if it's a
            directory, if it's a directory check if there is a directory called
            'fo' in there. If that's the case we add it to the list we return
            in the end.

            Returns a json file.
            """
            list_to_return = []
            files_in_mesh_dir = os.listdir(self.mesh_directory)
            for file_name in files_in_mesh_dir:
                abs_file_path = os.path.join(self.mesh_directory, file_name)
                if os.path.isdir(abs_file_path):
                    file_output_dir = os.path.join(abs_file_path, 'fo')
                    if os.path.isdir(file_output_dir):
                        list_to_return.append(file_name)
            return json.dumps({'data_folders': list_to_return})

        @cherrypy.expose
        def get_object_properties(self, object_name):
            """Return a list of properties for a given element.

            On catching 'get_object_properties'

            MEANINGFUL DESCRIPTION HERE

            Returns a json file.
            """
            object_directory = os.path.join(self.mesh_directory, object_name, 'fo')

            object_timesteps = []
            object_properties = []

            files_in_fo = os.listdir(object_directory)
            for timestep in files_in_fo:
                object_timesteps.append(timestep)

            return json.dumps({'object_timesteps': object_timesteps,
                               'object_properties': object_properties})

        @cherrypy.expose
        def mesher_init(self):
            """Load the mesher class.
            """
            os.chdir(self.mesh_directory)
            self.mesh_index = fem_mesh.UnpackMesh(
                node_path='case.nodes.bin',
                element_path='case.dc3d8.bin'
            )

        @cherrypy.expose
        def get_some_data(self):
            """On getting a POST:get_some_data from the webserver we give
            the required data back.
            """

            # Add a timestep
            timestep = self.mesh_index.add_timestep('nt11@00.1.bin')
            metafile = self.mesh_index.generate_meta_file()
            self.mesh_index.generate_triangles_from_quads()
            # Make a string from the temperatures, add a comma between every
            # value and then remove the last comma

            # Read in a prepared temperature file..
            f = open('generated_files/welding_sim_0.temperatures')
            prepfile = f.read()
            f.close()
            prepfilearray = prepfile.split(',')
            # prepfilearray = list(map(int, prepfilearray))
            # print(prepfilearray)
            meta = {'timestep': prepfilearray}

            # We need to keep this for when we assign colours in the shader
            # meta = {'timestep': timestep.flatten().tolist()}
            return json.dumps(meta)
