function handleAliasAddForm(placementElement, data) {

    var nodePathElement = document.querySelector("#nodepath");
    nodePathElement.value = data["nodepath"];
    templateElement = document.querySelector("#template");
    templateElement.value = data["alias_description_template"];
    var color = data["alias_color"];
    if (color != "") {
        colorElement = document.querySelector("#color");
        colorElement.value = color;
    }

    var rect = placementElement.getBoundingClientRect();
    var container = document.querySelector("#add-alias-form-container");
    container.style.top = `${rect.top + window.scrollY + 30}px`;
    container.style.left = `${rect.left + window.scrollX + 30}px`;

    updatePlaceholderTable('#alias-placeholder-table', data);

    container.style.display = "block";

    if (!isElementInViewport(container)) {
      // Form will be below button
      console.log("Scrolling element into view.")
      container.scrollIntoView(false);
    }
}

function handleAddAliasFormCancel() {
    var container = document.querySelector("#add-alias-form-container");
    container.style.display = "none";
}

function isElementInViewport(el) {

    var rect = el.getBoundingClientRect();

    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
}

function toggleVisibility(checkbox, cssClass, displayValue) {
    var display;
    if (checkbox.checked) {
        display = displayValue;
    } else {
        display = "none";
    }
    nodes = document.querySelectorAll(cssClass);
    nodes.forEach(element => {
        element.style.display = display;
    });
}

function onBackgroundColorChange(colorInput) {
    const color = colorInput.value
    const treeHtmlNodes = document.querySelectorAll('.astutus-tree-html');
    treeHtmlNodes.forEach(element => {
        element.style.background = color;
      });
    data = {
        "background-color": color
    }

    const xhr = new XMLHttpRequest();
    xhr.onload = () => {
        if (xhr.status >= 200 && xhr.status < 300) {
            // Nothing needed
        } else {
            console.log('Updating color failed.  xhr:', xhr);
            alert('Updating color failed.  xhr:' + xhr)
        }
    };
    xhr.open('PATCH', '/astutus/usb/settings');
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(JSON.stringify(data));
}

function getSortedKeys(obj) {
    var keys = Object.keys(obj);
    return keys.sort();
}

function updatePlaceholderTable(table_id, data) {
    $(table_id).empty();

    var dataKeys = getSortedKeys(data);
    var idx;
    var key;
    var value;
    var rowText;
    var newRow;
    for (idx = 0; idx < dataKeys.length; idx++) {
      key = dataKeys[idx];
      if (key != 'idx') {
            value = data[key];
            placeholder = `{${key}}`
            tdPlaceholder = `<td><div class="astutus-placeholder">${placeholder}</div></td>`;
            tdCurrentValue = `<td><div class="astutus-current-value">${value}</div></td>`;
            onClickText = `handleInsertButtonClick('${placeholder}')`
            tdbutton = `<td><div class="astutus-insert-placeholder"><button onclick="${onClickText}">Insert</button></div></td>`
            rowText = `<tr>${tdbutton}${tdPlaceholder}${tdCurrentValue}</tr>`;
        $(table_id).append(rowText)
        }
    }
  }

var templateSelectionStart;
var templateSelectionEnd
function rememberTemplateSelection( selectionStart, selectionEnd) {
    templateSelectionStart = selectionStart;
    templateSelectionEnd = selectionEnd;
}

function handleInsertButtonClick(value) {
    // Insert a placeholder into the template.
    const templateElement = document.querySelector("#template")
    var templateValue = templateElement.value
    var startStr = templateValue.substring(0, templateSelectionStart);
    // console.log("startStr: " + startStr);
    var endStr = templateValue.substring(templateSelectionEnd);
    // console.log("endStr: " + endStr);
    var replacementStr = startStr + value + endStr
    // console.log("replacementStr: " + replacementStr);
    templateElement.value = replacementStr
    var currentInsert = templateSelectionStart + value.length
    // console.log('Desired current insert: ' + currentInsert)
    templateSelectionStart = currentInsert
    templateSelectionEnd = currentInsert
    templateElement.selectionStart = currentInsert
    templateElement.selectionEnd = currentInsert
}

function onTreeButtonClick(button) {
    data = {};
    nodedata = JSON.parse(button.dataset['nodedata']);
    Object.assign(data, nodedata);
    dataForDir = JSON.parse(button.dataset['data_for_dir']);
    Object.assign(data, dataForDir);
    data["nodepath"] = button.dataset['nodepath'];
    // Currently button.dataset['info'] uses single quotes, but the JSON parser wants double quotes.
    info = button.dataset['info']
    if (info) {
        info = info.replace("'", '"')
        console.log('info: ', info)
        deviceInfo = JSON.parse()
        Object.assign(data, deviceInfo);
    }
    handleAliasAddForm(button, data);
}

function updateNodeData(button, buttonData) {
    // node_data = astutus.usb.tree.get_node_data(data, device_config, alias)
    var dirpath = button.dataset['dirpath'];
    var nodepath = button.dataset['nodepath'];
    var alias = aliases.findLongest(nodepath)
    var device_configuration = device_configurations.get(buttonData['node_id'])
    var span = button.nextElementSibling
    data = {
        'data': buttonData,
        'device_config': device_configuration,
        'alias': alias,
    }
    const xhr = new XMLHttpRequest();
    xhr.onload = () => {
        if (xhr.status >= 200 && xhr.status < 300) {
            const response = JSON.parse(xhr.responseText);
            span.innerHTML = response["html_label"];
            button.onclick = function () { onTreeButtonClick(button) }
            nodeData = response['node_data'];
            button.dataset['nodedata'] = JSON.stringify(nodeData);
        } else {
            console.log('Failure in updateNodeData.  xhr:', xhr);
            console.log('Request data:', data);
        }
    };
    xhr.open('PUT', '/astutus/usb/label' + dirpath);
    xhr.setRequestHeader('Content-Type', 'application/json');
    console.log('data:', data)
    xhr.send(JSON.stringify(data));
}

function updateButtonData(button) {
    var dirpath = button.dataset['dirpath'];
    console.log("dirpath: ", dirpath)
    var deviceInfo = button.dataset['info'];
    if (deviceInfo == undefined) {
        deviceInfo = "Nothing!"
    }
    data = {
        'info': deviceInfo,
    };
    const xhr = new XMLHttpRequest();
    xhr.onload = () => {
        if (xhr.status >= 200 && xhr.status < 300) {
            const response = JSON.parse(xhr.responseText);
            data_for_dir = response['data_for_dir'];
            button.dataset['data_for_dir'] = JSON.stringify(data_for_dir);
            nodeId = data_for_dir['node_id'];
            parentDirpath = data_for_dir["parent_dirpath"];
            if (parentDirpath in nodePathByDirPath) {
                parentNodePath = nodePathByDirPath[parentDirpath];
                nodePath = parentNodePath + "/" + nodeId;
            } else {
                nodePath = nodeId;
            }
            nodePathByDirPath[data_for_dir["dirpath"]] = nodePath;
            button.dataset['nodepath'] = nodePath;
            buttonIdx++;
            updateButtonData(buttons[buttonIdx]);
            updateNodeData(button, data_for_dir);
        } else {
            console.log('Failure in updateNodeData.  xhr:', xhr);
            console.log('Request data:', data);
        }
    };
    xhr.open('PUT', '/astutus/usb' + dirpath);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(JSON.stringify(data));
}

function updateDescription(buttonIdx) {
    // Start with the first button, and eventually process all buttons asynchronously.
    updateButtonData(buttons[buttonIdx])
}

var nodePathByDirPath = {}
var buttons;
var buttonIdx;
function updateAllDescriptions() {
    buttons = document.querySelectorAll("button.astutus-tree-item-button");
    buttonIdx = 0
    updateDescription(buttonIdx);
}

updateAllDescriptions();