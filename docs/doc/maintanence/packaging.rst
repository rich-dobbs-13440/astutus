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

    ./astutus/packaging/validate_pkg.sh


Then open up a browser to http://localhost:5000/astutus

Troubleshooting:  /tmp/try-astutus/astutus/packaging/dist/venv/lib/python3.8/site-packages/astutus

Deployment
----------

Should be discussed.


Publication
-----------

The aim is to publish to PyPI.  Working at getting things good
enough for initial publication.  Basically should get
licensed defined adequately, and minimal command.


(dist_venv) rich@wendy:~/src/github.com/rich-dobbs-13440/astutus/packaging/dist$ ls
astutus-0.1.2-py3-none-any.whl  astutus-0.1.2.tar.gz  content
(dist_venv) rich@wendy:~/src/github.com/rich-dobbs-13440/astutus/packaging/dist$ twine upload astutus-0.1.2-py3-none-any.whl

Command 'twine' not found, but can be installed with:

sudo apt install twine


(dist_venv) rich@wendy:~/src/github.com/rich-dobbs-13440/astutus/packaging/dist$ twine upload astutus-0.1.2-py3-none-any.whl
Uploading distributions to https://upload.pypi.org/legacy/
Enter your username: rich.dobbs.13440
Enter your password:
Uploading astutus-0.1.2-py3-none-any.whl
100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 10.5M/10.5M [00:19<00:00, 559kB/s]
NOTE: Try --verbose to see response content.
HTTPError: 400 Client Error: 'text/rst' is an invalid value for Description-Content-Type. Error: Invalid description content type: type/subtype is not valid See https://packaging.python.org/specifications/core-metadata for more information. for url: https://upload.pypi.org/legacy/