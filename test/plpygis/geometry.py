"""
Test Geometry
"""

import unittest
from shapely import geometry
from plpygis import Geometry, Point, LineString, Polygon
from plpygis import MultiPoint, MultiLineString, MultiPolygon, GeometryCollection

geojson_pt = {"type":"Point","coordinates":[0.0,0.0]}
geojson_ln = {"type":"LineString","coordinates":[[107,60],[102,59]]}
geojson_pg = {"type":"Polygon","coordinates":[[[100,0],[101.0,0.0],[101.0,1.0],[100.0,1.0],[100.0,0.0]]]}
geojson_mpt = {"type":"MultiPoint","coordinates":[[0,0],[1,1]]}
geojson_mln = {"type":"MultiLineString","coordinates":[[[0,0],[1,1]],[[2,2],[3,3]]]}
geojson_mpg = {"type":"MultiPolygon","coordinates":[[[[1,0],[111,0.0],[101.0,1.0],[100.0,1.0],[1,0]]],[[[100,0],[101.0,0.0],[101.0,1.0],[100.0,1.0],[100.0,0.0]]]]}
geojson_gc = {"type":"GeometryCollection","geometries":[{"type":"Point","coordinates":[10,0]},{"type":"LineString","coordinates":[[11,0],[12,1]]}]}

class GeometryTestCase(unittest.TestCase):
    def test_missing_ewkb(self):
        """
        missing EWKB
        """
        self.assertRaises(TypeError, Geometry, None, None)

    def test_malformed_ewkb_len(self):
        """
        malformed EWKB (insufficient bytes)
        """
        self.assertRaises(Exception, Geometry, "0101", None)

    def test_malformed_ewkb_firstbyte(self):
        """
        malformed EWKB (bad first byte)
        """
        self.assertRaises(Exception, Geometry, "5101", None)

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
        self.assertEquals(geom.__str__(), wkb)

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
        self.assertEquals(geom.__str__(), wkb)

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
        self.assertEquals(geom.__str__(), wkb)

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
        self.assertEquals(geom.__str__(), wkb)

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
        postgis_type = "geometry(PointZM,4326)"
        self.assertEquals(geom.postgis_type, postgis_type)
        self.assertEquals(geom.__repr__(), "<Point: 'geometry(PointZM,4326)'>")
        self.assertEquals(geom.__str__(), wkb)

#    def test_translate_wkt(self):
#        """
#        load and dump WKT
#        """
#        point = "Point (59410.57968 7208125.2)"
#        geom = Geometry.from_wkt(point, 3857)
#        self.assertEquals(geom.srid, 3857)
#        wkt = geom.wkt
#        self.assertEquals(wkt.upper(), point.upper())
#
#    def test_translate_ewkt(self):
#        """
#        load and dump EWKT
#        """
#        point = "SRID=900913;Point (0 0)"
#        geom = Geometry.from_ewkt(point)
#        self.assertEquals(geom.srid, 900913)
#        ewkt = geom.ewkt
#        self.assertEquals(ewkt.upper(), point.upper())

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
