# plpygis

`plpygis` is a pure Python module with no dependencies that can convert geometries between [Well-known binary](https://en.wikipedia.org/wiki/Well-known_binary) (WKB/EWKB), [Well-known Text](https://en.wikipedia.org/wiki/Well-known_text_representation_of_geometry) (WKT/EWKT) and GeoJSON representations. `plpygis` is mainly intended for use in PostgreSQL [PL/Python](https://www.postgresql.org/docs/current/plpython.html) functions to augment [PostGIS](https://postgis.net/)'s native capabilities.

## Basic usage

`plpygis` implements several subclasses of the `Geometry` class, such as `Point`, `LineString`, `MultiPolygon` and so on:

```python
>>> from plpygis import Point
>>> p = Point((-124.005, 49.005), srid=4326)
>>> print(p.ewkb)
0101000020e6100000b81e85eb51005fc0713d0ad7a3804840
>>> print(p.geojson)
{'type': 'Point', 'coordinates': [-124.005, 49.005]}
>>> p.z = 1
>>> print(p.wkt)
POINT Z (-124.005 49.005 1)
```

## Usage with PostGIS

`plpygis` is designed to provide an easy way to implement PL/Python functions that accept `geometry` arguments or return `geometry` results. The following example will take a PostGIS `geometry(Point)` and use an external service to create a `geometry(PointZ)`.

```pgsql
CREATE OR REPLACE FUNCTION add_elevation(geom geometry(POINT))
  RETURNS geometry(POINTZ)
AS $$
  from plpygis import Geometry
  from requests import get
  p = Geometry(geom)

  response = get(f'https://api.open-meteo.com/v1/elevation?longitude={p.x}&latitude={p.y}')
  if response.status_code == 200:
      content = response.json()
      p.z = content['elevation'][0]
      return p
  else:
      return None
$$ LANGUAGE plpython3u;
```

The `Geometry()` constructor will convert a PostGIS `geometry` that has been passed as a parameter to the PL/Python function into one of its `plpygis` subclasses. A `Geometry` that is returned from the PL/Python function will automatically be converted back to a PostGIS `geometry`.

The function above can be called as part of an SQL query:

```pgsql
SELECT
    name,
    add_elevation(geom)
FROM
    city;
```

## Documentation

Full `plpygis` documentation is available at <http://plpygis.readthedocs.io/>.

[![Continuous Integration](https://github.com/bosth/plpygis/workflows/tests/badge.svg)](https://github.com/bosth/plpygis/actions?query=workflow%3A%22tests%22) [![Documentation Status](https://readthedocs.org/projects/plpygis/badge/?version=latest)](http://plpygis.readthedocs.io/en/latest/?badge=latest)
