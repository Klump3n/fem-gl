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
import re
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
            self.timestep_list = []

        @cherrypy.expose
        def index(self):
            """Just serve the static dir.
            """
            pass

        @cherrypy.expose
        def get_object_list(self):
            """Return a list of folders that potentially hold FEM data on
            catching 'get_object_list'

            Check all the files we find in self.mesh_directory, check if it's a
            directory, if it's a directory check if there is a directory called
            'fo' in there. If that's the case we add it to the list we return
            in the end.

            Returns a json file.
            """
            files_in_mesh_dir = os.listdir(self.mesh_directory)

            data_folders = []

            for file_name in files_in_mesh_dir:
                abs_file_path = os.path.join(self.mesh_directory, file_name)
                if os.path.isdir(abs_file_path):
                    file_output_dir = os.path.join(abs_file_path, 'fo')
                    if os.path.isdir(file_output_dir):
                        data_folders.append(file_name)
            return json.dumps({'data_folders': data_folders})

        @cherrypy.expose
        def get_object_properties(self, object_name):
            """Return a list of properties for a given element on catching
            'get_object_properties'

            Go through all timestep folders and look in every ef- and nf-folder
            for files. Append every file to an array, afterwards find the unique
            files in that array. Append this list to a list containing an entry
            for a simple wireframe (i.e. no field values, just the bare mesh).

            Returns a json file.
            """
            object_directory = os.path.join(self.mesh_directory, object_name, 'fo')

            # Get the smallest timestep.
            dirs_in_fo = os.listdir(object_directory)

            object_timesteps = []

            for timestep in dirs_in_fo:
                timestep_path = os.path.join(object_directory, timestep)
                if os.path.isdir(timestep_path):
                    object_timesteps.append(timestep)
            object_timesteps = sorted(object_timesteps)

            initial_timestep = object_timesteps[0]

            # Get all available properties.
            file_array = []
            for path, _, files in os.walk(object_directory):
                if (os.path.basename(path) == 'nf' or
                    os.path.basename(path) == 'ef'):
                    for single_file in files:
                        if re.match(r'(.*)\.bin', single_file):
                            file_array.append(single_file)
            unique_field_names = np.unique(file_array)

            object_properties = ['wireframe']

            for field_name in unique_field_names:
                # Remove the .bin ending from the file.
                name_without_ending = re.match(r'(.*)\.bin', field_name).groups(0)[0]
                object_properties.append(name_without_ending)

            return json.dumps({'object_properties': object_properties,
                               'initial_timestep': initial_timestep})


        def get_sorted_timesteps(self, object_name):
            """Generate a sorted list of timesteps.

            Go through all the folders in the object/fo folder. Every folder
            here is a timestep.

            Returns a list of lists.
            """
            object_directory = os.path.join(self.mesh_directory, object_name, 'fo')

            object_timesteps = []
            sorted_timesteps = []

            dirs_in_fo = os.listdir(object_directory)

            for timestep in dirs_in_fo:
                timestep_path = os.path.join(object_directory, timestep)
                if os.path.isdir(timestep_path):
                    object_timesteps.append([float(timestep), timestep])

            sorted_timesteps = sorted(object_timesteps)
            return sorted_timesteps

        @cherrypy.expose
        def get_object_timesteps(self, object_name):
            """Return a list of the available timesteps for a given element on
            catching 'get_object_timesteps'

            Go through all the folders in the object/fo folder. Every folder
            here is a timestep.

            Returns a json file.
            """
            object_timesteps = self.get_sorted_timesteps(object_name)
            sorted_timesteps = []
            for timestep in object_timesteps:
                sorted_timesteps.append(timestep[1])
            return json.dumps({'object_timesteps': sorted_timesteps})

        @cherrypy.expose
        def get_timestep_before(self, object_name, current_timestep):
            """Given a timestep, find the previous timestep.

            Return the same timestep if there is no timestep before.
            """
            object_timesteps = self.get_sorted_timesteps(object_name)
            sorted_timesteps = []
            for it in object_timesteps:
                sorted_timesteps.append(it[1])
            object_index = sorted_timesteps.index(current_timestep)
            if object_index == 0:
                return json.dumps({'previous_timestep': sorted_timesteps[0]})
            else:
                return json.dumps({'previous_timestep': sorted_timesteps[object_index - 1]})

        @cherrypy.expose
        def get_timestep_after(self, object_name, current_timestep):
            """Given a timestep, find the next timestep.

            Return the same timestep if there is no timestep after.
            """
            object_timesteps = self.get_sorted_timesteps(object_name)
            sorted_timesteps = []
            for it in object_timesteps:
                sorted_timesteps.append(it[1])

            number_of_timesteps = len(sorted_timesteps)
            object_index = sorted_timesteps.index(current_timestep)
            if object_index == number_of_timesteps - 1:
                return json.dumps({'next_timestep': sorted_timesteps[number_of_timesteps - 1]})
            else:
                return json.dumps({'next_timestep': sorted_timesteps[object_index + 1]})

        @cherrypy.expose
        def mesher_init(self, nodepath, elementpath):
            """Load the mesher class.
            """
            os.chdir(self.mesh_directory)
            self.mesh_index = fem_mesh.UnpackMesh(
                node_path=nodepath,
                element_path=elementpath
            )

            surface_nodes = self.mesh_index.return_unique_surface_nodes()
            surface_indexfile = self.mesh_index.return_surface_indices()
            surface_metadata = self.mesh_index.return_metadata()

            return json.dumps({'surface_nodes': surface_nodes,
                               'surface_indexfile': surface_indexfile,
                               'surface_metadata': surface_metadata.tolist()})

        @cherrypy.expose
        def get_timestep_data(self, object_name, field, timestep):
            """On getting a POST:get_some_data from the webserver we give
            the required data back.
            """

            timestep_data = self.mesh_index.return_data_for_unique_nodes(object_name, field, timestep)

            output_data = []
            for datapoint in timestep_data:
                output_data.append(datapoint[0])

            return json.dumps({'timestep_data': output_data})
