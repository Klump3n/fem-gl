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
Unpacks some binary files and finds the surface of the mesh. Right now this is
limited to C3D8 file format.
"""

import struct
import numpy as np
import matplotlib.cm as cm
import sys


class UnpackMesh:
    """Unpacks mesh data from two binary files and does some magic to it.
    """

    def __init__(self, node_path, element_path):
        """Initialise the class by:

        - unpacking the nodes and the elements of the mesh
        - initialising the timestep array
        - initialising the surface quads for the elements
        - initialising the triangulated surface
        """
        self.get_binary_data(node_path, do='unpack', what='nodes')
        self.get_binary_data(element_path, do='unpack', what='elements')
        self.timesteps = []
        self.surface_quads = None
        self.surface_triangles = None

    def add_timestep(self, path):
        """Wrapper around the get_binary_data function.

        Makes adding a timestep less confusing.
        """
        self.get_binary_data(path, do='add', what='timestep')

    def get_binary_data(
            self, path,
            do,                 # {'unpack', 'add'}
            what                # {'nodes', 'elements', 'timestep'}
    ):
        """Unpack binary data.

        Specifying the what to do will either unpack nodes or elements or
        add a timestep to self.timesteps.

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
            print('Parsed {nodes_t} nodes.'.format(
                nodes_t=data.shape[0]))
        elif (do == 'unpack' and what == 'elements'):
            self.elements = data
            print('Parsed {elements_t} elements.'.format(
                elements_t=data.shape[0]))
        elif (do == 'add', what == 'timestep'):
            data = np.asarray(data)
            self.timesteps.append(data)

    def generate_surfaces_for_elements(self):
        """Finds the outward faces of the mesh (in other words: the surface).
        Returns a numpy array with the surface faces.

        The mesh consists of cubish elements with corner nodes.
        Count the unique occurrences of each node. For each element generate
        the six (outward pointing) faces. Iterate over all the points of
        each face and add the occurrences (as previously generated) up.
        Faces at the corner will have a count of 9, faces at the border a
        count of 12 and faces in the middle of the plane a count of 16.
        (You might want to draw it on a piece of paper.)
        """
        # self.elements is a map that points from each element to the nodes
        # that constitute an element. In that sense two neighbouring elements
        # will share at least 1 (corner) node. So that node will then appear
        # at least twice in self.elements
        _, node_counts = np.unique(self.elements,
                                   return_counts=True)

        # The ordering of the element indices that generate six outward
        # pointing faces. Each element has 8 entries, counting from 0.
        element_faces = [
            [0, 1, 5, 4],
            [1, 2, 6, 5],
            [2, 3, 7, 6],
            [3, 0, 4, 7],
            [4, 5, 6, 7],
            [3, 2, 1, 0]
        ]

        surfaces = []

        def append_face_to_surfaces(element, element_face):
            """Append the face to the output array.
            """
            face = [
                element[element_face[0]],
                element[element_face[1]],
                element[element_face[2]],
                element[element_face[3]]
            ]
            surfaces.append(face)

        for element in self.elements:
            for element_face in element_faces:
                node_weight = node_counts[element[element_face[0]]] \
                              + node_counts[element[element_face[1]]] \
                              + node_counts[element[element_face[2]]] \
                              + node_counts[element[element_face[3]]]

                if (
                        (node_weight == 9) or  # Corner faces
                        (node_weight == 12) or  # Border faces
                        (node_weight == 16)     # Plane faces
                ):
                    append_face_to_surfaces(element, element_face)
                else:
                    pass

        self.surface_quads = np.asarray(surfaces)
        print('Parsed {surface_quads_t} surface quads.'.format(
            surface_quads_t=self.surface_quads.shape[0]))
        return self.surface_quads

    def generate_triangles_from_quads(self):
        """From our list of quads generate outward pointing triangles.
        """
        if (self.surface_quads is None):
            self.generate_surfaces_for_elements()

        triangles = []

        # Two triangles in every quad. This generates outward pointing
        # triangles.
        polygon_coordinates_in_quad = [
            [0, 1, 2],
            [0, 2, 3]
        ]

        for quad in self.surface_quads:
            for polygon_coord in polygon_coordinates_in_quad:
                triangle = [
                    quad[polygon_coord[0]],
                    quad[polygon_coord[1]],
                    quad[polygon_coord[2]],
                ]
                triangles.append(triangle)

        self.surface_triangles = np.asarray(triangles)
        print('Parsed {surface_triangles_t} surface triangles.'.format(
            surface_triangles_t=self.surface_triangles.shape[0]))
        return self.surface_triangles

    def trianglulate_surface_dumbest_possible(self):
        """Get the coordinates of the triangles at the surface.

        This is the dumbest possible way. It's much better to give a complete
        list of all triangles and give an index list for OpenGL to work with.
        """
        if (self.surface_triangles is None):
            self.generate_triangles_from_quads()

        polygons = []
        for triangle in self.surface_triangles:
            polygon = [
                self.nodes[triangle[0]],
                self.nodes[triangle[1]],
                self.nodes[triangle[2]]
            ]
            polygons.append(polygon)
        self.polygons = np.asarray(polygons)
        return self.polygons

    def generate_output(self):
        """Produce some test output. This does not generate small files, it
        just stores the nodes and colors.
        """
        f = open('surface.triangles', 'w')
        g = open('surface.colors', 'w')

        def get_rgb(temp):
            # NOTE: this takes considerable time. Use binning later on.
            # Good ones are afmhot, CMRmap, gist_heat, gnuplot, gnuplot2.
            # See http://matplotlib.org/users/colormaps.html for more.
            color = cm.gnuplot2(int(temp), bytes=True)
            return '{r},{g},{b}'.format(r=color[0], g=color[1], b=color[2])

        for triangle in self.surface_triangles[:-1]:  # All but the last one
            for corner in triangle:
                f.write('{x},{y},{z},'.format(
                    x=self.nodes[corner, 0],
                    y=self.nodes[corner, 1],
                    z=self.nodes[corner, 2]
                ))
                temp_string = get_rgb(float(self.timesteps[0][corner]))
                g.write(temp_string + ',')
        for triangle in self.surface_triangles[-1:]:  # All but the last one
            # print(triangle)
            for corner in triangle[:-1]:
                f.write('{x},{y},{z},'.format(
                    x=self.nodes[corner, 0],
                    y=self.nodes[corner, 1],
                    z=self.nodes[corner, 2]
                ))
                temp_string = get_rgb(float(self.timesteps[0][corner]))
                g.write(temp_string + ',')
            for corner in triangle[-1:]:  # No comma and newline
                f.write('{x},{y},{z}'.format(
                    x=self.nodes[corner, 0],
                    y=self.nodes[corner, 1],
                    z=self.nodes[corner, 2]
                ))
                temp_string = get_rgb(float(self.timesteps[0][corner]))
                g.write(temp_string)
        f.close()
        g.close()

    def boil_down_surface_triangles(self):
        """Rewrite all indices. Generate a file with all triangles and
        a list with references to that list, the order in which they are drawn.
        """

        unique_nodes = np.unique(self.elements).shape[0]
        node_map = [None]*unique_nodes
        for index, value in enumerate(np.unique(self.surface_triangles)):
            node_map[value] = index

        def get_rgb(temp):
            # NOTE: this takes considerable time. Use binning later on.
            # Good ones are afmhot, CMRmap, gist_heat, gnuplot, gnuplot2.
            # See http://matplotlib.org/users/colormaps.html for more.
            color = cm.gnuplot2(int(temp), bytes=True)
            return '{r},{g},{b}'.format(r=color[0], g=color[1], b=color[2])

        unique_triangles = np.unique(self.surface_triangles)
        f = open('triangle_file', 'w')
        g = open('indexlist_file', 'w')
        h = open('temperature_file', 'w')
        for triangle in unique_triangles[:-1]:
            temp_string = get_rgb(float(self.timesteps[0][triangle]))
            f.write('{x},{y},{z},'.format(
                x=str(self.nodes[triangle][0]),
                y=str(self.nodes[triangle][1]),
                z=str(self.nodes[triangle][2])
            ))
            h.write(temp_string + ',')
        for triangle in unique_triangles[-1:]:
            temp_string = get_rgb(float(self.timesteps[0][triangle]))
            f.write('{x},{y},{z}'.format(
                x=str(self.nodes[triangle][0]),
                y=str(self.nodes[triangle][1]),
                z=str(self.nodes[triangle][2])
            ))
            h.write(temp_string)
        for triangle in self.surface_triangles[:-1]:
            for corner in triangle:
                g.write('{corner_t},'.format(corner_t=node_map[corner]))
        for triangle in self.surface_triangles[-1:]:
            for corner in triangle[:-1]:
                g.write('{corner_t},'.format(corner_t=node_map[corner]))
            for corner in triangle[-1:]:
                g.write('{corner_t}o'.format(corner_t=node_map[corner]))
        f.close()
        g.close()
        h.close()


if __name__ == '__main__':
    """If we use the file as a standalone program this is called.
    """

    # Some test case
    testdata = UnpackMesh(
        node_path='testdata/case.nodes.bin',
        element_path='testdata/case.dc3d8.bin'
    )

    # Add a timestep
    testdata.add_timestep('testdata/nt11@16.7.bin')
    # testdata.trianglulate_surface_dumbest_possible()
    testdata.trianglulate_surface()
    testdata.boil_down_surface_triangles()
    testdata.generate_output()
    # print(testdata.timesteps[0].max())
