import sphinx.util

from docutils import nodes
from docutils.parsers.rst import Directive

from sphinx.util.docutils import SphinxDirective
# import logging

logger = sphinx.util.logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)


class DynLinkNode(nodes.General, nodes.Element):
    pass


def visit_dyn_link_node(self, node):
    pass


def depart_dyn_link_node(self, node):
    pass


class ScriptNode(nodes.General, nodes.Element):
    pass


def visit_script_node(self, node):
    logger.debug(f"Visiting node: {node} ")


def depart_script_node(self, node):
    logger.debug(f"Departing node: {node} ")


class DynLinksInMenuListNode(nodes.General, nodes.Element):

    def set_item_list_name(self, item_list_name):
        self.item_list_name = item_list_name

    def set_item_pattern(self, pattern):
        self.pattern = pattern

    def replace_node_content(self, dyn_link_list, docs_base, dyn_base):
        content = []
        script = ScriptNode()
        script += nodes.raw('', "\n<script>\n", format='html')
        dyn_links_json = self.dyn_links_as_json(dyn_link_list)
        script += nodes.raw('', f"\nvar dynLinkList = {dyn_links_json};\n", format='html')
        script += nodes.raw('', f"astutus_docs_base = '{docs_base}';\n", format='html')
        script += nodes.raw('', f"astutus_dyn_base = '{dyn_base}';\n", format='html')
        script += nodes.raw('', "astutusDynPage.applyDynamicLinks(", format='html')
        script += nodes.raw('', "dynLinkList, astutus_docs_base, astutus_dyn_base", format='html')
        if self.item_list_name is not None:
            script += nodes.raw('', f", {self.item_list_name}", format='html')
        if self.pattern is not None:
            script += nodes.raw('', f", '{self.pattern}'", format='html')
        script += nodes.raw('', ");\n", format='html')
        script += nodes.raw('', "</script>\n", format='html')
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
            # search_snippet_link = f"'search_pattern': '{basename}#'"
            # line = "    {" + search_snippet_link + ", " + replacement_url_snippet + "}"
            # js_links.append(line)
        items_text = ',\n'.join(items)
        return '[' + items_text + ']'


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
    logger.debug("Got to generate_menu_modification")
    if app.config.astutus_docs_base == '':
        raise ValueError("You must define 'astutus_docs_base' if you are using Astutus capabilities.")
    if app.config.astutus_dyn_base == "":
        raise ValueError("You must define 'astutus_dyn_base' if you are using Astutus capabilities.")
    env = app.builder.env
    if not hasattr(env, 'dyn_link_list'):
        env.dyn_link_list = []
    for node in doctree.traverse(DynLinksInMenuListNode):
        node.replace_node_content(env.dyn_link_list, app.config.astutus_docs_base, app.config.astutus_dyn_base)


class DynLinksInMenuDirective(Directive):

    optional_arguments = 2

    def run(self):
        node = DynLinksInMenuListNode('')
        if len(self.arguments) > 0:
            node.set_item_list_name(self.arguments[0])
        else:
            node.set_item_list_name(None)
        if len(self.arguments) > 1:
            node.set_item_pattern(self.arguments[1])
        else:
            node.set_item_pattern(None)

        return [node]


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
        html=(visit_script_node, depart_script_node)
    )
    app.add_config_value('astutus_docs_base', '', 'html')
    app.add_config_value('astutus_dyn_base', '', 'html')
    app.add_directive('astutus_dyn_link', DynLinkDirective)
    app.add_directive('astutus_dyn_links_in_menus', DynLinksInMenuDirective)
    app.connect('doctree-resolved', generate_menu_modification)
    return {
        'version': '0.1',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
