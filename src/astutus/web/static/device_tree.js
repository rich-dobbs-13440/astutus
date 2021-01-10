function handleTreeItemClick(data) {
    $("#nodepath").val(data["nodepath"]);
    $("#template").val(data["alias_description_template"]);
    var color = data["alias_color"];
    if (color != "") {
        $("#color").val(color);
    }

    var container = $("#add-alias-form-container");
    var nodeButton = $("#" + data["idx"]);
    var buttonOffset = nodeButton.offset();
    container.css("top", buttonOffset.top + 30);
    container.css("left", buttonOffset.left + 30);

    updatePlaceholderTable('#alias-placeholder-table', data);


    container.show();

    if (!isElementInViewport(container)) {
      // Form will be below button
      console.log("Scrolling element into view.")
      var domDivElement = container[0];
      domDivElement.scrollIntoView(false);
    }
}

function handleAddAliasFormCancel() {
    $("#add-alias-form-container").hide();
}

function isElementInViewport(el) {

    if (typeof jQuery === "function" && el instanceof jQuery) {
        el = el[0];
    }

    var rect = el.getBoundingClientRect();

    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
}

function toggleVisibility(checkbox, cssClass, displayValue) {
    if (checkbox.checked) {
        $(cssClass).css("display" , displayValue);
    } else {
        $(cssClass).css("display" , "none");
    }
}

function onBackgroundColorChange(colorInput) {
    $(".tree_html").css("background-color", colorInput.value)
    data = {
        "background-color": colorInput.value
    }
    // TODO: should be patch, not post.
    $.post('/astutus/usb/settings', data)
        .fail(function(jqxhr, settings, ex) { alert('failed, ' + ex); });
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
    console.log("Need to handle inserting " + value + ' at (' + templateSelectionStart + ', ' +  templateSelectionEnd + ')');
    console.log("The entire string: " + $("#template").val());
    var templateValue = $("#template").val();
    var startStr = templateValue.substring(0, templateSelectionStart);
    console.log("startStr: " + startStr);
    var endStr = templateValue.substring(templateSelectionEnd);
    console.log("endStr: " + endStr);
    var replacementStr = startStr + value + endStr
    console.log("replacementStr: " + replacementStr);
    $("#template").val(replacementStr)
    var currentInsert = templateSelectionStart + value.length
    console.log('Desired current insert: ' + currentInsert)
    templateSelectionStart = currentInsert
    templateSelectionEnd = currentInsert
    $("#template")[0].selectionStart = currentInsert
    $("#template")[0].selectionEnd = currentInsert
}