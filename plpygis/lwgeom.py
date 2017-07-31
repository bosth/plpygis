import struct
from binascii import hexlify, unhexlify

WKBZFLAG    = 0x80000000
WKBMFLAG    = 0x40000000
WKBSRIDFLAG = 0x20000000
WKBTYPE     = 0x1fffffff

class HexReader():
    """
    A reader for generic hex data. The current position in the stream of bytes
    will be retained as data is read.
    """
    def __init__(self, data, order, offset = 0):
        self._data = data
        self._order = order
        self._offset = offset

    def _get_value(self, fmt):
        value = struct.unpack_from("{}{}".format(self._order, fmt), self._data, self._offset)[0]
        self._offset += struct.calcsize(fmt)
        return value

    def get_int(self):
        """
        Get the next four-byte integer from the stream of bytes.

        :rtype: int
        """
        return self._get_value("I")

def read_ewkb_header(ewkb):
    """
    Read the header from a hex-encoded (E)WKB and extract the LWGEOM metadata. The
    function will return the type, SRID and two flags indicating the presence
    of Z and M dimensions.

    :param ewkb: hex-encoded bytes
    :type ewkb: str
    :return: tuple of geometry type, SRID, z-dimension, m-dimension
    :rtype: tuple(int, int, bool, bool)
    """
    if not ewkb:
        raise TypeError("No EWKB provided")
    ewkb = unhexlify(ewkb)

    if struct.unpack_from("b", ewkb)[0] == 0:
        reader = HexReader(ewkb, ">", 1)  # big-endian reader
    else:
        reader = HexReader(ewkb, "<", 1)  # little-endian reader
    header = reader.get_int()
    lwgeomtype = header & WKBTYPE
    dimz = bool(header & WKBZFLAG)
    dimm = bool(header & WKBMFLAG)
    if header & WKBSRIDFLAG:
        srid = reader.get_int()
    else:
        srid = None
    return lwgeomtype, srid, dimz, dimm

def strip_ewkb_srid(ewkb):
    """
    Remove the SRID flag from an EWKB.

    :param ewkb: hex-encoded bytes
    :type ewkb: str
    :return: hex-encoded bytes
    :rtype: str
    """
    if not ewkb:
        raise TypeError("No EWKB provided")
    ewkb = unhexlify(ewkb)
    if struct.unpack_from("b", ewkb)[0] == 0:
        order = ">"
        reader = HexReader(ewkb, order, 1)  # big-endian reader
        newhdr = hexlify(struct.pack("{}{}".format(order, "b"), 0))
    else:
        order = "<"
        reader = HexReader(ewkb, order, 1)  # little-endian reader
        newhdr = hexlify(struct.pack("{}{}".format(order, "b"), 1))

    header = reader.get_int()
    header = header & ~WKBSRIDFLAG
    newhdr += hexlify(struct.pack("{}{}".format(order, "I"), header))
    return (newhdr + hexlify(ewkb[9:])).decode("ascii")
