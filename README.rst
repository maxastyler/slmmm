=====
slmmm
=====


.. image:: https://img.shields.io/pypi/v/slmmm.svg
        :target: https://pypi.python.org/pypi/slmmm

.. image:: https://img.shields.io/travis/maxastyler/slmmm.svg
        :target: https://travis-ci.com/maxastyler/slmmm

.. image:: https://readthedocs.org/projects/slmmm/badge/?version=latest
        :target: https://slmmm.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status




A grpc-controlled slm controller running with Qt5 and pyqtgraph


* Free software: MIT license
* Documentation: https://slmmm.readthedocs.io.

Examples
--------

.. code:: python

    from slmmm import SLMController

    controller = SLMController(2020)
    controller.start_server()
    controller.set_image(np.random.randint(0, 255, (500, 500), dtype=np.uint8))

    controller.stop_server()

Features
--------

* Runs a server, so you don't need to worry about running a UI event loop
* Convenience class `SLMController` to allow easy interaction with the SLM screen

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
