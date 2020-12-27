Packaging
=========

Build
-----

At this time, the building is being done on Wendy (a desktop 
machine that I built in 2014).  It is currently running 
Linux Mint 20 (Ulyana) with the Cinnamon desktop.

In theory, the process is:

.. code-block:: console

    git clone git@github.com:rich-dobbs-13440/astutus.git
    ./astutus/packaging/build.sh


Validation
----------

.. code-block:: console

    cd astutus/packaging/dist
    python3 -m venv venv
    pip install astutus-0.1.0-py3-none-any.whl
    python3 -m astutus.web.flask_app


Deployment
----------

Should be discussed.


Publication
-----------

The aim is to publish to PyPi.  Working at getting things good
enough for initial publication.  Basically should get
licensed defined adequately, and minimal command.
