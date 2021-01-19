var astutusDynPage = {

    linkHasItems: function(link, itemPattern) {
        replacementUrl = link['replacement_url'];
        return replacementUrl.includes(itemPattern);
    },

    getReplacementUrl: function(link, itemPattern, item) {
        if (itemPattern == undefined) {
            itemPattern = '<idx>';
        }
        replacementUrl = link['replacement_url'];
        itemValue = item['value'];
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
                    if (astutusDynPage.linkHasItems(link, itemPattern)) {
                        var first = true;
                        for (item of itemList) {
                            replacementUrl = astutusDynPage.getReplacementUrl(link, itemPattern, item)
                            if (first) {
                                element.href = replacementUrl + sectionLink;
                                first = false;
                            } else {
                                // Duplicate list item and add to end of list.
                                var li = element.parentElement;
                                var ul = li.parentElement;
                                var liClone = li.cloneNode(li)
                                aElement = liClone.getElementsByTagName('A')[0];
                                aElement.href = replacementUrl;
                                ul.appendChild(liClone)
                            }
                        }
                    } else {
                        replacementUrl = link['replacement_url']
                        element.href = replacementUrl + sectionLink;
                    }
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

