var astutusUsbPlaceholderInserter = {
    create: function (tableSelector, templateSelector, inserterVariableName) {
        // Create a variable to hold methods and instance variables
        return {
            'tableSelector': tableSelector,
            'tableElement': document.querySelector(tableSelector),
            'templateSelector': templateSelector,
            'templateElement': document.querySelector(templateSelector),
            'inserterVariableName': inserterVariableName,
            'templateSelectionStart': null,
            'templateSelectionEnd': null,
            updatePlaceholderTable: function(data) {
                var dataKeys = this.getSortedKeys(data);
                var idx;
                var key;
                var value;
                var rowText;
                lines = [];
                for (idx = 0; idx < dataKeys.length; idx++) {
                    key = dataKeys[idx];
                    if (this.do_include_in_placeholder_table(key)) {
                        value = data[key];
                        placeholder = `{${key}}`
                        tdPlaceholder = `<td><div class="astutus-placeholder">${placeholder}</div></td>`;
                        tdCurrentValue = `<td><div class="astutus-current-value">${value}</div></td>`;
                        onClickText = `${inserterVariableName}.handleInsertButtonClick('${placeholder}')`
                        tdbutton = `<td><div class="astutus-insert-placeholder"><button onclick="${onClickText}">Insert</button></div></td>`
                        rowText = `<tr>${tdbutton}${tdPlaceholder}${tdCurrentValue}</tr>`;
                        lines.push(rowText)
                    }
                }
                this.tableElement.innerHTML = lines.join("\n")
            },
            getSortedKeys: function (obj) {
                var keys = Object.keys(obj);
                return keys.sort();
            },
            do_include_in_placeholder_table: function(key) {
                if (key == 'idx') {
                    return false;
                }
                if (key == 'idx') {
                    return false;
                }
                if (key.startsWith('alias_')) {
                    return false;
                }
                if (key.startsWith('resolved_')) {
                    return false;
                }
                if (key.startsWith('terminal_')) {
                    return false;
                }
                return true;
            },
            rememberTemplateSelection: function(selectionStart, selectionEnd) {
                this.templateSelectionStart = selectionStart;
                this.templateSelectionEnd = selectionEnd;
            },
            handleInsertButtonClick: function(value) {
                // Insert a placeholder into the template.
                var templateValue = this.templateElement.value
                var startStr = templateValue.substring(0, this.templateSelectionStart);
                // console.log("startStr: " + startStr);
                var endStr = templateValue.substring(this.templateSelectionEnd);
                // console.log("endStr: " + endStr);
                var replacementStr = startStr + value + endStr;
                // console.log("replacementStr: " + replacementStr);
                this.templateElement.value = replacementStr
                var currentInsert = this.templateSelectionStart + value.length;
                // console.log('Desired current insert: ' + currentInsert)
                this.templateSelectionStart = currentInsert;
                this.templateSelectionEnd = currentInsert;
                this.templateElement.selectionStart = currentInsert;
                this.templateElement.selectionEnd = currentInsert;
            }
        };
    }
};
