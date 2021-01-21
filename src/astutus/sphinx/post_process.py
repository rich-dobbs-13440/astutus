import os
import pathlib
import re

import sphinx.util

logger = sphinx.util.logging.getLogger(__name__)


# Since the Jinja2 templates may not be legal HTML5, this process will be based
# on text manipulation, rather than DOM transformation or XSLT transformations.

def prepare_breadcrumbs_navigation(html_text):
    """ Strip out existing breadcrumb navigation section and replace it with Jinja2 variable.

    The breadcrumb navigation section is probably specific to the Sphinx Read the Docs format.
    """
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
                add_to_output('{{ breadcrumbs_list_items | safe }}')
                add_to_output('</ul>')
            elif '/<ul>' in line:
                pass
                # add_to_output(line)
            elif '<hr/>' in line:
                # add_to_output(line)
                pass
            elif '</div>' in line:
                add_to_output(line)
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
        elif '<![endif]-->' in line:
            add_to_output('<!-- Indenting fix for if lt IE 9 pragma: /> /> -->')
        elif '</head>' in line:
            # Add additional head material
            add_to_output('<link rel="apple-touch-icon" sizes="180x180" href="/static/apple-touch-icon.png"/>')
            add_to_output('<link rel="icon" type="image/png" sizes="32x32" href="/static/favicon-32x32.png"/>')
            add_to_output('<link rel="icon" type="image/png" sizes="16x16" href="/static/favicon-16x16.png"/>')
            add_to_output('<link rel="manifest" href="/static/site.webmanifest"/>')
            add_to_output('<link rel="stylesheet" href="/static/app.css" />')

            # Should this be hosted locally to avoid issues with Raspi not connected to internet?
            # cdn = '//cdnjs.cloudflare.com/ajax/libs'
            # add_to_output(f'<link rel="stylesheet" href="{cdn}/jstree/3.3.8/themes/default/style.min.css" />')
            # add_to_output(f'<script src="{cdn}/jstree/3.3.8/jstree.min.js"></script>')
            add_to_output('<script src="/static/app.js"></script>')
            add_to_output(line)
        elif '««INCLUDE»»' in line:
            pattern = r"««INCLUDE»»\s*([\w,\.,/]+)\s*««END_INCLUDE»»"
            matches = re.search(pattern, line)
            if not matches:
                assert False, line
            filename = matches.group(1)
            add_to_output('{% include "' + filename + '" %}')
        elif '««DESTINATION»»' in line:
            pattern = r"««DESTINATION»»\s*([\w,\.,/]+)\s*««END_DESTINATION»»"
            matches = re.search(pattern, line)
            if not matches:
                assert False, line
            filename = matches.group(1)
            # Send back the discovered output file in the regular output
            # return channels as an HTML comment.
            add_to_output(f'<!-- DYNAMIC_TEMPLATE_OUTPUT_FILE {filename} -->')
        elif '<link rel="search" title="Search" href="../search.html" />' in line:
            # src/astutus/web/static/_docs/search.html
            add_to_output('<link rel="search" title="Search" href="/static/_docs/search.html" />')
        elif 'action="../search.html"' in line:
            # Handle: <form id="rtd-search-form" class="wy-form" action="../search.html" method="get">
            add_to_output(line.replace('action="../search.html"', 'action="/static/_docs/search.html"'))
        elif '<title>' in line:
            # This pattern matches every thing between markers.
            # Whitespace needs to be stripped out to make a good title.
            pattern = r'««HTML_TITLE»»([^«]+)««END_HTML_TITLE»»'
            matches = re.search(pattern, html_text)
            if matches:
                title_text = matches.group(1).strip()
                add_to_output(f'<title>{title_text}</title>')
            else:
                add_to_output(line)
        elif '««HTML_TITLE»»' in line:
            pass
        elif '../_static/' in line:
            pattern = r"\"(\.\.\/)*_static/"
            subst = "\"/astutus/_static/"
            modified_line = re.sub(pattern, subst, line)
            add_to_output(modified_line)
        else:
            add_to_output(line)
    return "\n".join(output_lines)


def indent_html_text(html_text):
    """ Attempts to indent html in a somewhat meaningful fashion.

    Presumes that the html_text provide is not indented at all.

    Needs some semi-manual patch up to take care of HTML comments.

    """
    # Note:  Doesn't handle embedded javascript.  Move that to a Jinja2 template?
    # Or app.js?  Or make this function smart for indentation of Javascript?
    output_chunks = []
    nesting = 0
    indent = "  "
    state = 'regular'
    for line in html_text.splitlines():
        # In case head is messed up, get things back to sanity.
        if '<body' in line:
            nesting = 1
        if nesting > 0:
            output_chunks.append(indent * nesting)
        output_chunks.append(line)
        output_chunks.append("\n")
        if state == 'regular':
            nesting += line.count("<")
            nesting -= line.count("</") * 2
            nesting -= line.count("/>")
        if line == '<script>':
            state = 'in_script'
        elif line == '</script>':
            nesting -= 1
            state = 'regular'
        if '<!DOCTYPE html>' in line:
            nesting = 0
    return "".join(output_chunks)


def process_dynamic_template(input_path, output_basepath):
    """  Process the Sphinx generated html file to produced a styled Jinja template

    The destination filepath can be automatically derived from the input
    name, or may be explicitly specified by a directive in the template rst file.

    """
    with open(input_path, "r") as input_file:
        html_text = input_file.read()

    html_text = prepare_breadcrumbs_navigation(html_text)
    html_text = apply_line_oriented_replacements(html_text)
    html_text = indent_html_text(html_text)

    if '<!-- DYNAMIC_TEMPLATE_OUTPUT_FILE' not in html_text:
        # skip this file
        return

    # There has been a directive in the template file to override the
    # autogenerated template destination.  This is probably to allow
    # placing the template in a subject specific folder with the
    # templates directory.
    pattern = r'\<!--\s+DYNAMIC_TEMPLATE_OUTPUT_FILE\s+([\w,\/,\.]+)\s-->'
    matches = re.search(pattern, html_text)
    output_relative_filepath = matches.group(1)
    output_path = os.path.join(output_basepath, output_relative_filepath)

    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    with open(output_path, "w") as output_file:
        output_file.write(html_text)
    print(f"INFO: Wrote out file output_path: {output_path}\n")


def post_process(app, exception):
    logger.warn("Got to post process")
    # logger.warn(f"app: {dir(app)}")
    logger.warn(f"outdir: {app.outdir}")
    source_dir = pathlib.Path(app.outdir) / app.config.astutus_dyn_pages_dir
    logger.warn(f"source_dir: {source_dir}")
    destin_dir = pathlib.Path(app.outdir).parent / app.config.astutus_dynamic_templates
    os.makedirs(destin_dir)
    logger.warn(f"destin_dir: {destin_dir}")

    for dirpath, dirnames, filenames in os.walk(source_dir):
        print(f"dirpath: {dirpath}\n")
        for filename in filenames:
            input_path = os.path.join(dirpath, filename)
            print(f"input_path: {input_path}")
            process_dynamic_template(input_path, destin_dir)
