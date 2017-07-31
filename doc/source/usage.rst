Basic usage
===========

``plpygis`` is a Python conveter to and from the PostGIS `geometry <https://postgis.net/docs/using_postgis_dbmanagement.html#RefObject>`_ type, WKT, EWKT, WKB, EWKB, GeoJSON and Shapely geometries, or using ``__geo_interface__``. ``plpygis`` is intended for use in PL/Python allowing procedural Python code to complement PostGIS types and functions.

``Geometry``
------------

New ``Geometry`` instances can be created using a `Well-Known Binary (WKB) <https://en.wikipedia.org/wiki/Well-known_text#Well-known_binary>`_ representation of the geometry.

.. code-block:: python

    >>> from plpygis import Geometry
    >>> geom = Geometry("01010000000000000000004AC00000000000000000")

Creation
~~~~~~~~

``Geometry`` instances may also be created from different representations of a geometry.

``Geometry`` instances can be converted using the following methods:

* ``from_wkt()``
* ``from_ewk()``
* ``from_geojson()``
* ``from_shapely()``

.. code-block:: python

    >>> from plpygis import Geometry
    >>> geom = Geometry.from_wkt("POINT(-52 0)")

The ``shape()`` method can convert from any instance that provides ``__geo_interface__`` (see `A Python Protocol for Geospatial Data <https://gist.github.com/sgillies/2217756>`_).

An optional ``srid`` keyword argument may be used with any of the above to set the geometry's SRID. If the representation already provides an SRID (EWKT and Shapely) or implies a particular SRID (GeoJSON), it will be overridden by the user-specified value.

Type
~~~~

Every ``Geometry`` has a type that can be accessed using the instance's ``type`` property. The following types are supported:

* Point
* LineString
* Polygon
* MultiPoint
* MultiLineString
* MultiPolygon
* GeometryCollection

The following EWKB types are not supported:

* Unknown
* CircularString
* CompoundCurve
* CurvePolygon
* MultiCurve
* MultiSurface
* PolyhedralSurface
* Triangle
* Tin

Conversion
~~~~~~~~~~

``Geometry`` instances can also be converted to other representations using the following properties:

* ``wkt``
* ``ewkt``
* ``geojson``
* ``shapely``
* ``wkb``

.. code-block:: python

    >>> from plpygis import Geometry
    >>> geom = Geometry.from_wkt("POINT(-52 0)", 4326)
    >>> print geom.ewkt
    SRID=4326;POINT (-52 0)

``Geometry`` also implements ``__geo_interface__``.

Lazy evaluation
---------------

``plpygis`` uses `Shapely <https://pypi.python.org/pypi/Shapely>`_ for most of its type conversions. However, it uses native WKB parsing to extract header information that indicates the geometry type, SRID and the presence of a Z or M dimension. Full parsing of the entire geometry only occurs when needed.
