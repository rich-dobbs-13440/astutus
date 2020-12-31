#!/usr/bin/env python3

# Since the Jinja2 templates may not be legal HTML5, this process will be based
# on text manipulation, rather than DOM transformation. or XSLT transformations.

input_path = "../docs/_build/html/flask_app_templates/flask_app_dyn_usb.html"
output_path = "../src/astutus/web/templates/transformed_dyn_usb.html"

with open(input_path, "r") as input_file:
    html_text = input_file.read()

replacements = [
    ("../_static/", "{{ static_base }}/"),
    ("../index.html", "/astutus/doc/index.htlm")
]

for replacement in replacements:
    old, new = replacement
    html_text = html_text.replace(old, new)

with open(output_path, "w") as output_file:
    output_file.write(html_text)
