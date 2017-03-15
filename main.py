#!/usr/bin/env python

# fem-gl-backend -- parsing binary mesh files and preparing
# them for displaying via WebGL
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

"""main.py
Unpacks some binary files and finds the surface of the mesh.
"""

import struct
import numpy as np
# from numba import jit
import sys


class UnpackMesh:
    """Unpacks mesh data from two binary files and does some magic to it."""

    timesteps = []              # Array to hold the timesteps

    def __init__(self, node_path, element_path):
        self.action(node_path, do='unpack', what='nodes')
        self.action(element_path, do='unpack', what='elements')
        # self.unpack_nodes(node_path)
        # self.unpack_elements(element_path)

    def add_timestep_2(self, path):
        """Wrapper around the action function.

        Makes adding a timestep less confusing.
        """
        self.action(path, do='add', what='timestep')

    def action(self, path, do, what):
        if (do == 'unpack' and what == 'nodes'):
            size_of_data = 8  # 8 bytes of ...
            data_type = 'd'   # ... doubles
            points_per_unit = 3  # 3 coords per node
        elif (do == 'unpack' and what == 'elements'):
            size_of_data = 4  # 4 bytes of ...
            data_type = 'i'   # ... integers
            points_per_unit = 8  # 8 points per element
        elif (do == 'add', what == 'timestep'):
            size_of_data = 8  # 8 bytes of ...
            data_type = 'd'   # ... doubles
            points_per_unit = 1  # 1 data point per unit.
        else:
            raise ValueError('Unknown parameters. Doing nothing.')

        f = open(path, 'rb')
        f_data = f.read()
        f_data_points = int(len(f_data) / size_of_data)
        struct_format = '<{size}'.format(size=f_data_points) + data_type
        data = struct.unpack(struct_format, f_data)
        data = np.asarray(data)
        data.shape = (int(f_data_points/points_per_unit), points_per_unit)
        if (do == 'unpack' and what == 'nodes'):
            self.nodes = data
            print('Parsed {nodes} nodes.'.format(nodes=data.shape[0]))
        elif (do == 'unpack' and what == 'elements'):
            self.elements = data
            print('Parsed {elements} elements.'.format(
                elements=data.shape[0]))
        elif (do == 'add', what == 'timestep'):
            data = np.asarray(data)
            self.timesteps.append(data)

    # def unpack_nodes(self, path):
    #     """Unpack the nodes from the given path.

    #     Read binary file, then get amount of data points (doubles). Finally
    #     cast a numpy array and reshape it to (N, 3)
    #     """
    #     f = open(path, 'rb')
    #     f_data = f.read()
    #     f_data_points = int(len(f_data) / 8)
    #     struct_format = '<{size}d'.format(size=f_data_points)
    #     data = struct.unpack(struct_format, f_data)
    #     data = np.asarray(data)
    #     data.shape = (int(f_data_points/3), 3)
    #     self.nodes = data
    #     print('Parsed {nodes} number of nodes.'.format(nodes=data.shape[0]))

    # def unpack_elements(self, path):
    #     """Unpack the elements from the given path.

    #     Read binary file, get amount of data points (integers). Finally
    #     cast a numpy array and reshape it to (N, 8)
    #     """
    #     f = open(path, 'rb')
    #     f_data = f.read()
    #     f_data_points = int(len(f_data) / 4)
    #     struct_format = '<{size}i'.format(size=f_data_points)
    #     data = struct.unpack(struct_format, f_data)
    #     data = np.asarray(data)
    #     data.shape = (int(f_data_points/8), 8)
    #     self.elements = data
    #     print('Parsed {elements} number of elements.'.format(
    #         elements=data.shape[0]))

    # def add_timestep(self, path):
    #     """Unpack the data from a given timestep (NOTE: specify).

    #     Read binary file, get amount of data points (integers). Finally
    #     cast a numpy array and append it to the class array.
    #     """
    #     f = open(path, 'rb')
    #     f_data = f.read()
    #     f_data_points = int(len(f_data) / 8)
    #     struct_format = '<{size}d'.format(size=f_data_points)
    #     data = struct.unpack(struct_format, f_data)
    #     data = np.asarray(data)
    #     self.timesteps.append(data)

    # @jit # If we ever run into time problems uncomment this. Compiling takes
    # some time but for larger meshes this should speed up analysing.
    def find_surface(self):
        """Find the surface points in a given (NOTE: specify) data set.

        Count the number of occurrences of any given data point
        in the element definition. Parse the one that appear 1 (corner),
        2 (border) or 4 (surface) times.

        Return the points that define the surface in three distinct numpy
        arrays.
        """
        # Find the surface by counting the occurrence of elements
        # Surface elements will occour fewer times
        unique, counts = np.unique(self.elements, return_counts=True)
        corner_elements = np.where(counts == 1)
        corner_points = self.nodes[corner_elements[0]]
        border_elements = np.where(counts == 2)
        border_points = self.nodes[border_elements[0]]
        surface_elements = np.where(counts == 4)
        surface_points = self.nodes[surface_elements[0]]
        return corner_points, border_points, surface_points


if __name__ == '__main__':
    """If we use the file as a standalone program call the main() function.
    """
    # Some test case
    testdata = UnpackMesh(
        node_path='testdata/case.nodes.bin',
        element_path='testdata/case.dc3d8.bin'
    )
    # Add a timestep
    testdata.add_timestep_2('testdata/nt11@00.1.bin')
    corner_points, border_points, surface_points = testdata.find_surface()
