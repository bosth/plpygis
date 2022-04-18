PL/Python
=========

The PostgreSQL documentation has a complete reference on authoring `PL/Python <https://www.postgresql.org/docs/current/static/plpython.html>`_ functions.

This section will cover uses of PL/Python with ``plpygis``.

Enabling PL/Python 
------------------

Prior to using PL/Python, it must be loaded in the current database:

.. code-block:: psql

    # CREATE LANGUAGE plpython3u;

.. warning::

    PL/Python is an "untrusted" language, meaning that Python code will have unrestricted access to the system at the same level as the database administrator.

Python 2 and Python 3
~~~~~~~~~~~~~~~~~~~~~

``plpygis`` is compatible with both Python 2 and Python 3. For Python 3, the language is ``plpython3u`` and for Python 2 it is ``plpython2u`` (the generic ``plpythonu`` currently refers to Python 2 in PostgreSQL but this may change in the future).

Function declarations
---------------------

PL/Python function declarations follow the following template:

.. code-block:: postgres

    CREATE FUNCTION funcname (argument-list)
      RETURNS return-type
    AS $$
      # PL/Python function body
    $$ LANGUAGE plpython3u;

Named arguments are provided as a comma-separated list, with the argument name preceding the argument type:

.. code-block:: postgres

    CREATE OR REPLACE FUNCTION make_point(x FLOAT, y FLOAT)
      RETURNS geometry 
    AS $$
      # PL/Python function body
    $$ LANGUAGE plpython3u;

.. warning::

    Variables passed as arguments should *never* be assigned to in a PL/Python function.

Type mappings
-------------

The mapping between types in PL/Python and is PostgreSQL is covered in the `Data Values <https://www.postgresql.org/docs/current/static/plpython-data.html>`_ section of the documentation; it is the role of ``plpygis`` to assist in mapping between PL/Python and PostGIS types.

PostGIS types
~~~~~~~~~~~~~

When authoring a Postgres function that takes a PostGIS geometry as an input parameter or returns a geometry as output, :class:`Geometry <plpygis.geometry.Geometry>` objects will provide the automatic conversion between types.

.. code-block:: postgres

    CREATE OR REPLACE FUNCTION make_point(x FLOAT, y FLOAT)
      RETURNS geometry 
    AS $$
      from plpygis import Point
      p = Point((x, y))
      return p
    $$ LANGUAGE plpython3u;

Input parameter
^^^^^^^^^^^^^^^

A PostGIS geometry passed as the argument to :meth:`Geometry() <plpygis.geometry.Geometry>` will initialize the instance.

.. code-block:: postgres

    CREATE OR REPLACE FUNCTION find_hemisphere(geom geometry)
      RETURNS TEXT
    AS $$
      from plpygis import Geometry
      point = Geometry(geom)
      if point.type != "Point":
          return None
      gj = point.geojson
      lon = gj["coordinates"][0]
      lat = gj["coordinates"][1]

      if lon < 0:
          return "West"
      elif lon > 0:
          return "East"
      else:
          return "Meridian"
    $$ LANGUAGE plpython3u;

.. code-block:: psql

    db=# SELECT name, find_hemisphere(ST_Centroid(geom)) FROM countries LIMIT 10;
              name           | find_hemisphere 
    -------------------------+-----------------
     Aruba                   | West 
     Afghanistan             | East 
     Angola                  | East 
     Anguilla                | West 
     Albania                 | East 
     American Samoa          | West 
     Andorra                 | East 
     Argentina               | West 
     Armenia                 | East 
     Bulgaria                | East
    (10 rows)

Return value
^^^^^^^^^^^^

A :class:`Geometry <plpygis.geometry.Geometry>` can be returned directly from a PL/Python function.

.. code-block:: postgres

    CREATE OR REPLACE FUNCTION make_point(x FLOAT, y FLOAT)
      RETURNS geometry 
    AS $$
      from plpygis import Point 
      return Point((x, y))
    $$ LANGUAGE plpython3u;

.. code-block:: psql

    db=# SELECT make_point(-52, 0);
                     make_point                 
    --------------------------------------------
     01010000000000000000004AC00000000000000000
    (1 row)

This custom ``make_point(x, y)`` functions identically to PostGIS's native `ST_MakePoint(x, y) <https://postgis.net/docs/ST_MakePoint.html>`_.

.. code-block:: psql

    db=# SELECT ST_MakePoint(-52, 0);
                    st_makepoint                
    --------------------------------------------
     01010000000000000000004AC00000000000000000
    (1 row)

``geometry`` and ``geography``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Both PostGIS ``geometry`` and ``geography`` types may be used as arguments or return types. ``plpygis`` does not support ``box2d``, ``box3d``, ``raster`` or any topology types.

``geometry`` and ``geography`` arguments will be treated identically by ``plpygis``, as they share an common WKB format.

However, a PL/Python function that has a return value of ``geography`` must not have an SRID of any value except 4326. It will also be treated differently by certain PostGIS functions.

Imagine two PL/Python functions that both create a polygon with lower-left coordinates at ``(0, 0)`` and upper-right coordinates at ``(50, 50)``. If ``box_geom`` has a return type of ``geometry`` and ``box_geog`` has a return type of ``geography``, area calculations will be evaluated as follows:

.. code-block:: psql

    db=# SELECT ST_Area(box_geom());
         st_area      
    ------------------
            2500
    (1 row)

    db=# SELECT ST_Area(box_geog());
         st_area      
    ------------------
     27805712533424.3
    (1 row)

Arrays and sets
---------------

In addition to returning single values, ``plpygis`` functions may return a list of geometries that can be either interpreted as a PostgreSQL `array <https://www.postgresql.org/docs/current/static/arrays.html>`_ or `set <https://www.postgresql.org/docs/current/static/xfunc-sql.html>`_.

.. code-block:: psql

    db=# CREATE OR REPLACE FUNCTION make_points(x FLOAT, y FLOAT)
      RETURNS SETOF geometry
    AS $$
      from plpygis import Geometry
      from shapely.geometry import Point
      p1 = Point(x, y)
      p2 = Point(y, x)
      return [Geometry.shape(p1), Geometry.shape(p2)]
    $$ LANGUAGE plpython3u;

    db=# SELECT ST_AsText(make_points(10,20));
      st_astext   
    --------------
     POINT(10 20)
     POINT(20 10)

Python's ``yield`` keyword may also be used to return elements in a set rather than returning them as elements in a list.

Shared data
-----------

Each PL/Python function has access to a shared dictionary ``SD`` that can be used to store data between function calls.

As with other data, ``plpygis.Geometry`` instances may be stored in the ``SD`` dictionary for future reference in later function calls.

``plpy``
--------

The ``plpy`` module provides access to helper functions, notably around logging to PostgreSQL's standard log files.

See `Utility Functions <https://www.postgresql.org/docs/current/static/plpython-util.html>`_  in the PostgreSQL documentation.

Aggregate functions
-------------------

PostGIS includes several spatial aggregate functions that accept a set of geometries as input parameters. An aggregate function definition requires different syntax from a normal PL/Python function:

.. code-block:: postgres

    CREATE AGGREGATE agg_fn (
        SFUNC = _state_function,
        STYPE = geometry,
        BASETYPE = geometry, -- optional
        FINALFUNC = wrapup_func, -- optional
        INITCOND = 'POINT(0 0)' -- optional
    );

An aggregate will accept individual inputs of the type defined by ``BASETYPE`` and incrementally producing a single type defined by ``STYPE``. If many geometries will be collapsed down to a single geometry, then both ``BASETYPE`` and ``STYPE`` will be ``geometry``. If many geometries will produce more than one geometry, then the types will be ``geometry`` and ``geometry[]`` respectively.

An example aggregate function would be ``point_cluster``, which takes `n` input geometries and outputs `m` geometries, where `m < n`.

.. code-block:: postgres

    CREATE AGGREGATE point_cluster (
        SFUNC = _point_cluster,
        BASETYPE = geometry,
        STYPE = geometry[],
        INITCOND = '{}'
    );

The function indicated by ``SFUNC`` must accept the ``STYPE`` as the first parameter and ``BASETYPE`` as the second parameter, returning another instance of ``STYPE``. If ``INITCOND`` is provided, this will be the value of the first argument passed to the first call of ``SFUNC``. If it is omitted, the value will be initially set to ``None``.

.. code-block:: postgres

    CREATE FUNCTION _point_cluster(geoms geometry[], newgeom geometry)
      RETURNS geometry[]
    AS $$
      # incremental clustering algorithm here
    $$ LANGUAGE plpython3u;

Alternatively, the ``SFUNC`` can simply collect all the individual geometries into a list and then rely on a single ``FINALFUNC`` to create a new list of geometries that represents the clustered points.

.. code-block:: postgres

    CREATE AGGREGATE point_cluster (
        SFUNC = array_append,
        BASETYPE = geometry,
        STYPE = geometry[],
        INITCOND = '{}',
        FINALFUNC = _point_cluster
    );

The parameter of the ``FINALFUNC`` will be a single ``geometry[]``, representing the collection of individual points.

.. code-block:: postgres

    CREATE FUNCTION _point_cluster(geoms geometry[])
      RETURNS geometry[]
    AS $$
      # clustering algorithm here
    $$ LANGUAGE plpython3u;
