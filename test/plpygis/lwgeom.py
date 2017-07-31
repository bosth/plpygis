"""
Test Geometry 
"""

import unittest
import plpygis.lwgeom

class LWGeomTestCase(unittest.TestCase):
    def test_missing_ewkb(self):
        """
        plpygis.lwgeom.read_ewkb_header: missing EWKB
        """
        self.assertRaises(Exception, plpygis.lwgeom.read_ewkb_header, None, None)
  
    def test_nonhex_ewkb(self):
        """
        plpygis.lwgeom.read_ewkb_header: non-hex EWKB
        """
        self.assertRaises(Exception, plpygis.lwgeom.read_ewkb_header, "xyz", None)
  
    def test_read_wkb_point(self):
        """
        plpygis.lwgeom.read_wkb: read WKB Point
        """
        type_, srid, dimz, dimm = plpygis.lwgeom.read_ewkb_header("010100000000000000000000000000000000000000")
        self.assertEquals(type_, 1)
        self.assertIsNone(srid)
        self.assertEquals(dimz, False)
        self.assertEquals(dimm, False)
  
    def test_read_ewkb_point(self):
        """
        plpygis.lwgeom.read_wkb_header: read EWKB Point,4326
        """
        type_, srid, dimz, dimm = plpygis.lwgeom.read_ewkb_header("0101000020E610000000000000000000000000000000000000")
        self.assertEquals(type_, 1)
        self.assertEquals(srid, 4326)
        self.assertEquals(dimz, False)
        self.assertEquals(dimm, False)
  
    def test_read_ewkb_pointz(self):
        """
        plpygis.lwgeom.read_wkb_header: read EWKB PointZ,4326
        """
        type_, srid, dimz, dimm = plpygis.lwgeom.read_ewkb_header("01010000A0E6100000000000000000000000000000000000000000000000000000")
        self.assertEquals(type_, 1)
        self.assertEquals(srid, 4326)
        self.assertEquals(dimz, True)
        self.assertEquals(dimm, False)
  
    def test_read_ewkb_pointm(self):
        """
        plpygis.lwgeom.read_wkb_header: read EWKB PointM,4326
        """
        type_, srid, dimz, dimm = plpygis.lwgeom.read_ewkb_header("0101000060E6100000000000000000000000000000000000000000000000000000")
        self.assertEquals(type_, 1)
        self.assertEquals(srid, 4326)
        self.assertEquals(dimz, False)
        self.assertEquals(dimm, True)
  
    def test_read_ewkb_pointzm(self):
        """
        plpygis.lwgeom.read_wkb_header: read EWKB PointZM,4326
        """
        type_, srid, dimz, dimm = plpygis.lwgeom.read_ewkb_header("01010000E0E61000000000000000000000000000000000000000000000000000000000000000000000")
        self.assertEquals(type_, 1)
        self.assertEquals(srid, 4326)
        self.assertEquals(dimz, True)
        self.assertEquals(dimm, True)
