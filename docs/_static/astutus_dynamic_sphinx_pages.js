var astutusDynPage = {

    linkHasItems: function(link, itemPattern) {
        replacementUrl = link['replacement_url'];
        return replacementUrl.includes(itemPattern);
    },

    getReplacementUrl: function(link, itemPattern, item) {
        replacementUrl = link['replacement_url'];
        itemValue = item['value'];
        return replacementUrl.replace(itemPattern, itemValue);
    },

    replaceForItemList: function(element, link, sectionHash, itemPattern, itemList) {
        if (itemList.length == 0) {
            // Remove the entire ul, since it has no items.
            var li = element.parentElement;
            var ul = li.parentElement;
            var ulParent = ul.parentElement;
            ulParent.removeChild(ul);
            return true;
        }
        var first = true;
        for (item of itemList) {
            replacementUrl = astutusDynPage.getReplacementUrl(link, itemPattern, item)
            if (first) {
                element.href = replacementUrl + sectionHash;
                if (link['replacement_url'].endsWith(itemPattern)) {
                    element.innerHTML = item['innerHTML'];
                }
                first = false;
            } else {
                // Duplicate list item and add to end of list.
                var li = element.parentElement;
                var ul = li.parentElement;
                var liClone = li.cloneNode(li)
                aElement = liClone.getElementsByTagName('A')[0];
                aElement.href = replacementUrl + sectionHash;
                if (link['replacement_url'].endsWith(itemPattern)) {
                    element.innerHTML = item['innerHTML'];
                }
                ul.appendChild(liClone)
            }
        }
        return false;
    },

    replaceHrefs: function (docName, menuLinks, dynLinkList, docsBase, dynBase, isDynamic, itemList, itemPattern) {
        if (itemList != undefined) {
            if (itemPattern == undefined) {
                itemPattern = '<idx>';
            }
        }
        menuLinks.forEach(aElement => {
            const rawHref = aElement.getAttribute("href");
            const originalHref = aElement.href;
            var href;
            if (isDynamic) {
                if (rawHref.startsWith("#")) {
                    href = docName + rawHref
                } else {
                    href = rawHref;
                }
            } else {
                href = rawHref;
            }
            console.log("rawHref", rawHref, "href", href, "orginalHref", originalHref);
            const idxOfHash = href.indexOf("#");
            var sectionHash = "";
            if (idxOfHash >= 0) {
                sectionHash = href.substring(idxOfHash);
            }
            var found = false;
            var removed = false;
            for (link of dynLinkList) {
                if (href.includes(link['search_pattern'])) {
                    if (astutusDynPage.linkHasItems(link, itemPattern)) {
                        removed = astutusDynPage.replaceForItemList(aElement, link, sectionHash, itemPattern, itemList)
                        console.log()
                    } else {
                        replacementUrl = link['replacement_url']
                        aElement.href = replacementUrl + sectionHash;
                    }
                    found = true;
                    console.log('Pattern found!', 'removed', removed, 'pattern', link['search_pattern'])
                    break;
                }
            }
            if (!found) {
                // Fix up hrefs for static documentation pages for flask deployed configuration
                if (isDynamic) {
                    // Remove all relative upward references
                    var hrefRelativeToDocs = rawHref.replace(/\.\.\//g, '')
                    aElement.href = docsBase + "/" + hrefRelativeToDocs;
                } else {
                    aElement.href = docsBase + "/" + rawHref;
                }

            }
            if (!removed) {
                console.log("Original rawHref", rawHref, "originalHref", originalHref, "current aElement.href", aElement.href);
            }
        });
    },

    applyDynamicLinks: function (docName, dynLinkList, docsBase, dynBase, isDynamic, itemList, itemPattern) {
        var menuLinks = document.querySelectorAll("div.toctree-wrapper ul li a");
        astutusDynPage.replaceHrefs(docName, menuLinks, dynLinkList, docsBase, dynBase, isDynamic, itemList, itemPattern);
        menuLinks = document.querySelectorAll("div.wy-menu-vertical ul li a");
        astutusDynPage.replaceHrefs(docName, menuLinks, dynLinkList, docsBase, dynBase, isDynamic, itemList, itemPattern);
    }

}
