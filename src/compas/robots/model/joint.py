from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from compas.data import Data
from compas.files import URDFElement
from compas.files import URDFParser
from compas.geometry import Frame
from compas.geometry import Rotation
from compas.geometry import Transformation
from compas.geometry import Translation
from compas.geometry import Vector
from compas.geometry import transform_vectors
from compas.robots.model.base import FrameProxy
from compas.robots.model.base import _attr_from_data
from compas.robots.model.base import _attr_to_data
from compas.robots.model.base import _parse_floats

__all__ = [
    'Joint',
    'ParentLink',
    'ChildLink',
    'Calibration',
    'Dynamics',
    'Limit',
    'Axis',
    'Mimic',
    'SafetyController'
]


class ParentLink(Data):
    """Describes a parent relation between a joint its parent link."""

    def __init__(self, link):
        super(ParentLink, self).__init__()
        self.link = link

    def __str__(self):
        return str(self.link)

    def get_urdf_element(self):
        return URDFElement('parent', {'link': self.link})

    @property
    def data(self):
        return {
            'link': self.link,
        }

    @data.setter
    def data(self, data):
        self.link = data['link']

    @classmethod
    def from_data(cls, data):
        return cls(data['link'])


class ChildLink(Data):
    """Describes a child relation between a joint and its child link."""

    def __init__(self, link):
        super(ChildLink, self).__init__()
        self.link = link

    def __str__(self):
        return str(self.link)

    def get_urdf_element(self):
        return URDFElement('child', {'link': self.link})

    @property
    def data(self):
        return {
            'link': self.link,
        }

    @data.setter
    def data(self, data):
        self.link = data['link']

    @classmethod
    def from_data(cls, data):
        return cls(data['link'])


class Calibration(Data):
    """Reference positions of the joint, used to calibrate the absolute position."""

    def __init__(self, rising=0.0, falling=0.0, reference_position=0.0):
        super(Calibration, self).__init__()
        self.rising = float(rising)
        self.falling = float(falling)
        self.reference_position = float(reference_position)

    def get_urdf_element(self):
        attributes = {
            'rising': self.rising,
            'falling': self.falling,
            'reference_position': self.reference_position,
        }
        attributes = dict(filter(lambda x: x[1], attributes.items()))
        return URDFElement('calibration', attributes)

    @property
    def data(self):
        return {
            'rising': self.rising,
            'falling': self.falling,
            'reference_position': self.reference_position,
        }

    @data.setter
    def data(self, data):
        self.rising = data['rising']
        self.falling = data['falling']
        self.reference_position = data['reference_position']


class Dynamics(Data):
    """Physical properties of the joint used for simulation of dynamics."""

    def __init__(self, damping=0.0, friction=0.0, **kwargs):
        super(Dynamics, self).__init__()
        self.damping = float(damping)
        self.friction = float(friction)
        self.attr = kwargs

    def get_urdf_element(self):
        attributes = {
            'damping': self.damping,
            'friction': self.friction,
        }
        attributes.update(self.attr)
        return URDFElement('dynamics', attributes)

    @property
    def data(self):
        return {
            'damping': self.damping,
            'friction': self.friction,
            'attr': _attr_to_data(self.attr),
        }

    @data.setter
    def data(self, data):
        self.damping = data['damping']
        self.friction = data['friction']
        self.attr = _attr_from_data(data['attr'])


class Limit(Data):
    """Joint limit properties.

    Attributes
    ----------
    effort : float
        Maximum joint effort.
    velocity : float
        Maximum joint velocity.
    lower : float
        Lower joint limit (radians for revolute joints, meter for prismatic joints).
    upper : float
        Upper joint limit (radians for revolute joints, meter for prismatic joints).

    """

    def __init__(self, effort=0.0, velocity=0.0, lower=0.0, upper=0.0, **kwargs):
        super(Limit, self).__init__()
        self.effort = float(effort)
        self.velocity = float(velocity)
        self.lower = float(lower)
        self.upper = float(upper)
        self.attr = kwargs

    def get_urdf_element(self):
        attributes = {
            'lower': self.lower,
            'upper': self.upper,
        }
        attributes = dict(filter(lambda x: x[1], attributes.items()))
        attributes['effort'] = self.effort
        attributes['velocity'] = self.velocity
        attributes.update(self.attr)
        return URDFElement('limit', attributes)

    @property
    def data(self):
        return {
            'effort': self.effort,
            'velocity': self.velocity,
            'lower': self.lower,
            'upper': self.upper,
            'attr': _attr_to_data(self.attr),
        }

    @data.setter
    def data(self, data):
        self.effort = data['effort']
        self.velocity = data['velocity']
        self.lower = data['lower']
        self.upper = data['upper']
        self.attr = _attr_from_data(data['attr'])

    def scale(self, factor):
        """Scale the upper and lower limits by a given factor.

        Parameters
        ----------
        factor : float
            Scale factor.

        Returns
        -------
        None

        """
        self.lower *= factor
        self.upper *= factor


class Mimic(Data):
    """Description of joint mimic."""

    def __init__(self, joint, multiplier=1.0, offset=0.):
        super(Mimic, self).__init__()
        self.joint = joint  # == joint name
        self.multiplier = float(multiplier)
        self.offset = float(offset)

    def get_urdf_element(self):
        attributes = {'joint': self.joint}
        if self.multiplier != 1.0:
            attributes['multiplier'] = self.multiplier
        if self.offset != 0.0:
            attributes['offset'] = self.offset
        return URDFElement('mimic', attributes)

    @property
    def data(self):
        return {
            'joint': self.joint,
            'multiplier': self.multiplier,
            'offset': self.offset,
        }

    @data.setter
    def data(self, data):
        self.joint = data['joint']
        self.multiplier = data['multiplier']
        self.offset = data['offset']

    @classmethod
    def from_data(cls, data):
        mimic = cls(data['joint'])
        mimic.data = data
        return mimic

    def calculate_position(self, mimicked_joint_position):
        return self.multiplier * mimicked_joint_position + self.offset


class SafetyController(Data):
    """Safety controller properties."""

    def __init__(self, k_velocity, k_position=0.0, soft_lower_limit=0.0, soft_upper_limit=0.0):
        super(SafetyController, self).__init__()
        self.k_velocity = float(k_velocity)
        self.k_position = float(k_position)
        self.soft_lower_limit = float(soft_lower_limit)
        self.soft_upper_limit = float(soft_upper_limit)

    def get_urdf_element(self):
        attributes = {
            'k_position': self.k_position,
            'soft_lower_limit': self.soft_lower_limit,
            'soft_upper_limit': self.soft_upper_limit,
        }
        attributes = dict(filter(lambda x: x[1], attributes.items()))
        attributes['k_velocity'] = self.k_velocity
        return URDFElement('safety_controller', attributes)

    @property
    def data(self):
        return {
            'k_velocity': self.k_velocity,
            'k_position': self.k_position,
            'soft_lower_limit': self.soft_lower_limit,
            'soft_upper_limit': self.soft_upper_limit,
        }

    @data.setter
    def data(self, data):
        self.k_velocity = data['k_velocity']
        self.k_position = data['k_position']
        self.soft_lower_limit = data['soft_lower_limit']
        self.soft_upper_limit = data['soft_upper_limit']

    @classmethod
    def from_data(cls, data):
        sc = cls(data['k_velocity'])
        sc.data = data
        return sc


class Axis(Data):
    """Representation of an axis or vector.

    Attributes
    ----------
    x : float
        X coordinate.
    y: float
        Y coordinate.
    z : float
        Z coordinate.
    attr : dict
        Additional axis attributes.

    """

    def __init__(self, xyz='1 0 0', **kwargs):
        # We are not using Vector here because we
        # cannot attach _urdf_source to it due to __slots__
        super(Axis, self).__init__()
        xyz = _parse_floats(xyz)
        xyz = Vector(*xyz)
        if xyz.length != 0:
            xyz.unitize()
        self.x = xyz[0]
        self.y = xyz[1]
        self.z = xyz[2]
        self.attr = kwargs

    def get_urdf_element(self):
        attributes = {'xyz': "{} {} {}".format(self.x, self.y, self.z)}
        attributes.update(self.attr)
        return URDFElement('axis', attributes)

    @property
    def data(self):
        return {
            'x': self.x,
            'y': self.y,
            'z': self.z,
            'attr': _attr_to_data(self.attr),
        }

    @data.setter
    def data(self, data):
        self.x = data['x']
        self.y = data['y']
        self.z = data['z']
        self.attr = _attr_from_data(data['attr'])

    def copy(self):
        """Create a copy of the axis instance."""
        cls = type(self)
        return cls("%f %f %f" % (self.x, self.y, self.z))

    def transform(self, transformation):
        """Transform the axis in place.

        Parameters
        ----------
        transformation : :class:`~compas.geometry.Transformation`
            The transformation used to transform the axis.

        """
        xyz = transform_vectors(
            [[self.x, self.y, self.z]], transformation.matrix)
        self.x = xyz[0][0]
        self.y = xyz[0][1]
        self.z = xyz[0][2]

    def transformed(self, transformation):
        """Return a transformed copy of the axis.

        Parameters
        ----------
        transformation : :class:`~compas.geometry.Transformation`
            The transformation used to transform the axis.

        Returns
        -------
        :class:`Axis`
            The transformed axis.

        """
        xyz = transform_vectors(
            [[self.x, self.y, self.z]], transformation.matrix)
        return Vector(xyz[0][0], xyz[0][1], xyz[0][2])

    @property
    def vector(self):
        """Vector of the axis."""
        return Vector(self.x, self.y, self.z)

    def __str__(self):
        return "[%.3f, %.3f, %.3f]" % (self.x, self.y, self.z)


class Joint(Data):
    """Representation of the kinematics and dynamics of a joint and its safety limits.

    Attributes
    ----------
    name : str
        Unique name for the joint.
    type : str | int
        Joint type either as a string or an index number. See class attributes for named constants and supported types.
    origin : :class:`Frame`
        Frame defining the transformation from the parent link to the child link frame.
    parent : :class:`ParentLink` | str
        Parent link instance or parent link name.
    child : :class:`ChildLink` | str
        Child link instance or name of child link.
    axis : :class:`Axis`
        Joint axis specified in the joint frame. Represents the axis of
        rotation for revolute joints, the axis of translation for prismatic
        joints, and the surface normal for planar joints. The axis is
        specified in the joint frame of reference.
    calibration : :class:`Calibration`
        Reference positions of the joint, used to calibrate the absolute position of the joint.
    dynamics : :class:`Dynamics`
        Physical properties of the joint. These values are used to
        specify modeling properties of the joint, particularly useful for
        simulation.
    limit : :class:`Limit`
        Joint limit properties.
    safety_controller : :class:`SafetyController`
        Safety controller properties.
    mimic : :class:`Mimic`
        Used to specify that the defined joint mimics another existing joint.
    attr : dict
        Non-standard attributes.
    child_link : :class:`Link`
        Joint's child link
    position : float
        The current position of the joint. This depends on the
        joint type, i.e. for revolute joints, it will be the rotation angle
        in radians, for prismatic joints the translation in meters.

    Class Attributes
    ----------------
    REVOLUTE : int
        Revolute joint type.
    CONTINUOUS : int
        Continuous joint type.
    PRISMATIC : int
        Prismatic joint type.
    FIXED : int
        Fixed joint type.
    FLOATING : int
        Floating joint type.
    PLANAR : int
        Planar joint type.
    SUPPORTED_TYPES : list[str]
        String representations of the supported joint types.
    """

    REVOLUTE = 0
    CONTINUOUS = 1
    PRISMATIC = 2
    FIXED = 3
    FLOATING = 4
    PLANAR = 5

    SUPPORTED_TYPES = ('revolute', 'continuous', 'prismatic', 'fixed',
                       'floating', 'planar')

    def __init__(self, name, type, parent, child, origin=None, axis=None,
                 calibration=None, dynamics=None, limit=None,
                 safety_controller=None, mimic=None, **kwargs):

        type_idx = type

        if isinstance(type_idx, str) and type_idx in Joint.SUPPORTED_TYPES:
            type_idx = Joint.SUPPORTED_TYPES.index(type_idx)

        if type_idx not in range(len(Joint.SUPPORTED_TYPES)):
            raise ValueError('Unsupported joint type: %s' % type)

        super(Joint, self).__init__()
        self.name = name
        self.type = type_idx
        self.parent = parent if isinstance(parent, ParentLink) else ParentLink(parent)
        self.child = child if isinstance(child, ChildLink) else ChildLink(child)
        self.origin = origin or Frame.from_euler_angles([0., 0., 0.])
        self.axis = axis or Axis()
        self.calibration = calibration
        self.dynamics = dynamics
        self.limit = limit
        self.safety_controller = safety_controller
        self.mimic = mimic
        self.attr = kwargs
        self.child_link = None
        self.position = 0
        # The following are world-relative frames representing the origin and the axis, which change with
        # the joint state, while `origin` and `axis` above are parent-relative and static.
        self.current_origin = self.origin.copy()
        self.current_axis = self.axis.copy()

    @property
    def origin(self):
        return self._origin

    @origin.setter
    def origin(self, value):
        self._origin = FrameProxy.create_proxy(value)

    @property
    def current_origin(self):
        return self._current_origin

    @current_origin.setter
    def current_origin(self, value):
        self._current_origin = FrameProxy.create_proxy(value)

    def get_urdf_element(self):
        attributes = {
            'name': self.name,
            'type': self.SUPPORTED_TYPES[self.type]
        }
        attributes.update(self.attr)
        elements = [self.parent, self.child, self.axis, self.calibration, self.dynamics,
                    self.limit, self.safety_controller, self.mimic, self.origin]
        return URDFElement('joint', attributes, elements)

    @property
    def data(self):
        return {
            'name': self.name,
            'type': self.SUPPORTED_TYPES[self.type],
            'parent': self.parent.data,
            'child': self.child.data,
            'origin': self.origin.data if self.origin else None,
            'axis': self.axis.data if self.axis else None,
            'calibration': self.calibration.data if self.calibration else None,
            'dynamics': self.dynamics.data if self.dynamics else None,
            'limit': self.limit.data if self.limit else None,
            'safety_controller': self.safety_controller.data if self.safety_controller else None,
            'mimic': self.mimic.data if self.mimic else None,
            'attr': _attr_to_data(self.attr),
            'position': self.position,
        }

    @data.setter
    def data(self, data):
        self.name = data['name']
        self.type = Joint.SUPPORTED_TYPES.index(data['type'])
        self.parent = ParentLink.from_data(data['parent'])
        self.child = ChildLink.from_data(data['child'])
        self.origin = Frame.from_data(data['origin']) if data['origin'] else None
        self.axis = Axis.from_data(data['axis']) if data['axis'] else None
        self.calibration = Calibration.from_data(data['calibration']) if data['calibration'] else None
        self.dynamics = Dynamics.from_data(data['dynamics']) if data['dynamics'] else None
        self.limit = Limit.from_data(data['limit']) if data['limit'] else None
        self.safety_controller = SafetyController.from_data(data['safety_controller']) if data['safety_controller'] else None
        self.mimic = Mimic.from_data(data['mimic']) if data['mimic'] else None
        self.attr = _attr_from_data(data['attr'])
        self.position = data['position']

    @classmethod
    def from_data(cls, data):
        joint = cls(
            data['name'],
            data['type'],
            ParentLink.from_data(data['parent']),
            ChildLink.from_data(data['child'])
        )
        joint.data = data
        return joint

    @property
    def current_transformation(self):
        """Current transformation of the joint."""
        return Transformation.from_frame(self.current_origin)

    def transform(self, transformation):
        """Transform the joint in place.

        Parameters
        ----------
        transformation : :class:`~compas.geometry.Transformation`
            The transformation used to transform the joint.

        Returns
        -------
        None

        """
        self.current_origin.transform(transformation)
        self.current_axis.transform(transformation)

    def _create(self, transformation):
        """Internal method to initialize the transformation tree.

        Parameters
        ----------
        transformation : :class:`~compas.geometry.Transformation`
            The transformation used to transform the joint.

        Returns
        -------
        None

        """
        self.current_origin = self.origin.transformed(transformation)
        self.current_axis.transform(self.current_transformation)

    def calculate_revolute_transformation(self, position):
        """Returns a transformation of a revolute joint.

        A revolute joint rotates about the axis and has a limited range
        specified by the upper and lower limits.

        Parameters
        ----------
        position : float
            Angle in radians.

        Returns
        -------
        :class:`Rotation`
            Transformation of type rotation for the revolute joint.

        """
        if not self.limit:
            raise ValueError('Revolute joints are required to define a limit')

        position = max(min(position, self.limit.upper), self.limit.lower)
        return self.calculate_continuous_transformation(position)

    def calculate_continuous_transformation(self, position):
        """Returns a transformation of a continuous joint.

        A continuous joint rotates about the axis and has no upper and lower
        limits.

        Parameters
        ----------
        position : float
            Angle in radians

        Returns
        -------
        :class:`Rotation`
            Transformation of type rotation for the continuous joint.

        """
        return Rotation.from_axis_and_angle(self.current_axis.vector, position, self.current_origin.point)

    def calculate_prismatic_transformation(self, position):
        """Returns a transformation of a prismatic joint.

        A prismatic joint slides along the axis and has a limited range
        specified by the upper and lower limits.

        Parameters
        ----------
        position : float
            Translation movement in meters.

        Returns
        -------
        :class:`Translation`
            Transformation of type translation for the prismatic joint.

        """
        if not self.limit:
            raise ValueError('Prismatic joints are required to define a limit')

        position = max(min(position, self.limit.upper), self.limit.lower)
        return Translation.from_vector(self.current_axis.vector * position)

    # does this ever happen?
    def calculate_fixed_transformation(self, position):
        """Returns an identity transformation.

        The fixed joint is is not really a joint because it cannot move. All
        degrees of freedom are locked.

        Returns
        -------
        :class:`Translation`
            Identity transformation.

        """
        return Transformation()

    def calculate_floating_transformation(self, position):
        """Returns a transformation of a floating joint.

        A floating joint allows motion for all 6 degrees of freedom.
        """
        raise NotImplementedError

    def calculate_planar_transformation(self, position):
        """Returns a transformation of a planar joint.

        A planar joint allows motion in a plane perpendicular to the axis.
        """
        raise NotImplementedError

    def calculate_transformation(self, position):
        """Returns the transformation of the joint.

        This function calls different calculate_*_transformation depends on self.type

        Parameters
        ----------
        position : float
            Position in radians or meters depending on the joint type.
        """

        # Set the transformation function according to the type
        if not hasattr(self, '_calculate_transformation'):
            switcher = {
                Joint.REVOLUTE: self.calculate_revolute_transformation,
                Joint.CONTINUOUS: self.calculate_continuous_transformation,
                Joint.PRISMATIC: self.calculate_prismatic_transformation,
                Joint.FIXED: self.calculate_fixed_transformation,
                Joint.FLOATING: self.calculate_floating_transformation,
                Joint.PLANAR: self.calculate_planar_transformation
            }
            self._calculate_transformation = switcher.get(self.type)

        return self._calculate_transformation(position)

    def is_configurable(self):
        """Returns ``True`` if the joint can be configured, otherwise ``False``."""
        return self.type != Joint.FIXED and self.mimic is None

    def is_scalable(self):
        """Returns ``True`` if the joint can be scaled, otherwise ``False``."""
        return self.type in [Joint.PLANAR, Joint.PRISMATIC]

    def scale(self, factor):
        """Scale the joint origin and limit (only if scalable) by a given factor.

        Parameters
        ----------
        factor : float
            Scale factor.

        Returns
        -------
        None
        """
        self.current_origin.scale(factor)
        if self.is_scalable():
            self.limit.scale(factor)


URDFParser.install_parser(Joint, 'robot/joint')
URDFParser.install_parser(ParentLink, 'robot/joint/parent')
URDFParser.install_parser(ChildLink, 'robot/joint/child')
URDFParser.install_parser(Calibration, 'robot/joint/calibration')
URDFParser.install_parser(Dynamics, 'robot/joint/dynamics')
URDFParser.install_parser(Limit, 'robot/joint/limit')
URDFParser.install_parser(Axis, 'robot/joint/axis')
URDFParser.install_parser(Mimic, 'robot/joint/mimic')
URDFParser.install_parser(SafetyController, 'robot/joint/safety_controller')

URDFParser.install_parser(Frame, 'robot/joint/origin', proxy_type=FrameProxy)
