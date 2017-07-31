from .lwgeom import read_ewkb_header, strip_ewkb_srid
import shapely.wkb
import shapely.wkt
from shapely.geometry import mapping, shape as Shape
from shapely.geos import lgeos, WKBWriter

class Geometry(object):
    """
    A representation of a PostGIS geometry.
    
    PostGIS geometries are either an OpenGIS Consortium Simple Features for SQL
    specification type or a PostGIS extended type. The object's canonical form
    is stored in WKB or EWKB format along with an SRID and flags indicating
    whether the coordinates are 3DZ, 3DM or 4D.

    ``Geometry`` objects can be created in a number of ways.

    From an (E)WKB::

        >>> geom = Geometry("0101000080000000000000000000000000000000000000000000000000")

    From an WKT::

        >>> geom = Geometry.from_wkt("POINT(0 0)")
        >>> geom = Geometry.from_wkt("POINT(0 0)", 4326)

    From an EWKT::

        >>> geom = Geometry.from_ewkt("SRID=4326;POINT(0 0)")

    From a GeoJSON::

        >>> geom = Geometry.from_geojson({'type': 'Point', 'coordinates': (0.0, 0.0)})

    From a Shapely object::

        >>> from shapely.geometry import Point
        >>> geom = Geometry.from_shapely(Point((0, 0)), 4326)

    From any object supporting ``__geo_interface``::

        >>> from shapefile import Reader
        >>> feature = Reader("lines.shp").shape(0)
        >>> geom = Geometry.shape(feature)

    A ``Geometry`` can be converted as long as it is one of the following
    types: ``Point``, ``LineString``, ``Polygon``, ``MultiPoint``, ``MultiLineString``,
    ``MultiPolygon`` or ``GeometryCollection``. Any M dimension will be lost in
    conversion.
    """
 
    __slots__ = ["_wkb", "_sgeom", "_type", "_srid", "_dimz", "_dimm"]

    _LWGEOMTYPE = {
          0 : "Unknown",
          1 : "Point",
          2 : "LineString",
          3 : "Polygon",
          4 : "MultiPoint",
          5 : "MultiLineString",
          6 : "MultiPolygon",
          7 : "GeometryCollection",
          8 : "CircularString",
          9 : "CompoundCurve",
         10 : "CurvePolygon",
         11 : "MultiCurve",
         12 : "MultiSurface",
         13 : "PolyhedralSurface",
         14 : "Triangle",
         15 : "Tin"
    }

    def __init__(self, wkb):
        """
        Create a Geometry from a hex-encoded (E)WKB.

        The (E)WKB header will be immediately parsed to extract the type, SRID
        and dimension information.
        """
        self._wkb = wkb
        self._sgeom = None
        self._type, self._srid, self._dimz, self._dimm = read_ewkb_header(self._wkb)

    @classmethod
    def shape(cls, shape, srid=4326):
        """
        Create a Geometry using ``__geo_interface__`` and the specified SRID. By
        default we assume that the geometry uses an SRID of 4326.

        :param shape: object suppporting ``__geo_interface__``
        :type shape: object
        :keyword srid: SRID
        :type srid: int or None
        :return: new geometry instance
        :rtype: plpygis.Geometry
        """
        sgeom = Shape(shape)
        sgeom = Geometry._add_shapely_srid(sgeom, srid)
        return cls(sgeom.wkb_hex)

    @classmethod
    def from_shapely(cls, sgeom, srid=None):
        """
        Create a Geometry from a Shapely geometry and the specified SRID.

        The Shapely geometry will not be modified.

        :param sgeom: geometry
        :type sgeom: shapely.geometry
        :keyword srid: SRID
        :type srid: int or None
        :return: new geometry instance
        :rtype: plpygis.Geometry
        """
        if srid:
            sgeom = Shape(sgeom)
            sgeom = Geometry._add_shapely_srid(sgeom, srid)
        return cls(sgeom.wkb_hex)

    @classmethod
    def from_geojson(cls, geojson, srid=4326):
        """
        Create a Geometry from a GeoJSON. The SRID can be overridden from the
        expected 4326.

        :param geojson: GeoJSON
        :type geojson: dict
        :keyword srid: SRID
        :type srid: int or None
        :return: new geometry instance
        :rtype: plpygis.Geometry
        """
        sgeom = Shape(geojson)
        sgeom = Geometry._add_shapely_srid(sgeom, srid)
        return cls(sgeom.wkb_hex)

    @classmethod
    def from_wkt(cls, wkt, srid=None):
        """
        Create a Geometry from a WKT and the specified SRID. EWKT will also be
        correctly handled if it is provided.

        :param wkt: WKT or EWKT
        :type wkt: str
        :keyword srid: SRID
        :type srid: int or None
        :return: new geometry instance
        :rtype: plpygis.Geometry
        """
        if wkt.startswith("SRID="):
            ewkt = wkt.split(";")
            wkt = ewkt[1]
            if srid is None:
                srid = int(ewkt[0].replace("SRID=", ""))
        sgeom = shapely.wkt.loads(wkt)
        sgeom = Geometry._add_shapely_srid(sgeom, srid)
        return cls(sgeom.wkb_hex)

    @classmethod
    def from_ewkt(cls, wkt):
        """
        Create a Geometry from an EWKT.

        :param wkt: EWKT
        :type wkt: str
        :keyword srid: SRID
        :type srid: int or None
        :return: new geometry instance
        :rtype: plpygis.Geometry
        """
        return cls.from_wkt(wkt)

    def strip_srid(self):
        """
        Remove the SRID designation from a Geometry. The coordinates will not
        be converted.
        """
        if self._srid:
            self._wkb = strip_ewkb_srid(self._wkb)
            self._srid = None
            self._sgeom = None

    @property
    def type(self):
        """
        Get the geometry type.
        
        :rtype: str
        """
        return self._LWGEOMTYPE[self._type]

    @property
    def srid(self):
        """
        Get the geometry SRID.
        
        :rtype: int
        """
        return self._srid

    @property
    def dimz(self):
        """
        ``True`` if the geometry has a Z dimension.
        
        :rtype: bool
        """
        return self._dimz

    @property
    def dimm(self):
        """
        ``True`` if the geometry has a M dimension.
        
        .. warning::
        
            The M dimension will be lost in conversion to other types.
        
        :rtype: bool
        """
        return self._dimm

    @property
    def postgis_type(self):
        """
        Get the type of the geometry in PostGIS format, including additional
        dimensions and SRID if they exist.
        
        :rtype: str
        """
        type_ = self._LWGEOMTYPE[self._type]
        dimz = "Z" if self._dimz else ""
        dimm = "M" if self._dimm else ""
        if self._srid:
            return "geometry({}{}{},{})".format(type_, dimz, dimm, self._srid)
        else:
            return "geometry({}{}{})".format(type_, dimz, dimm)

    def __repr__(self):
        return "<{}: '{}'>".format(self.__class__.__name__, self.postgis_type)

    def __str__(self):
        return self._wkb

    @property
    def __geo_interface__(self):
        return self.geojson

    def _to_shapely(self):
        if not self._sgeom:
            if self._type == 0 or self._type > 7:
                raise ValueError("Can not convert geometries of type {}".format(self.type))
            self._sgeom = shapely.wkb.loads(self._wkb, hex=True)
            srid = Geometry._get_shapely_srid(self._sgeom)
            if (srid or self._srid) and srid != self._srid:
                raise ValueError("SRID mismatch: {} {}".format(srid, self._srid))
        return self._sgeom

    @property
    def shapely(self):
        """
        Get the geometry as a Shapely geometry. The geometry will be created
        with the same SRID as the original WKB.
        
        :rtype: shapely.geometry
        """
        return self._to_shapely()
    
    @property
    def geojson(self):
        """
        Get the geometry as a GeoJSON dict. There is no check that the
        GeoJSON is using an SRID of 4326.
        
        :rtype: dict
        """
        shape = self.shapely
        geojson = mapping(shape)
        return geojson
    
    @property
    def wkt(self):
        """
        Get the geometry as a WKT.
        
        :rtype: str
        """
        return self.shapely.wkt
    
    @property
    def ewkt(self):
        """
        Get the geometry as an EWKT.

        :rtype: str
        """
        wkt = self.wkt
        if self._srid:
            return "SRID={};{}".format(self._srid, wkt)
        else:
            return wkt

    @property
    def wkb(self):
        """
        Get the geometry as an (E)WKB.

        :rtype: str
        """
        return self._wkb

    @staticmethod
    def _get_shapely_srid(sgeom):
        """
        Get the SRID of a Shapely geometry.
        """
        srid = lgeos.GEOSGetSRID(sgeom._geom)
        if srid == 0:
            return None
        else:
            return srid

    @staticmethod
    def _add_shapely_srid(sgeom, srid):
        """
        Add an SRID to a Shapely geometry, replacing any existing SRID.
        """
        if not srid:
            return sgeom
        else:
            WKBWriter.defaults["include_srid"] = True
            lgeos.GEOSSetSRID(sgeom._geom, srid)
            return sgeom
