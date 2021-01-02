Flask Application Templates
===========================

These Restructured Text pages are used to generate styled HTML pages that
contain placeholders.

The placeholders are then replaced with Jinja2 dynamic markup, and
stored as templates to be used by the Flask application.

The names of the templates should all start with "flask_app_dyn_" since
that is used in generating the destination name in script that
processes the files.

.. toctree::
    :maxdepth: 1
    :caption: Dynamic Templates:

    flask_app_dyn_usb
    flask_app_dyn_astutus
    flask_app_dyn_raspi
    flask_app_dyn_raspi_find


To create a new dynamic page, here are some steps that you'll need to do:

    - Add the name of the dynamic template to the toc list above.
    - Create a rst file with that name in the docs/flask_app/templates/ with appropriate placeholders.
    - Create a new app.route handler in flask_app, or a blueprint used by flask_app.
    - Create or updated any include Jinja2 templates that are included.
    - Customize the breadcrumbs
    - Customize the links if needed
    - Generate and use any route specific dynamic data

To debug dynamic pages:

    - Run ./packaging/build.sh
    - Examine ./src/astutus/web/templates for contents of the the transformed templates.
    - Run ./packaging/validate_pkg_flask_app.sh
    - Use a browser to view the web-site and debug your new or revised page.
