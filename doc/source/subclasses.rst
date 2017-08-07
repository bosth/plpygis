``Geometry`` subclasses
=======================

Creating a new ``plpygis`` geometry from a WKB, GeoJSON or Shapely instance, will produce a new subclass of the base :class:`Geometry <plpygis.geometry.Geometry>` class:

* :class:`Point <plpygis.geometry.Point>`
* :class:`LineString <plpygis.geometry.LineString>`
* :class:`Polygon <plpygis.geometry.Polygon>`
* :class:`MultiPoint <plpygis.geometry.MultiPoint>`
* :class:`LineString <plpygis.geometry.MultiLineString>`
* :class:`MultiPolygon <plpygis.geometry.MultiPolygon>`
* :class:`GeometryCollection <plpygis.geometry.GeometryCollection>`

Creation
--------

New instances of the three base shapes (points, lines and polygons) may be created by passing in coordinates:

.. code-block:: python

    >>> point = Point((0, 0))
    >>> line = LineString([(0, 0), (0, 1)])
    >>> poly = Polygon([[(0, 0), (0, 10), (10, 10), (10, 0), (0, 0)], [(4, 4), (4, 6), (6, 6), (6, 4), (4, 4)]])

Composition
-----------

Individual :class:`LineString <plpygis.geometry.LineString>` instances are composed of a list of :class:`Point <plpygis.geometry.Point>` instances that each represent a vertex in the line. Similarly, :class:`Polygon <plpygis.geometry.Polygon>` instances are composed of a list of :class:`LineString <plpygis.geometry.LineString>` instances that each represent linear rings.

.. note::

  The first linear ring in a polygon should represent the exterior ring, while subsequent linear rings are internal boundaries. ``plpygis`` will not validate geometries when they are created.

The four collection types, :class:`MultiPoint <plpygis.geometry.MultiPoint>`, :class:`LineString <plpygis.geometry.MultiLineString>`, :class:`MultiPolygon <plpygis.geometry.MultiPolygon>` and :class:`GeometryCollection <plpygis.geometry.GeometryCollection>`, are each composed of a list of other geometries of the appropriate type. At creation time, the collection types are created by passing in a list of existing instances:

.. code-block:: python

    >>> p1 = Point((0, 0))
    >>> p2 = Point((1, 1))
    >>> mp = MultiPoint([p1, p2])

SRIDs
-----

An SRID may be added at creation time with an optional ``SRID`` parameter:

.. code-block:: python

    >>> point = Point((0, 0), srid=4326)

``plpygis`` will detect conflicts when multigeometries or collections are created with mixed SRIDs.

.. warning::

    Changing the SRID of an instance that is part of another geometry (such as a :class:`Point <plpygis.geometry.Point>` that is a vertex in a :class:`LineString <plpygis.geometry.LineString>` or a vertex in the linear ring of a :class:`Polygon <plpygis.geometry.Polygon>`) will *not* be detected. When converted to a WKB or Shapely instance, only the SRID of the "parent" geometry will be used.

Dimensionality
--------------

The ``dimz`` and ``dimm`` boolean parameters will indicate whether the geometry will have Z and M dimensions. ``plpygis`` will attempt to match provided coordinates with the requested dimensions or will set them to an initial value of ``0`` if they have not been provided:

.. code-block:: python

    >>> p1 = Point((0, 0, 1), dimz=True, dimm=True)
    >>> print "p1", p1.x, p1.y, p1.z, p1.m
    p1 0 0 1 0
    >>> p2 = Point((0, 0, 1), dimm=True)
    >>> print "p2", p2.x, p2.y, p2.z, p2.m
    p2 0 0 None 1
    >>> p3 = Point((0, 0, 1, 2))
    >>> print "p3", p3.x, p3.y, p3.z, p3.m
    p3 0 0 1 2

The dimensionality of an existing instance may be altered after creation, by setting ``dimz`` or ``dimm``. Adding a dimension will add a Z or M coordinate with an initial value of ``0`` to the geometry and all geometries encompassed within it (*e.g.*, each vertex in a :class:`LineString <plpygis.geometry.LineString>` or each :class:`Point <plpygis.geometry.Point>` in a :class:`MultiPoint <plpygis.geometry.MultiPoint>` will gain the new dimension).

A new dimension may also be added to a single :class:`Point <plpygis.geometry.Point>` by assigning to the :meth:`z <plpygis.geometry.Point.z>` or :meth:`m <plpygis.geometry.Point.m>` properties.

Adding a new dimension to a :class:`Point <plpygis.geometry.Point>` that is a vertex in a :class:`LineString <plpygis.geometry.LineString>` or a vertex in the linear ring of a :class:`Polygon <plpygis.geometry.Polygon>` will *not* change the dimensionality of the :class:`LineString <plpygis.geometry.LineString>` or the :class:`Polygon <plpygis.geometry.Polygon>`. The dimensionality of "parent" instance *must* also be changed for the new coordinates to be reflected when converting to other representations.

.. code-block:: python

    >>> p1 = Point((0, 0))
    >>> p2 = Point((1, 1))
    >>> mp = MultiPoint([p1, p2])
    >>> print mp.dimz
    False
    >>> p1.z = 2
    >>> print mp.dimz
    False
    >>> mp.dimz = True
    >>> print mp.dimz
    True
    >>> print "p1.z", p1.z, "p2.z", p2.z
    p1.z 2 p2.z 0

Performance considerations
--------------------------

``plpygis`` will cache the initial WKB state if an object is created directly from a WKB. As soon as any coordinates or composite geometries are referenced the cached WKB is lost and a subsequent request that requires the WKB will necessitate it being generated from scratch. For large geometries with many points, this can affect performance. Therefore, if doing a conversion to a Shapely geometry - an action which relies on the availability of the WKB - it is recommended that this conversion be done before any other operations on the ``plpygis`` geometry.

.. note::

    Getting :meth:`type <plpygis.geometry.Geometry.type>`, :meth:`srid <plpygis.geometry.Geometry.srid>`, :meth:`dimz <plpygis.geometry.Geometry.dimz>` and :meth:`dimm <plpygis.geometry.Geometry.dimm>` are considered "safe" operations. However writing a new SRID or changing the dimensionality will also result in the cached WKB being lost. The geometries type may never be changed.
