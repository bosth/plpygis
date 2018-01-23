"""
Test Geometry
"""

import unittest
from shapely import geometry
from plpygis import Geometry, Point, LineString, Polygon
from plpygis import MultiPoint, MultiLineString, MultiPolygon, GeometryCollection
from plpygis.exceptions import DependencyError, WkbError, SridError, DimensionalityError

geojson_pt = {"type":"Point","coordinates":[0.0,0.0]}
geojson_ln = {"type":"LineString","coordinates":[[107,60],[102,59]]}
geojson_pg = {"type":"Polygon","coordinates":[[[100,0],[101.0,0.0],[101.0,1.0],[100.0,1.0],[100.0,0.0]]]}
geojson_mpt = {"type":"MultiPoint","coordinates":[[0,0],[1,1]]}
geojson_mln = {"type":"MultiLineString","coordinates":[[[0,0],[1,1]],[[2,2],[3,3]]]}
geojson_mpg = {"type":"MultiPolygon","coordinates":[[[[1,0],[111,0.0],[101.0,1.0],[100.0,1.0],[1,0]]],[[[100,0],[101.0,0.0],[101.0,1.0],[100.0,1.0],[100.0,0.0]]]]}
geojson_gc = {"type":"GeometryCollection","geometries":[{"type":"Point","coordinates":[10,0]},{"type":"LineString","coordinates":[[11,0],[12,1]]}]}
wkb_ln = "0102000000050000000000000040BE40409D640199EB373F400000000080AC3E40BF244710FD1939400000000000503940D2A6484BEB41374000000000801D3740248729C89C832A400000000000833340940338EFAFBB2C40"
wkb_pg = "010300000002000000060000000000000000003440000000000080414000000000000024400000000000003E40000000000000244000000000000024400000000000003E4000000000000014400000000000804640000000000000344000000000000034400000000000804140040000000000000000003E40000000000000344000000000000034400000000000002E40000000000000344000000000000039400000000000003E400000000000003440"
wkb_mpt = "010400008002000000010100008000000000000059400000000000006940000000000000000001010000800000000000000000000000000000F03F0000000000000000"
wkb_mln = "010500004002000000010200004002000000000000000000000000000000000000000000000000004940000000000000F03F000000000000F03F0000000000003940010200004002000000000000000000F0BF000000000000F0BF000000000000F03F2DB29DEFA7C60140ED0DBE3099AA0A400000000000388F40"
wkb_mpg = "01060000000200000001030000000100000004000000000000000000444000000000000044400000000000003440000000000080464000000000008046400000000000003E4000000000000044400000000000004440010300000002000000060000000000000000003440000000000080414000000000000024400000000000003E40000000000000244000000000000024400000000000003E4000000000000014400000000000804640000000000000344000000000000034400000000000804140040000000000000000003E40000000000000344000000000000034400000000000002E40000000000000344000000000000039400000000000003E400000000000003440"
wkb_gc = "0107000000020000000101000000000000000000000000000000000000000102000000020000000000000000000000000000000000F03F000000000000F03F000000000000F03F"

class GeometryTestCase(unittest.TestCase):
    def test_missing_ewkb(self):
        """
        missing EWKB
        """
        self.assertRaises(WkbError, Geometry, None, None)

    def test_malformed_ewkb_len(self):
        """
        malformed EWKB (insufficient bytes)
        """
        self.assertRaises(Exception, Geometry, "0101", None)

    def test_malformed_ewkb_firstbyte(self):
        """
        malformed EWKB (bad first byte)
        """
        self.assertRaises(WkbError, Geometry, "5101", None)

    def test_unsupported_ewkb_type(self):
        """
        unsupported EWKB type
        """
        "010100000000000000000000000000000000000000"
        self.assertRaises(WkbError, Geometry, "010800000000000000000000000000000000000000", None)

    def test_read_wkb_point(self):
        """
        read WKB Point
        """
        wkb = "010100000000000000000000000000000000000000"
        geom = Geometry(wkb)
        self.assertEquals(geom.type, "Point")
        self.assertIsNone(geom.srid)
        self.assertEquals(geom.dimz, False)
        self.assertEquals(geom.dimm, False)
        postgis_type = "geometry(Point)"
        self.assertEquals(geom.postgis_type, postgis_type)
        self.assertEquals(geom.__repr__(), "<Point: 'geometry(Point)'>")
        geom.srid = geom.srid # clear cached WKB
        self.assertEquals(geom.__str__().lower(), wkb.lower())

    def test_read_ewkb_point_srid(self):
        """
        read EWKB Point,4326
        """
        wkb = "0101000020E610000000000000000000000000000000000000"
        geom = Geometry(wkb)
        self.assertEquals(geom.type, "Point")
        self.assertEquals(geom.srid, 4326)
        self.assertEquals(geom.dimz, False)
        self.assertEquals(geom.dimm, False)
        postgis_type = "geometry(Point,4326)"
        self.assertEquals(geom.postgis_type, postgis_type)
        self.assertEquals(geom.__repr__(), "<Point: 'geometry(Point,4326)'>")
        geom.srid = geom.srid # clear cached WKB
        self.assertEquals(geom.__str__().lower(), wkb.lower())

    def test_read_ewkb_pointz(self):
        """
        read EWKB PointZ,4326
        """
        wkb = "01010000A0E6100000000000000000000000000000000000000000000000000000"
        geom = Geometry(wkb)
        self.assertEquals(geom.type, "Point")
        self.assertEquals(geom.srid, 4326)
        self.assertEquals(geom.dimz, True)
        self.assertEquals(geom.dimm, False)
        postgis_type = "geometry(PointZ,4326)"
        self.assertEquals(geom.postgis_type, postgis_type)
        self.assertEquals(geom.__repr__(), "<Point: 'geometry(PointZ,4326)'>")
        geom.srid = geom.srid # clear cached WKB
        self.assertEquals(geom.__str__().lower(), wkb.lower())

    def test_read_ewkb_pointm(self):
        """
        read EWKB PointM,4326
        """
        wkb = "0101000060E6100000000000000000000000000000000000000000000000000000"
        geom = Geometry(wkb)
        self.assertEquals(geom.type, "Point")
        self.assertEquals(geom.srid, 4326)
        self.assertEquals(geom.dimz, False)
        self.assertEquals(geom.dimm, True)
        postgis_type = "geometry(PointM,4326)"
        self.assertEquals(geom.postgis_type, postgis_type)
        self.assertEquals(geom.__repr__(), "<Point: 'geometry(PointM,4326)'>")
        geom.srid = geom.srid # clear cached WKB
        self.assertEquals(geom.__str__().lower(), wkb.lower())

    def test_read_ewkb_pointzm(self):
        """
        read EWKB PointZM,4326
        """
        wkb = "01010000E0E61000000000000000000000000000000000000000000000000000000000000000000000"
        geom = Geometry(wkb)
        self.assertEquals(geom.type, "Point")
        self.assertEquals(geom.srid, 4326)
        self.assertEquals(geom.dimz, True)
        self.assertEquals(geom.dimm, True)
        geom.srid = geom.srid # clear cached WKB
        postgis_type = "geometry(PointZM,4326)"
        self.assertEquals(geom.postgis_type, postgis_type)
        self.assertEquals(geom.__repr__(), "<Point: 'geometry(PointZM,4326)'>")
        geom.srid = geom.srid # clear cached WKB
        self.assertEquals(geom.__str__().lower(), wkb.lower())

    def test_read_wkb_linestring(self):
        """
        read WKB LineString
        """
        wkb = wkb_ln
        geom = Geometry(wkb)
        self.assertEquals(geom.type, "LineString")
        self.assertEquals(geom.srid, None)
        self.assertEquals(geom.dimz, False)
        self.assertEquals(geom.dimm, False)
        postgis_type = "geometry(LineString)"
        geom.vertices
        self.assertEquals(geom.postgis_type, postgis_type)
        self.assertEquals(geom.__repr__(), "<LineString: 'geometry(LineString)'>")
        geom.srid = geom.srid # clear cached WKB
        self.assertEquals(geom.__str__().lower(), wkb.lower())

    def test_read_wkb_polygon(self):
        """
        read WKB Polygon
        """
        wkb = wkb_pg
        geom = Geometry(wkb)
        self.assertEquals(geom.type, "Polygon")
        self.assertEquals(geom.srid, None)
        self.assertEquals(geom.dimz, False)
        self.assertEquals(geom.dimm, False)
        postgis_type = "geometry(Polygon)"
        self.assertEquals(geom.exterior.type, "LineString")
        self.assertEquals(geom.postgis_type, postgis_type)
        self.assertEquals(geom.__repr__(), "<Polygon: 'geometry(Polygon)'>")
        geom.srid = geom.srid # clear cached WKB
        self.assertEquals(geom.__str__().lower(), wkb.lower())

    def test_read_wkb_multipoint(self):
        """
        read WKB MultiPoint
        """
        wkb = wkb_mpt
        geom = Geometry(wkb)
        self.assertEquals(geom.type, "MultiPoint")
        self.assertEquals(geom.srid, None)
        self.assertEquals(geom.dimz, True)
        self.assertEquals(geom.dimm, False)
        postgis_type = "geometry(MultiPointZ)"
        self.assertEquals(geom.postgis_type, postgis_type)
        self.assertEquals(geom.__repr__(), "<MultiPoint: 'geometry(MultiPointZ)'>")
        geom.srid = geom.srid # clear cached WKB
        self.assertEquals(geom.__str__().lower(), wkb.lower())
        for g in geom.geometries:
            self.assertEquals(g.type, "Point")

    def test_read_wkb_multilinestring(self):
        """
        read WKB MultiLineString
        """
        wkb = wkb_mln
        geom = Geometry(wkb)
        self.assertEquals(geom.type, "MultiLineString")
        self.assertEquals(geom.srid, None)
        self.assertEquals(geom.dimz, False)
        self.assertEquals(geom.dimm, True)
        postgis_type = "geometry(MultiLineStringM)"
        self.assertEquals(geom.postgis_type, postgis_type)
        self.assertEquals(geom.__repr__(), "<MultiLineString: 'geometry(MultiLineStringM)'>")
        geom.srid = geom.srid # clear cached WKB
        self.assertEquals(geom.__str__().lower(), wkb.lower())
        for g in geom.geometries:
            self.assertEquals(g.type, "LineString")

    def test_read_wkb_multipolygon(self):
        """
        read WKB MultiPolygon
        """
        wkb = wkb_mpg
        geom = Geometry(wkb)
        self.assertEquals(geom.type, "MultiPolygon")
        self.assertEquals(geom.srid, None)
        self.assertEquals(geom.dimz, False)
        self.assertEquals(geom.dimm, False)
        postgis_type = "geometry(MultiPolygon)"
        self.assertEquals(geom.postgis_type, postgis_type)
        self.assertEquals(geom.__repr__(), "<MultiPolygon: 'geometry(MultiPolygon)'>")
        geom.srid = geom.srid # clear cached WKB
        self.assertEquals(geom.__str__().lower(), wkb.lower())
        for g in geom.geometries:
            self.assertEquals(g.type, "Polygon")

    def test_read_wkb_geometrycollection(self):
        """
        read WKB GeometryCollection
        """
        wkb = wkb_gc
        geom = Geometry(wkb)
        self.assertEquals(geom.type, "GeometryCollection")
        self.assertEquals(geom.srid, None)
        self.assertEquals(geom.dimz, False)
        self.assertEquals(geom.dimm, False)
        postgis_type = "geometry(GeometryCollection)"
        self.assertEquals(geom.postgis_type, postgis_type)
        self.assertEquals(geom.__repr__(), "<GeometryCollection: 'geometry(GeometryCollection)'>")
        geom.srid = geom.srid # clear cached WKB
        self.assertEquals(geom.__str__().lower(), wkb.lower())
        self.assertEquals(geom.geometries[0].type, "Point")
        self.assertEquals(geom.geometries[1].type, "LineString")

    def test_multigeometry_changedimensionality(self):
        """
        change dimensionality of a MultiGeometry
        """
        wkb = wkb_gc
        geom = Geometry(wkb)
        self.assertEquals(geom.dimz, False)
        self.assertEquals(geom.dimm, False)
        geom.dimz = True
        geom.dimm = True
        self.assertEquals(geom.dimz, True)
        self.assertEquals(geom.dimm, True)
        geom.srid = geom.srid # clear cached WKB
        self.assertNotEquals(geom.__str__().lower(), wkb.lower())

    def test_translate_geojson_pt(self):
        """
        load and dump GeoJSON point
        """
        geom = Geometry.from_geojson(geojson_pt)
        self.assertEquals(geom.srid, 4326)
        self.assertEquals(Point, type(geom))
        geojson = geom.geojson
        self.assertEquals(geojson, geojson_pt)

    def test_translate_geojson_ln(self):
        """
        load and dump GeoJSON line
        """
        geom = Geometry.from_geojson(geojson_ln)
        self.assertEquals(geom.srid, 4326)
        self.assertEquals(LineString, type(geom))
        geojson = geom.geojson
        self.assertEquals(geojson, geojson_ln)

    def test_translate_geojson_pg(self):
        """
        load and dump GeoJSON polygon
        """
        geom = Geometry.from_geojson(geojson_pg)
        self.assertEquals(geom.srid, 4326)
        self.assertEquals(Polygon, type(geom))
        geojson = geom.geojson
        self.assertEquals(geojson, geojson_pg)

    def test_translate_geojson_mpt(self):
        """
        load and dump GeoJSON multipoint
        """
        geom = Geometry.from_geojson(geojson_mpt)
        self.assertEquals(geom.srid, 4326)
        self.assertEquals(MultiPoint, type(geom))
        geojson = geom.geojson
        self.assertEquals(geojson, geojson_mpt)

    def test_translate_geojson_mln(self):
        """
        load and dump GeoJSON multiline
        """
        geom = Geometry.from_geojson(geojson_mln)
        self.assertEquals(geom.srid, 4326)
        self.assertEquals(MultiLineString, type(geom))
        geojson = geom.geojson
        self.assertEquals(geojson, geojson_mln)

    def test_translate_geojson_mpg(self):
        """
        load and dump GeoJSON multipolygon
        """
        geom = Geometry.from_geojson(geojson_mpg)
        self.assertEquals(geom.srid, 4326)
        self.assertEquals(MultiPolygon, type(geom))
        geojson = geom.geojson
        self.assertEquals(geojson, geojson_mpg)

    def test_translate_geojson_gc(self):
        """
        load and dump GeoJSON GeometryCollection
        """
        geom = Geometry.from_geojson(geojson_gc)
        self.assertEquals(geom.srid, 4326)
        self.assertEquals(GeometryCollection, type(geom))
        geojson = geom.geojson
        self.assertEquals(geojson, geojson_gc)

    def test_geo_interface(self):
        """
        access using __geo_interface__
        """
        geom = Geometry.from_geojson(geojson_pt)
        self.assertEquals(geojson_pt, geom.__geo_interface__)

    def test_shape(self):
        """
        access using __geo_interface__ and shape
        """
        point = Point.from_geojson(geojson_pt)
        geom = Geometry.shape(point)
        self.assertEquals(point.__geo_interface__, geom.__geo_interface__)

    def test_shapely_dump(self):
        """
        convert to Shapely
        """
        point = Point((123,123))
        sgeom = point.shapely
        self.assertEquals(sgeom.wkb_hex.upper(), point.wkb.upper())

    def test_shapely_load(self):
        """
        convert from Shapely
        """
        sgeom = geometry.Point(99,-99)
        point = Geometry.from_shapely(sgeom)
        self.assertEquals(sgeom.wkb_hex.upper(), point.wkb.upper())

    def test_strip_srid(self):
        """
        strip SRID
        """
        geom1 = Geometry("010100000000000000000000000000000000000000")
        geom2 = Geometry("0101000020E610000000000000000000000000000000000000")
        self.assertIsNone(geom1.srid)
        self.assertEquals(geom2.srid, 4326)
        geom2.srid = None
        self.assertIsNone(geom2.srid)
        self.assertEquals(geom1.wkb, geom2.wkb)
        geom2.srid = None
        self.assertIsNone(geom2.srid)
        self.assertEquals(geom1.wkb, geom2.wkb)

    def test_bounds_point(self):
        """
        check bounds of Point
        """
        geom = Geometry.from_geojson(geojson_pt)
        bounds = geom.bounds
        self.assertEquals(bounds[0], 0.0)
        self.assertEquals(bounds[1], 0.0)
        self.assertEquals(bounds[2], 0.0)
        self.assertEquals(bounds[3], 0.0)

    def test_bounds_linestring(self):
        """
        check bounds of LineString
        """
        geom = Geometry.from_geojson(geojson_pt)
        bounds = geom.bounds
        self.assertEquals(bounds[0], 0.0)
        self.assertEquals(bounds[1], 0.0)
        self.assertEquals(bounds[2], 0.0)
        self.assertEquals(bounds[3], 0.0)

    def test_bounds_point(self):
        """
        check bounds of Point
        """
        geom = Geometry.from_geojson(geojson_pt)
        bounds = geom.bounds
        self.assertEquals(bounds[0], 0.0)
        self.assertEquals(bounds[1], 0.0)
        self.assertEquals(bounds[2], 0.0)
        self.assertEquals(bounds[3], 0.0)

    def test_bounds_point(self):
        """
        check bounds of Point
        """
        geom = Geometry.from_geojson(geojson_pt)
        bounds = geom.bounds
        self.assertEquals(bounds[0], 0.0)
        self.assertEquals(bounds[1], 0.0)
        self.assertEquals(bounds[2], 0.0)
        self.assertEquals(bounds[3], 0.0)

    def test_bounds_linestring(self):
        """
        check bounds of LineString
        """
        geom = Geometry.from_geojson(geojson_ln)
        bounds = geom.bounds
        self.assertEquals(bounds[0], 102)
        self.assertEquals(bounds[1], 59)
        self.assertEquals(bounds[2], 107)
        self.assertEquals(bounds[3], 60)

    def test_bounds_polygon(self):
        """
        check bounds of Polygon
        """
        geom = Geometry.from_geojson(geojson_pg)
        bounds = geom.bounds
        self.assertEquals(bounds[0], 100)
        self.assertEquals(bounds[1], 0)
        self.assertEquals(bounds[2], 101)
        self.assertEquals(bounds[3], 1)

    def test_bounds_multipoint(self):
        """
        check bounds of MultiPoint
        """
        geom = Geometry.from_geojson(geojson_mpt)
        bounds = geom.bounds
        self.assertEquals(bounds[0], 0)
        self.assertEquals(bounds[1], 0)
        self.assertEquals(bounds[2], 1)
        self.assertEquals(bounds[3], 1)

    def test_bounds_multilinestring(self):
        """
        check bounds of MultiLineString
        """
        geom = Geometry.from_geojson(geojson_mln)
        bounds = geom.bounds
        self.assertEquals(bounds[0], 0)
        self.assertEquals(bounds[1], 0)
        self.assertEquals(bounds[2], 3)
        self.assertEquals(bounds[3], 3)

    def test_bounds_multipolygon(self):
        """
        check bounds of MultiPolygon
        """
        geom = Geometry.from_geojson(geojson_mpg)
        bounds = geom.bounds
        self.assertEquals(bounds[0], 1)
        self.assertEquals(bounds[1], 0)
        self.assertEquals(bounds[2], 111)
        self.assertEquals(bounds[3], 1)

    def test_bounds_geomcollection(self):
        """
        check bounds of GeometryCollection
        """
        geom = Geometry.from_geojson(geojson_gc)
        bounds = geom.bounds
        self.assertEquals(bounds[0], 10)
        self.assertEquals(bounds[1], 0)
        self.assertEquals(bounds[2], 12)
        self.assertEquals(bounds[3], 1)

    def test_mixed_dimensionality(self):
        """
        detect mixed dimensionality in MultiGeometries
        """
        p1 = Point((0, 1, 2))
        p2 = Point((0, 1))
        self.assertRaises(DimensionalityError, MultiPoint, [p1, p2], None)

    def test_invalid_point_dimension(self):
        """
        detect extra dimensions in Point creation
        """
        p1 = Point((0, 1, 2, 3))
        self.assertRaises(DimensionalityError, Point, ((0, 1, 2, 3, 4)), None)

    def test_dimension_reading(self):
        """
        check dimensions are set correctly
        """
        p = Point((0, 1))
        self.assertFalse(p.dimz)
        self.assertFalse(p.dimm)
        p = Point((0, 1, 2))
        self.assertTrue(p.dimz)
        self.assertFalse(p.dimm)
        p = Point((0, 1, 2, 3))
        self.assertTrue(p.dimz)
        self.assertTrue(p.dimm)
        p = Point((0, 1, 2, 3), dimz=False, dimm=False)
        self.assertTrue(p.dimz)
        self.assertTrue(p.dimm)
        p = Point((0, 1), dimz=True, dimm=True)
        self.assertTrue(p.dimz)
        self.assertTrue(p.dimm)
        p = Point((0, 1), dimz=True)
        self.assertTrue(p.dimz)
        self.assertFalse(p.dimm)
        p = Point((0, 1), dimm=True)
        self.assertFalse(p.dimz)
        self.assertTrue(p.dimm)
        p = Point((0, 1, 2), dimz=True)
        self.assertTrue(p.dimz)
        self.assertFalse(p.dimm)
        p = Point((0, 1, 2), dimm=True)
        self.assertFalse(p.dimz)
        self.assertTrue(p.dimm)
        p = Point((0, 1, 2), dimz=True, dimm=True)
        self.assertTrue(p.dimz)
        self.assertTrue(p.dimm)

    def test_modify_point(self):
        """
        modify Point
        """
        wkb = "010100000000000000000000000000000000000000"
        p = Geometry(wkb)
        oldx = p.x
        oldy = p.y
        oldsrid = p.srid
        self.assertFalse(p.dimz)
        self.assertFalse(p.dimm)
        newx = -99
        newy = -101
        newz = 88
        newm = 8
        newsrid = 900913
        self.assertNotEquals(p.x, newx)
        self.assertNotEquals(p.y, newy)
        self.assertNotEquals(p.z, newz)
        self.assertNotEquals(p.m, newm)
        self.assertNotEquals(p.srid, newsrid)
        p.x = newx
        p.y = newy
        p.z = newz
        p.m = newm
        p.srid = newsrid
        self.assertEquals(p.x, newx)
        self.assertEquals(p.y, newy)
        self.assertEquals(p.z, newz)
        self.assertEquals(p.m, newm)
        self.assertEquals(p.srid, newsrid)
        self.assertNotEquals(p.__str__().lower(), wkb.lower())
        p.x = oldx
        p.y = oldy
        p.srid = oldsrid
        p.dimz = None
        p.dimm = None
        self.assertEquals(p.__str__().lower(), wkb.lower())
