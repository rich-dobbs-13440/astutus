var astutusDynPage = {

    replaceHrefs: function (menuLinks, dynLinkList, docs_base, dyn_base) {
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
            if (href == element.href) {
                // Fix up hrefs for static documentation pages for flask deployed configuration
                var raw_href = element.getAttribute("href");
                if (raw_href.startsWith("../")) {
                    element.href = docs_base + raw_href;
                }
            }
            console.log("Original href", href, "current href", element.href)
        });
    },

    applyDynamicLinks: function (dynLinkList, docs_base, dyn_base) {
        var menuLinks = document.querySelectorAll("div.toctree-wrapper ul li a");
        astutusDynPage.replaceHrefs(menuLinks, dynLinkList, docs_base, dyn_base)
        menuLinks = document.querySelectorAll("div.wy-menu-vertical ul li a");
        astutusDynPage.replaceHrefs(menuLinks, dynLinkList, docs_base, dyn_base)
    }

}

