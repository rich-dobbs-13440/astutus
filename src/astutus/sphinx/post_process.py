import os
import pathlib
import re
import urllib.parse

import sphinx.util
import astutus.util

logger = sphinx.util.logging.getLogger(__name__)


def log_as_info(msg):
    ansi = astutus.util.AnsiSequenceStack()
    start = ansi.push
    info = '#FFFF33'  # Color our info messages as yellow
    end = ansi.end
    logger.info(f"{start(info)}{msg}{end(info)}")


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
        # Pretty print html at the end.
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


def extract_tags_from_path(path):
    tag_search_pattern = r'\/(\<\w+\>)\/'
    matches = re.search(tag_search_pattern, path)
    if matches:
        tags = list(matches.groups())
    else:
        tags = []
    return tags


def replace_relative_href(line: str, docname: str, dyn_links: dict, dyn_base: str) -> (str, list):
    # Extract out the value of the href using regexp
    # <li class="toctree-l2"><a class="reference internal" href="raspi/dyn_raspi.html">Raspberry Pi’s</a></li>
    pattern = r'href=\"([^\"]+)\"'
    matches = re.search(pattern, line)
    href_value = matches.group(1)
    # Make a fake http url from the docname, and use that to resolve relative paths including "#"
    server = "http://fake/"
    base_url = server + docname + ".html"
    href_absolute_url = urllib.parse.urljoin(base_url, href_value)
    # Extract out the docname for the href, to be able to lookup the dynamic link.
    href_parts = urllib.parse.urlsplit(href_absolute_url)
    logger.debug(f'href_parts: {href_parts}')
    href_docname = href_parts[2].replace('.html', '')
    # Find the dynamic link if it has been defined.
    replacement_href_value = dyn_links.get(href_docname)
    if replacement_href_value is None:
        replacement_href_value = href_absolute_url.replace(server, dyn_base + '/')
        replacements_tags = []
    else:
        replacements_tags = extract_tags_from_path(replacement_href_value)
    subst = f'href="{replacement_href_value}" orig_href="{href_value}"'
    modified_line = re.sub(pattern, subst, line)
    return modified_line, replacements_tags


def wrap_in_jinja2_loop(line_with_angled_tags, tags):

    line_with_jinja2_substitutions = line_with_angled_tags
    for tag in tags:
        jinja2_variable = tag.replace('<', '{{ ').replace('>', '_item.value }}')
        line_with_jinja2_substitutions = line_with_jinja2_substitutions.replace(tag, jinja2_variable)
    loop_variable = tags[-1].replace('<', '').replace('>', '') + '_item'
    # TODO: Replace link text
    logger.warning(f'line_with_angled_tags: {line_with_angled_tags}')
    # Pattern in plain language:
    #       Find the anchor element, including all of its attributes.
    #          This assumes that attribute values are double quoted without any sort of embedded quotes.
    #          The attribute values are capture in a non-matching group.
    #       Select the link text, which cannot contain a > symbol, followed by closing html anchor tag
    # pattern_to_pick_out_link_text = r'<a\s+([\w]+\=\"[^\"]+\"\s*)*>([^>]*)</a>'
    pattern_to_pick_out_link_text = r'(<a\s+(?:[\w]+\=\"[^\"]+\"\s*)*>?)([^>]*?)(</a>?)'
    # Replace the second matching group, keeping the first and third just like that originally are.
    substitution = r'\g<1>{{ ' + loop_variable + r'.link_text }}\g<3>'
    line_with_jinja2_substitutions = re.sub(pattern_to_pick_out_link_text, substitution, line_with_jinja2_substitutions)
    logger.warning(f'line_with_jinja2_substitutions: {line_with_jinja2_substitutions}')
    lines = []
    # Indentation is the leading blanks in the initial line.  At this point, the assumption is that the
    # the raw HTML has been indented.
    indentation = line_with_angled_tags.replace(line_with_angled_tags.lstrip(), '')
    indent = '    '
    loop_list = loop_variable + '_list'
    lines.append(indentation + '{% for ' + loop_variable + ' in ' + loop_list + '  %}')
    lines.append(indent + line_with_jinja2_substitutions)
    lines.append(indentation + '{% endfor  %}')
    # Handle the case where the developer has forgotten to include the loop list variable
    # in the call to the Jinja2 template:
    #   Tactic: Use the undefined loop_list variable in the template in a fashion
    #           that will trigger a server error with an easy-to-diagnose exception and traceback:
    #
    #               jinja2.exceptions.UndefinedError: 'idx_list_____must_be_defined_in_template_call' is undefined
    lines.append(indentation + '{% if ' + loop_list + ' is not defined %}')
    lines.append(indentation + indent + '{{ ' + loop_list + '_____must_be_defined_in_template_call.__' + ' }}')
    lines.append(indentation + '{% endif  %}')
    return lines


def fix_navigation_hrefs(html_text, docname, dyn_link_list, dyn_base):
    ''' Fix up hrefs used in table of contents. '''
    # For this implementation, want the dynamic links as a dictionary, not a list
    dyn_links = {}
    for link in dyn_link_list:
        # path includes leading slash when parsing urls, docnames do not, and
        # are relative to the top.  Best to just fix it up.
        key = '/' + link['docname']
        dyn_links[key] = link['replacement_url']
    # Use simple state machine to process the document on a line-by-line basis.
    output_chunks = []
    state = 'outside_nav'
    li_selector = None
    for line in html_text.splitlines():
        if state == 'outside_nav':
            output_chunks.append(line)
            # Handle side bar menu in read-the-docs theme:
            # <div class="wy-menu wy-menu-vertical" data-spy="affix" role="navigation" aria-label="main navigation">
            if 'wy-menu-vertical' in line and '<div ' in line:
                state = 'in_nav'
                li_selector = '<li class="toctree'
            # Handle embedded toc links: <div class="toctree-wrapper compound">
            elif 'toctree-wrapper' in line and '<div ' in line:
                state = 'in_nav'
                li_selector = '<li class="toctree'
            # Handle bread navigation: <div role="navigation" aria-label="breadcrumbs navigation">
            elif 'aria-label="breadcrumbs navigation"' in line and '<div ' in line:
                state = 'in_nav'
                li_selector = '<li><a href="'
        elif state == 'in_nav':
            # Handle a link like this:
            # <li class="toctree-l2"><a class="reference internal" href="raspi/dyn_raspi.html">Raspberry Pi’s</a></li>
            if li_selector in line:
                # Replace relative href with an absolute href based on the doc and dynamic link modifications.
                modified_line, tags = replace_relative_href(line, docname, dyn_links, dyn_base)
                if len(tags) == 0:
                    output_chunks.append(modified_line)
                else:
                    output_chunks.extend(wrap_in_jinja2_loop(modified_line, tags))
            elif '</div>' in line:
                state = 'outside_nav'
                output_chunks.append(line)
            else:
                output_chunks.append(line)
    return "\n".join(output_chunks)


def process_dynamic_template(input_path, output_basepath, docname, dyn_link_list, dyn_base):
    """  Process the Sphinx generated html file to produced a styled Jinja template

    The destination filepath can be automatically derived from the input
    name, or may be explicitly specified by a directive in the template rst file.

    """
    with open(input_path, "r") as input_file:
        html_text = input_file.read()

    # Leave the original breadcrumbs in place, in prep for automated fix up.
    # html_text = prepare_breadcrumbs_navigation(html_text)
    html_text = apply_line_oriented_replacements(html_text)
    html_text = indent_html_text(html_text)
    html_text = fix_navigation_hrefs(html_text, docname, dyn_link_list, dyn_base)

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
    output_path = os.path.join(output_basepath, output_relative_filepath).strip()

    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    with open(output_path, "w") as output_file:
        output_file.write(html_text)
    log_as_info(f"Wrote out file output_path: {output_path}")


def post_process(app, exception):
    log_as_info("Got to post process")
    # logger.warn(f"app: {dir(app)}")
    log_as_info(f"outdir: {app.outdir}")
    source_dir = pathlib.Path(app.outdir) / app.config.astutus_dyn_pages_dir
    log_as_info(f"source_dir: {source_dir}")
    destin_dir = pathlib.Path(app.outdir).parent / app.config.astutus_dynamic_templates
    os.makedirs(destin_dir)
    log_as_info(f"destin_dir: {destin_dir}")

    # log_as_info(f"app.env.tocs: {app.env.tocs}")
    log_as_info(f"app.env.astutus_dyn_link_list: {app.env.astutus_dyn_link_list}")

    for dirpath, dirnames, filenames in os.walk(source_dir):
        log_as_info(f"dirpath: {dirpath}")
        for filename in filenames:
            input_path = os.path.join(dirpath, filename)
            log_as_info(f"input_path: {input_path}")
#
            relative_path = os.path.relpath(input_path, app.outdir)
            log_as_info(f"relative_path: {relative_path} ")
            docname, extension = relative_path.rsplit('.', 1)
            log_as_info(f"docname: {docname}")
            # log_as_info(f"toc: {app.env.tocs[docname]}")
            process_dynamic_template(
                input_path, destin_dir, docname, app.env.astutus_dyn_link_list, app.config.astutus_dyn_base)
            # logger.info(f"examine_toctree env.tocs.get: {app.env.tocs.get(fromdocname)}")
