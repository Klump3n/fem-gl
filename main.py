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
        self.action(node_path, do='unpack', what='nodes')
        self.action(element_path, do='unpack', what='elements')

    def add_timestep(self, path):
        """Wrapper around the action function.

        Makes adding a timestep less confusing.
        """
        self.action(path, do='add', what='timestep')

    def action(self, path, do, what):
        """Unpack binary data.

        Specifying the action will either unpack nodes or elements or add
        a timestep.

        Open a file and read it as binary, unpack into an array in a specified
        format, cast the array to numpy and reshape it.
        """
        if (do == 'unpack' and what == 'nodes'):
            size_of_data = 8    # 8 bytes of ...
            data_type = 'd'     # ... doubles
            points_per_unit = 3  # 3 coords per node
        elif (do == 'unpack' and what == 'elements'):
            size_of_data = 4    # 4 bytes of ...
            data_type = 'i'     # ... integers
            points_per_unit = 8  # 8 points per element
        elif (do == 'add', what == 'timestep'):
            size_of_data = 8    # 8 bytes of ...
            data_type = 'd'     # ... doubles
            points_per_unit = 1  # 1 data point per unit.
        else:
            raise ValueError('Unknown parameters. Doing nothing.')

        f = open(path, 'rb')
        bin_data = f.read()
        bin_data_points = int(len(bin_data) / size_of_data)

        # I.e. '<123i' or '<123d' for bin_data_points = 123
        struct_format = '<{size}'.format(size=bin_data_points) + data_type

        data = struct.unpack(struct_format, bin_data)
        data = np.asarray(data)
        data.shape = (int(bin_data_points/points_per_unit), points_per_unit)
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

    def find_surface(self):
        """Find the surface points in a given (NOTE: specify) data set.

        Count the number of occurrences of any given data point
        in the element definition. Parse the one that appear 1 (corner),
        2 (border) or 4 (surface) times.

        Return the points that define the surface in three distinct numpy
        arrays.
        """
        unique_nodes, node_counts = np.unique(self.elements,
                                              return_counts=True)
        corner_nodes = np.where(node_counts == 1)
        corner_points = self.nodes[corner_nodes[0]]
        border_nodes = np.where(node_counts == 2)
        border_points = self.nodes[border_nodes[0]]
        plane_nodes = np.where(node_counts == 4)
        plane_points = self.nodes[plane_nodes[0]]
        return [corner_nodes, border_nodes, plane_nodes,
                corner_points, border_points, plane_points]

    def generate_surfaces_for_elements(self):
        """Finds the outward faces of the mesh.

        Count the unique occurrences of each node. For each element generate
        the six (outward pointing) faces. Iterate over all the points of
        each face and add the occurrences (as previously generated) up.
        Faces at the corner will have a count of 9, faces at the border a
        count of 12 and faces in the middle of the plane a count of 16.
        """
        unique_nodes, node_counts = np.unique(self.elements,
                                              return_counts=True)

        # The element indices that generate six outward pointing faces. Each
        # element has 8 entries, so count from 0 to 7.
        faces = [
            [0, 1, 5, 4],
            [1, 2, 6, 5],
            [2, 3, 7, 6],
            [3, 0, 4, 7],
            [4, 5, 6, 7],
            [3, 2, 1, 0]
        ]

        corner_faces = []
        border_faces = []
        plane_faces = []

        for element in self.elements:
            for face in faces:
                node_weight = node_counts[element[face[0]]] \
                              + node_counts[element[face[1]]] \
                              + node_counts[element[face[2]]] \
                              + node_counts[element[face[3]]]
                if (node_weight == 9):
                    corner_faces.append(
                        [element[face[0]], element[face[1]],
                         element[face[2]], element[face[3]]]
                    )
                elif (node_weight == 12):
                    border_faces.append(
                        [element[face[0]], element[face[1]],
                         element[face[2]], element[face[3]]]
                    )
                elif (node_weight == 16):
                    plane_faces.append(
                        [element[face[0]], element[face[1]],
                         element[face[2]], element[face[3]]]
                    )
                else:
                    pass
        corner_faces = np.asarray(corner_faces)
        border_faces = np.asarray(border_faces)
        plane_faces = np.asarray(plane_faces)
        return [corner_faces, border_faces, plane_faces]


if __name__ == '__main__':
    """If we use the file as a standalone program this is called.
    """

    # Some test case
    testdata = UnpackMesh(
        node_path='testdata/case.nodes.bin',
        element_path='testdata/case.dc3d8.bin'
    )

    # Add a timestep
    testdata.add_timestep('testdata/nt11@00.1.bin')
    corner_faces, \
        border_faces, \
        plane_faces = testdata.generate_surfaces_for_elements()
