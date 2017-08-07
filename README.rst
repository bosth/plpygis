=======
plpygis
=======

``plpygis`` is a Python conveter to and from the PostGIS ``geometry`` type, WKB, EWKB, GeoJSON and Shapely geometries and additionally supports ``__geo_interface__``. ``plpygis`` is intended for use in PL/Python functions.

Basic usage
===========

The ``Geometry`` class and its subclasses can be used to convert to and from PostGIS geometries. The following example will take a PostGIS multipolygon geometry named ``geom`` and find its largest component polygon.

``Geometry()`` can convert a Postigs ``geometry`` that has been passed as a parameter to a PL/Python function. A ``Geometry`` that is returned from the PL/Python function will automatically be converted back to a PostGIS ``geometry``.

.. code-block:: postgres
 
    CREATE OR REPLACE FUNCTION largest_poly(geom geometry)
      RETURNS geometry 
    AS $$
      from plpygis import Geometry
      polygons = Geometry(geom)
      if polygons.type == "Polygon":
          return polygons
      elif polygons.type == "MultiPolygon":
          largest = max(polygons.shapely, key=lambda polygon: polygon.area)
          return Geometry.from_shapely(largest)
      else:
          return None
    $$ LANGUAGE plpythonu;

.. image:: https://readthedocs.org/projects/plpygis/badge/?version=latest
    :target: http://plpygis.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status
