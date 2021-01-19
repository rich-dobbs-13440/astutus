var astutusDynPage = {

    getReplacementUrl: function(link, itemPattern, itemList, idx) {
        if (itemList == undefined) {
            return link['replacement_url'];
        }
        if (itemPattern == undefined) {
            itemPattern = '<idx>';
        }
        replacementUrl = link['replacement_url']
        itemValue = itemList[idx]['value'];
        return replacementUrl.replace(itemPattern, itemValue);
    },

    replaceHrefs: function (menuLinks, dynLinkList, docsBase, dynBase, itemList, itemPattern) {
        if (itemList != undefined) {
            if (itemPattern == undefined) {
                itemPattern = '<idx>';
            }
        }
        menuLinks.forEach(element => {
            var rawHref = element.getAttribute("href");
            var originalHref = element.href;
            var replaced = false;
            for (link of dynLinkList) {
                if (rawHref.includes(link['search_pattern'])) {
                    sectionIdx = rawHref.indexOf("#");
                    var sectionLink = "";
                    if (sectionIdx >= 0) {
                        sectionLink = rawHref.substring(sectionIdx);
                    }
                    idx = 0
                    replacementUrl = astutusDynPage.getReplacementUrl(link, itemPattern, itemList, idx)
                    element.href = replacementUrl + sectionLink;
                    replaced = true;
                    break;
                }
            }
            if (!replaced) {
                // Fix up hrefs for static documentation pages for flask deployed configuration
                if (originalHref.includes(dynBase)) {
                    // Assume for now that the dynamic rst files are one directory below configuration directory:
                    element.href = docsBase + "/" + rawHref.replace('../', '')

                } else {
                    element.href = docsBase + "/" + rawHref;
                }

            }
            console.log("Original rawHref", rawHref, "originalHref", originalHref, "current element.href", element.href)
        });
    },

    applyDynamicLinks: function (dynLinkList, docsBase, dynBase, itemList, itemPattern) {
        var menuLinks = document.querySelectorAll("div.toctree-wrapper ul li a");
        astutusDynPage.replaceHrefs(menuLinks, dynLinkList, docsBase, dynBase, itemList, itemPattern);
        menuLinks = document.querySelectorAll("div.wy-menu-vertical ul li a");
        astutusDynPage.replaceHrefs(menuLinks, dynLinkList, docsBase, dynBase, itemList, itemPattern);
    }

}

