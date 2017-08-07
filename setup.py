import os
from setuptools import setup
from plpygis._version import __version__

def readme():
    with open('README.rst') as f:
        return f.read()

setup(
    name="plpygis",
    version=__version__,
    url="https://github.com/bosth/plpygis",
    license="GNU GPLv3",
    author="Benjamin Trigona-Harany",
    author_email="bosth@alumni.sfu.ca",
    description="PostGIS Python tools",
    long_description=readme(),
    packages=["plpygis"],
    include_package_data=True,
    platforms="any",
    classifiers = [
        "Topic :: Database",
        "Topic :: Scientific/Engineering :: GIS"
    ],
    extras_require = {
        "shapely_support":  ["Shapely>=1.5.0"]
    },
    test_suite="nose.collector",
    tests_require=["nose"],
    keywords=["gis geospatial postgis postgresql plpython"]
)
