r""" A Sphinx extension for styled, dynamic web pages with Flask web applications.

Overview
--------

At this time, the extension is targeted at the  **sphinx_rtd_theme** Sphinx theme.

At this time, the Sphinx extension is not designed to be installed separately from the
Astutus python package.


Configuration
-------------

The package can be used by adding this line into your Sphinx documentation conf.py file:

.. code-block:: python

    extensions = [
        ...,
        'astutus.sphinx.dyn_pages',
    ]

In addition, you need to add the extension's CSS file  into you _static folder:

    astutus_dynamic_sphinx_pages.css

There are a number of configuration variables that must be defined:

.. code-block:: python

    # Options for the Astutus dynamic pages custom extension.
    astutus_dyn_pages_dir = "app"  # relative to the configuration directory.
    astutus_dyn_base = "/your_applications_urls_leading_path"  # web app URL path to get to top of dynamic pages.
    astutus_dyn_extra_head_material = " what every you want to add in the HTML head section of dynamic pages. "

Optional configuration variables have good-enough default values that it is not expected that
user's of the extension will need to customize them.  At this time, the extension has one
optional configuration variable:

    astutus_dyn_styled_templates_path = 'astutus_dyn_styled_templates'


Directives
----------

The directives implemented are:

**.\. astutus_dyn_include::** *use Jinja2 template in a styled page*

**.\. astutus_dyn_link::** *fix up the .\.toc_tree:: directive to work with the page*

**.\. astutus_dyn_bookmark::** *customize the browser bookmark (and tab title) for a page*

**.\. astutus_dyn_breadcrumb::** *customize the Read-the-Docs breadcrumb navigation for a page*

**.\. astutus_dyn_destination::** *place the styled template in a particular location*

**.\. astutus_toggle_note::** *write a note that can be expanded or collapsed*


"""
# from astutus.sphinx.dyn_pages import read_post_processing_directive_value  # noqa
