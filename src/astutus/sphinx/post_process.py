""" Handle the post processing step that converts the styled html pages to Jinja2 templates.

Implementation
--------------

At this time, the details of how the toctree directive works are not understood,
nor the process by which the html writer interacts with the theme.  Consequently,
for pragmatic reasons, instead of creating a specialized builder or writer, the insertion of
Jinja2 markup for use in the Flask application is handled as a post processing step.

The information needed for this step comes from post processing "directive markup" embedded in
Sphinx generated documents, as well as Sphinx application configuration and environment values.

The markup is described in astutus.sphinx.dyn_pages module documentation.

The resulting Jinja templates are stored in a distinct subdirectory directory within the Sphinx _build
directory.  It is expected that the astutus.sphinx extension user's build process will move the
resulting files as required by the flask application that they are developing.

"""
import os
import pathlib
import re
import urllib.parse
from typing import Dict, List, Optional, Set, Tuple  # noqa

import astutus.sphinx
import astutus.util

import sphinx.util
import sphinx.application

logger = sphinx.util.logging.getLogger(__name__)


def log_as_info(msg: str) -> None:
    """ Log at the information for this module in a distinct color for development and troubleshooting."""
    make_distinct = False
    if make_distinct:
        ansi = astutus.util.AnsiSequenceStack()
        start = ansi.push
        info = '#FFFF33'  # Color our info messages as yellow
        end = ansi.end
        logger.info(f"{start(info)}{msg}{end(info)}")
    else:
        logger.info(msg)


# Since the Jinja2 templates may not be legal HTML5, this process will be based
# on text manipulation, rather than DOM transformation or XSLT transformations.

def indented_html_text_from_html_lines(html_lines: List[str]) -> str:
    """ Attempts to indent html in a somewhat meaningful fashion.

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


def extract_tags_from_path(path: str) -> List[str]:
    r""" For something that looks like a path, extract tags indicated by angle brackets, such as <idx>. """
    tag_search_pattern = r'\/(\<\w+\>)\/'
    matches = re.search(tag_search_pattern, path)
    if matches:
        tags = list(matches.groups())
    else:
        tags = []
    return tags


class FilePostProcessor(object):
    r""" Convert a Sphinx generated \*.html file into a Jinja2 template for use with Flask.

    Any post-processing directives are read and implemented, and then the result is written
    as a reasonably-well indented Jinja2 template for use in creating dynamic HTML pages.

    The key directive to allow dynamic pages is .\. astutus_dyn_include::, which
    allows variable-driven content generation templates created by the web site
    developer to be placed into the Read-the-Docs styled page.

    Other directives are used to fix up navigation to dynamic pages using the vertical
    side bar menu generated from the toc_tree directive styled usin the Read-the-Docs theme,
    as well as the bread crumb navigation at the top of the page.


    .. currentmodule:: astutus.sphinx.post_process

    .. rubric:: Methods

    .. autosummary::

        ~FilePostProcessor.__init__
        ~FilePostProcessor.apply_line_oriented_replacements
        ~FilePostProcessor.execute_and_write
        ~FilePostProcessor.fix_navigation_hrefs
        ~FilePostProcessor.parse_li_a_href_link_line
        ~FilePostProcessor.set_destination_filename
        ~FilePostProcessor.strip_post_processing_markup
        ~FilePostProcessor.wrap_in_jinja2_loop
        ~FilePostProcessor.write_template

    """
    def __init__(
            self,
            input_path: str,
            docname: str,
            dyn_link_list: List[Dict],
            dyn_base: str,
            extra_head_material: str,
            default_template_prefix: str):

        self.input_path = input_path
        self.docname = docname
        self.dyn_link_list = dyn_link_list
        self.dyn_base = dyn_base
        self.extra_head_material = extra_head_material
        self.default_template_prefix = default_template_prefix
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

    def set_destination_filename(self, relative_file_path: str) -> None:
        """ Set the destination relative filepath based on the provided input.

        The destination relative filepat may be specified by the
        astutus_dyn_destination directive.

        If no directive is provided, the system uses a reasonable default
        destination based on the docname of the file.
        """
        if relative_file_path is None:
            # Take docname, split into path and filename
            if self.docname.find('/') == -1:
                self.destination_relative_filepath = self.default_template_prefix + self.docname + '.html'
            else:
                path, name = self.docname.rsplit('/', 1)
                self.destination_relative_filepath = path + '/' + self.default_template_prefix + name + '.html'
        else:
            self.destination_relative_filepath = relative_file_path

    def execute_and_write(self, output_basepath: str) -> None:
        """  Process the Sphinx generated html file to produced a styled Jinja template

        The phases of the processing are:

            * Read whole-file related post processing directives from the HTML text.
            * Process the file line-by-line to make appropriate and necessary modifications.
            * Write the resulting processed lines out as Jinja2 template file.

        """
        with open(self.input_path, "r") as input_file:
            html_text = input_file.read()

        self.title = astutus.sphinx.read_post_processing_directive_value('HTML_TITLE', html_text)
        self.breadcrumb = astutus.sphinx.read_post_processing_directive_value('BREADCRUMB', html_text)
        self.set_destination_filename(
            astutus.sphinx.read_post_processing_directive_value('DESTINATION', html_text))

        html_lines = [line.strip() for line in html_text.splitlines() if line.strip() != '']
        html_lines = self.apply_line_oriented_replacements(html_lines)
        html_lines = self.fix_navigation_hrefs(html_lines)
        html_lines = self.strip_post_processing_markup(html_lines)

        html_text = indented_html_text_from_html_lines(html_lines)

        self.write_template(output_basepath, html_text)

    def apply_line_oriented_replacements(self, input_html_lines: List[str]) -> List[str]:
        """ Applies line oriented replacements, but does not handle table-of-contents modifications.

        Line oriented replacements include:
            * Remove HTML navigation features not supported for dynamic pages.
            * Fixing up general links as needed to work with the Flask application.

        Table of contents fix-ups are handled in a separate method.

        """
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
                filename = astutus.sphinx.read_post_processing_directive_value('INCLUDE', line)
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

    def parse_li_a_href_link_line(self, original_li_line: str) -> Tuple[str, List[str], str]:
        """ Takes a line containing a <li><a href="...">link_text</a></li> and parses it.

        :return: li_template, replacements_tags, link_replacement_text
        """
        # Extract out the value of the href using regexp
        # <li class="toctree-l2"><a class="reference internal" href="raspi/styled_raspi.html">Raspberry Pi’s</a></li>
        pattern = r'href=\"([^\"]+)\"'
        matches = re.search(pattern, original_li_line)
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
            # Just make the href an absolute path, but otherwise don't change it.
            replacement_href_value = href_absolute_url.replace(server, self.dyn_base + '/')
            replacements_tags = []
            # Keep the same link text in this this case.
            link_replacement_text = None
        else:
            # If a dyn_link is found, the url for the href is replaced, as well as the link text.
            # These may contain tags to indicate variable aspects of the href and link text.
            replacement_href_value = dyn_link['replacement_url']
            replacements_tags = extract_tags_from_path(replacement_href_value)
            link_replacement_text = dyn_link['replacement_text']
        subst = f'href="{replacement_href_value}" orig_href="{href_value}"'
        li_template = re.sub(pattern, subst, original_li_line)
        # At this juncture, the variabls are still marked with angled brackets, rather than
        # Jinja2 braces.
        return li_template, replacements_tags, link_replacement_text

    def wrap_in_jinja2_loop(self, list_item_line_with_angled_tags: str, tags: List[str], link_text: str) -> List[str]:
        """ Take a list item wrapped anchor and returns lines that implement with a Jinja2 loop around it.

        The Flask application will provide data when rendering the template
        to provide a menu with a dynamic number of entries.
        """
        line_with_jinja2_substitutions = list_item_line_with_angled_tags
        for tag in tags:
            jinja2_variable = tag.replace('<', '{{ ').replace('>', '_item.value }}')
            line_with_jinja2_substitutions = line_with_jinja2_substitutions.replace(tag, jinja2_variable)
        loop_variable = tags[-1].replace('<', '').replace('>', '') + '_item'
        log_as_info(f'line_with_angled_tags: {list_item_line_with_angled_tags}')
        # Pattern in plain language:
        #       Find the anchor element, including all of its attributes.
        #          This assumes that attribute values are double quoted without any sort of embedded quotes.
        #          The attribute values are capture in a non-matching group.
        #       Select the link text, which cannot contain a > symbol, followed by closing html anchor tag
        # pattern_to_pick_out_link_text = r'<a\s+([\w]+\=\"[^\"]+\"\s*)*>([^>]*)</a>'
        pattern_to_pick_out_link_text = r'(<a\s+(?:[\w]+\=\"[^\"]+\"\s*)*>?)([^>]*?)(</a>?)'
        # Replace the second matching group, keeping the first and third just like that originally are.
        if link_text is None:
            substitution = r'\g<1>{{ ' + loop_variable + r'.link_text }}\g<3>'
        else:
            log_as_info(f"link_text: {link_text}")
            substitution = r'\g<1>' + link_text + r'\g<3>'
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

    def fix_navigation_hrefs(self, input_html_lines: List[str]) -> List[str]:
        ''' Fix up hrefs used in table of contents.

        The original hrefs do not necessarily have the right nesting for routes used in the Flask application.
        They also may need to be converted to elements that represent variable parts of the route, such as
        used with RESTful web applications.  The variable parts of the route are identified by angle brackets
        similar to that used in Flask routing in the replacement dynamic links.  These are expanded into
        Jinja2 variables and loops.

        '''
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
                # <li class="toctree-l2"><a class="reference internal" href="raspi/styled_index.html">Raspberry Pi’s</a></li>  # noqa
                if li_selector in line:
                    # Replace relative href with an absolute href based on the doc and dynamic link modifications.
                    li_template, tags, replacement_link_text = self.parse_li_a_href_link_line(line)
                    if len(tags) == 0:
                        output_lines.append(li_template)
                    else:
                        output_lines.extend(self.wrap_in_jinja2_loop(li_template, tags, replacement_link_text))
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

    def strip_post_processing_markup(self, input_html_lines: List[str]) -> List[str]:
        """ Remove any post processing markup.  This markup should not be in the template."""
        output_lines = []
        for line in input_html_lines:
            if not astutus.sphinx.dyn_pages.post_processing_mark_found(None, line):
                output_lines.append(line)
        return output_lines

    def write_template(self, output_basepath: str, html_text: str) -> None:
        """ Write the processed template to a location relative to the output base path.

        The actual location is derived from the output base path combined with a file-specific
        relative filepath.
        """
        output_path = os.path.join(output_basepath, self.destination_relative_filepath).strip()
        output_dir = os.path.dirname(output_path)
        os.makedirs(output_dir, exist_ok=True)
        with open(output_path, "w") as output_file:
            output_file.write(html_text)
        log_as_info(f"Wrote out file output_path: {output_path}")


def handle_build_finished(app: sphinx.application.Sphinx, exception) -> None:
    r""" Post-process all generated HTML files that will be used as styled Jinja2 templates.

    This method is triggered by the 'build-finished' event.  It connects the Sphinx application
    to the post processing class astutus.sphinx.post_process.FilePostProcessor.

    At this time, the source styled \*.html are found by examining the contents within the
    directory identified by the astutus_dyn_pages_dir configuration variable.

    The files are placed in a location identified by the astutus_dyn_styled_templates_path
    configuration variable.
    """
    # TODO: Replace walking through the directory with keeping a list as files are identified.

    log_as_info("Got handle_build_finished")
    # logger.warn(f"app: {dir(app)}")
    log_as_info(f"outdir: {app.outdir}")
    source_dir = pathlib.Path(app.outdir) / app.config.astutus_dyn_pages_dir
    log_as_info(f"source_dir: {source_dir}")
    destin_dir = pathlib.Path(app.outdir).parent / app.config.astutus_dyn_styled_templates_path
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
                app.config.astutus_dyn_extra_head_material,
                app.config.astutus_dyn_default_template_prefix)
            processor.execute_and_write(destin_dir)
