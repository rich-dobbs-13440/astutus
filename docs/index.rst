.. Astutus documentation master file, created by
   sphinx-quickstart on Sat Dec 19 07:40:43 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Astutus
==================

Astutus is a repository to demonstrate the range and depth of my
python development skills.  It also serves as a useful codebase
from which I can search and reuse code as needed. Finally, it
serves as repository of things that I've learned and want to be
able to efficiently reuse.

Using the Astutus Web Application
---------------------------------

If you are viewing this documentation by running the web application,
just click this link:

.. raw:: html

   <p><a href="/astutus">Astutus From the Browser</a></p>

If that link doesn't work, you will need to install the Python
package and run the web application:

.. code-block:: console

   python3 -m venv astutus_venv
   source astutus_venv/bin/activate
   pip install astutus
   astutus-web-app

After that, open up your browser to:

.. raw:: html

   <p><a href="http://localhost:5000/astutus/doc/index.html">Welcome to Astutus</a></p>


Git repository
--------------

The code can be found at https://github.com/rich-dobbs-13440/astutus.

Why is it called **Astutus**?
-----------------------------

The same name should be used for a repository as for the python package.
In both cases, the name should be short, memorable, and easily searchable.

For example, **flask** is
a good name, because when searching on the internet for software,
it is easy to make a good search, just by searching for
**python flask**.  In contrast, **robot** is a poor name for a
testing framework, since there are a lot of things related to
robot and robots that might use python.

So the first thing to do in selecting a package name is to to
do a search.  In this case, I started with animals in Colorado.
This lead to https://en.wikipedia.org/wiki/Ring-tailed_cat.
Which has a species name of Bassariscus astutus.  Hmmm.  Maybe
astutus would be a good package name.  So search for **astutus**.
Essentially no hits for software related items.

As a bonus:  Here is the meaning in Latin:  https://en.wiktionary.org/wiki/astutus

Meaning:  shrewd, sagacious, expert, astute.

**I like that!**


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   roadmap_to_documentation
   flask_app_templates/flask_app_dyn_astutus
   backlog
   maintanence/guidelines
   source/modules


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


This documentation for |release| was produced at |today|.

.. astutus_dyn_links_in_menus::

