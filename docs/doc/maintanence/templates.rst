Styled Flask Application Templates
==================================

The pages within the 'app' directory are used to generate styled HTML pages that
contain Jinja2 markup.  They contain directives defined by a custom extension
to Sphinx. The subpackage that implements the extension is astutus.sphinx.


To create a new dynamic page, here are some steps that you'll need to do:

    - Create a rst file with that name in the docs/flask_app/templates/ with
      appropriate directives.
    - Create a new app.route handler in flask_app, or a blueprint used by flask_app.
    - Create or updated any include Jinja2 templates that are included.
    - Customize the breadcrumbs.
    - Customize the links if needed.
    - Generate and use any route specific dynamic data.

To debug dynamic pages:

    - Run ./packaging/build.sh
    - Examine ./src/astutus/web/templates for contents of the the transformed templates.
    - Run ./packaging/validate_pkg_flask_app.sh
    - Use a browser to view the web-site and debug your new or revised page.

For routine efficient use, combine the functions:

.. code-block:: console

    ./packaging/build.sh && ./packaging/validate_pkg_flask_app.sh
