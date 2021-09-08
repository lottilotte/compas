from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import sys
import collections
import compas

from compas.files import OBJ

from compas.utilities import geometric_key
from compas.geometry import centroid_points
from compas.geometry import subtract_vectors
from compas.geometry import distance_point_point
from compas.geometry import midpoint_line
from compas.geometry import normalize_vector
from compas.geometry import add_vectors
from compas.geometry import scale_vector

from compas.datastructures import Graph

from .operations import network_split_edge

from .combinatorics import network_is_connected
from .complementarity import network_complement
from .duality import network_find_cycles
from .transformations import network_transform
from .transformations import network_transformed
from .traversal import network_shortest_path
from .smoothing import network_smooth_centroid

from .planarity import network_count_crossings
from .planarity import network_find_crossings
from .planarity import network_is_crossed
from .planarity import network_is_xy


class Network(Graph):
    """Geometric implementation of an edge graph.

    Parameters
    ----------
    name: str, optional
        The name of the graph.
        Defaults to "Graph".
    default_node_attributes: dict, optional
        Default values for node attributes.
    default_edge_attributes: dict, optional
        Default values for edge attributes.

    """

    complement = network_complement
    is_connected = network_is_connected
    shortest_path = network_shortest_path
    split_edge = network_split_edge
    smooth = network_smooth_centroid
    transform = network_transform
    transformed = network_transformed
    find_cycles = network_find_cycles

    count_crossings = network_count_crossings
    find_crossings = network_find_crossings
    is_crossed = network_is_crossed
    is_xy = network_is_xy

    if not compas.IPY:
        from .matrices import network_adjacency_matrix
        from .matrices import network_connectivity_matrix
        from .matrices import network_degree_matrix
        from .matrices import network_laplacian_matrix
        from .planarity import network_embed_in_plane
        from .planarity import network_is_planar
        from .planarity import network_is_planar_embedding

        adjacency_matrix = network_adjacency_matrix
        connectivity_matrix = network_connectivity_matrix
        degree_matrix = network_degree_matrix
        laplacian_matrix = network_laplacian_matrix

        embed_in_plane = network_embed_in_plane
        is_planar = network_is_planar
        is_planar_embedding = network_is_planar_embedding

    def __init__(self, name=None, default_node_attributes=None, default_edge_attributes=None):
        name = name or 'Network'
        _default_node_attributes = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        _default_edge_attributes = {}
        if default_node_attributes:
            _default_node_attributes.update(default_node_attributes)
        if default_edge_attributes:
            _default_edge_attributes.update(default_edge_attributes)
        super(Network, self).__init__(name=name,
                                      default_node_attributes=_default_node_attributes,
                                      default_edge_attributes=_default_edge_attributes)

    def __str__(self):
        tpl = "<Network with {} nodes, {} edges>"
        return tpl.format(self.number_of_nodes(), self.number_of_edges())

    # --------------------------------------------------------------------------
    # customisation
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # special properties
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # constructors
    # --------------------------------------------------------------------------

    @classmethod
    def from_obj(cls, filepath, precision=None):
        """Construct a network from the data contained in an OBJ file.

        Parameters
        ----------
        filepath : path string, file-like object or URL string
            A path, a file-like object or a URL pointing to a file.
        precision: str, optional
            The precision of the geometric map that is used to connect the lines.

        Returns
        -------
        Network
            A network object.

        Examples
        --------
        >>>
        """
        network = cls()
        obj = OBJ(filepath, precision)
        obj.read()
        nodes = obj.vertices
        edges = obj.lines
        for i, (x, y, z) in enumerate(nodes):
            network.add_node(i, x=x, y=y, z=z)
        for u, v in edges:
            network.add_edge(u, v)
        return network

    @classmethod
    def from_lines(cls, lines, precision=None):
        """Construct a network from a set of lines represented by their start and end point coordinates.

        Parameters
        ----------
        lines : list
            A list of pairs of point coordinates.
        precision: str, optional
            The precision of the geometric map that is used to connect the lines.

        Returns
        -------
        Network
            A network object.

        Examples
        --------
        >>>
        """
        network = cls()
        edges = []
        node = {}
        for line in lines:
            sp = line[0]
            ep = line[1]
            a = geometric_key(sp, precision)
            b = geometric_key(ep, precision)
            node[a] = sp
            node[b] = ep
            edges.append((a, b))
        key_index = dict((k, i) for i, k in enumerate(iter(node)))
        for key, xyz in iter(node.items()):
            i = key_index[key]
            network.add_node(i, x=xyz[0], y=xyz[1], z=xyz[2])
        for u, v in edges:
            i = key_index[u]
            j = key_index[v]
            network.add_edge(i, j)
        return network

    @classmethod
    def from_nodes_and_edges(cls, nodes, edges):
        """Construct a network from nodes and edges.

        Parameters
        ----------
        nodes : list , dict
            A list of node coordinates or a dictionary of keys pointing to node coordinates to specify keys.
        edges : list of tuple of int

        Returns
        -------
        Network
            A network object.

        Examples
        --------
        >>>
        """
        network = cls()

        if sys.version_info[0] < 3:
            mapping = collections.Mapping
        else:
            mapping = collections.abc.Mapping

        if isinstance(nodes, mapping):
            for key, (x, y, z) in nodes.items():
                network.add_node(key, x=x, y=y, z=z)
        else:
            for i, (x, y, z) in enumerate(nodes):
                network.add_node(i, x=x, y=y, z=z)

        for u, v in edges:
            network.add_edge(u, v)

        return network

    # --------------------------------------------------------------------------
    # converters
    # --------------------------------------------------------------------------

    def to_obj(self):
        """Write the network to an OBJ file.

        Parameters
        ----------
        filepath : path string or file-like object
            A path or a file-like object pointing to a file.

        Examples
        --------
        >>>
        """
        raise NotImplementedError

    def to_points(self):
        """Return the coordinates of the network.

        Examples
        --------
        >>>
        """
        return [self.node_coordinates(key) for key in self.nodes()]

    def to_lines(self):
        """Return the lines of the network as pairs of start and end point coordinates.

        Examples
        --------
        >>>
        """
        return [self.edge_coordinates(u, v) for u, v in self.edges()]

    def to_nodes_and_edges(self):
        """Return the nodes and edges of a network.

        Returns
        -------
        tuple
            A 2-tuple containing

            * a list of nodes, represented by their XYZ coordinates, and
            * a list of edges.

            Each face is a list of indices referencing the list of node coordinates.

        Examples
        --------
        >>>
        """
        key_index = dict((key, index) for index, key in enumerate(self.nodes()))
        nodes = [self.node_coordinates(key) for key in self.nodes()]
        edges = [(key_index[u], key_index[v]) for u, v in self.edges()]
        return nodes, edges

    # --------------------------------------------------------------------------
    # helpers
    # --------------------------------------------------------------------------

    def key_gkey(self, precision=None):
        """Returns a dictionary that maps node dictionary keys to the corresponding
        *geometric key* up to a certain precision.

        Parameters
        ----------
        precision : str (3f)
            The float precision specifier used in string formatting.

        Returns
        -------
        dict
            A dictionary of key-geometric key pairs.

        """
        gkey = geometric_key
        xyz = self.node_coordinates
        return {key: gkey(xyz(key), precision) for key in self.nodes()}

    def gkey_key(self, precision=None):
        """Returns a dictionary that maps *geometric keys* of a certain precision
        to the keys of the corresponding nodes.

        Parameters
        ----------
        precision : str (3f)
            The float precision specifier used in string formatting.

        Returns
        -------
        dict
            A dictionary of geometric key-key pairs.

        """
        gkey = geometric_key
        xyz = self.node_coordinates
        return {gkey(xyz(key), precision): key for key in self.nodes()}

    node_gkey = key_gkey
    gkey_node = gkey_key

    # --------------------------------------------------------------------------
    # builders
    # --------------------------------------------------------------------------

    def add_node(self, key=None, attr_dict=None, **kwattr):
        if key is None:
            key = self._max_int_key = self._max_int_key + 1
        try:
            if key > self._max_int_key:
                self._max_int_key = key
        except (ValueError, TypeError):
            pass
        return super(Network, self).add_node(key, attr_dict=attr_dict, **kwattr)

    # --------------------------------------------------------------------------
    # modifiers
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # info
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # accessors
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # node attributes
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # edge attributes
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # node topology
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # edge topology
    # --------------------------------------------------------------------------

    # def edge_connected_edges(self, u, v):
    #     """Return the edges connected to an edge.

    #     Parameters
    #     ----------
    #     u : hashable
    #         The identifier of the first node of the edge.
    #     v : hashable
    #         The identifier of the secondt node of the edge.

    #     Returns
    #     -------
    #     list
    #         A list of connected edges.

    #     """
    #     edges = []
    #     for nbr in self.node_neighbors(u):
    #         if nbr in self.edge[u]:
    #             edges.append((u, nbr))
    #         else:
    #             edges.append((nbr, u))
    #     for nbr in self.node_neighbors(v):
    #         if nbr in self.edge[v]:
    #             edges.append((v, nbr))
    #         else:
    #             edges.append((nbr, v))
    #     return edges

    # --------------------------------------------------------------------------
    # node geometry
    # --------------------------------------------------------------------------

    def node_coordinates(self, key, axes='xyz'):
        """Return the coordinates of a node.

        Parameters
        ----------
        key : hashable
            The identifier of the node.
        axes : str, optional
            The components of the node coordinates to return.
            Default is ``'xyz'``.

        Returns
        -------
        list
            The coordniates of the node.
        """
        return [self.node[key][axis] for axis in axes]

    def node_laplacian(self, key):
        """Return the vector from the node to the centroid of its 1-ring neighborhood.

        Parameters
        ----------
        key : hashable
            The identifier of the node.

        Returns
        -------
        list
            The laplacian vector.
        """
        c = centroid_points([self.node_coordinates(nbr) for nbr in self.neighbors(key)])
        p = self.node_coordinates(key)
        return subtract_vectors(c, p)

    def node_neighborhood_centroid(self, key):
        """Compute the centroid of the neighboring nodes.

        Parameters
        ----------
        key : hashable
            The identifier of the node.

        Returns
        -------
        list
            The coordinates of the centroid.
        """
        return centroid_points([self.node_coordinates(nbr) for nbr in self.neighbors(key)])

    # --------------------------------------------------------------------------
    # edge geometry
    # --------------------------------------------------------------------------

    def edge_coordinates(self, u, v, axes='xyz'):
        """Return the coordinates of the start and end point of an edge.

        Parameters
        ----------
        u : hashable
            The key of the start node.
        v : hashable
            The key of the end node.
        axes : str (xyz)
            The axes along which the coordinates should be included.

        Returns
        -------
        tuple
            The coordinates of the start point and the coordinates of the end point.
        """
        return self.node_coordinates(u, axes=axes), self.node_coordinates(v, axes=axes)

    def edge_length(self, u, v):
        """Return the length of an edge.

        Parameters
        ----------
        u : hashable
            The key of the start node.
        v : hashable
            The key of the end node.

        Returns
        -------
        float
            The length of the edge.
        """
        a, b = self.edge_coordinates(u, v)
        return distance_point_point(a, b)

    def edge_vector(self, u, v):
        """Return the vector of an edge.

        Parameters
        ----------
        u : hashable
            The key of the start node.
        v : hashable
            The key of the end node.

        Returns
        -------
        list
            The vector from u to v.
        """
        a, b = self.edge_coordinates(u, v)
        ab = subtract_vectors(b, a)
        return ab

    def edge_point(self, u, v, t=0.5):
        """Return the location of a point along an edge.

        Parameters
        ----------
        u : hashable
            The key of the start node.
        v : hashable
            The key of the end node.
        t : float (0.5)
            The location of the point on the edge.
            If the value of ``t`` is outside the range ``0-1``, the point will
            lie in the direction of the edge, but not on the edge vector.

        Returns
        -------
        list
            The XYZ coordinates of the point.
        """
        a, b = self.edge_coordinates(u, v)
        ab = subtract_vectors(b, a)
        return add_vectors(a, scale_vector(ab, t))

    def edge_midpoint(self, u, v):
        """Return the location of the midpoint of an edge.

        Parameters
        ----------
        u : hashable
            The key of the start node.
        v : hashable
            The key of the end node.

        Returns
        -------
        list
            The XYZ coordinates of the midpoint.
        """
        a, b = self.edge_coordinates(u, v)
        return midpoint_line((a, b))

    def edge_direction(self, u, v):
        """Return the direction vector of an edge.

        Parameters
        ----------
        u : hashable
            The key of the start node.
        v : hashable
            The key of the end node.

        Returns
        -------
        list
            The direction vector of the edge.
        """
        return normalize_vector(self.edge_vector(u, v))
