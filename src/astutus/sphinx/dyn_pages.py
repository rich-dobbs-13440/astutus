import sphinx.util


import docutils
import astutus
import astutus.sphinx.post_process
from sphinx.util.docutils import SphinxDirective


logger = sphinx.util.logging.getLogger(__name__)


class DynLinkNode(docutils.nodes.General, docutils.nodes.Element):
    pass


def visit_dyn_link_node(self, node):
    pass


def depart_dyn_link_node(self, node):
    pass


def visit_generic_node(self, node):
    logger.debug(f"Visiting node: {node} ")


def depart_generic_node(self, node):
    logger.debug(f"Departing node: {node} ")


class ScriptNode(docutils.nodes.General, docutils.nodes.Element):
    pass


class DynBookmarkNode(docutils.nodes.General, docutils.nodes.Element):
    pass


class DynIncludeNode(docutils.nodes.General, docutils.nodes.Element):
    pass


class DynDestinationNode(docutils.nodes.General, docutils.nodes.Element):
    pass


class DynLinksInMenuListNode(docutils.nodes.General, docutils.nodes.Element):

    def set_item_list_name(self, item_list_name):
        self.item_list_name = item_list_name

    def set_item_pattern(self, pattern):
        self.pattern = pattern

    def set_replace_replace_inner_html(self, replace_inner_html):
        if replace_inner_html is None:
            self.replace_inner_html = True
        elif replace_inner_html == "false":
            self.replace_inner_html = False
        elif replace_inner_html == "true":
            self.replace_inner_html = True
        else:
            raise ValueError("Expecting 'true' or 'false'")

    def replace_node_content(self, dyn_link_list, docs_base, dyn_base):
        content = []
        script = ScriptNode()
        script += docutils.nodes.raw('', "\n<script>\n", format='html')
        dyn_links_json = self.dyn_links_as_json(dyn_link_list)
        script += docutils.nodes.raw('', f"const astutusDocname = '{self.docname}';\n", format='html')
        script += docutils.nodes.raw('', f"const astutusDynLinkList = \n{dyn_links_json};\n", format='html')
        script += docutils.nodes.raw('', f"const astutusDocsBase = '{docs_base}';\n", format='html')
        script += docutils.nodes.raw('', f"const astutusDynBase = '{dyn_base}';\n", format='html')
        script += docutils.nodes.raw('', "astutusDynPage.applyDynamicLinks(", format='html')
        script += docutils.nodes.raw('', "astutusDocname", format='html')
        script += docutils.nodes.raw('', ", astutusDynLinkList", format='html')
        script += docutils.nodes.raw('', ", astutusDocsBase", format='html')
        script += docutils.nodes.raw('', ", astutusDynBase", format='html')
        if self.item_list_name is not None:
            script += docutils.nodes.raw('', f", {self.item_list_name}", format='html')
            if self.pattern is not None:
                script += docutils.nodes.raw('', f", '{self.pattern}'", format='html')
                if self.replace_inner_html is False:
                    script += docutils.nodes.raw('', ", false", format='html')
        script += docutils.nodes.raw('', ");\n", format='html')
        script += docutils.nodes.raw('', "</script>\n", format='html')
        content.append(script)
        self.replace_self(content)

    @staticmethod
    def dyn_links_as_json(dyn_link_list):
        items = []
        # Don't want trailing comma in Javascript, so use join to make list
        for link in dyn_link_list:
            # Note: docname is a relative path without a file extension. So something like this:
            # {'docname': 'flask_app_templates/flask_app_dyn_astutus', 'replacement_url': '"/astutus"'}
            # For this to work from Sphinx configuration directory and other folders, must
            # retain only file name, and that will need to be unique.
            if link['docname'].find('/') >= 0:
                _, basename = link['docname'].rsplit('/', 1)
            else:
                basename = link['docname']
            search_snippet = f"'search_pattern': '{basename}.html'"
            replacement_url_snippet = f"'replacement_url':'{link['replacement_url']}'"
            item = "    {" + search_snippet + ", " + replacement_url_snippet + "}"
            items.append(item)
            search_snippet_link = f"'search_pattern': '{basename}#'"
            item = "    {" + search_snippet_link + ", " + replacement_url_snippet + "}"
            items.append(item)
        items_text = ',\n'.join(items)
        return '[' + items_text + ']'


class DynLinksInMenuDirective(SphinxDirective):

    optional_arguments = 3

    def run(self):
        node = DynLinksInMenuListNode('')
        node.docname = self.env.docname
        if len(self.arguments) > 0:
            item_list_name = self.arguments[0]
        else:
            item_list_name = None
        node.set_item_list_name(item_list_name)
        if len(self.arguments) > 1:
            item_pattern = self.arguments[1]
        else:
            item_pattern = None
        node.set_item_pattern(item_pattern)
        if len(self.arguments) > 2:
            replace_inner_html = self.arguments[2]
        else:
            replace_inner_html = None
        node.set_replace_replace_inner_html(replace_inner_html)
        return [node]

    @staticmethod
    def generate_menu_modification(app, doctree, fromdocname):
        """ Here the data needed for modifying the menu dynamically is added to the page.

        Rather than attempting to change the structure of the menus during document
        generation, the data needed for that task is dumped into a <script> block
        in the body of the page.  Then the menu modification Javascript function
        is called to modify the hrefs in the menus as the page loads.

        This code modifies the menus generated for the toctree directive, at least
        when used with the Read-the-Docs theme.  At this time it is not clear
        whether the same menus are used in other themes.

        The actual Javascript code is included in the head of the page
        using the standard html_js_files configuration variable.
        """
        # TODO: Once this is working again, move the addition of the file
        # to the setup function below.
        if app.config.astutus_docs_base == '':
            raise ValueError("You must define 'astutus_docs_base' if you are using Astutus capabilities.")
        if app.config.astutus_dyn_base == "":
            raise ValueError("You must define 'astutus_dyn_base' if you are using Astutus capabilities.")
        env = app.builder.env
        if not hasattr(env, 'dyn_link_list'):
            env.dyn_link_list = []
        for node in doctree.traverse(DynLinksInMenuListNode):
            logger.debug("Got to generate_menu_modification")
            node.replace_node_content(env.dyn_link_list, app.config.astutus_docs_base, app.config.astutus_dyn_base)


class DynLinkDirective(SphinxDirective):

    required_arguments = 1

    def run(self):
        logger.debug("DynLinkDirective.run")

        if not hasattr(self.env, 'dyn_link_list'):
            self.env.dyn_link_list = []

        # Some inconsistency in whether the argument will come back with
        # quotes or not.  Need to figure out how to use converters and use path as type.
        replacement_url = self.arguments[0].replace('"', '').replace("'", '')
        self.env.dyn_link_list.append({
            'docname': self.env.docname,
            'replacement_url': replacement_url
        })
        return []


class DynBookmarkDirective(SphinxDirective):

    required_arguments = 1
    final_argument_whitespace = True

    def run(self):
        logger.warning("DynBookmarkDirective.run")
        node = DynBookmarkNode('')
        node.value = self.arguments[0]
        return [node]

    @staticmethod
    def handle_insert_markup(app, doctree, fromdocname):
        """ Handle title modification by inserting post processing markup. """
        for node in doctree.traverse(DynBookmarkNode):
            logger.debug("DynBookmarkDirective.handle_title_modification")
            jinja2_value = node.value.replace('<', '{{ ').replace('>', ' }}')
            replacement = f'\n««HTML_TITLE»» {jinja2_value} ««END_HTML_TITLE»»\n'
            replacement_node = docutils.nodes.raw('', replacement, format='html')
            node.replace_self(replacement_node)


class DynIncludeDirective(SphinxDirective):

    required_arguments = 1

    def run(self):
        logger.warning("DynIncludeDirective.run")
        node = DynIncludeNode('')
        node.value = self.arguments[0]
        return [node]

    @staticmethod
    def handle_insert_markup(app, doctree, fromdocname):
        """ Handle include modification by inserting post processing markup. """
        for node in doctree.traverse(DynIncludeNode):
            logger.debug("DynBookmarkDirective.handle_title_modification")
            jinja2_value = node.value.replace('<', '{{ ').replace('>', ' }}')
            replacement = f'\n««INCLUDE»» {jinja2_value} ««END_INCLUDE»»\n'
            replacement_node = docutils.nodes.raw('', replacement, format='html')
            node.replace_self(replacement_node)


class DynDestinationDirective(SphinxDirective):

    required_arguments = 1

    def run(self):
        logger.warning("DynDestinationDirective.run")
        node = DynDestinationNode('')
        node.value = self.arguments[0]
        return [node]

    @staticmethod
    def handle_insert_markup(app, doctree, fromdocname):
        """ Handle title modification by inserting post processing markup. """
        for node in doctree.traverse(DynDestinationNode):
            logger.debug("DynBookmarkDirective.handle_title_modification")
            jinja2_value = node.value.replace('<', '{{ ').replace('>', ' }}')
            replacement = f'\n««DESTINATION»» {jinja2_value} ««END_DESTINATION»»\n'
            replacement_node = docutils.nodes.raw('', replacement, format='html')
            node.replace_self(replacement_node)


def config_inited(app, config):
    """ Check that the required configuration variables have been initialized"""
    logger.warn("Got to config_inited")
    if app.config.astutus_docs_base == '':
        raise ValueError("You must define 'astutus_docs_base' if you are using Astutus capabilities.")
    if app.config.astutus_dyn_base == "":
        raise ValueError("You must define 'astutus_dyn_base' if you are using Astutus capabilities.")
    if app.config.astutus_dyn_pages_dir == "":
        raise ValueError("You must define 'astutus_dyn_pages_dir' if you are using Astutus capabilities.")


class ToggleNoteNode(docutils.nodes.note):
    pass


class ToggleNoteDirective(SphinxDirective):

    has_content = True
    optional_arguments = 2
    final_argument_whitespace = True

    def run(self):
        logger.warning("ToggleNoteDirective.run")
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
    def make_style_node():
        content = """
<style>
    div.astutus-toggle input[type=checkbox] {
        display: none;
    }
    div.astutus-toggle input[type=checkbox]:checked ~ div.astutus-toggle {
        display: none;
    }
    input[type=checkbox]:checked + label p.astutus-toggle-symbol:before {
        content: "⊞";
    }
    input[type=checkbox] + label p.astutus-toggle-symbol:before {
        content: "⊟";
    }
</style>          """
        return docutils.nodes.raw('', content, format='html')

    @staticmethod
    def handle_insert_markup(app, doctree, fromdocname):
        logger.debug(f"ToggleNoteDirective.handle_insert_markup  fromdocname: {fromdocname}")
        found = False
        idx = 0
        for node in doctree.traverse(ToggleNoteNode):
            logger.warning("ToggleNoteDirective.handle_insert_markup")
            found = True
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
        if found:
            for document in doctree.traverse(docutils.nodes.document):
                # Want the stylesheet to be above content to be styled.
                document.children.insert(0, ToggleNoteDirective.make_style_node())
                # logger.warning(f"ToggleNoteDirective.handle_insert_markup  {document}")


def setup(app):
    app.add_node(
        DynLinkNode,
        html=(visit_dyn_link_node, depart_dyn_link_node)
    )
    app.add_node(
        DynLinksInMenuListNode,
    )
    app.add_node(
        ScriptNode,
        html=(visit_generic_node, depart_generic_node)
    )
    app.add_node(
        DynBookmarkNode,
        html=(visit_generic_node, depart_generic_node)
    )
    app.add_node(
        ToggleNoteNode,
        html=(visit_generic_node, depart_generic_node)
    )
    app.add_config_value('astutus_docs_base', '', 'html')
    app.add_config_value('astutus_dyn_base', '', 'html')
    app.add_config_value('astutus_dyn_pages_dir', 'astutus_dyn_pages', 'html')
    app.add_config_value('astutus_dynamic_templates', 'astutus_dynamic_templates', 'html')
    app.add_directive('astutus_dyn_link', DynLinkDirective)

    app.add_directive('astutus_dyn_links_in_menus', DynLinksInMenuDirective)
    app.connect('doctree-resolved', DynLinksInMenuDirective.generate_menu_modification)

    app.add_directive('astutus_dyn_bookmark', DynBookmarkDirective)
    app.connect('doctree-resolved', DynBookmarkDirective.handle_insert_markup)

    app.add_directive('astutus_dyn_include', DynIncludeDirective)
    app.connect('doctree-resolved', DynIncludeDirective.handle_insert_markup)

    app.add_directive('astutus_dyn_destination', DynDestinationDirective)
    app.connect('doctree-resolved', DynDestinationDirective.handle_insert_markup)

    app.add_directive('astutus_toggle_note', ToggleNoteDirective)
    app.connect('doctree-resolved', ToggleNoteDirective.handle_insert_markup)

    app.connect('config-inited', config_inited)
    app.connect('build-finished', astutus.sphinx.post_process.post_process)

    return {
        'version': astutus.__version__,
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
