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


# Override theme to issue with tables.
def setup(app):
    app.add_css_file('css/theme_overrides.css')


# For now, keep the original source in the docs directory, but
# longer term, should be installed there when the extension
# is installed.  # Should be able to do this automatically
# in the extension!  Probably should only add to pages
# where it is used.
html_js_files = ['astutus_dynamic_sphinx_pages.js']

# Options for the Astutus dynamic pages custom extension.
astutus_docs_base = "/static/_docs"
astutus_dyn_base = "/astutus"
