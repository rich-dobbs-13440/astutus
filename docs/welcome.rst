Welcome
=======

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

.. warning::

   This work is targeted at Linux-like computers.  At this time, it has only been
   used with Linux Mint and Raspberry Pi OS.  The actual functionality depends
   on operating system specific utilities that are not available in Windows-based
   computers.


Where is the Code?
------------------

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


What's the Best Thing About This?
---------------------------------

This package includes a web application that both hosts the
documentation and provides a user interface.  All of this
is implemented using Sphinx, which provides easy, highly
productive authoring of the content and a clean, attractive
styling of content. Although, its not there yet, it is
expected that this will be available as an **stand-alone,
easily-applied Sphinx extension**.
