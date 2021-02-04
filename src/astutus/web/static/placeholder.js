var astutusUsbPlaceholderInserter = {
    create: function (tableSelector, templateSelector) {
        // Create a variable to hold methods and instance variables
        var inserter =  {
            'tableSelector': tableSelector,
            'templateSelector': templateSelector,
            'tableElement': null,
            'templateElement': null,
            'templateSelectionStart': null,
            'templateSelectionEnd': null,
            initialize: function() {
                this['tableElement'] = document.querySelector(this.tableSelector);
                this['templateElement'] = document.querySelector(this.templateSelector);
                var theInstance = this;
                rememberTemplateSelectionClosure = function() {
                    theInstance.rememberTemplateSelection();
                }
                this.templateElement.addEventListener('blur', rememberTemplateSelectionClosure);
            },
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
                        tdbutton = `<td><div class="astutus-insert-placeholder"><button data-placeholder="${placeholder}">Insert</button></div></td>`
                        rowText = `<tr>${tdbutton}${tdPlaceholder}${tdCurrentValue}</tr>`;
                        lines.push(rowText)
                    }
                }
                this.tableElement.innerHTML = lines.join('\n');
                var theInstance = this;
                for (button of this.tableElement.getElementsByTagName('BUTTON')) {
                    button.addEventListener('click', function(evt) { theInstance.handleInsertButtonClick(evt);} );
                }

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
            rememberTemplateSelection: function() {
                this.templateSelectionStart = this.templateElement.selectionStart;
                this.templateSelectionEnd = this.templateElement.selectionEnd;
            },
            handleInsertButtonClick: function(event) {
                button = event.srcElement;
                placeholder = button.dataset.placeholder;
                // Insert a placeholder into the template.
                var templateValue = this.templateElement.value
                var startStr = templateValue.substring(0, this.templateSelectionStart);
                // console.log("startStr: " + startStr);
                var endStr = templateValue.substring(this.templateSelectionEnd);
                // console.log("endStr: " + endStr);
                var replacementStr = startStr + placeholder + endStr;
                // console.log("replacementStr: " + replacementStr);
                this.templateElement.value = replacementStr
                var currentInsert = this.templateSelectionStart + placeholder.length;
                // console.log('Desired current insert: ' + currentInsert)
                this.templateSelectionStart = currentInsert;
                this.templateSelectionEnd = currentInsert;
                this.templateElement.selectionStart = currentInsert;
                this.templateElement.selectionEnd = currentInsert;
            }
        };
        inserter.initialize()
        return inserter;
    }
};
