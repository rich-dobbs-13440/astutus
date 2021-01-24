import astutus
import astutus.sphinx.post_process
import astutus.util
import docutils

import sphinx.addnodes
import sphinx.util
from sphinx.util.docutils import SphinxDirective

logger = sphinx.util.logging.getLogger(__name__)


def log_as_info(msg):
    # Kludgy to use a closure to get colored logging specific to our code,
    # but easier than modifying logger format.
    ansi = astutus.util.AnsiSequenceStack()
    start = ansi.push
    info = '#FFA500'  # Color our info messages as orange
    end = ansi.end
    logger.info(f"{start(info)}{msg}{end(info)}")


def visit_generic_node(self, node):
    logger.debug(f"Visiting node: {node} ")


def depart_generic_node(self, node):
    logger.debug(f"Departing node: {node} ")


class LinkNode(docutils.nodes.General, docutils.nodes.Element):
    pass


class LinkDirective(SphinxDirective):

    required_arguments = 1
    optional_arguments = 1
    final_argument_whitespace = True

    def run(self):
        logger.debug("LinkDirective.run")

        if not hasattr(self.env, 'astutus_dyn_link_list'):
            self.env.astutus_dyn_link_list = []

        # Some inconsistency in whether the argument will come back with
        # quotes or not.  Need to figure out how to use converters and use path as type.
        replacement_url = self.arguments[0].replace('"', '').replace("'", '')
        if len(self.arguments) > 1:
            replacement_text = self.arguments[1]
        else:
            replacement_text = None

        self.env.astutus_dyn_link_list.append({
            'docname': self.env.docname,
            'replacement_url': replacement_url,
            'replacement_text': replacement_text,
        })
        return []


class BreadCrumbNode(docutils.nodes.General, docutils.nodes.Element):
    pass


class BreadCrumbDirective(SphinxDirective):
    required_arguments = 1
    final_argument_whitespace = True

    def run(self):
        log_as_info("DynBreadCrumbDirective.run")
        node = BreadCrumbNode('')
        jinja2_value = self.arguments[0].replace('<', '{{ ').replace('>', ' }}')
        node.markup = f'\n««BREADCRUMB»» {jinja2_value} ««END_BREADCRUMB»»\n'
        return [node]

    @staticmethod
    def handle_insert_markup(app, doctree, fromdocname):
        for node in doctree.traverse(BreadCrumbNode):
            replacement_node = docutils.nodes.raw('', node.markup, format='html')
            node.replace_self(replacement_node)


class BookmarkNode(docutils.nodes.General, docutils.nodes.Element):
    pass


class BookmarkDirective(SphinxDirective):

    required_arguments = 1
    final_argument_whitespace = True

    def run(self):
        log_as_info("\nBookmarkDirective.run")
        node = BookmarkNode('')
        jinja2_value = self.arguments[0].replace('<', '{{ ').replace('>', ' }}')
        node.markup = f'\n««HTML_TITLE»» {jinja2_value} ««END_HTML_TITLE»»\n'
        return [node]

    @staticmethod
    def handle_insert_markup(app, doctree, fromdocname):
        """ Handle title modification by inserting post processing markup. """
        for node in doctree.traverse(BookmarkNode):
            replacement_node = docutils.nodes.raw('', node.markup, format='html')
            node.replace_self(replacement_node)


class IncludeNode(docutils.nodes.General, docutils.nodes.Element):
    pass


class IncludeDirective(SphinxDirective):

    required_arguments = 1

    def run(self):
        log_as_info("\nIncludeDirective.run")
        node = IncludeNode('')
        node.value = self.arguments[0]
        return [node]

    @staticmethod
    def handle_insert_markup(app, doctree, fromdocname):
        """ Handle include modification by inserting post processing markup. """
        for node in doctree.traverse(IncludeNode):
            logger.debug("BookmarkDirective.handle_title_modification")
            jinja2_value = node.value.replace('<', '{{ ').replace('>', ' }}')
            replacement = f'\n««INCLUDE»» {jinja2_value} ««END_INCLUDE»»\n'
            replacement_node = docutils.nodes.raw('', replacement, format='html')
            node.replace_self(replacement_node)


class DestinationNode(docutils.nodes.General, docutils.nodes.Element):
    pass


class DestinationDirective(SphinxDirective):

    required_arguments = 1

    def run(self):
        log_as_info("\nDestinationDirective.run")
        node = DestinationNode('')
        node.value = self.arguments[0]
        return [node]

    @staticmethod
    def handle_insert_markup(app, doctree, fromdocname):
        """ Handle title modification by inserting post processing markup. """
        for node in doctree.traverse(DestinationNode):
            log_as_info("\nDestinationDirective.handle_insert_markup")
            jinja2_value = node.value.replace('<', '{{ ').replace('>', ' }}')
            replacement = f'\n««DESTINATION»» {jinja2_value} ««END_DESTINATION»»\n'
            replacement_node = docutils.nodes.raw('', replacement, format='html')
            node.replace_self(replacement_node)


class ToggleNoteNode(docutils.nodes.note):
    pass


class ToggleNoteDirective(SphinxDirective):

    has_content = True
    optional_arguments = 2
    final_argument_whitespace = True

    def run(self):
        log_as_info("\nToggleNoteDirective.run")
        if len(self.arguments) > 0:
            toggle_start = self.arguments[0]
        else:
            toggle_start = 'expanded'

        if len(self.arguments) > 1:
            extra_title_text = self.arguments[1]
        else:
            extra_title_text = ''

        # node = ToggleNoteNode('')

        # node += docutils.nodes.raw('', '\n'.join(self.content), format='html')
        # return [node]
        self.assert_has_content()
        text = '\n'.join(self.content)
        # Create the admonition node, to be populated by `nested_parse`.
        node = ToggleNoteNode(rawsource=text)
        if toggle_start == 'expanded':
            node.collapsed = False
        elif toggle_start == 'collapsed':
            node.collapsed = True
        else:
            raise ValueError("For the ToggleNoteDirective, expecting the first argument to be collapsed or expanded")
        node.extra_title_text = extra_title_text
        # Parse the directive contents.
        self.state.nested_parse(self.content, self.content_offset, node)
        return [node]

    @staticmethod
    def handle_insert_markup(app, doctree, fromdocname):
        logger.debug(f"ToggleNoteDirective.handle_insert_markup  fromdocname: {fromdocname}")
        idx = 0
        for node in doctree.traverse(ToggleNoteNode):
            log_as_info("\nToggleNoteDirective.handle_insert_markup")
            children = node.children
            container = docutils.nodes.container()
            container['classes'] += ['astutus-toggle', 'admonition', 'note']
            checkbox_id = f'astutus-toggle-{idx}'
            idx += 1
            if node.collapsed:
                checked_value = 'checked'
            else:
                checked_value = ''
            container += docutils.nodes.raw(
                '', f'<input type="checkbox" id="{checkbox_id}" {checked_value} />\n', format='html')
            title_text = f'Note: {node.extra_title_text}'
            title_paragraph_text = f'<p class="astutus-toggle-symbol admonition-title">{title_text}</p>'
            container += docutils.nodes.raw(
                '', f'<label for="{checkbox_id}">{title_paragraph_text}</label>\n', format='html')
            toggled_container = docutils.nodes.container()
            toggled_container['classes'] += ["astutus-toggle"]
            toggled_container += docutils.nodes.Text('\n')
            toggled_container += children
            container += toggled_container
            node.replace_self(container)


def config_inited(app, config):
    """ Check that the required configuration variables have been initialized"""
    log_as_info('Got to config_inited')
    if app.config.astutus_docs_base == '':
        raise ValueError("You must define 'astutus_docs_base' if you are using Astutus capabilities.")
    if app.config.astutus_dyn_base == "":
        raise ValueError("You must define 'astutus_dyn_base' if you are using Astutus capabilities.")
    if app.config.astutus_dyn_pages_dir == "":
        raise ValueError("You must define 'astutus_dyn_pages_dir' if you are using Astutus capabilities.")

    # For now, keep the original source files in the docs directory, but
    # longer term, they should be installed there when the extension
    # is installed.  Haven't figured out a way to selectively
    # add this only to the files where the directives are used.
    app.add_css_file('astutus_dynamic_sphinx_pages.css')


def setup(app):

    app.add_config_value('astutus_docs_base', '', 'html')
    app.add_config_value('astutus_dyn_base', '', 'html')
    app.add_config_value('astutus_dyn_pages_dir', 'astutus_dyn_pages', 'html')
    app.add_config_value('astutus_dynamic_templates', 'astutus_dynamic_templates', 'html')

    app.add_node(
        LinkNode,
        html=(visit_generic_node, depart_generic_node)
    )
    app.add_node(
        BreadCrumbNode,
        html=(visit_generic_node, depart_generic_node)
    )
    app.add_node(
        BookmarkNode,
        html=(visit_generic_node, depart_generic_node)
    )
    app.add_node(
        ToggleNoteNode,
        html=(visit_generic_node, depart_generic_node)
    )

    app.add_directive('astutus_dyn_link', LinkDirective)

    app.add_directive('astutus_dyn_breadcrumb', BreadCrumbDirective)
    app.connect('doctree-resolved', BreadCrumbDirective.handle_insert_markup)

    app.add_directive('astutus_dyn_bookmark', BookmarkDirective)
    app.connect('doctree-resolved', BookmarkDirective.handle_insert_markup)

    app.add_directive('astutus_dyn_include', IncludeDirective)
    app.connect('doctree-resolved', IncludeDirective.handle_insert_markup)

    app.add_directive('astutus_dyn_destination', DestinationDirective)
    app.connect('doctree-resolved', DestinationDirective.handle_insert_markup)

    app.add_directive('astutus_toggle_note', ToggleNoteDirective)
    app.connect('doctree-resolved', ToggleNoteDirective.handle_insert_markup)

    app.connect('config-inited', config_inited)
    app.connect('build-finished', astutus.sphinx.post_process.post_process)

    return {
        'version': astutus.__version__,
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
