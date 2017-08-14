Examples
========

Geometry functions
------------------

Some functions that analyze or manipulate geometries are possible in SQL but are easier to model in a procedural language. The following example will take a PostGIS multipolygon geometry named ``geom`` and find its largest component polygon.

.. code-block:: postgres
 
    CREATE OR REPLACE FUNCTION largest_poly(geom geometry)
      RETURNS geometry 
    AS $$
      from plpygis import Geometry
      polygons = Geometry(geom)
      if polygons.type == 'Polygon':
          return polygons
      elif polygons.type == 'MultiPolygon':
          largest = max(polygons.shapely, key=lambda polygon: polygon.area)
          return Geometry.from_shapely(largest)
      else:
          return None
    $$ LANGUAGE plpythonu;

An equivalent function is possible in pure SQL and will have significantly better performance:

.. code-block:: postgres

    CREATE OR REPLACE FUNCTION largest_poly_fast(polygons geometry)
      RETURNS geometry
    AS $$
      WITH geoms AS (
          SELECT (ST_Dump(polygons)).geom AS geom 
      )
      SELECT geom
      FROM geoms
      ORDER BY ST_Area(geom) DESC LIMIT 1;
    $$ LANGUAGE sql;

External services
-----------------

Another application of ``plpygis`` is accessing external services or commands directly from PostgreSQL.

.. code-block:: postgres

    CREATE OR REPLACE FUNCTION geocode(geom geometry)
      RETURNS text
    AS $$
      from geopy import Nominatim
      from plpygis import Geometry
      shape = Geometry(geom).shapely
      centroid = shape.centroid
      lon = centroid.x
      lat = centroid.y

      nominatim = Nominatim()
      location = nominatim.reverse((lat, lon))
      return location.address
    $$ LANGUAGE plpythonu;

.. code-block:: psql

    db=# SELECT name, geocode(geom) FROM countries LIMIT 5;
              name           |                       geocode
    -------------------------+-----------------------------------------------------------
     Angola                  | Ringoma, Bié, Angola
     Anguilla                | Eric Reid Road, The Valley, Anguilla
     Albania                 | Bradashesh, Elbasan, Qarku i Elbasanit, 3001, Shqipëria
     American Samoa          | Aunu u, Sa'Ole County, Eastern District, American Samoa
     Andorra                 | Bordes de Rigoder, les Bons, Encamp, AD200, Andorra
    (5 rows)

.. todo:

  * adding dimensions to existing geometries
