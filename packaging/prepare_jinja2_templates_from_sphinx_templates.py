#!/usr/bin/env python3

# Since the Jinja2 templates may not be legal HTML5, this process will be based
# on text manipulation, rather than DOM transformation or XSLT transformations.


def prepare_wy_menu_vertical(html_text):
    """ A simple state machine to prepare the menu for jinja2 substition  """
    output_lines = []

    # Create a closure to produce output
    def add_to_output(line):
        # Strip all whitespace from lines, since the sphinx generated pages are completely inconsistent.
        # Probably should pretty print html at the end.
        stripped_line = line.strip()
        # print(f"stripped_line: {stripped_line}")
        if stripped_line != "":
            output_lines.append(stripped_line)

    state = "before"
    nesting = 0
    for line in html_text.splitlines():
        if state == "before":
            if 'class="wy-menu wy-menu-vertical"' in line:
                state = "in_div"
            add_to_output(line)
        elif state == "in_div":
            if '<p class="caption"><span class="caption-text">Contents:</span></p>' in line:
                state = "ready_for_menu"
            add_to_output(line)
        elif state == "ready_for_menu":
            if '<ul class="current">' in line:
                nesting += 1
                state = "in_list_items"
            add_to_output(line)
        elif state == "in_list_items":
            nesting += line.count("<li")
            nesting -= line.count("</li>")
            nesting += line.count("<ul")
            nesting -= line.count("/ul>")
            print(f"skipped line: {line}")
            if nesting <= 0:
                state = "done_with_menu"
                add_to_output("{{ wy_menu_vertical }}")
                add_to_output("</ul>")
        elif state == "done_with_menu":
            add_to_output(line)
    return "\n".join(output_lines)


def prepare_breadcrumbs_navigation(html):
    output_lines = []

    # Create a closure to produce output
    def add_to_output(line):
        # Strip all whitespace from lines, since the sphinx generated pages are completely inconsistent.
        # Probably should pretty print html at the end.
        stripped_line = line.strip()
        # print(f"stripped_line: {stripped_line}")
        if stripped_line != "":
            output_lines.append(stripped_line)

    state = 'before'
    for line in html_text.splitlines():
        if state == 'before':
            if '<div role="navigation" aria-label="breadcrumbs navigation">' in line:
                state = 'in'
            add_to_output(line)
        elif state == 'in':
            if '<ul class="wy-breadcrumbs">' in line:
                add_to_output(line)
                add_to_output('{{ breadcrumbs_list_items }}')
            elif '/<ul>' in line:
                add_to_output(line)
            elif '<hr/>' in line:
                add_to_output(line)
            elif '</div>' in line:
                add_to_output
                state = 'after'
        elif state == 'after':
            add_to_output(line)
    return "\n".join(output_lines)


def apply_line_oriented_replacements(html_text):
    output_lines = []

    # Create a closure to produce output
    def add_to_output(line):
        # Strip all whitespace from lines, since the sphinx generated pages are completely inconsistent.
        # Probably should pretty print html at the end.
        stripped_line = line.strip()
        # print(f"stripped_line: {stripped_line}")
        if stripped_line != "":
            output_lines.append(stripped_line)

    for line in html_text.splitlines():
        if 'rel="next"' in line:
            pass  # Remove the next link and button
        elif 'rel="prev"' in line:
            pass  # Remove the previous link and button
        elif 'View page source' in line:
            pass
        else:
            add_to_output(line)
    return "\n".join(output_lines)


input_path = "../docs/_build/html/flask_app_templates/flask_app_dyn_usb.html"
output_path = "../src/astutus/web/templates/transformed_dyn_usb.html"

with open(input_path, "r") as input_file:
    html_text = input_file.read()

replacements = [
    ("../_static/", "{{ static_base }}/"),
    ("../index.html", "/astutus/doc/index.html")
]

for replacement in replacements:
    old, new = replacement
    html_text = html_text.replace(old, new)

html_text = prepare_wy_menu_vertical(html_text)
html_text = prepare_breadcrumbs_navigation(html_text)
html_text = apply_line_oriented_replacements(html_text)

# TODO: Pretty print the HTML

with open(output_path, "w") as output_file:
    output_file.write(html_text)
