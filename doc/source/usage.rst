Basic usage
===========

``plpygis`` is a Python converter to and from the PostGIS `geometry <https://postgis.net/docs/using_postgis_dbmanagement.html#RefObject>`_ type, WKB, EWKB, WKT, EWKT, GeoJSON, Shapely geometries and any object that supports ``__geo_interface__``. ``plpygis`` is intended for use in PL/Python, allowing procedural Python code to complement PostGIS types and functions.

:class:`Geometry <plpygis.geometry.Geometry>`
---------------------------------------------

New :class:`Geometry <plpygis.geometry.Geometry>` instances can be created using a `Well-Known Binary (WKB) <https://en.wikipedia.org/wiki/Well-known_text#Well-known_binary>`_ representation of the geometry in hexadecimal form.

.. code-block:: python

    >>> from plpygis import Geometry
    >>> geom = Geometry("01010000000000000000004AC00000000000000000")

Creation
~~~~~~~~

:class:`Geometry <plpygis.geometry.Geometry>` instances may also be created from different representations of a geometry.

:class:`Geometry <plpygis.geometry.Geometry>` instances can be converted using the following methods:

* :meth:`from_wkt() <plpygis.geometry.Geometry.from_wkt()>`
* :meth:`from_geojson() <plpygis.geometry.Geometry.from_geojson()>`
* :meth:`from_shapely() <plpygis.geometry.Geometry.from_shapely()>`

.. code-block:: python

    >>> from plpygis import Geometry
    >>> point = Geometry.from_geojson({'type': 'Point', 'coordinates': [-52.0, 0.0]})
    >>> polygon = Geometry.from_wkt("POLYGON ((0 0, 1 0, 1 1, 0 1, 0 0))")

The :meth:`shape() <plpygis.geometry.Geometry.shape()>` method can convert from any instance that provides ``__geo_interface__`` (see `A Python Protocol for Geospatial Data <https://gist.github.com/sgillies/2217756>`_).

An optional ``srid`` keyword argument may be used with any of the above to set the geometry's SRID. If the representation already provides an SRID (such as with some Shapely geometries) or implies a particular SRID (GeoJSON), it will be overridden by the user-specified value.

Geometry types
~~~~~~~~~~~~~~

Every :class:`Geometry <plpygis.geometry.Geometry>` has a type that can be accessed using the instance's :meth:`type <plpygis.geometry.Geometry.type>` property. The following geometry types are supported:

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

:class:`Geometry <plpygis.geometry.Geometry>` instances can also be converted to other representations using the following properties:

* :meth:`geojson <plpygis.geometry.Geometry.geojson>`
* :meth:`shapely <plpygis.geometry.Geometry.shapely>`
* :meth:`wkb <plpygis.geometry.Geometry.wkb>`
* :meth:`ewkb <plpygis.geometry.Geometry.ewkb>`
* :meth:`wkt <plpygis.geometry.Geometry.wkt>`
* :meth:`ewkt <plpygis.geometry.Geometry.ewkt>`

.. code-block:: python

    >>> from plpygis import Geometry
    >>> geom = Geometry("01010000000000000000004AC00000000000000000")
    >>> print(geom.wkt)
    POINT (-52 0)

:class:`Geometry <plpygis.geometry.Geometry>` also implements :attr:`__geo_interface__ <plpygis.geometry.Geometry.__geo_interface__>`.

Conversion to GeoJSON or Shapely will result in the M dimension being lost as these representation only support X, Y and Z coordinates (see `RFC 7946 <ttps://tools.ietf.org/html/rfc7946#section-3.1.1>`_).

The precision of coordinates in WKT/EWKT can be controlled by setting :attr:`plpygis.wkt.PRECISION <plpygis.wkt.PRECISION>`; by default, this value is 6.

Exceptions
----------

All ``plpygis`` exceptions inherit from the :class:`PlpygisError <plpygis.exceptions.PlpygisError>` class. The specific exceptions that may be raised are:

* :py:exc:`DependencyError <plpygis.exceptions.DependencyError>`: missing dependency required for an optional feature, such as :meth:`shapely <plpygis.geometry.Geometry.shapely>`
* :py:exc:`CollectionError <plpygis.exceptions.CollectionError>`: error when attempting to create a multigeometry or geometry collection
* :py:exc:`CoordinateError <plpygis.exceptions.CoordinateError>`: error in the coordinates used to create a :class:`Geometry <plpygis.geometry.Geometry>`
* :py:exc:`DimensionalityError <plpygis.exceptions.DimensionalityError>`: error pertaining to the Z or M coordinates of a :class:`Geometry <plpygis.geometry.Geometry>`
* :py:exc:`GeojsonError <plpygis.exceptions.GeojsonError>`: error reading a GeoJSON
* :py:exc:`SridError <plpygis.exceptions.SridError>`: error pertaining to a :class:`Geometry <plpygis.geometry.Geometry>`'s SRIDs
* :py:exc:`WkbError <plpygis.exceptions.WkbError>`: error reading or writing a WKB
* :py:exc:`WktError <plpygis.exceptions.WktError>`: error reading or writing a WKT
