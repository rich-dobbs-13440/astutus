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


class DynLinksInMenuListNode(nodes.General, nodes.Element):
    pass


class ScriptNode(nodes.General, nodes.Element):
    pass


def visit_script_node(self, node):
    logger.debug(f"Visiting node: {node} ")


def depart_script_node(self, node):
    logger.debug(f"Departing node: {node} ")


class DynLinksInMenuDirective(Directive):

    def run(self):
        return [DynLinksInMenuListNode('')]


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


def generate_menu_modification(app, doctree, fromdocname):
    logger.debug("Got to generate_menu_modification")
    if app.config.astutus_docs_base == '':
        raise ValueError("You must define 'astutus_docs_base' if you are using Astutus capabilities.")
    if app.config.astutus_dyn_base == "":
        raise ValueError("You must define 'astutus_dyn_base' if you are using Astutus capabilities.")
    env = app.builder.env
    if not hasattr(env, 'dyn_link_list'):
        env.dyn_link_list = []

    for node in doctree.traverse(DynLinksInMenuListNode):
        content = []
        script = ScriptNode()
        script += nodes.raw('', "\n<script>\n", format='html')
        script += nodes.raw('', "\nvar dynLinkList = [\n", format='html')
        # Don't want trailing comma in Javascript, so use join to make list
        js_links = []
        for link in env.dyn_link_list:
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
            line = "    {" + search_snippet + ", " + replacement_url_snippet + "}"
            js_links.append(line)
            search_snippet_link = f"'search_pattern': '{basename}#'"
            line = "    {" + search_snippet_link + ", " + replacement_url_snippet + "}"

        script += nodes.raw('', ',\n'.join(js_links), format='html')
        script += nodes.raw('', "\n];\n", format='html')
        script += nodes.raw('', f"astutus_docs_base = '{app.config.astutus_docs_base}';", format='html')
        script += nodes.raw('', f"astutus_dyn_base = '{app.config.astutus_dyn_base}';", format='html')
        script += nodes.raw('', '''
function replaceHrefs(menuLinks, dynLinkList, docs_base, dyn_base) {
    menuLinks.forEach(element => {
        href = element.href;
        for (link of dynLinkList) {
            if (href.includes(link['search_pattern'])) {
                sectionIdx = href.indexOf("#");
                var sectionLink = "";
                if (sectionIdx >= 0) {
                    sectionLink = href.substring(sectionIdx);
                }
                element.href = link['replacement_url'] + sectionLink;
                break;
            }
        }
        if (href == element.href && !href.includes(dyn_base)) {
            // Fix up hrefs for static documentation pages for flask deployed configuration
            const url = new URL(href)
            element.href = docs_base + url.pathname + url.hash;
        }
        console.log("Original href", href, "current href", element.href)
    });
}

function applyDynamicLinks(dynLinkList, docs_base, dyn_base) {
    var menuLinks = document.querySelectorAll("div.toctree-wrapper ul li a");
    replaceHrefs(menuLinks, dynLinkList, docs_base, dyn_base)
    menuLinks = document.querySelectorAll("div.wy-menu-vertical ul li a");
    replaceHrefs(menuLinks, dynLinkList, docs_base, dyn_base)
}

applyDynamicLinks(dynLinkList, astutus_docs_base, astutus_dyn_base)
        ''', format='html')
        script += nodes.raw('', "\n</script>\n", format='html')
        content.append(script)
        node.replace_self(content)


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
