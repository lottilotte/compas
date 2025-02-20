from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from math import factorial

from compas.geometry.primitives import Primitive
from compas.geometry.primitives import Point
from compas.geometry.primitives import Vector


def binomial_coefficient(n, k):
    """Returns the binomial coefficient of the :math:`x^k` term in the
    polynomial expansion of the binomial power :math:`(1 + x)^n`.

    Parameters
    ----------
    n : int
        The number of terms.
    k : int
        The index of the coefficient.

    Returns
    -------
    int
        The coefficient.

    Notes
    -----
    Arranging binomial coefficients into rows for successive values of `n`,
    and in which `k` ranges from 0 to `n`, gives a triangular array known as
    Pascal's triangle.

    """
    return int(factorial(n) / float(factorial(k) * factorial(n - k)))


def bernstein(n, k, t):
    """k:sup:`th` of `n` + 1 Bernstein basis polynomials of degree `n`. A
    weighted linear combination of these basis polynomials is called a Bernstein
    polynomial.

    Parameters
    ----------
    n : int
        The degree of the polynomial.
    k : int
        The number of the basis polynomial.
    t : float
        The variable.

    Returns
    -------
    float
        The value of the Bernstein basis polynomial at `t`.

    Notes
    -----
    When constructing Bezier curves, the weights are simply the coordinates
    of the control points of the curve.

    References
    ----------
    More info at [1]_.

    .. [1] https://en.wikipedia.org/wiki/Bernstein_polynomial

    Examples
    --------
    >>> bernstein(3, 2, 0.5)
    0.375

    """
    if k < 0:
        return 0
    if k > n:
        return 0
    return binomial_coefficient(n, k) * t ** k * (1 - t) ** (n - k)


class Bezier(Primitive):
    """A Bezier curve is defined by control points and a degree.

    A Bezier curve of degree `n` is a linear combination of ``n + 1`` Bernstein
    basis polynomials of degree `n`.

    Parameters
    ----------
    points : sequence[point]
        A sequence of control points, represented by their location in 3D space.

    Attributes
    ----------
    points : list[:class:`~compas.geometry.Point`]
        The control points.
    degree : int, read-only
        The degree of the curve.

    Examples
    --------
    >>> curve = Bezier([[0.0, 0.0, 0.0], [0.5, 1.0, 0.0], [1.0, 0.0, 0.0]])
    >>> curve.degree
    2

    """

    __slots__ = ['_points']

    def __init__(self, points):
        super(Bezier, self).__init__()
        self._points = []
        self.points = points

    # ==========================================================================
    # data
    # ==========================================================================

    @property
    def data(self):
        """dict : The data dictionary that represents the curve."""
        return {'points': [list(point) for point in self.points]}

    @data.setter
    def data(self, data):
        self.points = data['points']

    @classmethod
    def from_data(cls, data):
        """Construct a curve from its data representation.

        Parameters
        ----------
        data : dict
            The data dictionary.

        Returns
        -------
        :class:`~compas.geometry.Bezier`
            The constructed bezier curve.

        Examples
        --------
        >>> from compas.geometry import Bezier
        >>> data = {'points': [[0.0, 0.0, 0.0], [0.5, 1.0, 0.0], [1.0, 0.0, 0.0]]}
        >>> curve = Bezier.from_data(data)

        """
        return cls(data['points'])

    # ==========================================================================
    # properties
    # ==========================================================================

    @property
    def points(self):
        return self._points

    @points.setter
    def points(self, points):
        if points:
            self._points = [Point(*point) for point in points]

    @property
    def degree(self):
        return len(self.points) - 1

    # ==========================================================================
    # constructors
    # ==========================================================================

    # ==========================================================================
    # methods
    # ==========================================================================

    def transform(self, T):
        """Transform this curve.

        Parameters
        ----------
        T : :class:`~compas.geometry.Transformation`
            The transformation.

        Returns
        -------
        None

        """
        for point in self.points:
            point.transform(T)

    def point(self, t):
        """Compute a point on the curve.

        Parameters
        ----------
        t : float
            The value of the curve parameter. Must be between 0 and 1.

        Returns
        -------
        :class:`~compas.geometry.Point`
            the corresponding point on the curve.

        Examples
        --------
        >>> curve = Bezier([[0.0, 0.0, 0.0], [0.5, 1.0, 0.0], [1.0, 0.0, 0.0]])
        >>> curve.point(0.0)
        Point(0.000, 0.000, 0.000)
        >>> curve.point(1.0)
        Point(1.000, 0.000, 0.000)

        """
        n = self.degree
        point = Point(0, 0, 0)
        for i, p in enumerate(self.points):
            b = bernstein(n, i, t)
            point += p * b
        return point

    def tangent(self, t):
        """Compute the tangent vector at a point on the curve.

        Parameters
        ----------
        t : float
            The value of the curve parameter. Must be between 0 and 1.

        Returns
        -------
        :class:`~compas.geometry.Vector`
            The corresponding tangent vector.

        Examples
        --------
        >>> curve = Bezier([[0.0, 0.0, 0.0], [0.5, 1.0, 0.0], [1.0, 0.0, 0.0]])
        >>> curve.tangent(0.5)
        Vector(1.000, 0.000, 0.000)

        """
        n = self.degree
        v = Vector(0, 0, 0)
        for i, p in enumerate(self.points):
            a = bernstein(n - 1, i - 1, t)
            b = bernstein(n - 1, i, t)
            c = n * (a - b)
            v += p * c
        v.unitize()
        return v

    def locus(self, resolution=100):
        """Compute the locus of all points on the curve.

        Parameters
        ----------
        resolution : int
            The number of intervals at which a point on the curve should be computed.

        Returns
        -------
        list[:class:`~compas.geometry.Point`]
            Points along the curve.

        Examples
        --------
        >>> curve = Bezier([[0.0, 0.0, 0.0], [0.5, 1.0, 0.0], [1.0, 0.0, 0.0]])
        >>> points = curve.locus(10)
        >>> len(points) == 10
        True
        >>> points[0]
        Point(0.000, 0.000, 0.000)
        >>> points[-1]
        Point(1.000, 0.000, 0.000)

        """
        locus = []
        divisor = float(resolution - 1)
        for i in range(resolution):
            t = i / divisor
            locus.append(self.point(t))
        return locus
