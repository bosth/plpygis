"""
Test Geometry
"""

import pytest
from plpygis import Geometry, Point, LineString, Polygon
from plpygis import MultiPoint, MultiLineString, MultiPolygon, GeometryCollection
from plpygis.exceptions import WkbError, SridError, DimensionalityError, CoordinateError, GeojsonError, CollectionError, WktError, DependencyError
from copy import copy, deepcopy

geojson_pt = {"type":"Point","coordinates":[0.0,0.0]}
geojson_ln = {"type":"LineString","coordinates":[[107,60],[102,59]]}
geojson_pg = {"type":"Polygon","coordinates":[[[100,0],[101.0,0.0],[101.0,1.0],[100.0,1.0],[100.0,0.0]]]}
geojson_mpt = {"type":"MultiPoint","coordinates":[[0,0],[1,1]]}
geojson_mln = {"type":"MultiLineString","coordinates":[[[0,0],[1,1]],[[2,2],[3,3]]]}
geojson_mpg = {"type":"MultiPolygon","coordinates":[[[[1,0],[111,0.0],[101.0,1.0],[100.0,1.0],[1,0]]],[[[100,0],[101.0,0.0],[101.0,1.0],[100.0,1.0],[100.0,0.0]]]]}
geojson_gc = {"type":"GeometryCollection","geometries":[{"type":"Point","coordinates":[10,0]},{"type":"LineString","coordinates":[[11,0],[12,1]]}]}
geojson_err = {"type":"Hello","coordinates":[0.0,0.0]}
geojson_pg_ring = {"type":"Polygon","coordinates":[[[100,0], [101,0],[201,1],[100,1],[100,0]],[[100.2,0.2],[100.8,0.2],[100.8,0.8],[100.2,0.8],[100.2,0.2]]]}
wkb_ln = "0102000000050000000000000040BE40409D640199EB373F400000000080AC3E40BF244710FD1939400000000000503940D2A6484BEB41374000000000801D3740248729C89C832A400000000000833340940338EFAFBB2C40"
wkb_pg = "010300000002000000060000000000000000003440000000000080414000000000000024400000000000003E40000000000000244000000000000024400000000000003E4000000000000014400000000000804640000000000000344000000000000034400000000000804140040000000000000000003E40000000000000344000000000000034400000000000002E40000000000000344000000000000039400000000000003E400000000000003440"
wkb_mpt = "010400008002000000010100008000000000000059400000000000006940000000000000000001010000800000000000000000000000000000F03F0000000000000000"
wkb_mln = "010500004002000000010200004002000000000000000000000000000000000000000000000000004940000000000000F03F000000000000F03F0000000000003940010200004002000000000000000000F0BF000000000000F0BF000000000000F03F2DB29DEFA7C60140ED0DBE3099AA0A400000000000388F40"
wkb_mpg = "01060000000200000001030000000100000004000000000000000000444000000000000044400000000000003440000000000080464000000000008046400000000000003E4000000000000044400000000000004440010300000002000000060000000000000000003440000000000080414000000000000024400000000000003E40000000000000244000000000000024400000000000003E4000000000000014400000000000804640000000000000344000000000000034400000000000804140040000000000000000003E40000000000000344000000000000034400000000000002E40000000000000344000000000000039400000000000003E400000000000003440"
wkb_gc = "0107000000020000000101000000000000000000000000000000000000000102000000020000000000000000000000000000000000F03F000000000000F03F000000000000F03F"
wkb_mpt_srid = "0104000020e8030000020000000101000000000000000000000000000000000000000101000000000000000000f03f000000000000f03f"

def test_missing_ewkb():
    """
    Error on missing EWKB
    """
    with pytest.raises(WkbError):
        Geometry(None)

def test_malformed_ewkb_len():
    """
    malformed EWKB (insufficient bytes)
    """
    with pytest.raises(Exception):
        Geometry("0101")

def test_wkb_type():
    """
    malformed EWKB (insufficient bytes)
    """
    with pytest.raises(WkbError):
        Geometry(0)

def test_malformed_ewkb_firstbyte():
    """
    malformed EWKB (bad first byte)
    """
    with pytest.raises(WkbError):
        Geometry("5101")

def test_unsupported_ewkb_type():
    """
    unsupported EWKB type
    """
    with pytest.raises(WkbError):
        Geometry("010800000000000000000000000000000000000000")

def test_read_wkb_point():
    """
    read WKB Point
    """
    wkb = "010100000000000000000000000000000000000000"
    geom = Geometry(wkb)
    assert geom.type == "Point"
    assert geom.srid is None
    assert not geom.dimz
    assert not geom.dimm
    postgis_type = "geometry(Point)"
    assert geom.postgis_type == postgis_type
    assert geom.__repr__() == "<Point: 'geometry(Point)'>"
    geom.srid = geom.srid  # clear cached WKB
    assert geom.__str__().lower() == wkb.lower()

def test_read_wkb_point_big_endian():
    """
    read WKB Point
    """
    geom = Geometry("000000000140000000000000004010000000000000")
    assert isinstance(geom, Point)
    assert geom.x == 2
    assert geom.y == 4
    assert geom.z is None

def test_read_ewkb_point_srid():
    """
    read EWKB Point,4326
    """
    wkb = "0101000020E610000000000000000000000000000000000000"
    geom = Geometry(wkb)
    assert geom.type == "Point"
    assert geom.srid == 4326
    assert not geom.dimz
    assert not geom.dimm
    postgis_type = "geometry(Point,4326)"
    assert geom.postgis_type == postgis_type
    assert geom.__repr__() == "<Point: 'geometry(Point,4326)'>"
    geom.srid = geom.srid # clear cached WKB
    assert geom.ewkb == wkb.lower()
    assert geom.wkb != geom.ewkb
    assert geom.__str__().lower() == wkb.lower()

def test_read_ewkb_pointz():
    """
    read EWKB PointZ,4326
    """
    wkb = "01010000A0E6100000000000000000000000000000000000000000000000000000"
    geom = Geometry(wkb)
    assert geom.type == "Point"
    assert geom.srid == 4326
    assert geom.dimz
    assert not geom.dimm
    postgis_type = "geometry(PointZ,4326)"
    assert geom.postgis_type == postgis_type
    assert geom.__repr__() == "<Point: 'geometry(PointZ,4326)'>"
    geom.srid = geom.srid # clear cached WKB
    assert geom.ewkb == wkb.lower()
    assert geom.wkb != geom.ewkb
    assert geom.__str__().lower() == wkb.lower()

def test_read_ewkb_pointm():
    """
    read EWKB PointM,4326
    """
    wkb = "0101000060E6100000000000000000000000000000000000000000000000000000"
    geom = Geometry(wkb)
    assert geom.type == "Point"
    assert geom.srid == 4326
    assert not geom.dimz
    assert geom.dimm
    postgis_type = "geometry(PointM,4326)"
    assert geom.postgis_type == postgis_type
    assert geom.__repr__() == "<Point: 'geometry(PointM,4326)'>"
    geom.srid = geom.srid # clear cached WKB
    assert geom.ewkb == wkb.lower()
    assert geom.wkb != geom.ewkb
    assert geom.__str__().lower() == wkb.lower()

def test_read_ewkb_pointzm():
    """
    read EWKB PointZM,4326
    """
    wkb = "01010000E0E61000000000000000000000000000000000000000000000000000000000000000000000"
    geom = Geometry(wkb)
    assert geom.type == "Point"
    assert geom.srid == 4326
    assert geom.dimz
    assert geom.dimm
    geom.srid = geom.srid # clear cached WKB
    postgis_type = "geometry(PointZM,4326)"
    assert geom.postgis_type == postgis_type
    assert geom.__repr__() == "<Point: 'geometry(PointZM,4326)'>"
    geom.srid = geom.srid # clear cached WKB
    assert geom.ewkb == wkb.lower()
    assert geom.wkb != geom.ewkb
    assert geom.__str__().lower() == wkb.lower()

def test_read_wkb_data_error():
    """
    read WKB with good header but malformed data
    """
    wkb = "0000000001000000000000"
    geom = Geometry(wkb)
    assert geom.type == "Point"
    with pytest.raises(WkbError):
        geom.x

def test_read_wkb_linestring():
    """
    read WKB LineString
    """
    wkb = wkb_ln
    geom = Geometry(wkb)
    assert geom.type == "LineString"
    assert geom.srid is None
    assert not geom.dimz
    assert not geom.dimm
    postgis_type = "geometry(LineString)"
    geom.vertices
    assert geom.postgis_type == postgis_type
    assert geom.__repr__() == "<LineString: 'geometry(LineString)'>"
    geom.srid = geom.srid # clear cached WKB
    assert geom.__str__().lower() == wkb.lower()

def test_read_wkb_polygon():
    """
    read WKB Polygon
    """
    wkb = wkb_pg
    geom = Geometry(wkb)
    assert geom.type == "Polygon"
    assert geom.srid is None
    assert not geom.dimz
    assert not geom.dimm
    postgis_type = "geometry(Polygon)"
    assert geom.exterior.type == "LineString"
    assert geom.postgis_type == postgis_type
    assert geom.__repr__() == "<Polygon: 'geometry(Polygon)'>"
    geom.srid = geom.srid # clear cached WKB
    assert geom.__str__().lower() == wkb.lower()

def test_read_wkb_multipoint():
    """
    read WKB MultiPoint
    """
    wkb = wkb_mpt
    geom = Geometry(wkb)
    assert geom.type == "MultiPoint"
    assert geom.srid is None
    assert geom.dimz
    assert not geom.dimm
    postgis_type = "geometry(MultiPointZ)"
    assert geom.postgis_type == postgis_type
    assert geom.__repr__() == "<MultiPoint: 'geometry(MultiPointZ)'>"
    geom.srid = geom.srid # clear cached WKB
    assert geom.__str__().lower() == wkb.lower()
    for g in geom.geometries:
        assert g.type == "Point"
    for g in geom.points:
        assert g.type == "Point"
    assert wkb == geom.wkb

def test_read_wkb_multilinestring():
    """
    read WKB MultiLineString
    """
    wkb = wkb_mln
    geom = Geometry(wkb)
    assert geom.type == "MultiLineString"
    assert geom.srid is None
    assert not geom.dimz
    assert geom.dimm
    postgis_type = "geometry(MultiLineStringM)"
    assert geom.postgis_type == postgis_type
    assert geom.__repr__() == "<MultiLineString: 'geometry(MultiLineStringM)'>"
    geom.srid = geom.srid # clear cached WKB
    assert geom.__str__().lower() == wkb.lower()
    for g in geom.geometries:
        assert g.type == "LineString"
    for g in geom.linestrings:
        assert g.type == "LineString"
    assert wkb == geom.wkb

def test_read_wkb_multipolygon():
    """
    read WKB MultiPolygon
    """
    wkb = wkb_mpg
    geom = Geometry(wkb)
    assert geom.type == "MultiPolygon"
    assert geom.srid is None
    assert not geom.dimz
    assert not geom.dimm
    postgis_type = "geometry(MultiPolygon)"
    assert geom.postgis_type == postgis_type
    assert geom.__repr__() == "<MultiPolygon: 'geometry(MultiPolygon)'>"
    geom.srid = geom.srid # clear cached WKB
    assert geom.__str__().lower() == wkb.lower()
    for g in geom.geometries:
        assert g.type == "Polygon"
    for g in geom.polygons:
        assert g.type == "Polygon"
    assert wkb == geom.wkb

def test_read_wkb_geometrycollection():
    """
    read WKB GeometryCollection
    """
    wkb = wkb_gc
    geom = Geometry(wkb)
    assert geom.type == "GeometryCollection"
    assert geom.srid is None
    assert not geom.dimz
    assert not geom.dimm
    postgis_type = "geometry(GeometryCollection)"
    assert geom.postgis_type == postgis_type
    assert geom.__repr__() == "<GeometryCollection: 'geometry(GeometryCollection)'>"
    geom.srid = geom.srid # clear cached WKB
    assert geom.__str__().lower() == wkb.lower()
    assert geom.geometries[0].type == "Point"
    assert geom.geometries[1].type == "LineString"
    assert wkb == geom.wkb

def test_read_wkb_srid():
    wkb_mpt_srid = "0104000020e8030000020000000101000000000000000000000000000000000000000101000000000000000000f03f000000000000f03f"
    geom = Geometry(wkb_mpt_srid)
    wkb = geom.wkb
    ewkb = geom.ewkb
    assert wkb != ewkb

def test_write_wkb_srid():
    p = Point([100, 100], srid=4236)
    p2 = Geometry(p.wkb)
    assert p.x == p2.x
    assert p.y == p2.y
    assert p.dimz == p2.dimz
    assert p.dimm == p2.dimm
    assert p2.srid is None

    p3 = Geometry(p.ewkb)
    assert p.x == p3.x
    assert p.y == p3.y
    assert p.dimz == p3.dimz
    assert p.dimm == p3.dimm
    assert p.srid == p3.srid

def test_multigeometry_raise_error():
    """
    raise error when adding wrong type to a multigeometry
    """
    pt = Point((0,1))
    ls = LineString([(0,1), (2,3)])

    MultiPoint([pt, copy(pt)])

    with pytest.raises(CollectionError):
        MultiPoint([pt, ls])

    with pytest.raises(CollectionError):
        MultiLineString([pt, ls])

    with pytest.raises(CollectionError):
        MultiPolygon([pt, ls])

    with pytest.raises(CollectionError):
        GeometryCollection([pt, ls, True])

def test_multigeometry_nochangedimensionality():
    mp = MultiPoint([Point((0, 1, 2)), Point((5, 6, 7))])
    mp.dimz = True
    assert mp.dimz is True
    mp.dimm = False
    assert mp.dimm is False

def test_point_nullifyzm():
    p = Point((0, 1, 2, 3))
    assert p.dimz is True
    p.z = None
    assert p.dimz is False
    p.dimz = False
    assert p.dimz is False

    assert p.dimm is True
    p.m = None
    assert p.dimm is False
    p.dimm = False
    assert p.dimm is False

def test_multigeometry_changedimensionality():
    """
    change dimensionality of a MultiGeometry
    """
    wkb = wkb_gc
    geom = Geometry(wkb)
    assert not geom.dimz
    assert not geom.dimm
    geom.dimz = True
    geom.dimm = True
    assert geom.dimz
    assert geom.dimm
    geom.srid = geom.srid # clear cached WKB
    assert geom.__str__().lower() != wkb.lower()

def test_malformed_coordinates():
    """
    malformed coordinates (wrong type)
    """
    coordinates = (1, "test")
    with pytest.raises(CoordinateError):
        Point(coordinates)

    coordinates = [(1, 2), [(1, 2), (3, 4)]]
    with pytest.raises(CoordinateError):
        LineString(coordinates)

def test_multigeometry_srid():
    """
    create geometry with SRID
    """
    p1 = Point((0, 0), srid=1000)
    p2 = Point((1, 1), srid=1000)
    mp = MultiPoint([p1, p2], srid=1000)
    assert mp.ewkb == wkb_mpt_srid

def test_multigeometry_srid_exception():
    """
    mixed SRIDs on multigeometry creation
    """
    p1 = Point((0, 0), srid=1000)
    p2 = Point((1, 1), srid=1000)
    with pytest.raises(SridError):
        MultiPoint([p1, p2])

    p1 = Point((0, 0), srid=1000)
    p2 = Point((1, 1), srid=1000)
    with pytest.raises(SridError):
        MultiPoint([p1, p2], 4326)

def test_translate_geojson_pt():
    """
    load and dump GeoJSON point
    """
    geom = Geometry.from_geojson(geojson_pt)
    assert geom.srid == 4326
    assert Point == type(geom)
    geojson = geom.geojson
    assert geojson == geojson_pt

def test_translate_geojson_ln():
    """
    load and dump GeoJSON line
    """
    geom = Geometry.from_geojson(geojson_ln)
    assert geom.srid == 4326
    assert LineString == type(geom)
    geojson = geom.geojson
    assert geojson == geojson_ln

def test_translate_geojson_pg():
    """
    load and dump GeoJSON polygon
    """
    geom = Geometry.from_geojson(geojson_pg)
    assert geom.srid == 4326
    assert Polygon == type(geom)
    geojson = geom.geojson
    assert geojson == geojson_pg

def test_translate_geojson_mpt():
    """
    load and dump GeoJSON multipoint
    """
    geom = Geometry.from_geojson(geojson_mpt)
    assert geom.srid == 4326
    assert MultiPoint == type(geom)
    geojson = geom.geojson
    assert geojson == geojson_mpt

def test_translate_geojson_mln():
    """
    load and dump GeoJSON multiline
    """
    geom = Geometry.from_geojson(geojson_mln)
    assert geom.srid == 4326
    assert MultiLineString == type(geom)
    geojson = geom.geojson
    assert geojson == geojson_mln

def test_translate_geojson_mpg():
    """
    load and dump GeoJSON multipolygon
    """
    geom = Geometry.from_geojson(geojson_mpg)
    assert geom.srid == 4326
    assert MultiPolygon == type(geom)
    geojson = geom.geojson
    assert geojson == geojson_mpg

def test_translate_geojson_gc():
    """
    load and dump GeoJSON GeometryCollection
    """
    geom = Geometry.from_geojson(geojson_gc)
    assert geom.srid == 4326
    assert GeometryCollection == type(geom)
    geojson = geom.geojson
    assert geojson == geojson_gc

def test_translate_geojson_error():
    """
    catch invalid GeoJSON
    """
    with pytest.raises(GeojsonError):
        Geometry.from_geojson(geojson_err)

def test_geo_interface():
    """
    access using __geo_interface__
    """
    geom = Geometry.from_geojson(geojson_pt)
    assert geojson_pt == geom.__geo_interface__

def test_shape():
    """
    access using __geo_interface__ and shape
    """
    point = Point.from_geojson(geojson_pt)
    geom = Geometry.shape(point)
    assert point.__geo_interface__ == geom.__geo_interface__

def test_shapely_dump():
    """
    convert to Shapely
    """
    point = Point((123,123))
    try:
        from shapely import geometry
        sgeom = point.shapely
        assert sgeom.wkb == point.wkb
    except ImportError:
        with pytest.raises(DependencyError):
            sgeom = point.shapely

def test_shapely_load():
    """
    convert from Shapely
    """
    try:
        import shapely
        from shapely import geometry
        sgeom = geometry.Point(99,-99)
        point = Geometry.from_shapely(sgeom)
        assert point.wkb == sgeom.wkb
        assert point.ewkb == shapely.to_wkb(sgeom, include_srid=True)
    except ImportError:
        with pytest.raises(DependencyError):
            point = Geometry.from_shapely(1)

def test_strip_srid():
    """
    strip SRID
    """
    geom1 = Geometry("010100000000000000000000000000000000000000")
    geom2 = Geometry("0101000020E610000000000000000000000000000000000000")
    assert geom1.srid is None
    assert geom2.srid == 4326
    geom2.srid = None
    assert geom2.srid is None
    assert geom1.wkb == geom2.wkb
    geom2.srid = None
    assert geom2.srid is None
    assert geom1.wkb == geom2.wkb

def test_bounds_point():
    """
    check bounds of Point
    """
    geom = Geometry.from_geojson(geojson_pt)
    bounds = geom.bounds
    assert bounds[0] == 0.0
    assert bounds[1] == 0.0
    assert bounds[2] == 0.0
    assert bounds[3] == 0.0

def test_bounds_linestring():
    """
    check bounds of LineString
    """
    geom = Geometry.from_geojson(geojson_ln)
    bounds = geom.bounds
    assert bounds[0] == 102
    assert bounds[1] == 59
    assert bounds[2] == 107
    assert bounds[3] == 60

def test_bounds_polygon():
    """
    check bounds of Polygon
    """
    geom = Geometry.from_geojson(geojson_pg)
    bounds = geom.bounds
    assert bounds[0] == 100
    assert bounds[1] == 0
    assert bounds[2] == 101
    assert bounds[3] == 1

def test_bounds_multipoint():
    """
    check bounds of MultiPoint
    """
    geom = Geometry.from_geojson(geojson_mpt)
    bounds = geom.bounds
    assert bounds[0] == 0
    assert bounds[1] == 0
    assert bounds[2] == 1
    assert bounds[3] == 1

def test_bounds_multilinestring():
    """
    check bounds of MultiLineString
    """
    geom = Geometry.from_geojson(geojson_mln)
    bounds = geom.bounds
    assert bounds[0] == 0
    assert bounds[1] == 0
    assert bounds[2] == 3
    assert bounds[3] == 3

def test_bounds_multipolygon():
    """
    check bounds of MultiPolygon
    """
    geom = Geometry.from_geojson(geojson_mpg)
    bounds = geom.bounds
    assert bounds[0] == 1
    assert bounds[1] == 0
    assert bounds[2] == 111
    assert bounds[3] == 1

def test_bounds_geomcollection():
    """
    check bounds of GeometryCollection
    """
    geom = Geometry.from_geojson(geojson_gc)
    bounds = geom.bounds
    assert bounds[0] == 10
    assert bounds[1] == 0
    assert bounds[2] == 12
    assert bounds[3] == 1

def test_mixed_dimensionality():
    """
    detect mixed dimensionality in MultiGeometries
    """
    p1 = Point((0, 1, 2))
    p2 = Point((0, 1))
    with pytest.raises(DimensionalityError):
        MultiPoint([p1, p2])

def test_invalid_point_dimension():
    """
    detect extra dimensions in Point creation
    """
    with pytest.raises(DimensionalityError):
        Point((0, 1, 2, 3, 4))

def test_dimension_reading():
    """
    check dimensions are set correctly
    """
    p = Point((0, 1))
    assert not p.dimz
    assert not p.dimm
    p = Point((0, 1, 2))
    assert p.dimz
    assert not p.dimm
    p = Point((0, 1, 2, 3))
    assert p.dimz
    assert p.dimm
    p = Point((0, 1, 2, 3), dimz=False, dimm=False)
    assert p.dimz
    assert p.dimm
    p = Point((0, 1), dimz=True, dimm=True)
    assert p.dimz
    assert p.dimm
    p = Point((0, 1), dimz=True)
    assert p.dimz
    assert not p.dimm
    p = Point((0, 1), dimm=True)
    assert not p.dimz
    assert p.dimm
    p = Point((0, 1, 2), dimz=True)
    assert p.dimz
    assert not p.dimm
    p = Point((0, 1, 2), dimm=True)
    assert not p.dimz
    assert p.dimm
    p = Point((0, 1, 2), dimz=True, dimm=True)
    assert p.dimz
    assert p.dimm

def test_modify_point():
    """
    modify Point
    """
    wkb = "010100000000000000000000000000000000000000"
    p = Geometry(wkb)
    oldx = p.x
    oldy = p.y
    oldsrid = p.srid
    assert not p.dimz
    assert not p.dimm
    newx = -99
    newy = -101
    newz = 88
    newm = 8
    newsrid = 900913
    assert p.x != newx
    assert p.y != newy
    assert p.z != newz
    assert p.m != newm
    assert p.srid != newsrid
    p.x = newx
    p.y = newy
    p.z = newz
    p.m = newm
    p.srid = newsrid
    assert p.x == newx
    assert p.y == newy
    assert p.z == newz
    assert p.m == newm
    assert p.srid == newsrid
    assert p.__str__().lower() != wkb.lower()
    p.x = oldx
    p.y = oldy
    p.srid = oldsrid
    p.dimz = None
    p.dimm = None
    assert p.__str__().lower() == wkb.lower()

def test_binary_wkb_roundtrip():
    ewkb = b'\x01\x01\x00\x00\x20\xe6\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    geom = Geometry(ewkb)
    assert geom.ewkb == ewkb
    assert geom.srid == 4326
    assert geom.wkb != ewkb

def test_byte_array_wkb_string():
    wkb = bytearray(b'010100000000000000000000000000000000000000')
    assert str(Geometry(wkb)) == wkb.decode('ascii')

def test_point_coordinates():
    """
    get coordinates of a Point
    """
    coordinates = (1, 2, 3, 4)
    p = Point(coordinates)
    assert p.coordinates == coordinates
    assert p._coordinates(dimm=True, dimz=True) == coordinates
    assert p._coordinates(dimm=False) == (1, 2, 3)
    assert p._coordinates(dimz=False) == (1, 2, 4)
    assert p._coordinates(dimm=False, dimz=False) == (1, 2)

    assert p._coordinates(dimm=True, dimz=True, tpl=False) == list(coordinates)
    assert p._coordinates(dimm=False, tpl=False) == [1, 2, 3]
    assert p._coordinates(dimz=False, tpl=False) == [1, 2, 4]
    assert p._coordinates(dimm=False, dimz=False, tpl=False) == [1, 2]

def test_linestring_coordinates():
    """
    get coordinates of a LineString
    """
    coordinates = [(1, 2, 3, 4), (6, 7, 8, 9)]
    ls = LineString(coordinates)
    assert ls.coordinates == coordinates
    assert ls._coordinates(dimm=True, dimz=True) == coordinates
    assert ls._coordinates(dimm=False) == [(1, 2, 3), (6, 7, 8)]
    assert ls._coordinates(dimz=False) == [(1, 2, 4), (6, 7, 9)]
    assert ls._coordinates(dimz=False, dimm=False) == [(1, 2), (6, 7)]

    assert ls._coordinates(dimm=True, dimz=True, tpl=False) == [[1, 2, 3, 4], [6, 7, 8, 9]]
    assert ls._coordinates(dimm=False, tpl=False) == [[1, 2, 3], [6, 7, 8]]
    assert ls._coordinates(dimz=False, tpl=False) == [[1, 2, 4], [6, 7, 9]]
    assert ls._coordinates(dimz=False, dimm=False, tpl=False) == [[1, 2], [6, 7]]

def test_polygon_coordinates():
    """
    get coordinates of a Polygon
    """
    coordinates = [[(1, 2, 3, 4), (6, 7, 8, 9), (10, 11, 12, 13), (1, 2, 3, 4)]]
    p = Polygon(coordinates)
    assert p.coordinates == coordinates
    assert p._coordinates(dimm=True, dimz=True) == coordinates

    coordinates = [list(map(list, sub)) for sub in coordinates]
    assert p._coordinates(dimm=True, dimz=True, tpl=False) == coordinates

def test_multipoint_coordinates():
    """
    get coordinates of a MultiPoint
    """
    coordinates =  [ (170.0, 45.0), (180.0, 45.0), (-100.0, 45.0), (-170.0, 45.0) ]
    mp = MultiPoint([Point(p) for p in coordinates])
    assert mp.coordinates == coordinates

def test_multilinestring_coordinates():
    """
    get coordinates of a MultiLineString
    """
    coordinates = [ [ (170.0, 45.0), (180.0, 45.0) ], [ (-180.0, 45.0), (-170.0, 45.0) ] ]
    ml = MultiLineString([LineString(c) for c in coordinates])
    assert ml.coordinates == coordinates

def test_multipolygon_coordinates():
    """
    get coordinates of a MultiPolygon
    """
    coordinates = [ [ [ (180.0, 40.0), (180.0, 50.0), (170.0, 50.0), (170.0, 40.0), (180.0, 40.0) ] ], [ [ (-170.0, 40.0), (-170.0, 50.0), (-180.0, 50.0), (-180.0, 40.0), (-170.0, 40.0) ] ] ]
    mp = MultiPolygon([Polygon(c) for c in coordinates])
    assert mp.coordinates == coordinates

def test_point_copy():
    """
    copy a Point object
    """
    p1 = Point((0, 1, 2), srid=4326, dimm=True)
    p2 = copy(p1)
    p3 = copy(p1)

    assert p1.coordinates == p2.coordinates
    assert p1.srid == p2.srid
    assert p1.wkb == p2.wkb
    assert p1 != p2
    assert p1 != p3

    p1.x = 10
    assert p1.x != p2.x
    assert p2.x == p3.x

def test_multipoint_create():
    """
    create a MultiPoint object
    """
    p1 = Point((0, 1, 2))
    p2 = Point((3, 4, 5))
    p3 = Point((6, 7, 8))
    mp = MultiPoint([p1, p2, p3], srid=4326)

    p1.x = 100
    assert mp.geometries[0].x == p1.x
    assert p1.x == 100

def test_multipoint_copy():
    """
    copy a MultiPoint object
    """
    p1 = Point((0, 1, 2))
    p2 = Point((3, 4, 5))
    p3 = Point((6, 7, 8))
    mp1 = MultiPoint([p1, p2, p3], srid=4326)
    mp2 = copy(mp1)

    assert mp1.coordinates == mp2.coordinates

def test_geometrycollection_create():
    """
    create a GeometryCollection object
    """
    pt = Point((0, 1, 2))
    ls = LineString([(3, 4, 5), (9, 10, 11)])
    pl = Polygon([[(1, 2, 3), (6, 7, 8), (10, 11, 12), (1, 2, 3)]])
    gc1 = GeometryCollection([pt, ls, pl])
    gc2 = copy(gc1)
    for i, _ in enumerate(gc1):
        assert gc1[i] == gc2[i]
    pt.x = 100
    assert gc1.coordinates == gc2.coordinates

    gc1.geometries[0].x = 200
    assert gc1.coordinates == gc2.coordinates

def test_geometrycollection_copy():
    """
    modify a GeometryCollection object
    """
    pt = Point((0, 1, 2))
    ls = LineString([(3, 4, 5), (9, 10, 11)])
    pl = Polygon([[(1, 2, 3), (6, 7, 8), (10, 11, 12), (1, 2, 3)]])
    gc1 = GeometryCollection([pt, ls, pl])
    gc1.wkb
    gc2 = copy(gc1)
    assert gc1.wkb == gc2.wkb

    gc2.geometries[0].x = 123
    assert gc1.coordinates == gc2.coordinates
    assert gc2.geometries[0].x == 123
    assert gc1.wkb == gc2.wkb

    pt = Point((-1, -5, -1))
    gc2[1] = pt
    assert gc1.coordinates != gc2.coordinates
    assert gc2.geometries[1].x == -1
    assert gc2.geometries[1].y == -5
    assert gc1.wkb != gc2.wkb

def test_geometrycollection_deepcopy():
    """
    modify a GeometryCollection object
    """
    pt = Point((0, 1, 2))
    ls = LineString([(3, 4, 5), (9, 10, 11)])
    pl = Polygon([[(1, 2, 3), (6, 7, 8), (10, 11, 12), (1, 2, 3)]])
    gc1 = GeometryCollection([pt, ls, pl])
    gc1.wkb
    gc2 = deepcopy(gc1)
    assert gc1.wkb == gc2.wkb
    geoms = zip(gc1.geometries, gc2.geometries)
    for a, b in geoms:
        assert a.wkb == b.wkb
        assert a is not b

    pt = Point((-1, -5, -1))
    gc2[1] = pt
    assert gc1.coordinates != gc2.coordinates

    gc1.geometries[0].x = 0.5
    assert gc1.geometries[0].x == 0.5
    assert gc2.geometries[0].x == 0
    assert gc1[0].wkb != gc2[0].wkb

def test_geometrycollection_edit_wkb():
    """
    Editing object changes WKB
    """
    pt = Point((0, 0))
    gc = GeometryCollection([pt])
    wkb1 = gc.wkb

    pt.x = 1
    wkb2 = gc.wkb

    assert wkb1 != wkb2

def test_geometrycollection_index():
    """
    Overloaded [] access correct item in multigeometry
    """
    pt = Point((0, 0))
    gc = GeometryCollection([pt])

    assert gc.geometries[0] == gc[0]

def test_multigeometry_add():
    """
    Add operator for multigeometries
    """
    p1 = Point((1, 1, 1))
    p2 = Point((2, 2, 2))
    p3 = Point((3, 3, 3))
    p4 = Point((4, 4, 4))

    mp1 = MultiPoint([p1, p2])
    assert len(mp1) == 2

    mpX = mp1 + p1
    assert len(mp1) == 2
    assert len(mpX) == 3
    assert type(mpX) == MultiPoint
    
    ls = LineString([(3, 4, 5), (9, 10, 11)])

    mg = mp1 + ls
    assert len(mg) == 3
    assert type(mg) == GeometryCollection

    mp2 = MultiPoint([p3, p4])
    mp3 = mp1 + mp2
    assert mp3[0].x == 1
    assert mp3[1].x == 2
    assert mp3[2].x == 3
    assert mp3[3].x == 4
    assert len(mp3) == 4
    assert type(mp3) == MultiPoint

def test_multigeometry_iadd():
    p1 = Point((1, 1, 1))
    p2 = Point((2, 2, 2))
    p3 = Point((3, 3, 3))
    p4 = Point((4, 4, 4))
    p5 = Point((5, 5, 5))

    mp1 = MultiPoint([p1, p2])
    mp1 += p3
    assert len(mp1) == 3
    assert type(mp1) == MultiPoint

    mp2 = MultiPoint([p4, p5])
    mp1 += mp2
    assert len(mp1) == 5
    assert type(mp1) == MultiPoint

    ls = LineString([(3, 4, 5), (9, 10, 11)])
    with pytest.raises(CollectionError):
        mp1 += ls

    gc = GeometryCollection([p1, ls])
    gc += p2
    assert len(gc) == 3
    assert type(gc) == GeometryCollection

    gc += mp2
    assert len(gc) == 5
    assert type(gc) == GeometryCollection

def test_geometry_add():
    p1 = Point((1, 1, 1))
    p2 = Point((2, 2, 2))
    p3 = Point((3, 3, 3))

    mp1 = p1 + p2
    assert type(mp1) == MultiPoint
    assert len(mp1) == 2
    assert mp1[0].x == 1
    assert mp1[0].y == 1
    assert mp1[0].z == 1
    assert mp1[1].x == 2
    assert mp1[1].y == 2
    assert mp1[1].z == 2

    mp2 = MultiPoint([p2, p3])

    mp3 = p1 + mp2
    assert type(mp3) == MultiPoint
    assert len(mp3) == 3

    mp4 = mp2 + p1
    assert type(mp4) == MultiPoint
    assert len(mp4) == 3

def test_geometry_add_ls():
    ls1 = LineString([(3, 4, 5), (9, 10, 11)])
    ls2 = LineString([(9, 0, 0), (1, 1, 1)])

    mls = ls1 + ls2
    assert len(mls) == 2
    assert type(mls) == MultiLineString

def test_geometry_add_pg():
    geojson_pg = {"type":"Polygon","coordinates":[[[100,0],[101.0,0.0],[101.0,1.0],[100.0,1.0],[100.0,0.0]]]}
    pg1 = Geometry.from_geojson(geojson_pg, srid=4326)
    pg2 = Geometry(wkb_pg)
    pg2.srid = 4326

    mpg = pg1 + pg2
    assert len(mpg) == 2
    assert type(mpg) == MultiPolygon
    
def test_geometry_add_gc():
    p1 = Point((1, 1, 1))
    p2 = Point((2, 2, 2))
    ls = LineString([(3, 4, 5), (9, 10, 11)])
    mg1 = p1 + ls
    assert len(mg1) == 2
    assert type(mg1) == GeometryCollection

    mg2 = mg1 + p2
    assert len(mg2) == 3
    assert type(mg2) == GeometryCollection

    mg3 = p2 + mg1
    assert len(mg3) == 3
    assert type(mg3) == GeometryCollection

def test_geometry_add_srid():
    p1 = Point((1, 1, 1), srid=4326)
    p2 = Point((2, 2, 2), srid=1234)

    with pytest.raises(CollectionError):
        mp = p1 + p2

    p2.srid = 4326
    mp = p1 + p2
    assert len(mp) == 2

def test_geometry_add_srid():
    p1 = Point((0, 0), 4326)
    p2 = Point((1, 1), 4326)
    p3 = Point((2, 2), 1234)
    p4 = Point((3, 3), 1234)

    mp1 = p1 + p2
    assert mp1.srid == 4326
    mp2 = p3 + p4
    assert mp2.srid == 1234

    with pytest.raises(CollectionError):
        mp3 = mp1 + mp2

    mp1.srid = 3857
    mp2.srid = 3857
    mp3 = mp1 + mp2
    assert mp3.srid == 3857
    assert len(mp3) == 4

def test_geometry_add_srid():
    p1 = Point((0, 0))
    p2 = Point((1, 1), 4326)
    p3 = Point((2, 2))
    p4 = Point((3, 3), 1234)

    mp1 = MultiPoint([p1], 4326)
    mp1 += p2
    assert mp1.srid == 4326

    with pytest.raises(CollectionError):
        mp1 += p4

    mp2 = MultiPoint([p3], 1234)
    mp2 += p4
    assert mp2.srid == 1234

    with pytest.raises(CollectionError):
        mp3 = mp1 + mp2
        assert len(mp3) == 3

def test_multigeometry_getset():
    p0 = Point((0, 0))
    p1 = Point((1, 1))
    p2 = Point((2, 2))
    mp = MultiPoint([p0, p1])
    assert len(mp) == 2
    assert mp[0].x == 0
    assert mp[0].y == 0
    assert mp[1].x == 1
    assert mp[1].y == 1

    mp[0] = p2
    assert mp[0].x == 2
    assert mp[0].y == 2
    assert mp[1].x == 1
    assert mp[1].y == 1

    ls = LineString([(3, 4), (9, 10)])
    with pytest.raises(CollectionError):
        mp[0] = ls

    gc = GeometryCollection([ls, p0])
    with pytest.raises(CollectionError):
        mp[0] = gc
    gc[0] = mp
    assert type(gc[0]) == MultiPoint

def test_interior_ring():
    p = Geometry.from_geojson(geojson_pg_ring)
    exterior = p.exterior
    interior = p.interior

    assert type(exterior) == LineString
    assert len(interior) == 1

def test_wkt_read_point():
    p = Geometry.from_wkt("POINT Z (0 1 1)")
    assert p.type == "Point"
    assert p.x == 0
    assert p.dimz is True
    assert p.dimm is False

def test_wkt_read_linestring():
    l = Geometry.from_wkt("LINESTRING (30 10, 10 30.5, 40 40) ")
    assert l.type == "LineString"
    assert l.vertices[0].x == 30
    assert l.vertices[0].y == 10
    assert l.vertices[1].x == 10
    assert l.vertices[1].y == 30.5
    assert l.dimz is False
    assert l.dimm is False

def test_wkt_read_polygon():
    p = Geometry.from_wkt("POLYGON ((99 0, 1 0, 1 1, 0 1, 0 0))")
    assert p.type == "Polygon"
    assert p.exterior.type == "LineString" 
    assert len(p.exterior.vertices) == 5
    assert p.exterior.vertices[0].x == 99
    assert p.interior == []
    assert p.dimz is False
    assert p.dimm is False

def test_wkt_read_polygon_interior():
    p = Geometry.from_wkt("POLYGON M ((7.5 1 9, 4 0 -1, 4 4 44, 0 4 0.5, 0 0 1), (1 1 -9, 1 1 2, 2 2 2, 0 2 1, 0.5 1 1))")
    assert p.type == "Polygon"
    assert p.exterior.type == "LineString" 
    assert len(p.exterior.vertices) == 5
    assert p.exterior.vertices[0].x == 7.5
    assert p.exterior.vertices[0].m == 9
    assert len(p.interior) == 1
    assert len(p.interior[0].vertices) == 5
    assert p.dimz is False
    assert p.dimm is True

def test_wkt_read_multipoint():
    mp = Geometry.from_wkt("MULTIPOINT ((0 1), (2 3))")
    assert mp.type == "MultiPoint"
    assert len(mp) == 2
    assert mp[0].x == 0
    assert mp[0].y == 1
    assert mp[1].x == 2
    assert mp[1].y == 3
    assert mp.dimz is False
    assert mp.dimm is False

def test_wkt_read_multilinestring():
    ml = Geometry.from_wkt("MULTILINESTRING ((0 0, 1 1), (2 2, 3 3))")
    assert ml.type == "MultiLineString"
    assert len(ml) == 2
    assert str(ml[0].wkb) == "01020000000200000000000000000000000000000000000000000000000000f03f000000000000f03f"
    assert ml.dimz is False
    assert ml.dimm is False

def test_wkt_read_multipolygon():
    mp = Geometry.from_wkt("MULTIPOLYGON (((1 1, 1 3, 3 3, 3 1, 1 1)), ((4 3, 6 3, 6 1, 4 1, 4 3)))  ")
    assert mp.type == "MultiPolygon"
    assert len(mp) == 2
    assert str(mp[0].wkb) == "01030000000100000005000000000000000000f03f000000000000f03f000000000000f03f0000000000000840000000000000084000000000000008400000000000000840000000000000f03f000000000000f03f000000000000f03f"
    assert mp.dimz is False
    assert mp.dimm is False

def test_wkt_read_collection():
    mp = Geometry.from_wkt("GEOMETRYCOLLECTION (MULTIPOINT((0 0), (1 1)), POINT(3 4), LINESTRING(2 3, 3 4))")
    assert mp.type == "GeometryCollection"
    assert len(mp) == 3
    assert mp[0].type == "MultiPoint"
    assert mp[1].type == "Point"
    assert mp[2].type == "LineString"
    assert mp[1].x == 3
    assert mp[1].y == 4
    assert str(mp[0].wkb) == "0104000000020000000101000000000000000000000000000000000000000101000000000000000000f03f000000000000f03f"
    assert mp.dimz is False
    assert mp.dimm is False

def test_wkt_read_collection_dimensions():
    with pytest.raises(DimensionalityError):
        Geometry.from_wkt("GEOMETRYCOLLECTION (MULTIPOINT((0 0), (1 1)), POINT M (3 4 1), LINESTRING(2 3, 3 4))")

def test_ewkt_read_point():
    p = Geometry.from_wkt("SRID=4326;POINT Z (0 1 1)")
    assert p.type == "Point"
    assert p.srid == 4326
    assert p.x == 0
    assert p.dimz is True
    assert p.dimm is False

def test_ewkt_read_collection():
    mp = Geometry.from_wkt("SRID=4326;GEOMETRYCOLLECTION (MULTIPOINT((0 0), (1 1)), POINT(3 4), LINESTRING(2 3, 3 4))")
    assert mp.type == "GeometryCollection"
    assert mp.srid == 4326
    assert len(mp) == 3
    assert mp[0].type == "MultiPoint"
    assert mp[1].type == "Point"
    assert mp[2].type == "LineString"
    assert mp[1].x == 3
    assert mp[1].y == 4
    assert str(mp[0].wkb) == "0104000000020000000101000000000000000000000000000000000000000101000000000000000000f03f000000000000f03f"
    assert mp.dimz is False
    assert mp.dimm is False

def test_ewkt_read_point():
    with pytest.raises(WktError):
        Geometry.from_wkt("SRID=hello;POINT Z (0 1 1)")

def test_ewkt_read_empty():
    with pytest.raises(WktError):
        Geometry.from_wkt("POINT Z EMPTY")
    with pytest.raises(WktError):
        Geometry.from_wkt("LINESTRING ZM EMPTY")
    with pytest.raises(WktError):
        Geometry.from_wkt("POLYGON EMPTY")

    mg = Geometry.from_wkt("MULTIPOINT EMPTY")
    assert mg.type == "MultiPoint"
    assert len(mg) == 0

    mg = Geometry.from_wkt("MULTILINESTRING EMPTY")
    assert mg.type == "MultiLineString"
    assert len(mg) == 0

    mg = Geometry.from_wkt("MULTIPOLYGON EMPTY")
    assert mg.type == "MultiPolygon"
    assert len(mg) == 0

    mg = Geometry.from_wkt("GEOMETRYCOLLECTION EMPTY")
    assert mg.type == "GeometryCollection"
    assert len(mg) == 0
        
def test_read_wkt_malformed():
    with pytest.raises(WktError):
        Geometry.from_wkt("POINT(0 1 1)")

    with pytest.raises(WktError):
        Geometry.from_wkt("POINT ZMX (0 1 1)")

    with pytest.raises(WktError):
        Geometry.from_wkt("POINT EMPTY")

    with pytest.raises(WktError):
        Geometry.from_wkt("HELLO")

    with pytest.raises(WktError):
        Geometry.from_wkt("POLYGON (0 1)")

    with pytest.raises(WktError):
        Geometry.from_wkt("POLYGON (0 1) extra")

def test_wkt_write_empty_collection():
    mp = MultiPoint([])
    assert mp.type == "MultiPoint"
    assert len(mp) == 0
    assert mp.wkt == "MULTIPOINT EMPTY"

def test_wkt_write_point():
    wkt = "SRID=900913;POINT ZM (0 1 2 3)"
    geom = Geometry.from_wkt(wkt)
    assert geom.wkt == wkt.split(";")[1]
    assert geom.ewkt == wkt

def test_wkt_write_linestring():
    wkt = "LINESTRING (0 0, 0 1, 1 2)"
    geom = Geometry.from_wkt(wkt)
    assert geom.wkt == wkt
    
def test_wkt_write_polygon():
    wkt = "POLYGON ((0 0, 4 0, 4 4, 0 4, 0 0), (1 1, 1 2, 2 2, 2 1, 1 1))"
    geom = Geometry.from_wkt(wkt)
    assert geom.wkt == wkt
    
def test_wkt_write_multipoint():
    wkt = "MULTIPOINT ((0 0), (1 1))"
    geom = Geometry.from_wkt(wkt)
    assert geom.wkt == wkt
    
def test_wkt_write_multilinestring():
    wkt = "MULTILINESTRING ((0 0, 1 1), (2 2, 3 3))"
    geom = Geometry.from_wkt(wkt)
    assert geom.wkt == wkt
    
def test_wkt_write_multipolygon():
    wkt = "MULTIPOLYGON (((1 1, 1 3, 3 3, 3 1, 1 1)), ((4 3, 6 3, 6 1, 4 1, 4 3)), ((1 1, 1 3, 3 3, 3 1, 1 1)), ((0 0, 4 0, 4 4, 0 4, 0 0), (1 1, 1 2, 2 2, 2 1, 1 1)))"
    geom = Geometry.from_wkt(wkt)
    assert geom.wkt == wkt
    
def test_wkt_write_linestring():
    wkt = "GEOMETRYCOLLECTION (MULTIPOINT ((0 0), (1 1)), POINT (3 4), LINESTRING (2 3, 3 4))"
    geom = Geometry.from_wkt(wkt)
    assert geom.wkt == wkt

def test_wkt_rounding():
    p = Point((1, 1000, 1000.0000, 1.1000))
    assert p.wkt == "POINT ZM (1 1000 1000 1.1)"

def test_wkt_read_srid():
    p = Geometry.from_wkt("POINT (0 1)", srid=1234)
    assert p.type == "Point"
    assert p.srid == 1234

def test_ewkt_read_srid():
    p = Geometry.from_wkt("SRID=4326;POINT (0 1)", srid=1234)
    assert p.type == "Point"
    assert p.srid == 1234
