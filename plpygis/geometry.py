import numbers
from copy import copy, deepcopy
from .exceptions import (
    DependencyError,
    WkbError,
    SridError,
    DimensionalityError,
    CoordinateError,
    GeojsonError,
    CollectionError,
    WktError
)
from .hex import HexReader, HexWriter, HexBytes
from .wkt import WktReader, WktWriter

class Geometry:
    r"""A representation of a PostGIS geometry.

    PostGIS geometries are either an OpenGIS Consortium Simple Features for SQL
    specification type or a PostGIS extended type. The object's canonical form
    is stored in WKB or EWKB format along with an SRID and flags indicating
    whether the coordinates are 3DZ, 3DM or 4D.

    ``Geometry`` objects can be created in a number of ways. In all cases, a
    subclass for the particular geometry type will be instantiated.

    From an (E)WKB::

        >>> Geometry(b'\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        <Point: 'geometry(Point)'>

    From the hexadecimal string representation of an (E)WKB::

        >>> Geometry("0101000080000000000000000000000000000000000000000000000000")
        <Point: 'geometry(PointZ)'>

    The response above indicates an instance of the ``Point`` class has been
    created and that it represents a PostGIS ``geometry(PointZ)`` type.

    From a GeoJSON::

        >>> Geometry.from_geojson({'type': 'Point', 'coordinates': (0.0, 0.0)})
        <Point: 'geometry(Point,4326)'>

    From a Shapely object::

        >>> from shapely import Point
        >>> point = Point(0, 0)
        >>> Geometry.from_shapely(point, 3857)
        <Point: 'geometry(Point,3857)'>

    From any object supporting ``__geo_interface__``::

        >>> from shapefile import Reader
        >>> feature = Reader("test/multipoint.shp").shape(0)
        >>> Geometry.shape(feature)
        <MultiPoint: 'geometry(MultiPoint)'>

    A ``Geometry`` can be read as long as it is one of the following
    types: ``Point``, ``LineString``, ``Polygon``, ``MultiPoint``, ``MultiLineString``,
    ``MultiPolygon`` or ``GeometryCollection``. The M dimension will be preserved.
    """

    _WKBTYPE = 0x1FFFFFFF
    _WKBZFLAG = 0x80000000
    _WKBMFLAG = 0x40000000
    _WKBSRIDFLAG = 0x20000000
    __slots__ = ["_wkb", "_reader", "_srid", "_dimz", "_dimm"]

    def __new__(cls, wkb, srid=None, dimz=False, dimm=False):
        if cls == Geometry:
            if not wkb:
                raise WkbError("No EWKB provided")
            wkb = HexBytes(wkb)
            newcls, dimz, dimm, srid, reader = Geometry._from_wkb(wkb)
            geom = super().__new__(newcls)
            geom._wkb = wkb
            geom._reader = reader
            geom._srid = srid
            geom._dimz = dimz
            geom._dimm = dimm
        else:
            geom = super().__new__(cls)
            geom._wkb = None
            geom._reader = None
        return geom

    def __copy__(self):
        cls = self.__class__
        return cls(self.coordinates, self.srid, self.dimz, self.dimm)

    def __deepcopy__(self, _):
        return self.__copy__()

    def __add__(self, other):
        if self.srid != other.srid:
            raise CollectionError(
                    "Can not add mixed SRID types")

        if issubclass(type(other), _MultiGeometry):
            return other + self

        if type(self) is type(other):
            if type(self) is Point:
                cls = MultiPoint
            elif type(self) is LineString:
                cls = MultiLineString
            elif type(self) is Polygon:
                cls = MultiPolygon
        else:
            cls = GeometryCollection

        return cls([self, other], srid=self.srid)

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
        if type_ == "point":
            return Point(geojson["coordinates"], srid=srid)
        if type_ == "linestring":
            return LineString(geojson["coordinates"], srid=srid)
        if type_ == "polygon":
            return Polygon(geojson["coordinates"], srid=srid)
        if type_ == "multipoint":
            geometries = _MultiGeometry._multi_from_geojson(geojson, Point)
            return MultiPoint(geometries, srid=srid)
        if type_ == "multilinestring":
            geometries = _MultiGeometry._multi_from_geojson(geojson, LineString)
            return MultiLineString(geometries, srid=srid)
        if type_ == "multipolygon":
            geometries = _MultiGeometry._multi_from_geojson(geojson, Polygon)
            return MultiPolygon(geometries, srid=srid)
        raise GeojsonError(f"Invalid GeoJSON type: {type_}")

    def _read_wkt_geom(reader):
        type_ = reader.get_type()
        dimz, dimm = reader.get_dims()

        if type_ == "POINT":
            cls = Point
        elif type_ == "LINESTRING":
            cls = LineString
        elif type_ == "POLYGON":
            cls = Polygon
        elif type_ == "MULTIPOINT":
            cls = MultiPoint
        elif type_ == "MULTILINESTRING":
            cls = MultiLineString
        elif type_ == "MULTIPOLYGON":
            cls = MultiPolygon
        elif type_ == "GEOMETRYCOLLECTION":
            cls = GeometryCollection

        return cls._read_wkt(reader)

    @staticmethod
    def from_wkt(wkt, srid=None):
        """
        Create a Geometry from a WKT or EWKT.
        """
        reader = WktReader(wkt)
        reader.get_srid()
        geom = Geometry._read_wkt_geom(reader)
        reader.close()
        if srid:
            geom.srid = srid
        return geom

    @staticmethod
    def from_shapely(sgeom, srid=None):
        """
        Create a Geometry from a Shapely geometry and the specified SRID.

        The Shapely geometry will not be modified.
        """
        try:
            import shapely
            if srid:
                sgeom = shapely.set_srid(sgeom, srid)
            wkb_hex = shapely.to_wkb(sgeom, include_srid=True, hex=True)
            return Geometry(wkb_hex)
        except ImportError:
            raise DependencyError("Shapely")

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
        self._check_cache()
        self._srid = value

    @property
    def coordinates(self):
        """
        Get the geometry's coordinates.
        """
        return self._coordinates()

    @property
    def geojson(self):
        """
        Get the geometry as a GeoJSON dict. There is no check that the
        GeoJSON is using an SRID of 4326.
        """
        return self._to_geojson()

    @property
    def wkb(self):
        """
        Get the geometry as an WKB.
        """
        return self._to_wkb(use_srid=False, dimz=self.dimz, dimm=self.dimm)

    @property
    def wkt(self):
        """
        Get the geometry as an WKT.
        """
        return self._to_wkt(use_srid=False)

    @property
    def ewkb(self):
        """
        Get the geometry as an EWKB.
        """
        return self._to_wkb(use_srid=True, dimz=self.dimz, dimm=self.dimm)

    @property
    def ewkt(self):
        """
        Get the geometry as an EWKT.
        """
        return self._to_wkt(use_srid=True)

    @property
    def shapely(self):
        """
        Get the geometry as a Shapely geometry. If the geometry has an SRID,
        the Shapely object will be created with it set.
        """
        return self._to_shapely()

    @property
    def bounds(self):
        """
        Get the minimum and maximum extents of the geometry: (minx, miny, maxx,
        maxy).
        """
        return self._bounds()

    @property
    def postgis_type(self):
        """
        Get the type of the geometry in PostGIS format, including additional
        dimensions and SRID if they exist.
        """
        dimz = "Z" if self.dimz else ""
        dimm = "M" if self.dimm else ""
        if self.srid:
            return f"geometry({self.type}{dimz}{dimm},{self.srid})"
        return f"geometry({self.type}{dimz}{dimm})"

    @staticmethod
    def _from_wkb(wkb):
        try:
            if wkb.startswith(b"\x00"):
                reader = HexReader(wkb, ">")  # big-endian reader
            elif wkb.startswith(b"\x01"):
                reader = HexReader(wkb, "<")  # little-endian reader
            else:
                raise WkbError("First byte in WKB must be 0 or 1.")
        except TypeError as e:
            raise WkbError() from e
        return Geometry._get_wkb_type(reader) + (reader,)

    def _check_cache(self):
        if self._reader is not None:
            self._load_geometry()
            self._wkb = None
            self._reader = None

    def _to_wkb(self, use_srid, dimz, dimm):
        if self._wkb is not None:
            # use cached WKB if it is an EWKB and user requested EWKB
            if use_srid and self.srid is not None:
                return self._wkb
            # use cached WKB if it is a WKB and user requested WKB
            if not use_srid and self.srid is None:
                return self._wkb
        writer = HexWriter("<")
        self._write_wkb_header(writer, use_srid, dimz, dimm)
        self._write_wkb(writer, dimz, dimm)
        return writer.data
    
    def _to_wkt(self, use_srid):
        writer = WktWriter(self, use_srid)
        writer.add(
            self._as_wkt(writer)
        )
        return writer.wkt

    def _to_shapely(self):
        try:
            import shapely
            import shapely.wkb

            sgeom = shapely.wkb.loads(self.ewkb)
            srid = shapely.get_srid(sgeom)
            if srid == 0:
                srid = None
            if (srid or self.srid) and srid != self.srid:
                raise SridError(f"SRID mismatch: {srid} {self.srid}")
            return sgeom
        except ImportError:
            raise DependencyError("Shapely")

    def _to_geojson(self):
        coordinates = self._to_geojson_coordinates()
        geojson = {"type": self.type, "coordinates": coordinates}
        return geojson

    def __repr__(self):
        return f"<{self.type}: '{self.postgis_type}'>"

    def __str__(self):
        return self.ewkb.__str__()

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
                raise DimensionalityError("Mixed dimensionality in MultiGeometry")
            if self._dimm is None:
                self._dimm = geometry.dimm
            elif self._dimm != geometry.dimm:
                raise DimensionalityError("Mixed dimensionality in MultiGeometry")

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
            raise WkbError(f"Unsupported WKB type: {lwgeomtype}")
        return cls, dimz, dimm, srid

    @staticmethod
    def _read_wkb_header(reader):
        try:
            reader.get_char()
            header = reader.get_int()
            lwgeomtype = header & Geometry._WKBTYPE
            dimz = bool(header & Geometry._WKBZFLAG)
            dimm = bool(header & Geometry._WKBMFLAG)
            if header & Geometry._WKBSRIDFLAG:
                srid = reader.get_int()
            else:
                srid = None
        except TypeError as e:
            raise WkbError() from e
        return lwgeomtype, dimz, dimm, srid

    def _write_wkb_header(self, writer, use_srid, dimz, dimm):
        if not self.srid:
            use_srid = False
        writer.add_order()
        header = (
            self._LWGEOMTYPE
            | (Geometry._WKBZFLAG if dimz else 0)
            | (Geometry._WKBMFLAG if dimm else 0)
            | (Geometry._WKBSRIDFLAG if use_srid else 0)
        )
        writer.add_int(header)
        if use_srid:
            writer.add_int(self.srid)
        return writer

    def _as_wkt(self, writer):
        coords = self._to_wkt_coordinates(writer)
        if coords is None:
            return f"{writer.type(self)} EMPTY"
        else:
            coords = writer.wrap(coords)
            return f"{writer.type(self)} {coords}"


class _MultiGeometry(Geometry):
    __slots__ = ["_geometries"]

    def __init__(self, multitype, geometries=None, srid=None):
        if self._wkb:
            self._geometries = None
        else:
            if not all(isinstance(geometry, multitype) for geometry in geometries):
                raise CollectionError(
                    f"Found non-{multitype} when creating a Multi{multitype}"
                )
            self._geometries = geometries
            self._srid = srid
            self._set_multi_metadata()

    def __copy__(self):
        cls = self.__class__
        geometries = copy(self._geometries)
        return cls(geometries, self.srid)

    def __deepcopy__(self, _):
        cls = self.__class__
        geometries = [deepcopy(geometry) for geometry in self._geometries]
        return cls(geometries, self.srid)

    def __getitem__(self, index):
        return self._geometries[index]

    def __setitem__(self, index, value):
        if not issubclass(type(value), self.MULTITYPE):
            raise CollectionError(
                    f"Can not add {type(value)} to a {type(self)}")
        self._geometries[index] = value

    def __len__(self):
        return len(self._geometries)

    def __add__(self, other):
        if self.srid != other.srid:
            raise CollectionError(
                    "Can not add mixed SRID types")

        if type(other) is type(self):
            new_geom = copy(self)
            new_geom._geometries.extend(other._geometries)
        elif type(other) is self.MULTITYPE:
            new_geom = copy(self)
            new_geom._geometries.append(other)
        else:
            new_geom = GeometryCollection(self._geometries + [other],
                                          srid=self.srid)
        return new_geom

    def __iadd__(self, other):
        if self.srid != other.srid:
            raise CollectionError(
                    "Can not add mixed SRID types")

        if type(self) is GeometryCollection:
            if issubclass(type(other), _MultiGeometry):
                self._geometries.extend(other)
            else:
                self._geometries.append(other)
        elif type(self) is type(other):
            self._geometries.extend(other.geometries)
        elif type(other) is self.MULTITYPE:
            self._geometries.append(other)
        else:
            raise CollectionError(
                    f"Can not add a {type(other)} to a {type(self)}")
        return self

    def pop(self, index=-1):
        """
        Remove a geometry from the multigeometry.
        """
        return self._geometries.pop(index)

    @property
    def geometries(self):
        """
        List of all component geometries.
        """
        self._check_cache()
        return tuple(self._geometries)

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

    def _bounds(self):
        bounds = [g.bounds for g in self.geometries]
        minx = min(b[0] for b in bounds)
        miny = min(b[1] for b in bounds)
        maxx = max(b[2] for b in bounds)
        maxy = max(b[3] for b in bounds)
        return (minx, miny, maxx, maxy)

    @staticmethod
    def _multi_from_geojson(geojson, cls):
        geometries = []
        for coordinates in geojson["coordinates"]:
            geometry = cls(coordinates, srid=None)
            geometries.append(geometry)
        return geometries

    def _load_geometry(self):
        self._geometries = self.__class__._read_wkb(
            self._reader, self._dimz, self._dimm
        )

    def _set_multi_metadata(self):
        self._dimz = None
        self._dimm = None
        for geometry in self.geometries:
            if self._dimz is None:
                self._dimz = geometry.dimz
            elif self._dimz != geometry.dimz:
                raise DimensionalityError("Mixed dimensionality in MultiGeometry")
            if self._dimm is None:
                self._dimm = geometry.dimm
            elif self._dimm != geometry.dimm:
                raise DimensionalityError("Mixed dimensionality in MultiGeometry")
            if geometry._srid is not None:
                if self._srid != geometry._srid:
                    raise SridError(
                        "Geometry can not be different from SRID in MultiGeometry"
                    )
                geometry._srid = None

    def _coordinates(self, dimz=True, dimm=True, tpl=True):
        return [g._coordinates(dimz, dimm, tpl) for g in self.geometries]

    def _to_geojson_coordinates(self):
        return self._coordinates(dimm=False, tpl=False)

    def _load_geometry(self):
        self._geometries = _MultiGeometry._read_wkb(
            self._reader, self._dimz, self._dimm
        )

    @staticmethod
    def _read_wkb(reader, dimz, dimm):
        geometries = []
        try:
            for _ in range(reader.get_int()):
                cls, dimz, dimm, srid = Geometry._get_wkb_type(reader)
                coordinates = cls._read_wkb(reader, dimz, dimm)
                geometry = cls(coordinates, srid=srid, dimz=dimz, dimm=dimm)
                geometries.append(geometry)
        except TypeError as e:
            raise WkbError() from e
        return geometries

    @classmethod
    def _read_wkt(cls, reader):
        if reader.get_empty():
            geoms = []
        else:
            reader.get_openpar()
            geoms = [cls.MULTITYPE._read_wkt(reader)]
            while reader.get_comma(req=False):
                geom = cls.MULTITYPE._read_wkt(reader)
                geoms.append(geom)
            reader.get_closepar()
        return cls(geoms, srid=reader.srid)

    def _write_wkb(self, writer, dimz, dimm):
        writer.add_int(len(self.geometries))
        for geometry in self._geometries:
            geometry._write_wkb_header(writer, False, dimz, dimm)
            geometry._write_wkb(writer, dimz, dimm)

    def _to_wkt_coordinates(self, writer):
        if not self.geometries:
            return None

        return writer.join(
            [writer.wrap(geom._to_wkt_coordinates(writer)) for geom in self.geometries]
        )


class Point(Geometry):
    """
    A representation of a PostGIS Point.

    ``Point`` objects can be created directly.

        >>> Point((0, -52, 5), dimm=True, srid=4326)
        <Point: 'geometry(PointM,4326)'>

    The ``dimz`` and ``dimm`` parameters will indicate how to interpret the
    coordinates that have been passed as the first argument. By default, the
    third coordinate will be interpreted as representing the Z dimension.
    """

    _LWGEOMTYPE = 1
    __slots__ = ["_x", "_y", "_z", "_m"]

    def __init__(self, coordinates=None, srid=None, dimz=False, dimm=False):
        if self._wkb:
            self._x = None
            self._y = None
            self._z = None
            self._m = None
        else:
            for c in coordinates:
                if c is None:
                    continue
                if not isinstance(c, numbers.Number):
                    raise CoordinateError(
                        f"Coordinates must be numeric: {coordinates}", coordinates
                    )
            self._srid = srid
            self._x = coordinates[0]
            self._y = coordinates[1]
            num = len(coordinates)
            if num > 4:
                raise DimensionalityError(
                    f"Maximum dimensionality supported for coordinates is 4: {coordinates}"
                )
            if num == 2:  # fill in Z and M if we are supposed to have them, else None
                if dimz and dimm:
                    self._z = 0
                    self._m = 0
                elif dimz:
                    self._z = 0
                    self._m = None
                elif dimm:
                    self._z = None
                    self._m = 0
                else:
                    self._z = None
                    self._m = None
            elif num == 3:  # use the 3rd coordinate for Z or M as directed or as Z
                if dimz and dimm:
                    self._z = coordinates[2]
                    self._m = 0
                elif dimm:
                    self._z = None
                    self._m = coordinates[2]
                else:
                    self._z = coordinates[2]
                    self._m = None
            else:  # use both the 3rd and 4th coordinates, ensure not None
                self._z = coordinates[2]
                self._m = coordinates[3]

            self._dimz = self._z is not None
            self._dimm = self._m is not None

    @property
    def x(self):
        """
        X coordinate.
        """
        self._check_cache()
        return self._x

    @x.setter
    def x(self, value):
        self._check_cache()
        self._x = value

    @property
    def y(self):
        """
        M coordinate.
        """
        self._check_cache()
        return self._y

    @y.setter
    def y(self, value):
        self._check_cache()
        self._y = value

    @property
    def z(self):
        """
        Z coordinate.
        """
        if not self._dimz:
            return None
        self._check_cache()
        return self._z

    @z.setter
    def z(self, value):
        self._check_cache()
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
        self._check_cache()
        return self._m

    @m.setter
    def m(self, value):
        self._check_cache()
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
            return
        self._check_cache()
        if value and self._z is None:
            self._z = 0
        elif value is None:
            self._z = None
        self._dimz = value

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
            return
        self._check_cache()
        if value and self._m is None:
            self._m = 0
        elif value is None:
            self._m = None
        self._dimm = value

    def _coordinates(self, dimz=True, dimm=True, tpl=True):
        dimz = dimz & self.dimz
        dimm = dimm & self.dimm

        if dimz and dimm:
            coordinates = (self.x, self.y, self.z, self.m)
        elif dimz:
            coordinates = (self.x, self.y, self.z)
        elif dimm:
            coordinates = (self.x, self.y, self.m)
        else:
            coordinates = (self.x, self.y)

        if tpl:
            return coordinates
        return list(coordinates)

    def _to_geojson_coordinates(self):
        return self._coordinates(dimm=False, tpl=False)

    def _bounds(self):
        return (self.x, self.y, self.x, self.y)

    def _load_geometry(self):
        self._x, self._y, self._z, self._m = Point._read_wkb(
            self._reader, self._dimz, self._dimm
        )

    @staticmethod
    def _read_wkb(reader, dimz, dimm):
        try:
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
        except TypeError as e:
            raise WkbError() from e
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

    @staticmethod
    def _read_wkt_coordinates(reader):
        if reader.get_empty():
            raise WktError(reader, "Points with no coordinates are not supported in WKT.")
        reader.get_openpar()
        coords = reader.get_coordinates()
        reader.get_closepar()
        return coords

    @staticmethod
    def _read_wkt(reader):
        coords = Point._read_wkt_coordinates(reader)
        return Point(coords, dimz=reader.dimz, dimm=reader.dimm, srid=reader.srid)

    def _to_wkt_coordinates(self, writer):
        return writer.format(self.coordinates)

class LineString(Geometry):
    """
    A representation of a PostGIS Line.

    ``LineString`` objects can be created directly.

        >>> LineString([(0, 0, 0, 0), (1, 1, 0, 0), (2, 2, 0, 0)])
        <LineString: 'geometry(LineStringZM)'>

    The ``dimz`` and ``dimm`` parameters will indicate how to interpret the
    coordinates that have been passed as the first argument. By default, the
    third coordinate will be interpreted as representing the Z dimension.
    """

    _LWGEOMTYPE = 2
    __slots__ = ["_vertices"]

    def __init__(self, vertices=None, srid=None, dimz=False, dimm=False):
        if self._wkb:
            self._vertices = None
        else:
            self._srid = srid
            self._dimz = dimz
            self._dimm = dimm
            self._vertices = LineString._from_coordinates(
                vertices, dimz=dimz, dimm=dimm
            )
            self._set_dimensionality(self._vertices)

    @property
    def vertices(self):
        """
        List of vertices that comprise the line.
        """
        self._check_cache()
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
        if self.dimz == value:
            return
        for vertex in self.vertices:
            vertex.dimz = value
        self._dimz = value

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
        if self.dimm == value:
            return
        for vertex in self.vertices:
            vertex.dimm = value
        self._dimm = value

    def _coordinates(self, dimz=True, dimm=True, tpl=True):
        return [v._coordinates(dimz, dimm, tpl) for v in self.vertices]

    def _to_geojson_coordinates(self):
        return self._coordinates(dimz=False, tpl=False)

    def _bounds(self):
        x = [v.x for v in self.vertices]
        y = [v.y for v in self.vertices]
        return (min(x), min(y), max(x), max(y))

    @staticmethod
    def _from_coordinates(vertices, dimz, dimm):
        return [Point(vertex, dimz=dimz, dimm=dimm) for vertex in vertices]

    def _load_geometry(self):
        vertices = LineString._read_wkb(self._reader, self._dimz, self._dimm)
        self._vertices = LineString._from_coordinates(vertices, self._dimz, self._dimm)

    @staticmethod
    def _read_wkb(reader, dimz, dimm):
        vertices = []
        try:
            for _ in range(reader.get_int()):
                coordinates = Point._read_wkb(reader, dimz, dimm)
                vertices.append(coordinates)
        except TypeError as e:
            raise WkbError() from e
        return vertices

    def _write_wkb(self, writer, dimz, dimm):
        writer.add_int(len(self.vertices))
        for vertex in self.vertices:
            vertex._write_wkb(writer, dimz, dimm)

    @staticmethod
    def _read_wkt_coordinates(reader):
        reader.get_openpar()
        vertices = [reader.get_coordinates()]
        while reader.get_comma(req=False):
            coords = reader.get_coordinates()
            vertices.append(coords)
        reader.get_closepar()
        return vertices

    @staticmethod
    def _read_wkt(reader):
        if reader.get_empty():
            raise WktError(reader, "LineStrings with no coordinates are not supported in WKT.")
        vertices = LineString._read_wkt_coordinates(reader)
        return LineString(vertices, dimz=reader.dimz, dimm=reader.dimm, srid=reader.srid)

    def _to_wkt_coordinates(self, writer):
        return writer.join(
                    [v._to_wkt_coordinates(writer) for v in self.vertices]
        )

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
    third coordinate will be interpreted as representing the Z dimension.
    """

    _LWGEOMTYPE = 3
    __slots__ = ["_rings"]

    def __init__(self, rings=None, srid=None, dimz=False, dimm=False):
        if self._wkb:
            self._rings = None
        else:
            self._srid = srid
            self._dimz = dimz
            self._dimm = dimm
            self._rings = Polygon._from_coordinates(rings, dimz=dimz, dimm=dimm)
            self._set_dimensionality(self._rings)

    @property
    def rings(self):
        """
        List of linearrings that comprise the polygon.
        """
        self._check_cache()
        return self._rings

    @property
    def exterior(self):
        """
        The exterior ring of the polygon.
        """
        return self.rings[0]

    @property
    def interior(self):
        """
        A list of interior rings of the polygon.
        """
        return self.rings[1:]

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

    @property
    def dimm(self):
        """LineString([(0, 0, 0, 0), (1, 1, 0, 0), (2, 2, 0, 0)])
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

    def _coordinates(self, dimz=True, dimm=True, tpl=True):
        return [r._coordinates(dimz, dimm, tpl) for r in self.rings]

    def _to_geojson_coordinates(self):
        return self._coordinates(dimz=False, tpl=False)

    def _bounds(self):
        return self.exterior.bounds

    @staticmethod
    def _from_coordinates(rings, dimz, dimm):
        return [LineString(vertices, dimz=dimz, dimm=dimm) for vertices in rings]

    def _load_geometry(self):
        rings = Polygon._read_wkb(self._reader, self._dimz, self._dimm)
        self._rings = Polygon._from_coordinates(rings, self._dimz, self._dimm)

    @staticmethod
    def _read_wkb(reader, dimz, dimm):
        rings = []
        try:
            for _ in range(reader.get_int()):
                vertices = LineString._read_wkb(reader, dimz, dimm)
                rings.append(vertices)
        except TypeError as e:
            raise WkbError() from e
        return rings

    def _write_wkb(self, writer, dimz, dimm):
        writer.add_int(len(self.rings))
        for ring in self.rings:
            ring._write_wkb(writer, dimz, dimm)

    @staticmethod
    def _read_wkt_coordinates(reader):
        reader.get_openpar()
        rings = [LineString._read_wkt_coordinates(reader)]
        while reader.get_comma(req=False):
            ring = LineString._read_wkt_coordinates(reader)
            rings.append(ring)
        reader.get_closepar()
        return rings

    @staticmethod
    def _read_wkt(reader):
        if reader.get_empty():
            raise WktError(reader, "Polygons with no coordinates are not supported in WKT.")
        rings = Polygon._read_wkt_coordinates(reader)
        return Polygon(rings, dimz=reader.dimz, dimm=reader.dimm, srid=reader.srid)

    def _to_wkt_coordinates(self, writer):
        return writer.join(
                [writer.wrap(r._to_wkt_coordinates(writer)) for r in self.rings]
        )


class MultiPoint(_MultiGeometry):
    """
    A representation of a PostGIS MultiPoint.

    ``MultiPoint`` objects can be created directly from a list of ``Point``
    objects.

        >>> p1 = Point((0, 0, 0))
        >>> p2 = Point((1, 1, 0))
        >>> MultiPoint([p1, p2])
        <MultiPoint: 'geometry(MultiPointZ)'>

    The SRID and dimensionality of all geometries in the collection must be
    identical.
    """

    _LWGEOMTYPE = 4
    MULTITYPE = Point

    def __init__(self, points=None, srid=None):
        super().__init__(Point, geometries=points, srid=srid)

    @property
    def points(self):
        """
        List of all component points.
        """
        return self.geometries


class MultiLineString(_MultiGeometry):
    """
    A representation of a PostGIS MultiLineString

    ``MultiLineString`` objects can be created directly from a list of
    ``LineString`` objects.

        >>> l1 = LineString([(1, 1, 0), (2, 2, 0)], dimm=True)
        >>> l2 = LineString([(0, 0, 0), (0, 1, 0)], dimm=True)
        >>> MultiLineString([l1, l2])
        <MultiLineString: 'geometry(MultiLineStringM)'>

    The SRID and dimensionality of all geometries in the collection must be
    identical.
    """

    _LWGEOMTYPE = 5
    MULTITYPE = LineString

    def __init__(self, linestrings=None, srid=None):
        super().__init__(LineString, geometries=linestrings, srid=srid)

    @property
    def linestrings(self):
        """
        List of all component lines.
        """
        return self.geometries


class MultiPolygon(_MultiGeometry):
    """
    A representation of a PostGIS MultiPolygon.

    ``MultiPolygon`` objects can be created directly from a list of ``Polygon``
    objects.

        >>> p1 = Polygon([[(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)]])
        >>> p2 = Polygon([[(2, 2), (3, 2), (3, 3), (2, 3), (2, 2)]])
        >>> MultiPolygon([p1, p2], srid=4326)
        <MultiPolygon: 'geometry(MultiPolygon,4326)'>

    The SRID and dimensionality of all geometries in the collection must be
    identical.
    """

    _LWGEOMTYPE = 6
    MULTITYPE = Polygon

    def __init__(self, polygons=None, srid=None):
        super().__init__(Polygon, geometries=polygons, srid=srid)

    @property
    def polygons(self):
        """
        List of all component polygons.
        """
        return self.geometries


class GeometryCollection(_MultiGeometry):
    """
    A representation of a PostGIS GeometryCollection.

    ``GeometryCollection`` objects can be created directly from a list of
    geometries, including other collections.

        >>> p = Point((0, 0, 0))
        >>> l = LineString([(1, 1, 0), (2, 2, 0)])
        >>> GeometryCollection([p, l])
        <GeometryCollection: 'geometry(GeometryCollectionZ)'>

    The SRID and dimensionality of all geometries in the collection must be
    identical.
    """

    _LWGEOMTYPE = 7
    MULTITYPE = Geometry

    def __init__(self, geometries=None, srid=None):
        super().__init__(Geometry, geometries=geometries, srid=srid)

    def _to_geojson(self):
        geometries = [g._to_geojson() for g in self._geometries]
        geojson = {"type": self.type, "geometries": geometries}
        return geojson

    def _to_wkt_coordinates(self, writer):
        return writer.join(
                    [geom._as_wkt(writer) for geom in self.geometries]
        )

    @classmethod
    def _read_wkt(cls, reader):
        if reader.get_empty():
            geoms = []
        else:
            reader.get_openpar()
            geoms = [Geometry._read_wkt_geom(reader)]
            while reader.get_comma(req=False):
                geom = Geometry._read_wkt_geom(reader)
                geoms.append(geom)
            reader.get_closepar()
        return GeometryCollection(geoms, srid=reader.srid)
