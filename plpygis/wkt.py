import re
from .exceptions import WktError

def _regex(expr):
    return re.compile(fr"\s*{expr}\s*")

class WktReader:
    """
    A reader for Well-Knownn Text.
    """
    _TYPE = _regex("(POINT|LINESTRING|POLYGON|MULTIPOINT|MULTILINESTRING|MULTIPOLYGON|GEOMETRYCOLLECTION)")
    _DIMS = _regex("(ZM|Z|M)")
    _EMPTY = _regex("EMPTY")
    _OP = _regex("[(]")
    _CP = _regex("[)]")
    _COMMA = _regex("[,]")
    _NUMBER = _regex("[-]?[0-9]+[.]?[0-9]*")
    _SRID = _regex("SRID=[0-9]+;")

    def __init__(self, wkt, offset=0):
        self._data = wkt.upper().strip()
        self._start = offset
        self.pos = offset

    def close(self):
        """
        Terminate reading and raise error if unconsumed characters remain.
        """
        if self.pos != len(self._data):
            raise WktError(self, expected="end of WKT")

    def reset(self):
        """
        Start reading from the initial position again.
        """
        self.pos = self._start

    def _get_value(self, expr):
        match = expr.match(self._data, pos=self.pos)
        if match:
            self.pos = match.end()
            return match.group().strip()
        else:
            return None

    def _get_number(self):
        value = self._get_value(self._NUMBER)
        if not value:
            raise WktError(self, expected="number")
        return float(value)

    def get_type(self):
        value = self._get_value(self._TYPE)
        if not value:
            raise WktError(self, expected="geometry type")
        else:
            return value

    def get_dims(self):
        value = self._get_value(self._DIMS)

        if value == "Z":
            self.dimz = True
            self.dimm = False
        elif value == "M":
            self.dimz = False
            self.dimm = True
        elif value == "ZM":
            self.dimz = True
            self.dimm = True
        else:
            self.dimz = False
            self.dimm = False
        return self.dimz, self.dimm

    def get_empty(self):
        return self._get_value(self._EMPTY)

    def get_openpar(self):
        value = self._get_value(self._OP)
        if not value:
            raise WktError(self, expected="opening parenthesis")
        return True

    def get_closepar(self, req=True):
        value = self._get_value(self._CP)
        if not value:
            if req:
                raise WktError(self, expected="closing parenthesis")
            else:
                return False
        return True

    def get_srid(self):
        value = self._get_value(self._SRID)
        if value:
            value = value.strip("SRID=")
            value = value.strip(";")
            value = int(value)
        self.srid = value
        return value

    def get_comma(self, req=True):
        value = self._get_value(self._COMMA)
        if not value:
            if req:
                raise WktError(self, expected="comma")
            else:
                return False
        return True

    def get_coordinates(self):
        x = self._get_number()
        y = self._get_number()
        if self.dimz:
            z = self._get_number()
        if self.dimm:
            m = self._get_number()

        if self.dimz and self.dimm:
            return (x, y, z, m)
        elif self.dimz:
            return (x, y, z)
        elif self.dimm:
            return (x, y, m)
        else:
            return (x, y)


class WktWriter:
    """
    A writer for Well-Knownn Text.
    """
    def __init__(self, geom, use_srid=True):
        self.geom = geom
        self.dims = False
        self.add_srid(use_srid)
        
    def add_srid(self, use_srid):
        if use_srid and self.geom.srid:
            self.wkt = f"SRID={self.geom.srid};"
        else:
            self.wkt = ""

    def add_dims(self):
        if self.dims:
            return ""
        self.dims = True
        if self.geom.dimz and self.geom.dimm:
            return " ZM"
        elif self.geom.dimz:
            return " Z"
        elif self.geom.dimm:
            return " M"
        else:
            return ""

    def type(self, geom):
        wkt = geom.type.upper()
        wkt += self.add_dims()
        return wkt

    def add(self, text):
        self.wkt += text

    def format(self, coords):
        return " ".join([f"{float(c)}".rstrip("0").rstrip(".") for c in coords])

    def wrap(self, text):
        return f"({text})"

    def join(self, items):
        return ", ".join(items)
