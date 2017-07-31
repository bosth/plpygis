"""
Test Geometry 
"""

import unittest

from plpygis import Geometry
from shapely.geometry import Point
from shapely import geometry

class GeometryTestCase(unittest.TestCase):
    def test_missing_ewkb(self):
        """
        plpygis.Geometry.__init__: missing EWKB
        """
        self.assertRaises(TypeError, Geometry, None, None)

    def test_malformed_ewkb(self):
        """
        plpygis.Geometry.__init__: malformed EWKB
        """
        self.assertRaises(Exception, Geometry, "0101", None)

    def test_malformed_ewkb(self):
        """
        plpygis.Geometry.__init__: malformed EWKB
        """
        self.assertRaises(Exception, Geometry, "0101", None)
    
    def test_read_wkb_point(self):
        """
        plpygis.Geometry.__init__: read WKB Point
        """
        wkb = "010100000000000000000000000000000000000000"
        geom = Geometry(wkb)
        self.assertEquals(geom.type, "Point")
        self.assertIsNone(geom.srid)
        self.assertEquals(geom.dimz, False)
        self.assertEquals(geom.dimm, False)
        postgis_type = "geometry(Point)"
        self.assertEquals(geom.postgis_type, postgis_type)
        self.assertEquals(geom.__repr__(), "<Geometry: '{}'>".format(postgis_type))
        self.assertEquals(geom.__str__(), wkb)
  
    def test_read_ewkb_point(self):
        """
        plpygis.Geometry.__init__: read EWKB Point,4326
        """
        wkb = "0101000020E610000000000000000000000000000000000000"
        geom = Geometry(wkb)
        self.assertEquals(geom.type, "Point")
        self.assertEquals(geom.srid, 4326)
        self.assertEquals(geom.dimz, False)
        self.assertEquals(geom.dimm, False)
        postgis_type = "geometry(Point,4326)"
        self.assertEquals(geom.postgis_type, postgis_type)
        self.assertEquals(geom.__repr__(), "<Geometry: '{}'>".format(postgis_type))
        self.assertEquals(geom.__str__(), wkb)
  
    def test_read_ewkb_pointz(self):
        """
        plpygis.Geometry.__init__: read EWKB PointZ,4326
        """
        wkb = "01010000A0E6100000000000000000000000000000000000000000000000000000"
        geom = Geometry(wkb)
        self.assertEquals(geom.type, "Point")
        self.assertEquals(geom.srid, 4326)
        self.assertEquals(geom.dimz, True)
        self.assertEquals(geom.dimm, False)
        postgis_type = "geometry(PointZ,4326)"
        self.assertEquals(geom.postgis_type, postgis_type)
        self.assertEquals(geom.__repr__(), "<Geometry: '{}'>".format(postgis_type))
        self.assertEquals(geom.__str__(), wkb)
  
    def test_read_ewkb_pointm(self):
        """
        plpygis.Geometry.__init__: read EWKB PointM,4326
        """
        wkb = "0101000060E6100000000000000000000000000000000000000000000000000000"
        geom = Geometry(wkb)
        self.assertEquals(geom.type, "Point")
        self.assertEquals(geom.srid, 4326)
        self.assertEquals(geom.dimz, False)
        self.assertEquals(geom.dimm, True)
        postgis_type = "geometry(PointM,4326)"
        self.assertEquals(geom.postgis_type, postgis_type)
        self.assertEquals(geom.__repr__(), "<Geometry: '{}'>".format(postgis_type))
        self.assertEquals(geom.__str__(), wkb)
  
    def test_read_ewkb_pointzm(self):
        """
        plpygis.Geometry.__init__: read EWKB PointZM,4326
        """
        wkb = "01010000E0E61000000000000000000000000000000000000000000000000000000000000000000000"
        geom = Geometry(wkb)
        self.assertEquals(geom.type, "Point")
        self.assertEquals(geom.srid, 4326)
        self.assertEquals(geom.dimz, True)
        self.assertEquals(geom.dimm, True)
        postgis_type = "geometry(PointZM,4326)"
        self.assertEquals(geom.postgis_type, postgis_type)
        self.assertEquals(geom.__repr__(), "<Geometry: '{}'>".format(postgis_type))
        self.assertEquals(geom.__str__(), wkb)

    def test_translate_shapely(self):
        """
        plpygis.Geometry.translate_shapely: load and dump Shapely
        """
        point = Point(12623630.256, 5906238.1135)
        geom = Geometry.from_shapely(point, 900913)
        self.assertEquals(geom.srid, 900913)
        shape = geom.shapely
        self.assertTrue(shape.equals(point))

    def test_translate_shape(self):
        """
        plpygis.Geometry.translate_shape: load and dump using __geo_interface__
        """
        point = Point(-8343269.14719, 5534753.54055)
        geom = Geometry.shape(point, 900913)
        self.assertEquals(geom.srid, 900913)
        shape = geom.shapely
        self.assertTrue(shape.equals(point))

    def test_translate_wkt(self):
        """
        plpygis.geometry.translate_wkt: load and dump WKT
        """
        point = "Point (59410.57968 7208125.2)"
        geom = Geometry.from_wkt(point, 3857)
        self.assertEquals(geom.srid, 3857)
        wkt = geom.wkt
        self.assertEquals(wkt.upper(), point.upper())

    def test_translate_ewkt(self):
        """
        plpygis.geometry.translate_ewkt: load and dump EWKT
        """
        point = "SRID=900913;Point (0 0)"
        geom = Geometry.from_ewkt(point)
        self.assertEquals(geom.srid, 900913)
        ewkt = geom.ewkt
        self.assertEquals(ewkt.upper(), point.upper())

    def test_translate_geojson(self):
        """
        plpygis.geometry.translate_geojson: load and dump GeoJSON
        """
        point = {'type': 'Point', 'coordinates': (0.0, 0.0)}
        geom = Geometry.from_geojson(point)
        self.assertEquals(geom.srid, 4326)
        geojson = geom.geojson
        self.assertEquals(geojson, point)

    def test_geo_interface(self):
        """
        plpygis.geometry.geo_interface: access using __geo_interface__
        """
        point = {'type': 'Point', 'coordinates': (0.0, 0.0)}
        geom = Geometry.from_geojson(point)
        shape = geometry.shape(geom)
        self.assertEquals(shape.type, "Point")

    def test_srid_mismatch(self):
        """
        plpygis.geometry.srid_mismatch: detect srid mismatch
        """
        point = Point(0, 0)
        geom = Geometry.from_shapely(point, 4326)
        geom._wkb = "010100002031BF0D0000000000000000000000000000000000"
        self.assertRaises(ValueError, geom._to_shapely)

    def test_strip_srid(self):
        """
        plpygis.geometry.strip_srid: strip SRID
        """
        geom1 = Geometry("010100000000000000000000000000000000000000")
        geom2 = Geometry("0101000020E610000000000000000000000000000000000000")
        self.assertIsNone(geom1.srid)
        self.assertEquals(geom2.srid, 4326)
        geom2.strip_srid()
        self.assertIsNone(geom2.srid)
        self.assertEquals(geom1.wkb, geom2.wkb)
        geom2.strip_srid()
        self.assertIsNone(geom2.srid)
        self.assertEquals(geom1.wkb, geom2.wkb)
