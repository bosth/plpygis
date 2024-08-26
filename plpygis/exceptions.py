class PlpygisError(Exception):
    """
    Basic exception for ``plpygis``.
    """

    def __init__(self, msg):
        super().__init__(msg)


class CoordinateError(PlpygisError):
    """
    Exception for problems in the coordinates of geometries.
    """

    def __init__(self, geom, msg=None):
        if msg is None:
            msg = f"Geometry has invalid coordinates: {geom}"
        super().__init__(msg)


class CollectionError(PlpygisError):
    """
    Exception for problems with geometries in collection types.
    """

    def __init__(self, msg=None):
        if msg is None:
            msg = "Error in the geometries in a collection."
        super().__init__(msg)


class DependencyError(PlpygisError, ImportError):
    """
    Exception for a missing dependency.
    """

    def __init__(self, dep, msg=None):
        if msg is None:
            msg = f"Dependency '{dep}' is not available."
        super().__init__(msg)


class WkbError(PlpygisError):
    """
    Exception for problems in parsing WKBs.
    """

    def __init__(self, msg=None):
        if msg is None:
            msg = "Unreadable WKB."
        super().__init__(msg)


class WktError(PlpygisError):
    """
    Exception for problems in parsing WKTs.
    """

    def __init__(self, reader, msg=None, expected=None):
        pos = reader.pos
        if not msg:
            if expected is None:
                msg = f"Unreadable WKT at position {pos+1}."
            else:
                msg = f"Expected {expected} at position {pos+1}."
        super().__init__(msg)


class DimensionalityError(PlpygisError):
    """
    Exception for problems in dimensionality of geometries.
    """

    def __init__(self, msg=None):
        if msg is None:
            msg = "Geometry has invalid dimensionality."
        super().__init__(msg)


class SridError(PlpygisError):
    """
    Exception for problems in dimensionality of geometries.
    """

    def __init__(self, msg=None):
        if msg is None:
            msg = "Geometry has invalid SRID."
        super().__init__(msg)


class GeojsonError(PlpygisError):
    """
    Exception for problems in GeoJSONs.
    """

    def __init__(self, msg=None):
        if msg is None:
            msg = "Invalid GeoJSON."
        super().__init__(msg)
