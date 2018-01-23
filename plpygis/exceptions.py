class PlpygisError(Exception):
    """
    Basic exception for ``plpygis``.
    """
    def __init__(self, msg):
        super(PlpygisError, self).__init__(msg)
      

class DependencyError(PlpygisError, ImportError):
    """
    Exception for a missing dependency.
    """
    def __init__(self, dep, msg=None):
        if msg is None:
            msg = "Dependency '{}' is not available.".format(dep)
        super(DependencyError, self).__init__(msg)


class WkbError(PlpygisError):
    """
    Exception for problems in parsing WKBs.
    """
    def __init__(self, msg=None):
        if msg is None:
            msg = "Unreadable WKB."
        super(WkbError, self).__init__(msg)


class DimensionalityError(PlpygisError):
    """
    Exception for problems in dimensionality of geometries.
    """
    def __init__(self, msg=None):
        if msg is None:
            msg = "Geometry has invalid dimensionality."
        super(DimensionalityError, self).__init__(msg)


class SridError(PlpygisError):
    """
    Exception for problems in dimensionality of geometries.
    """
    def __init__(self, msg=None):
        if msg is None:
            msg = "Geometry has invalid SRID."
        super(SridError, self).__init__(msg)
