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
import sys

class UnpackMesh:
    """Unpacks mesh data from two binary files and does some magic to it."""

    timesteps = []              # Array to hold the timesteps

    def __init__(self, node_path, element_path):
        self.unpack_nodes(node_path)
        self.unpack_elements(element_path)

    def unpack_nodes(self, path):
        """Unpack the nodes from the given path.

        Read binary file, then get amount of data points (doubles). Finally
        cast a numpy array and reshape it to (N, 3)
        """
        f = open(path, 'rb')
        f_data = f.read()
        f_data_points = int(len(f_data) / 8)
        struct_format = '<{size}d'.format(size = f_data_points)
        data = struct.unpack(struct_format, f_data)
        data = np.asarray(data)
        data.shape = (int(f_data_points/3), 3)
        self.nodes = data

    def unpack_elements(self, path):
        """Unpack the elements from the given path.

        Read binary file, get amount of data points (integers). Finally
        cast a numpy array and reshape it to (N, 8)
        """
        f = open(path, 'rb')
        f_data = f.read()
        f_data_points = int(len(f_data) / 4)
        struct_format = '<{size}i'.format(size = f_data_points)
        data = struct.unpack(struct_format, f_data)
        data = np.asarray(data)
        data.shape = (int(f_data_points/8), 8)
        self.elements = data

    def add_timestep(self, path):
        """Unpack the data from a given timestep.

        Read binary file, get amount of data points (integers). Finally
        cast a numpy array
        """
        f = open(path, 'rb')
        f_data = f.read()
        f_data_points = int(len(f_data) / 8)
        struct_format = '<{size}d'.format(size = f_data_points)
        data = struct.unpack(struct_format, f_data)
        data = np.asarray(data)
        self.timesteps.append(data)


    def find_surface(self):
        # Find the surface by counting the occurrence of elements
        # Surface elements will occour fewer times
        unique, counts = np.unique(self.elements, return_counts=True)
        print(unique, counts)
        print(np.sort(counts)[1:100])
        # unique_x = np.unique(self.nodes[:,0])
        # print(self.nodes)
        # print(unique_x)
        # sys.exit()
        # num_of_nodes = self.nodes.shape[0]
        # for it in np.arange(num_of_nodes):
        #     pass
        # print(num_of_nodes)

def main():
    """Main routine of the program"""

    # Some test case
    testdata = UnpackMesh(
        node_path='testdata/case.nodes.bin',
        element_path='testdata/case.dc3d8.bin'
    )
    # Add a timestep
    testdata.add_timestep('testdata/nt11@00.1.bin')
    testdata.find_surface()

if __name__ == '__main__':
    main()
