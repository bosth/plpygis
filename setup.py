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
    license="GPL-3.0-only",
    author="Benjamin Trigona-Harany",
    author_email="plpygis@jaxartes.net",
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
        "shapely_support":  ["Shapely>=2.0.2"]
    },
    keywords=["gis geospatial postgis postgresql plpython"]
)
