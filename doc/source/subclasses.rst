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

Editing
-------

Coordinates may be accessed and modified after creation.

.. code-block:: python

    >>> point = Point((0, 0))
    >>> print(point.x)
    0
    >>> point.x = 10
    >>> print(point.x)
    10

Composition
-----------

Individual :class:`LineString <plpygis.geometry.LineString>` instances are composed of a list of :class:`Point <plpygis.geometry.Point>` instances that each represent a vertex in the line. Similarly, :class:`Polygon <plpygis.geometry.Polygon>` instances are composed of a list of :class:`LineString <plpygis.geometry.LineString>` instances that each represent linear rings.

The lists of vertices or linear rings can be modified, for example by adding a new :class:`Point <plpygis.geometry.Point>` to the end of a :class:`LineString <plpygis.geometry.LineString>`.

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

When creating a multigeometry with an SRID, each geometry must have the same SRID or no SRID.

.. code-block:: python

    >>> p1 = Point((0, 0), srid=4326)
    >>> p2 = Point((1, 1), srid=4326)
    >>> mp = MultiPoint([p1, p2], srid=4326)

    >>> p3 = Point((0, 0))
    >>> p4 = Point((1, 1))
    >>> mp = MultiPoint([p3, p4], srid=4326)

``plpygis`` will not allow the creation of a multigeometry with no SRID if any of the geometries have one.

.. warning::

    Changing the SRID of an instance that is part of another geometry (such as a :class:`Point <plpygis.geometry.Point>` that is a vertex in a :class:`LineString <plpygis.geometry.LineString>` or a vertex in the linear ring of a :class:`Polygon <plpygis.geometry.Polygon>`) will *not* be detected. When converted to a WKB or Shapely instance, only the SRID of the "parent" geometry will be used.

Dimensionality
--------------

The ``dimz`` and ``dimm`` boolean parameters will indicate whether the geometry will have Z and M dimensions. ``plpygis`` will attempt to match provided coordinates with the requested dimensions or will set them to an initial value of ``0`` if they have not been provided:

.. code-block:: python

    >>> p1 = Point((0, 0, 1), dimz=True, dimm=True)
    >>> print("p1", p1.x, p1.y, p1.z, p1.m)
    p1 0 0 1 0
    >>> p2 = Point((0, 0, 1), dimm=True)
    >>> print("p2", p2.x, p2.y, p2.z, p2.m)
    p2 0 0 None 1
    >>> p3 = Point((0, 0, 1, 2))
    >>> print("p3", p3.x, p3.y, p3.z, p3.m)
    p3 0 0 1 2

The dimensionality of an existing instance may be altered after creation, by setting ``dimz`` or ``dimm``. Adding a dimension will add a Z or M coordinate with an initial value of ``0`` to the geometry and all geometries encompassed within it (*e.g.*, each vertex in a :class:`LineString <plpygis.geometry.LineString>` or each :class:`Point <plpygis.geometry.Point>` in a :class:`MultiPoint <plpygis.geometry.MultiPoint>` will gain the new dimension).

A new dimension may also be added to a single :class:`Point <plpygis.geometry.Point>` by assigning to the :meth:`z <plpygis.geometry.Point.z>` or :meth:`m <plpygis.geometry.Point.m>` properties.

Adding a new dimension to a :class:`Point <plpygis.geometry.Point>` that is a vertex in a :class:`LineString <plpygis.geometry.LineString>` or a vertex in the linear ring of a :class:`Polygon <plpygis.geometry.Polygon>` will *not* change the dimensionality of the :class:`LineString <plpygis.geometry.LineString>` or the :class:`Polygon <plpygis.geometry.Polygon>`. The dimensionality of "parent" instance *must* also be changed for the new coordinates to be reflected when converting to other representations.

.. code-block:: python

    >>> p1 = Point((0, 0))
    >>> p2 = Point((1, 1))
    >>> mp = MultiPoint([p1, p2])
    >>> print(mp.dimz)
    False
    >>> p1.z = 2
    >>> print(p1.miz)
    True
    >>> print(mp.dimz)
    False
    >>> mp.dimz = True
    >>> print(mp.dimz)
    True
    >>> print("p1.z", p1.z, "p2.z", p2.z)
    p1.z 2 p2.z 0

Performance considerations
--------------------------

Lazy evaluation
^^^^^^^^^^^^^^^

``plpygis`` uses native WKB parsing to extract header information that indicates the geometry type, SRID and the presence of a Z or M dimension. Full parsing of the entire geometry only occurs when needed. It is therefore possible to test the type and dimensionality of a :class:`Geometry <plpygis.geometry.Geometry>` with only the first few bytes of data having been read. Perform these checks before performing any action that will require reading the remainder of the WKB.

Caching
^^^^^^^

``plpygis`` will cache the initial WKB it was created from. As soon as any coordinates or composite geometries are referenced, the cached WKB is lost and a subsequent request that requires the WKB will necessitate it being generated from scratch. For sets of large geometries, this can have a noticeable affect on performance. Therefore, if doing a conversion to a Shapely geometry - an action which relies on the availability of the WKB - it is recommended that this conversion be done before any other operations on the ``plpygis`` geometry.

.. note::

    Getting :meth:`type <plpygis.geometry.Geometry.type>`, :meth:`srid <plpygis.geometry.Geometry.srid>`, :meth:`dimz <plpygis.geometry.Geometry.dimz>` and :meth:`dimm <plpygis.geometry.Geometry.dimm>` are considered "safe" operations. However writing a new SRID or changing the dimensionality will also result in the cached WKB being lost. A geometry's type may never be changed.

As a summary, getting the following properties will not affect performance:

* :meth:`type <plpygis.geometry.Geometry.type>`
* :meth:`srid <plpygis.geometry.Geometry.srid>`
* :meth:`dimz <plpygis.geometry.Geometry.dimz>`
* :meth:`dimm <plpygis.geometry.Geometry.dimm>`

Setting the following properties will cause any cached WKB to be cleared: 

* :meth:`srid <plpygis.geometry.Geometry.srid>`
* :meth:`dimz <plpygis.geometry.Geometry.dimz>`
* :meth:`dimm <plpygis.geometry.Geometry.dimm>`

Getting the following property relies on the presence of the WKB (cached or generated):

* :meth:`shapely <plpygis.geometry.Geometry.shapely>`

If the :class:`Geometry <plpygis.geometry.Geometry>` was created from a WKB, the follwing actions will trigger a full parse and will clear the cached copy of the WKB:

* getting :meth:`geojson <plpygis.geometry.Geometry.geojson>` and :meth:`__geo_interface__ <plpygis.geometry.Geometry.__geo_interface__>`
* getting :meth:`shapely <plpygis.geometry.Geometry.shapely>`
* getting any :class:`Point <plpygis.geometry.Point>` coordinate
* getting :meth:`bounds <plpygis.geometry.Geometry.bounds>`
* getting :meth:`vertices <plpygis.geometry.LineString.vertices>`, :meth:`rings <plpygis.geometry.Polygon.rings>`
* getting any component geometry from :class:`MultiPoint <plpygis.geometry.MultiPoint>`, :class:`MultiLineString <plpygis.geometry.MultiLineString>`, :class:`MultiPolygon <plpygis.geometry.MultiPolygon>` or :class:`GeometryCollection <plpygis.geometry.GeometryCollection>`
