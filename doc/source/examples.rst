Examples
========

Conversion
----------

Some functions that analyze or manipulate geometries are possible in SQL but are easier to model in a procedural language. The following example will use `Shapely <https://github.com/Toblerity/Shapely>`_ to find the largest component polygon of a multipolygon.

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
    $$ LANGUAGE plpython3u;

A pure PL/pgSQL function will have significantly better performance:

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
    $$ LANGUAGE plpython3u;

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

Rendering output
----------------

The `gj2ascii <https://pypi.python.org/pypi/gj2ascii/0.4.1>`_ project allows geometries to be easily rendered with a PL/Python function.

.. code-block:: postgres

    CREATE FUNCTION show(geom geometry)
      RETURNS text
    AS $$
      from gj2ascii import render
      from plpygis import Geometry
      g = Geometry(geom)
      return render(g)
    $$ LANGUAGE plpython3u

.. code-block:: psql

    db=# SELECT show(geom) FROM countries WHERE name = 'Malta';
                                    show
    -------------------------------------------------------------
         + + + + +                                              +
     + + + + + + + + +                                          +
     + + + + + + + + + + +                                      +
       + + + + + + + + + +                                      +
           + + + + +                                            +
                                                                +
                                 +                              +
                             + +                                +
                           + + + + + + +                        +
                             + + + + + + + + +                  +
                             + + + + + + + + + + +              +
                             + + + + + + + + + + + + +          +
                             + + + + + + + + + + + + + +        +
                             + + + + + + + + + + + + + +        +
                             + + + + + + + + + + + + + + + +    +
                               + + + + + + + + + + + + + + + +  +
                                 + + + + + + + + + + + + + + + ++
                                   + + + + + + + + + + + + + + ++
                                     + + + + + + + + + + + + + ++
                                         + + + + + + + + + +    +
                                                 + + + + +
    (1 row)

Spatial aggregate function
--------------------------

Normally, the function ``show`` as defined above would print the geometries of individual rows, one each per line.

.. code-block:: psql

    db=# SELECT show(geom) FROM countries WHERE continent = 'Africa';

An aggregate version of ``show`` would take all the geometries and print them as a single map.

.. code-block:: psql

    db=# SELECT showall(geom) FROM countries WHERE continent = 'Africa';
                                   showall
    -------------------------------------------------------------
                         1 1 1 Q                                +
                   = = 1 1 1 1 Q                                +
                 = = = 1 1 1 1 1 ; ; ;   ; ; - - -              +
               = = 1 1 1 1 1 1 1 ; ; ; ; ; ; - - -              +
             = @ @ 1 1 1 1 1 1 1 ; ; ; ; ; ; - - -              +
             G @ @ > > 1 1 1 1 1 C ; ; ; ; ; - - - -            +
           @ @ @ @ @ > > 1 1 1 C C C O O ; ; H H H H            +
             @ @ @ @ > > > > C C C C O O O H H H H H H          +
           F F @ @ @ > > > C C C C O O O O H H H H H .          +
           F F > > > $ $ C C D C D ( O O H H H H H H 2 2 .      +
             0 0 0 > $ 4 # D D D D ( O O & H H H I 2 2 2 2   K L+
               J 0 ' ' 4 P D D D D ( O & & & I I I 2 2 2 2 2 2  +
                 : ' ' 4     D ( ( ( & & & & & I I I 2 2 2 2 L  +
                                 ( ( * ) ) ) ) ) S 8 8 8 L L    +
                             M   3 * * ) ) ) ) ) S 8 8 8 L      +
                                 3 * ) ) ) ) ) E R R 8 8        +
                                   ) ) ) ) ) ) R R R R          +
                                   ! ! ) ) ) ) ) R R R          +
                                   ! ! ! ! ) ) U U R R          +
                                   ! ! ! ! U U ) U ? ? ?        +
                                   ! ! ! U U U U ? A ? ?     9 9+
                                 B B B ! ! B U V V ?       9 9  +
                                   B B B % % % V V         9 9  +
                                     B B % % % T ? ?       9 9  +
                                     B B % % T T ?         9    +
                                     B B T T T T T              +
                                       T T T T T                +
                                       T T T T                  +
                                                                +
                                                                +
    (1 row)

The aggregate function is defined with the following properties:

.. code-block:: postgres

    CREATE AGGREGATE showall(geometry) (
      STYPE=geometry[],
      INITCOND='{}',
      SFUNC=array_append,
      FINALFUNC=_final_geom_show
    );

The ``STYPE`` of ``geometry[]`` indicates that after each individual ``geometry`` has been processed, there will be a PostgreSQL list of individual ``geometry`` objects as a result. ``INITCOND`` is used to ensure that list starts empty and can be added to incrementally by the native PostgreSQL function ``array_append``.

The function ``_final_geom_show`` will take the ``STYPE`` as the single parameter:

.. code-block:: postgres

    CREATE OR REPLACE FUNCTION _final_geom_show(geoms geometry[])
      RETURNS text
    AS $$
      from gj2ascii import render_multiple
      from plpygis import Geometry
      from itertools import cycle
      # assign an ascii character sequentially to each geometry
      chars = [chr(i) for i in range(33,126)]
      geojsons = [Geometry(g) for g in geoms]
      layers = zip(geojsons, chars)
      return render_multiple(layers, width)
    $$ LANGUAGE plpython3u

PL/Python automatically maps lists to Python arrays, so ``plpygis`` is only responsible for converting each elment of the list (in the example, above this is done using list comprehension: ``[Geometry(g) for g in geoms]``).
