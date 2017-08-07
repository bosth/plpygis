from .hex import HexReader, HexWriter

try:
    import shapely.wkb
    from shapely.geos import lgeos, WKBWriter
    SHAPELY = True
except ImportError:
    SHAPELY = False

class Geometry(object):
    """
    A representation of a PostGIS geometry.
    
    PostGIS geometries are either an OpenGIS Consortium Simple Features for SQL
    specification type or a PostGIS extended type. The object's canonical form
    is stored in WKB or EWKB format along with an SRID and flags indicating
    whether the coordinates are 3DZ, 3DM or 4D.

    ``Geometry`` objects can be created in a number of ways. In all cases, a
    subclass for the particular geometry type will be instantiated.

    From an (E)WKB::

        >>> Geometry("0101000080000000000000000000000000000000000000000000000000")
        <Point: 'geometry(PointZ)'>

    The response above indicates an instance of the ``Point`` class has been
    created and that it represents a PostGIS ``geometry(PointZ)`` type.

    From a GeoJSON::

        >>> Geometry.from_geojson({'type': 'Point', 'coordinates': (0.0, 0.0)})
        <Point: 'geometry(Point,4326)'>

    From a Shapely object::

        >>> from shapely.geometry import Point
        >>> Geometry.from_shapely(Point((0, 0)), 3857)
        <Point: 'geometry(Point,3857)'>

    From any object supporting ``__geo_interface__``::

        >>> from shapefile import Reader
        >>> feature = Reader("lines.shp").shape(0)
        >>> Geometry.shape(feature)
        <LineString: 'geometry(LineString)'>

    A ``Geometry`` can be read as long as it is one of the following
    types: ``Point``, ``LineString``, ``Polygon``, ``MultiPoint``, ``MultiLineString``,
    ``MultiPolygon`` or ``GeometryCollection``. The M dimension will be preserved.
    """
    def __new__(cls, wkb, srid=None, dimz=False, dimm=False):
        if cls == Geometry:
            newcls, dimz, dimm, srid, reader = Geometry._from_wkb(wkb)
            geom = super(Geometry, cls).__new__(newcls)
            geom._wkb = wkb
            geom._reader = reader
            geom._srid = srid
            geom._dimz = dimz
            geom._dimm = dimm
        else:
            geom = super(Geometry, cls).__new__(cls)
            geom._wkb = None
        return geom

    @staticmethod
    def from_geojson(geojson, srid=4326):
        """
        Create a Geometry from a GeoJSON. The SRID can be overridden from the
        expected 4326.
        """
        type_ = geojson["type"].lower()
        if type_ == "geometrycollection":
            geometries = []
            for geometry in geojson["geometries"]:
                geometries.append(Geometry.from_geojson(geometry, srid=None))
            return GeometryCollection(geometries, srid)
        elif type_ == "point":
            return Point(geojson["coordinates"], srid=srid)
        elif type_ == "linestring":
            return LineString(geojson["coordinates"], srid=srid)
        elif type_ == "polygon":
            return Polygon(geojson["coordinates"], srid=srid)
        elif type_ == "multipoint":
            geometries = _MultiGeometry._multi_from_geojson(geojson, Point)
            return MultiPoint(geometries, srid=srid)
        elif type_ == "multilinestring":
            geometries = _MultiGeometry._multi_from_geojson(geojson, LineString)
            return MultiLineString(geometries, srid=srid)
        elif type_ == "multipolygon":
            geometries = _MultiGeometry._multi_from_geojson(geojson, Polygon)
            return MultiPolygon(geometries, srid=srid)

    @staticmethod
    def from_shapely(sgeom, srid=None):
        """
        Create a Geometry from a Shapely geometry and the specified SRID.

        The Shapely geometry will not be modified.
        """
        if SHAPELY:
            WKBWriter.defaults["include_srid"] = True
            if srid:
                lgeos.GEOSSetSRID(sgeom._geom, srid)
            return Geometry(sgeom.wkb_hex)
        else:
            raise Exception("Shapely not available.")

    @staticmethod    
    def shape(shape, srid=None):
        """
        Create a Geometry using ``__geo_interface__`` and the specified SRID.
        """
        return Geometry.from_geojson(shape.__geo_interface__, srid)

    @property
    def type(self):
        """
        The geometry type.
        """
        return self.__class__.__name__
    
    @property
    def srid(self):
        """
        The geometry SRID.
        """
        return self._srid
    
    @srid.setter
    def srid(self, value):
        self._srid = value
        self._wkb = None

    @property
    def geojson(self):
        """
        Get the geometry as a GeoJSON dict. There is no check that the
        GeoJSON is using an SRID of 4326.
        """
        return self._to_geojson(dimz=self._dimz)

    @property
    def wkb(self):
        """
        Get the geometry as an (E)WKB.
        """
        return self._to_wkb(use_srid=True, dimz=self._dimz, dimm=self._dimm)

    @property
    def shapely(self):
        """
        Get the geometry as a Shapely geometry. If the geometry has an SRID,
        the Shapely object will be created with it set.
        """
        return self._to_shapely()

    @property
    def postgis_type(self):
        """
        Get the type of the geometry in PostGIS format, including additional
        dimensions and SRID if they exist.
        """
        dimz = "Z" if self._dimz else ""
        dimm = "M" if self._dimm else ""
        if self._srid:
            return "geometry({}{}{},{})".format(self.type, dimz, dimm, self._srid)
        else:
            return "geometry({}{}{})".format(self.type, dimz, dimm)

    @staticmethod
    def _from_wkb(wkb):
        if not wkb:
            raise TypeError("No EWKB provided")
        if wkb.startswith("00"):
            reader = Reader(wkb, ">")  # big-endian reader
        elif wkb.startswith("01"):
            reader = HexReader(wkb, "<")  # little-endian reader
        else:
            raise Exception("First byte in WKB must be 0 or 1.")
        return Geometry._get_wkb_type(reader) + (reader,)

    def _to_wkb(self, use_srid, dimz, dimm):
        if self._wkb is not None:
            return self._wkb
        writer = HexWriter("<")
        self._write_wkb_header(writer, use_srid, dimz, dimm)
        self._write_wkb(writer, dimz, dimm)
        return writer.data

    def _to_shapely(self):
        if SHAPELY:
            sgeom = shapely.wkb.loads(self.wkb, hex=True)
            srid = lgeos.GEOSGetSRID(sgeom._geom)
            if srid == 0:
                srid = None
            if (srid or self._srid) and srid != self._srid:
                raise ValueError("SRID mismatch: {} {}".format(srid, self._srid))
            return sgeom
        else:
            raise Exception("Shapely not available.")

    def _to_geojson(self, dimz):
        coordinates = self._to_geojson_coordinates(dimz)
        geojson = {
                "type" : self.type,
                "coordinates": coordinates
        }
        return geojson

    def __repr__(self):
        return "<{}: '{}'>".format(self.type, self.postgis_type)

    def __str__(self):
        return self.wkb

    @property
    def __geo_interface__(self):
        return self.geojson

    def _set_dimensionality(self, geometries):
        self._dimz = None
        self._dimm = None
        for geometry in geometries:
            if self._dimz is None:
                self._dimz = geometry.dimz
            elif self._dimz != geometry.dimz:
                raise Exception("Mixed dimensionality in MultiGeometry")
            if self._dimm is None:
                self._dimm = geometry.dimm
            elif self._dimm != geometry.dimm:
                raise Exception("Mixed dimensionality in MultiGeometry")

    @staticmethod
    def _get_wkb_type(reader):
        lwgeomtype, dimz, dimm, srid = Geometry._read_wkb_header(reader)
        if lwgeomtype == 1:
            cls = Point
        elif lwgeomtype == 2:
            cls = LineString
        elif lwgeomtype == 3:
            cls = Polygon
        elif lwgeomtype == 4:
            cls = MultiPoint
        elif lwgeomtype == 5:
            cls = MultiLineString
        elif lwgeomtype == 6:
            cls = MultiPolygon
        elif lwgeomtype == 7:
            cls = GeometryCollection
        else:
            raise Exception("Unsupported type: {}".format(lwgeomtype))
        return cls, dimz, dimm, srid

    @staticmethod
    def _read_wkb_header(reader):
        WKBZFLAG    = 0x80000000
        WKBMFLAG    = 0x40000000
        WKBSRIDFLAG = 0x20000000
        WKBTYPE     = 0x1fffffff
        
        reader.get_char()
        header = reader.get_int()
        lwgeomtype = header & WKBTYPE
        dimz = bool(header & WKBZFLAG)
        dimm = bool(header & WKBMFLAG)
        if header & WKBSRIDFLAG:
            srid = reader.get_int()
        else:
            srid = None
        return lwgeomtype, dimz, dimm, srid

    def _write_wkb_header(self, writer, use_srid, dimz, dimm):
        WKBZFLAG    = 0x80000000
        WKBMFLAG    = 0x40000000
        WKBSRIDFLAG = 0x20000000

        writer.add_order()
        header = (self._LWGEOMTYPE |
                  (WKBZFLAG if dimz else 0) |
                  (WKBMFLAG if dimm else 0) | 
                  (WKBSRIDFLAG if self._srid else 0))
        writer.add_int(header)
        if use_srid and self._srid:
            writer.add_int(self._srid)
        return writer

class _MultiGeometry(Geometry):
    @property
    def dimz(self):
        """
        Whether the geometry has a Z dimension.

        :getter: ``True`` if the geometry has a Z dimension.
        :setter: Add or remove the Z dimension from this and all geometries in the collection.
        :rtype: bool
        """
        return self._dimz

    @dimz.setter
    def dimz(self, value):
        if self._dimz == value:
            return
        for geometry in self.geometries:
            geometry.dimz = value
        self._dimz = value
        self._wkb = None

    @property
    def dimm(self):
        """
        Whether the geometry has an M dimension.

        :getter: ``True`` if the geometry has an M dimension.
        :setter: Add or remove the M dimension from this and all geometries in the collection.
        :rtype: bool
       """
        return self._dimm

    @dimm.setter
    def dimm(self, value):
        if self._dimm == value:
            return
        for geometry in self.geometries:
            geometry.dimm = value
        self._dimm = value
        self._wkb = None

    @staticmethod
    def _multi_from_geojson(geojson, cls):
        geometries = []
        for coordinates in geojson["coordinates"]:
            geometry = cls(coordinates, srid=None)
            geometries.append(geometry)
        return geometries

    def _load_data(self):
        self._geometries = GeometryCollection._read_wkb(self._reader, self._dimz, self._dimm)
        self._wkb = None

    def _set_multi_metadata(self):
        self._dimz = None
        self._dimm = None
        for geometry in self.geometries:
            if self._dimz is None:
                self._dimz = geometry.dimz
            elif self._dimz != geometry.dimz:
                raise Exception("Mixed dimensionality in MultiGeometry")
            if self._dimm is None:
                self._dimm = geometry.dimm
            elif self._dimm != geometry.dimm:
                raise Exception("Mixed dimensionality in MultiGeometry")
            if self._srid is None:
                if geometry.srid is not None:
                    self._srid = geometry.srid
            elif self._srid != geometry.srid and geometry.srid is not None:
                raise Exception("Mixed SRIDs in MultiGeometry")

    def _to_geojson_coordinates(self, dimz):
        coordinates = [g._to_geojson_coordinates(dimz=dimz) for g in self.geometries]
        return coordinates
            
    @classmethod
    def _from_wkb(cls, reader):
        lwgeomtype, dimz, dimm, srid = Geometry._read_wkb_header(reader)
        points = MultiPoint._read_wkb(reader, dimz, dimm)
        return cls(points, dimz=dimz, dimm=dimm)

    @staticmethod
    def _read_wkb(reader, dimz, dimm):
        geometries = []
        for _ in range(reader.get_int()):
            cls, dimz, dimm, srid = Geometry._get_wkb_type(reader)
            coordinates = cls._read_wkb(reader, dimz, dimm)
            geometry = cls(coordinates, srid=srid, dimz=dimz, dimm=dimm)
            geometries.append(geometry)
        return geometries

    def _write_wkb(self, writer, dimz, dimm):
        writer.add_int(len(self.geometries))
        for geometry in self.geometries:
            geometry._write_wkb_header(writer, False, dimz, dimm)
            geometry._write_wkb(writer, dimz, dimm)

class Point(Geometry):
    """
    A representation of a PostGIS Point.
    
    ``Point`` objects can be created directly.

        >>> Point((0, -52, 5), dimm=True, srid=4326)
        <Point: 'geometry(PointM,4326)'>

    The ``dimz`` and ``dimm`` parameters will indicate how to interpret the
    coordinates that have been passed as the first argument. By default, the
    third parameter will be interpreted as representing the Z dimension.
    """

    _LWGEOMTYPE = 1

    def __init__(self, coordinates=None, srid=None, dimz=False, dimm=False):
        if self._wkb:
            self._x = None
            self._y = None
            self._z = None
            self._m = None
        else:
            self._srid = srid
            coordinates = list(coordinates)
            self._x = coordinates[0]
            self._y = coordinates[1]
            num = len(coordinates)
            if num > 4:
                raise Exception("Maximum dimensionality supported for coordinates is 4: {}".format(coordinates))
            elif num == 2: # fill in Z and M if we are supposed to have them, else None
                if dimz and dimm:
                    coordinates.append(0)
                    coordinates.append(0)
                elif dimz:
                    coordinates.append(0)
                    coordinates.append(None)
                elif dimm:
                    coordinates.append(None)
                    coordinates.append(0)
                else:
                    coordinates.append(None)
                    coordinates.append(None)
            elif num == 3: # use the 3rd coordinate for Z or M as directed or as Z
                if dimz and dimm:
                    if coordinates[2] is None:
                        coordinates[2] = 0
                    coordinates.append(0)
                elif dimz:
                    if coordinates[2] is None:
                        coordinates[2] = 0
                    coordinates.append(None)
                elif dimm:
                    if coordinates[2] is None:
                        coordinates.append(0)
                    else:
                        coordinates.append(coordinates[2])
                        coordinates[2] = None
                else:
                    if coordinates[2] is not None:
                        dimz = True
                    coordinates.append(None)
            else: # use both the 3rd and 4th coordinates, ensure not None
                if dimz and dimm:
                    if coordinates[2] is None:
                        coordinates[2] = 0
                    if coordinates[3] is None:
                        coordinates[3] = 0
                elif dimz:
                    if coordinates[2] is None:
                        coordinates[2] = 0
                    if coordinates[3] is not None:
                        dimm = True
                elif dimm:
                    if coordinates[3] is None:
                        coordinates[3] = 0
                    if coordinates[2] is not None:
                        dimz = True
                else:
                    if coordinates[2] is not None:
                        dimz = True
                    if coordinates[3] is not None:
                        dimm = True

            self._dimz = dimz
            self._dimm = dimm
            self._z = coordinates[2]
            self._m = coordinates[3]
        
    @property
    def x(self):
        """
        X coordinate.
        """
        if self._x is None:
            self._load_data()
        return self._x

    @x.setter
    def x(self, value):
        if self._x is None:
            self._load_data()
        self._x = value
        
    @property
    def y(self):
        """
        M coordinate.
        """
        if self._y is None:
            self._load_data()
        return self._y

    @y.setter
    def y(self, value):
        if self._y is None:
            self._load_data()
        self._y = value
    
    @property
    def z(self):
        """
        Z coordinate.
        """
        if not self._dimz:
            return None
        if self._z is None:
            self._load_data()
        return self._z

    @z.setter
    def z(self, value):
        if self._dimz and self._z is None:
            self._load_data()
        self._z = value
        if value is None:
            self._dimz = False
        else:
            self._dimz = True
    
    @property
    def m(self):
        """
        M coordinate.
        """
        if not self._dimm:
            return None
        if self._m is None:
            self._load_data()
        return self._m

    @m.setter
    def m(self, value):
        if self._dimm and self._m is None:
            self._load_data()
        self._m = value
        if value is None:
            self._dimm = False
        else:
            self._dimm = True

    @property
    def dimz(self):
        """
        Whether the geometry has a Z dimension.

        :getter: ``True`` if the geometry has a Z dimension.
        :setter: Add or remove the Z dimension.
        :rtype: bool
        """
        return self._dimz

    @dimz.setter
    def dimz(self, value):
        if self._dimz == value:
            return None
        if value and self.z is None:
            self.z = 0
        elif value is None:
            self.z = None
        self._dimz = value
        self._wkb = None

    @property
    def dimm(self):
        """
        Whether the geometry has an M dimension.

        :getter: ``True`` if the geometry has an M dimension.
        :setter: Add or remove the M dimension.
        :rtype: bool
        """
        return self._dimm

    @dimm.setter
    def dimm(self, value):
        if self._dimm == value:
            return None
        if value and self.m is None:
            self.m = 0
        elif value is None:
            self.m = None
        self._dimm = value
        self._wkb = None

    def _to_geojson_coordinates(self, dimz):
        coordinates = [self.x, self.y]
        if dimz:
            coordinates.append(self.z)
        return coordinates

    def _load_data(self):
        self._x, self._y, self._z, self._m = Point._read_wkb(self._reader, self._dimz, self._dimm)
        self._wkb = None

    @classmethod
    def _from_wkb(cls, reader):
        lwgeomtype, dimz, dimm, srid = Geometry._read_wkb_header(reader)
        x, y, z, m = Point._read_wkb(reader, dimz, dimm)
        return cls((x, y, z, m), dimz=dimz, dimm=dimm)

    @staticmethod
    def _read_wkb(reader, dimz, dimm):
        x = reader.get_double()
        y = reader.get_double()
        if dimz and dimm:
            z = reader.get_double()
            m = reader.get_double()
        elif dimz:
            z = reader.get_double()
            m = None
        elif dimm:
            z = None
            m = reader.get_double()
        else:
            z = None
            m = None
        return x, y, z, m

    def _write_wkb(self, writer, dimz, dimm):
        writer.add_double(self.x)
        writer.add_double(self.y)
        if dimz and dimm:
            writer.add_double(self.z)
            writer.add_double(self.m)
        elif dimz:
            writer.add_double(self.z)
        elif dimm:
            writer.add_double(self.m)

class LineString(Geometry):
    """
    A representation of a PostGIS Line.
    
    ``LineString`` objects can be created directly.

        >>> LineString([(0, 0, 0, 0), (1, 1, 0, 0), (2, 2, 0, 0)])
        <LineString: 'geometry(LineStringZM)'>

    The ``dimz`` and ``dimm`` parameters will indicate how to interpret the
    coordinates that have been passed as the first argument. By default, the
    third parameter will be interpreted as representing the Z dimension.
    """

    _LWGEOMTYPE = 2

    def __init__(self, vertices=None, srid=None, dimz=False, dimm=False):
        if self._wkb:
            self._vertices = None
        else:
            self._srid = srid
            self._dimz = dimz
            self._dimm = dimm
            self._vertices = LineString._from_coordinates(vertices, dimz=dimz, dimm=dimm)
            self._set_dimensionality(self._vertices)
        
    @property
    def vertices(self):
        """
        List of vertices that comprise the line.
        """
        if self._vertices is None:
            self._load_data()
        return self._vertices

    @property
    def dimz(self):
        """
        Whether the geometry has a Z dimension.

        :getter: ``True`` if the geometry has a Z dimension.
        :setter: Add or remove the Z dimension from this and all vertices in the line.
        :rtype: bool
        """
        return self._dimz

    @dimz.setter
    def dimz(self, value):
        if self._dimz == value:
            return
        for vertex in self.vertices:
            vertex.dimz = value
        self._dimz = value
        self._wkb = None

    @property
    def dimm(self):
        """
        Whether the geometry has a M dimension.

        :getter: ``True`` if the geometry has a M dimension.
        :setter: Add or remove the M dimension from this and all vertices in the line.
        :rtype: bool
        """
        return self._dimm

    @dimm.setter
    def dimm(self, value):
        if self._dimm == value:
            return
        for vertex in self.vertices:
            vertex.dimm = value
        self._dimm = value
        self._wkb = None

    def _to_geojson_coordinates(self, dimz):
        coordinates = [v._to_geojson_coordinates(dimz=dimz) for v in self.vertices]
        return coordinates

    @staticmethod
    def _from_coordinates(vertices, dimz, dimm):
        return [Point(vertex, dimz=dimz, dimm=dimm) for vertex in vertices]
        
    def _load_data(self):
        vertices = LineString._read_wkb(self._reader, self._dimz, self._dimm)
        self._vertices = LineString._from_coordinates(vertices, self._dimz, self._dimm)
        self._wkb = None
           
    @classmethod
    def _from_wkb(cls, reader):
        lwgeomtype, dimz, dimm, srid = Geometry._read_wkb_header(reader)
        vertices = LineString._read_wkb(reader, dimz, dimm)
        return cls(vertices, dimz=dimz, dimm=dimm)

    @staticmethod
    def _read_wkb(reader, dimz, dimm):
        vertices = []
        for _ in range(reader.get_int()):
            coordinates = Point._read_wkb(reader, dimz, dimm)
            vertices.append(coordinates)
        return vertices

    def _write_wkb(self, writer, dimz, dimm):
        writer.add_int(len(self.vertices))
        for vertex in self._vertices:
            vertex._write_wkb(writer, dimz, dimm)

class Polygon(Geometry):
    """
    A representation of a PostGIS Polygon.
    
    ``Polygon`` objects can be created directly.

        >>> Polygon([[(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0), (0, 0, 0)]])
        <Polygon: 'geometry(PolygonZ)'>

    The first polygon in the list of linear rings is the exterior ring, while
    any subsequent rings are interior boundaries.

    The ``dimz`` and ``dimm`` parameters will indicate how to interpret the
    coordinates that have been passed as the first argument. By default, the
    third parameter will be interpreted as representing the Z dimension.
    """

    _LWGEOMTYPE = 3

    def __init__(self, rings=None, srid=None, dimz=False, dimm=False):
        if self._wkb:
            self._rings = None
        else:
            self._srid = srid
            self._dimz = dimz
            self._dimm = dimm
            self._rings = Polygon._from_coordinates(rings, dimz, dimm)
            self._set_dimensionality(self._rings)
        
    @property
    def rings(self):
        """
        List of linearrings that comprise the polygon.
        """
        if self._rings is None:
            self._load_data()
        return self._rings

    @property
    def exterior(self):
        """
        The exterior ring of the polygon.
        """
        return self._rings[0]

    @property
    def interior(self):
        """
        A list of interior rings of the polygon.
        """
        return self._rings[1:]

    @property
    def dimz(self):
        """
        Whether the geometry has a Z dimension.

        :getter: ``True`` if the geometry has a Z dimension.
        :setter: Add or remove the Z dimension from this and all linear rings in the polygon.
        :rtype: bool
        """
        return self._dimz

    @dimz.setter
    def dimz(self, value):
        if self._dimz == value:
            return
        for ring in self.rings:
            ring.dimz = value
        self._dimz = value
        self._wkb = None

    @property
    def dimm(self):
        """
        Whether the geometry has a M dimension.

        :getter: ``True`` if the geometry has a M dimension.
        :setter: Add or remove the M dimension from this and all linear rings in the polygon.
        :rtype: bool
        """
        return self._dimm

    @dimm.setter
    def dimm(self, value):
        if self._dimm == value:
            return
        for ring in self.rings:
            ring.dimm = value
        self._dimm = value
        self._wkb = None

    def _to_geojson_coordinates(self, dimz):
        coordinates = [r._to_geojson_coordinates(dimz=dimz) for r in self.rings]
        return coordinates
        
    @staticmethod
    def _from_coordinates(rings, dimz, dimm):
        return [LineString(vertices, dimz, dimm) for vertices in rings]
            
    def _load_data(self):
        rings = Polygon._read_wkb(self._reader, self._dimz, self._dimm)
        self._rings = Polygon._from_coordinates(rings, self._dimz, self._dimm)
        self._wkb = None

    @classmethod
    def _from_wkb(cls, reader):
        lwgeomtype, dimz, dimm, srid = Geometry._read_wkb_header(reader)
        rings = Polygon._read_wkb(reader, dimz, dimm)
        return cls(rings, dimz=dimz, dimm=dimm)

    @staticmethod
    def _read_wkb(reader, dimz, dimm):
        rings = []
        for _ in range(reader.get_int()):
            vertices = LineString._read_wkb(reader, dimz, dimm)
            rings.append(vertices)
        return rings
   
    def _write_wkb(self, writer, dimz, dimm):
        writer.add_int(len(self.rings))
        for ring in self.rings:
            ring._write_wkb(writer, dimz, dimm)

class MultiPoint(_MultiGeometry):
    """
    A representation of a PostGIS MultiPoint.
    
    ``MultiPoint`` objects can be created directly from a list of ``Point``
    objects.

        >>> p1 = Point((0, 0, 0))
        >>> p2 = Point((1, 1, 0))
        >>> MultiPoint([p1, p2])
        <MultiPoint: 'geometry(MultiPointZ)'>

    The dimensionality of all geometries in the collection must be identical.
    """

    _LWGEOMTYPE = 4

    def __init__(self, points=None, srid=None):
        if self._wkb:
            self._points = None
        else:
            self._points = points
            self._srid = srid
            self._set_multi_metadata()
        
    @property
    def points(self):
        """
        List of all component points.
        """
        if self._points is None:
            self._load_data()
        return self._points

    @property
    def geometries(self):
        """
        List of all component points.
        """
        return self.points

    def _load_data(self):
        self._points = MultiPoint._read_wkb(self._reader, self._dimz, self._dimm)
        self._wkb = None

class MultiLineString(_MultiGeometry):
    """
    A representation of a PostGIS MultiLineString

    ``MultiLineString`` objects can be created directly from a list of
    ``LineString`` objects.

        >>> l1 = LineString([(1, 1, 0), (2, 2, 0)], dimm=True)
        >>> l2 = LineString([(0, 0, 0), (0, 1, 0)], dimm=True)
        >>> MultiLineString([l1, l2])
        <MultiLineString: 'geometry(MultiLineStringM)'>

    The dimensionality of all geometries in the collection must be identical.
    """

    _LWGEOMTYPE = 5

    def __init__(self, linestrings=None, srid=None):
        if self._wkb:
            self._linestrings = None
        else:
            self._linestrings = linestrings 
            self._srid = srid
            self._set_multi_metadata()
        
    @property
    def linestrings(self):
        """
        List of all component lines.
        """
        if self._linestrings is None:
            self._load_data()
        return self._linestrings

    @property
    def geometries(self):
        """
        List of all component lines.
        """
        return self.linestrings

    def _load_data(self):
        self._linestrings = MultiLineString._read_wkb(self._reader, self._dimz, self._dimm)
        self._wkb = None
            
class MultiPolygon(_MultiGeometry):
    """
    A representation of a PostGIS MultiPolygon.
    
    ``MultiPolygon`` objects can be created directly from a list of ``Polygon``
    objects.

        >>> p1 = Polygon([[(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)]], srid=4326)
        >>> p2 = Polygon([[(2, 2), (3, 2), (3, 3), (2, 3), (2, 2)]], srid=4326)
        >>> MultiPolygon([p1, p2])
        <MultiPolygon: 'geometry(MultiPolygon,4326)'>

    The dimensionality of all geometries in the collection must be identical.
    """

    _LWGEOMTYPE = 6

    def __init__(self, polygons=None, srid=None, dimz=False, dimm=False):
        if self._wkb:
            self._polygons = None
        else:
            self._srid = srid
            self._dimz = dimz
            self._dimm = dimm
            self._polygons = polygons 
            self._set_multi_metadata()

    @property
    def polygons(self):
        """
        List of all component polygons.
        """
        if self._polygons is None:
            self._load_data()
        return self._polygons

    @property
    def geometries(self):
        """
        List of all component polygons.
        """
        return self.polygons
            
    def _load_data(self):
        self._polygons = MultiPolygon._read_wkb(self._reader, self._dimz, self._dimm)
        self._wkb = None

class GeometryCollection(_MultiGeometry):
    """
    A representation of a PostGIS GeometryCollection.
    
    ``GeometryCollection`` objects can be created directly from a list of
    geometries, including other collections.

        >>> p = Point((0, 0, 0))
        >>> l = LineString([(1, 1, 0), (2, 2, 0)])
        >>> GeometryCollection([p, l])
        <GeometryCollection: 'geometry(GeometryCollectionZ)'>

    The dimensionality of all geometries in the collection must be identical.
    """

    _LWGEOMTYPE = 7

    def __init__(self, geometries=None, srid=None, dimz=False, dimm=False):
        if self._wkb:
            self._geometries = None
        else:
            self._geometries = geometries 
            self._srid = srid
            self._set_multi_metadata()
        
    @property
    def geometries(self):
        """
        List of all component geometries.
        """
        if self._geometries is None:
            self._load_data()
        return self._geometries

    def _to_geojson(self, dimz):
        geometries = [g._to_geojson(dimz=dimz) for g in self.geometries]
        geojson = {
                "type" : self.__class__.__name__,
                "geometries": geometries
        }
        return geojson

    @classmethod
    def _from_wkb(cls, reader):
        lwgeomtype, dimz, dimm, srid = Geometry._read_wkb_header(reader)
        geometries = _MultiGeometry._read_wkb(reader, dimz, dimm)
        return cls(geometries, dimz=dimz, dimm=dimm)
