import os
import pathlib
import re
import urllib.parse

import sphinx.util
import astutus.util
import astutus.sphinx.dyn_pages

logger = sphinx.util.logging.getLogger(__name__)


def log_as_info(msg):
    ansi = astutus.util.AnsiSequenceStack()
    start = ansi.push
    info = '#FFFF33'  # Color our info messages as yellow
    end = ansi.end
    logger.info(f"{start(info)}{msg}{end(info)}")


# Since the Jinja2 templates may not be legal HTML5, this process will be based
# on text manipulation, rather than DOM transformation or XSLT transformations.

def indented_html_text_from_html_lines(html_lines):
    """ Attempts to indent html in a somewhat meaningful fashion.

    Presumes that the html_text provide is not indented at all.

    Needs some semi-manual patch up to take care of HTML comments.

    """
    output_chunks = []
    nesting = 0
    indent = "  "
    state = 'regular'
    for line in html_lines:
        # Remove any leading spaces that have got back in.
        line = line.strip()
        if line == '':
            continue
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


class FilePostProcessor:

    def __init__(self, input_path, docname, dyn_link_list, dyn_base, extra_head_material):
        self.input_path = input_path
        self.docname = docname
        self.dyn_link_list = dyn_link_list
        self.dyn_base = dyn_base
        self.extra_head_material = extra_head_material
        self.breadcrumb = None
        self.destination_relative_filepath = None
        self.title = None

        # For this implementation, want the dynamic links as a dictionary, not a list
        self.dyn_links = {}
        for link in self.dyn_link_list:
            # path includes leading slash when parsing urls, docnames do not, and
            # are relative to the top.  Best to just fix it up.
            key = '/' + link['docname']
            self.dyn_links[key] = link

    def set_destination_filename(self, relative_file_path):
        if relative_file_path is None:
            # Take docname, split into path and filename
            if self.docname.find('/') == -1:
                self.destination_relative_filepath = 'dyn_' + self.docname + '.html'
            else:
                path, name = self.docname.rsplit('/', 1)
                self.destination_relative_filepath = path + '/dyn_' + name + '.html'
        else:
            self.destination_relative_filepath = relative_file_path

    def execute_and_write(self, output_basepath):
        """  Process the Sphinx generated html file to produced a styled Jinja template

        The destination filepath can be automatically derived from the input
        name, or may be explicitly specified by a directive in the template rst file.

        """
        with open(self.input_path, "r") as input_file:
            html_text = input_file.read()

        self.title = astutus.sphinx.dyn_pages.read_post_processing_mark('HTML_TITLE', html_text)
        self.breadcrumb = astutus.sphinx.dyn_pages.read_post_processing_mark('BREADCRUMB', html_text)
        self.set_destination_filename(astutus.sphinx.dyn_pages.read_post_processing_mark('DESTINATION', html_text))

        html_lines = [line.strip() for line in html_text.splitlines() if line.strip() != '']
        html_lines = self.apply_line_oriented_replacements(html_lines)
        html_lines = self.fix_navigation_hrefs(html_lines)
        html_lines = self.strip_post_processing_markup(html_lines)

        html_text = indented_html_text_from_html_lines(html_lines)

        self.write_template(output_basepath, html_text)

    def apply_line_oriented_replacements(self, input_html_lines):
        output_lines = []
        for line in input_html_lines:
            if 'rel="next"' in line:
                pass  # Remove the next link and button
            elif 'rel="prev"' in line:
                pass  # Remove the previous link and button
            elif 'View page source' in line:
                pass
            elif '<![endif]-->' in line:
                output_lines.append('<!-- Indenting fix for if lt IE 9 pragma: /> /> -->')
            elif '</head>' in line:
                # Add additional head material.
                output_lines.append(self.extra_head_material)
                output_lines.append(line)
            elif astutus.sphinx.dyn_pages.post_processing_mark_found('INCLUDE', line):
                filename = astutus.sphinx.dyn_pages.read_post_processing_mark('INCLUDE', line)
                output_lines.append('{% include "' + filename + '" %}')
            elif '<link rel="search" title="Search" href="' in line:
                output_lines.append(f'<link rel="search" title="Search" href="{self.dyn_base}/search.html" />')
            elif 'action=' in line and 'search.html"' in line:
                # Handle: <form id="rtd-search-form" class="wy-form" action="../search.html" method="get">
                output_lines.append(
                    f'<form id="rtd-search-form" class="wy-form" action="{self.dyn_base}/search.html" method="get">')
            elif 'genindex.html' in line:
                output_lines.append(f'<link rel="index" title="Index" href="{self.dyn_base}/genindex.html" />')
            elif 'icon-home' in line and 'index.html' in line and '<li' not in line:
                # Handle <a href="../../index.html" class="icon icon-home"> Astutus
                idx = line.find('>')
                output_lines.append(f'<a href="{self.dyn_base}/index.html" class="icon icon-home">' + line[idx+1:])
            elif '<title>' in line:
                if self.title is not None:
                    output_lines.append(f'<title>{self.title}</title>')
                else:
                    output_lines.append(line)
            elif '../_static/' in line:
                pattern = r"\"(\.\.\/)*_static/"
                subst = f"\"{self.dyn_base}/_static/"
                modified_line = re.sub(pattern, subst, line)
                output_lines.append(modified_line)
            else:
                output_lines.append(line)
        return output_lines

    def replace_relative_href(self, line: str) -> (str, list):
        # Extract out the value of the href using regexp
        # <li class="toctree-l2"><a class="reference internal" href="raspi/dyn_raspi.html">Raspberry Pi’s</a></li>
        pattern = r'href=\"([^\"]+)\"'
        matches = re.search(pattern, line)
        href_value = matches.group(1)
        # Make a fake http url from the docname, and use that to resolve relative paths including "#"
        server = "http://fake/"
        base_url = server + self.docname + ".html"
        href_absolute_url = urllib.parse.urljoin(base_url, href_value)
        # Extract out the docname for the href, to be able to lookup the dynamic link.
        href_parts = urllib.parse.urlsplit(href_absolute_url)
        logger.debug(f'href_parts: {href_parts}')
        href_docname = href_parts[2].replace('.html', '')
        # Find the dynamic link if it has been defined.
        dyn_link = self.dyn_links.get(href_docname)
        if dyn_link is None:
            replacement_href_value = href_absolute_url.replace(server, self.dyn_base + '/')
            replacements_tags = []
            replacement_text = None
        else:
            replacement_href_value = dyn_link['replacement_url']
            replacements_tags = extract_tags_from_path(replacement_href_value)
            replacement_text = dyn_link['replacement_text']
        subst = f'href="{replacement_href_value}" orig_href="{href_value}"'
        modified_line = re.sub(pattern, subst, line)
        return modified_line, replacements_tags, replacement_text

    def wrap_in_jinja2_loop(self, line_with_angled_tags, tags, replacement_text):
        line_with_jinja2_substitutions = line_with_angled_tags
        for tag in tags:
            jinja2_variable = tag.replace('<', '{{ ').replace('>', '_item.value }}')
            line_with_jinja2_substitutions = line_with_jinja2_substitutions.replace(tag, jinja2_variable)
        loop_variable = tags[-1].replace('<', '').replace('>', '') + '_item'
        # TODO: Replace link text
        log_as_info(f'line_with_angled_tags: {line_with_angled_tags}')
        # Pattern in plain language:
        #       Find the anchor element, including all of its attributes.
        #          This assumes that attribute values are double quoted without any sort of embedded quotes.
        #          The attribute values are capture in a non-matching group.
        #       Select the link text, which cannot contain a > symbol, followed by closing html anchor tag
        # pattern_to_pick_out_link_text = r'<a\s+([\w]+\=\"[^\"]+\"\s*)*>([^>]*)</a>'
        pattern_to_pick_out_link_text = r'(<a\s+(?:[\w]+\=\"[^\"]+\"\s*)*>?)([^>]*?)(</a>?)'
        # Replace the second matching group, keeping the first and third just like that originally are.
        if replacement_text is None:
            substitution = r'\g<1>{{ ' + loop_variable + r'.link_text }}\g<3>'
        else:
            log_as_info(f"replacement_text: {replacement_text}")
            substitution = r'\g<1>' + replacement_text + r'\g<3>'
        line_with_jinja2_substitutions = re.sub(
            pattern_to_pick_out_link_text, substitution, line_with_jinja2_substitutions)
        log_as_info(f'line_with_jinja2_substitutions: {line_with_jinja2_substitutions}')
        lines = []
        # Indentation is the leading blanks in the initial line.  At this point, the assumption is that the
        # the raw HTML has been indented.
        # indentation = line_with_angled_tags.replace(line_with_angled_tags.lstrip(), '')
        # indent = '    '
        loop_list = loop_variable + '_list'
        lines.append('{% for ' + loop_variable + ' in ' + loop_list + '  %}')
        lines.append(line_with_jinja2_substitutions)
        lines.append('{% endfor  %}')
        # Handle the case where the developer has forgotten to include the loop list variable
        # in the call to the Jinja2 template:
        #   Tactic: Use the undefined loop_list variable in the template in a fashion
        #           that will trigger a server error with an easy-to-diagnose exception and traceback:
        #
        #               jinja2.exceptions.UndefinedError: 'idx_list_____must_be_defined_in_template_call' is undefined
        lines.append('{% if ' + loop_list + ' is not defined %}')
        lines.append('{{ ' + loop_list + '_____must_be_defined_in_template_call.__' + ' }}')
        lines.append('{% endif  %}')
        return lines

    def fix_navigation_hrefs(self, input_html_lines):
        ''' Fix up hrefs used in table of contents. '''

        # Use simple state machine to process the document on a line-by-line basis.
        output_lines = []
        state = 'outside_nav'
        substate = None
        li_selector = None
        for line in input_html_lines:
            if state == 'outside_nav':
                output_lines.append(line)
                # Handle side bar menu in read-the-docs theme:
                # <div class="wy-menu wy-menu-vertical" data-spy="affix" role="navigation" aria-label="main navigation">
                if 'wy-menu-vertical' in line and '<div ' in line:
                    state = 'in_nav'
                    li_selector = '<li class="toctree'
                    substate = 'wy-menu-vertical'
                # Handle embedded toc links: <div class="toctree-wrapper compound">
                elif 'toctree-wrapper' in line and '<div ' in line:
                    state = 'in_nav'
                    li_selector = '<li class="toctree'
                    substate = 'toctree-wrapper'
                # Handle bread navigation: <div role="navigation" aria-label="breadcrumbs navigation">
                elif 'aria-label="breadcrumbs navigation"' in line and '<div ' in line:
                    state = 'in_nav'
                    li_selector = '<li><a href="'
                    substate = 'breadcrumbs'
            elif state == 'in_nav':
                # Handle a link like this:
                # <li class="toctree-l2"><a class="reference internal" href="raspi/dyn_raspi.html">Raspberry Pi’s</a></li>  # noqa
                if li_selector in line:
                    # Replace relative href with an absolute href based on the doc and dynamic link modifications.
                    modified_line, tags, replacement_text = self.replace_relative_href(line)
                    if len(tags) == 0:
                        output_lines.append(modified_line)
                    else:
                        output_lines.extend(self.wrap_in_jinja2_loop(modified_line, tags, replacement_text))
                elif substate == 'breadcrumbs' and '<li>' in line:
                    if self.breadcrumb is None:
                        output_lines.append(line)
                    else:
                        output_lines.append(f'<li>{self.breadcrumb}</li>')
                elif '</div>' in line:
                    state = 'outside_nav'
                    output_lines.append(line)
                else:
                    output_lines.append(line)
        return output_lines

    def strip_post_processing_markup(self, input_html_lines):
        output_lines = []
        for line in input_html_lines:
            if not astutus.sphinx.dyn_pages.post_processing_mark_found(None, line):
                output_lines.append(line)
        return output_lines

    def write_template(self, output_basepath, html_text):
        output_path = os.path.join(output_basepath, self.destination_relative_filepath).strip()
        output_dir = os.path.dirname(output_path)
        os.makedirs(output_dir, exist_ok=True)
        with open(output_path, "w") as output_file:
            output_file.write(html_text)
        log_as_info(f"Wrote out file output_path: {output_path}")


def handle_build_finished(app, exception):
    log_as_info("Got handle_build_finished")
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
            relative_path = os.path.relpath(input_path, app.outdir)
            log_as_info(f"relative_path: {relative_path} ")
            docname, extension = relative_path.rsplit('.', 1)
            log_as_info(f"docname: {docname}")
            processor = FilePostProcessor(
                input_path,
                docname,
                app.env.astutus_dyn_link_list,
                app.config.astutus_dyn_base,
                app.config.astutus_dyn_extra_head_material)
            processor.execute_and_write(destin_dir)
