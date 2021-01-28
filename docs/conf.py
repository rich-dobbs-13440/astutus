# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
sys.path.insert(0, os.path.abspath('../src'))
import astutus  # noqa


# -- Project information -----------------------------------------------------

project = 'Astutus'
copyright = '2021, Rich Dobbs'
author = 'Rich Dobbs'

# The full version, including alpha/beta/rc tags
version = astutus.__version__
release = version + "a2021.01.14.22.19"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'astutus.sphinx.dyn_pages',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# For now, ignore warnings like this:
# WARNING: py:class reference target not found: sqlalchemy.ext.declarative.api.Model
# Sphinx does not handle complicated type hints, at least as currently configured.
nitpick_ignore = [
    ('py:class', 'sqlalchemy.ext.declarative.api.Model'),
    ('py:class', '{}'),
    ('py:class', "[<class 'dict'>]"),
    ('py:class', "[(<class 'int'>, <class 'str'>, <class 'str'>)]")
]

# These definition(s) are added to the top of every page - used in progress lists
rst_prolog = """

.. |in_progress| raw:: html

    <span style="background-color: light-gray">◉</span>

.. |done| raw:: html

    <span style="background-color: light-gray">✔</span>

.. |newly_done| raw:: html

    <span style="background-color: yellow">✔</span>

.. |dropped| raw:: html

    <span style="background-color: light-gray">🗴</span>

"""
# <input checked=""  disabled="" type="checkbox" style="cursor: default">
# <input checked disabled type="radio" style="cursor: default">

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Use the ringtail cat icon for docs too.
html_favicon = '_static/favicon.ico'
html_logo = '_static/favicon.ico'
# html_logo = '_static/android-chrome-192x192.png'

html_theme_options = {
    # 'style_nav_header_background': 'orange',
    'navigation_depth': 8,
}


def setup(app):
    app.add_css_file('css/theme_overrides.css')  # Override theme to issue with tables.
    app.add_css_file('css/app.css')  # Want this on all pages.


# Options for the Astutus dynamic pages custom extension.
astutus_dyn_pages_dir = "app"  # relative to the configuration directory.
astutus_dyn_base = "/astutus"  # web app URL path to get to top of dynamic pages.
astutus_dyn_extra_head_material = """
    <link rel="apple-touch-icon" sizes="180x180" href="/static/apple-touch-icon.png"/>
    <link rel="icon" type="image/png" sizes="32x32" href="/static/favicon-32x32.png"/>
    <link rel="icon" type="image/png" sizes="16x16" href="/static/favicon-16x16.png"/>
    <link rel="manifest" href="/static/site.webmanifest"/>

    <script src="/static/app.js"></script>
"""  # only inserted on dynamic pages.
