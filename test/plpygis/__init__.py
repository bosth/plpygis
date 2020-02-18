import doctest
import plpygis

from .geometry import GeometryTestCase


def load_tests(loader, tests, ignore):
    doctests = doctest.DocTestSuite(plpygis.geometry)
    assert doctests.countTestCases() > 0
    tests.addTests(doctests)
    return tests
