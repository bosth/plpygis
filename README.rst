=======
plpygis
=======

``plpygis`` is a Python tool that can convert a `PostGIS <https://postgis.net/>`_ ``geometry`` into an equivalent WKB, EWKB, GeoJSON or Shapely geometry. ``plpygis`` is intended for use in PostgreSQL `PL/Python <https://www.postgresql.org/docs/current/plpython.html>`_ functions.

Basic usage
===========

The ``Geometry`` class and its subclasses can be used to convert to and from PostGIS geometries. The following example will take a PostGIS multipolygon geometry named ``geom`` and find its largest component polygon.

``Geometry()`` can convert a PostGIS ``geometry`` that has been passed as a parameter to a PL/Python function. A ``Geometry`` that is returned from the PL/Python function will automatically be converted back to a PostGIS ``geometry``.

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
    $$ LANGUAGE plpython3u;

This can then be called as part of an SQL query:

.. code-block:: postgres

    SELECT largest_poly(geom) FROM countries;

Documentation
=============

Full ``plpygis`` documentation is available at http://plpygis.readthedocs.io/.

.. image:: https://readthedocs.org/projects/plpygis/badge/?version=latest
    :target: http://plpygis.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status
    
.. image:: https://github.com/bosth/plpygis/workflows/tests/badge.svg
    :target: https://github.com/bosth/plpygis/actions?query=workflow%3A%22tests%22
    :alt: Continuous Integration
