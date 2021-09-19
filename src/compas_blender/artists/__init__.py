"""
********************************************************************************
artists
********************************************************************************

.. currentmodule:: compas_blender.artists

Artists for visualising (painting) COMPAS data structures in Blender.


Base Classes
============

.. autosummary::
    :toctree: generated/

    BlenderArtist


Classes
=======

.. autosummary::
    :toctree: generated/

    FrameArtist
    NetworkArtist
    MeshArtist
    RobotModelArtist

"""
from compas.plugins import plugin
from compas.artists import Artist

from compas.geometry import Frame
from compas.datastructures import Mesh
from compas.datastructures import Network
from compas.robots import RobotModel

from .artist import BlenderArtist  # noqa: F401
from .frameartist import FrameArtist
from .meshartist import MeshArtist
from .networkartist import NetworkArtist
from .robotmodelartist import (  # noqa: F401
    BaseRobotModelArtist,
    RobotModelArtist
)


Artist.register(Frame, FrameArtist)
Artist.register(Mesh, MeshArtist)
Artist.register(Network, NetworkArtist)
Artist.register(RobotModel, RobotModelArtist)


@plugin(category='factories', pluggable_name='new_artist', requires=['bpy'])
def new_artist_blender(cls, *args, **kwargs):
    data = args[0]
    cls = Artist.ITEM_ARTIST[type(data)]
    return super(Artist, cls).__new__(cls)


__all__ = [
    'new_artist_blender',

    'FrameArtist',
    'NetworkArtist',
    'MeshArtist',
    'RobotModelArtist'
]
