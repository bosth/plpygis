Installation
============

Requirements
------------

``plpygis`` has no dependencies beyond an installation of Python 3 (Python 2 should also work). Additionally, ``plpygis`` can use `Shapely <https://github.com/Toblerity/Shapely>`_ (version 2.0 or greater) if available. Without it, conversion to and from Shapely geometries will be impossible.

Python Package Index
--------------------

``plpygis`` may be installed from PyPI.

.. code-block:: console

   $ pip install plpygis

It is recommended that ``plpygis`` is installed into the system installation of Python or it may not be available in PL/Python functions.

Source
------

The package sources are available at https://github.com/bosth/plpygis. Building and installing ``plpygis`` from source can be done with `setuptools <https://setuptools.readthedocs.io/en/latest/>`_:

.. code-block:: console

    $ python setup.py install

Tests
~~~~~

Tests require `nose <http://nose.readthedocs.io/en/latest/>`_: 

.. code-block:: console

    $ python setup.py test

Documentation
~~~~~~~~~~~~~

Building the documentation from source requires `Sphinx <http://www.sphinx-doc.org/>`_. By default, the documentation will be rendered in HTML:

.. code-block:: console

    $ python setup.py build_sphinx

For other documentation output formats, see the options in the ``docs`` subdirectory:

.. code-block:: console

    $ cd docs
    $ make
