from binascii import hexlify, unhexlify
from struct import calcsize, unpack_from, pack, error
from .exceptions import WkbError


class HexReader:
    """
    A reader for generic hex data. The current position in the stream of bytes
    will be retained as data is read.
    """

    def __init__(self, hexdata, order, offset=0):
        self._data = hexdata
        self._order = order
        self._ini_offset = offset
        self._cur_offset = offset

    def reset(self):
        """
        Start reading from the initial position again.
        """
        self._cur_offset = self._ini_offset

    def _get_value(self, fmt):
        try:
            value = unpack_from(f"{self._order}{fmt}", self._data, self._cur_offset)[0]
        except error as e:
            raise WkbError(e) from e
        self._cur_offset += calcsize(fmt)
        return value

    def get_char(self):
        """
        Get the next character from the stream of bytes.
        """
        return self._get_value("B")

    def get_int(self):
        """
        Get the next four-byte integer from the stream of bytes.
        """
        return self._get_value("I")

    def get_double(self):
        """
        Get the next double from the stream of bytes.
        """
        return self._get_value("d")


class HexWriter:
    """
    A writer for generic hex data.
    """

    def __init__(self, order):
        self._fmts = []
        self._values = []
        self._order = order

    def _add_value(self, fmt, value):
        self._fmts.append(fmt)
        self._values.append(value)

    def add_order(self):
        """
        Add the endianness to the stream of bytes.
        """
        if self._order == "<":
            self.add_char(1)
        else:
            self.add_char(0)

    def add_char(self, value):
        """
        Add a single character to the stream of bytes.
        """
        self._add_value("B", value)

    def add_int(self, value):
        """
        Add a four-byte integer to the stream of bytes.
        """
        self._add_value("I", value)

    def add_double(self, value):
        """
        Add a double to the stream of bytes.
        """
        self._add_value("d", value)

    @property
    def data(self):
        """
        Return the bytes as hex data.
        """
        fmt = self._order + "".join(self._fmts)
        data = pack(fmt, *self._values)
        return HexBytes(data)


class HexBytes(bytes):
    """A subclass of bytearray that represents binary WKB data.
    It can be converted to a hexadecimal representation of the data using str()
    and compared to a hexadecimal representation with the normal equality operator."""

    def __new__(cls, data):
        if not isinstance(data, (bytes, bytearray)):
            data = unhexlify(str(data))
        elif data[:2] in (b"00", b"01"):  # hex-encoded string as bytes
            data = unhexlify(data.decode("ascii"))
        return bytes.__new__(cls, data)

    def __str__(self):
        return hexlify(self).decode("ascii")

    def __eq__(self, other):
        if isinstance(other, str) and other[:2] in ("00", "01"):
            other = unhexlify(other)
        return super().__eq__(other)
