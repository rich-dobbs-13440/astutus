// import {astutusUsbPlaceholderInserter} from '/static/placeholder.js'
//import('/static/placeholder.js')

function addCheckRow() {
    var templateTable = document.querySelector('#rule-table-row-template-holder');
    var rows = templateTable.rows
    const lastRow = rows[rows.length -1];
    var clonedRow = lastRow.cloneNode(true);
    var checkTable = document.querySelector('#rule-table');
    checkTable.appendChild(clonedRow);

    var root = document.querySelector(':root');
    computedStyle = getComputedStyle(root);
    old_height = computedStyle.getPropertyValue('--astutus-table-scroll-non-scrolled-height')
    root.style.setProperty('--astutus-table-scroll-non-scrolled-height', old_height + 100);
}

function deleteRow(button) {
    node = button.parentNode;
    while (node != undefined) {
        console.log(node.nodeName);
        if (node.nodeName == 'TR') {
            break;
        }
        node = node.parentNode;
    }
    if (node != undefined) {
        tr = node;
        tr.parentNode.removeChild(tr);
    } else {
        alert('What went wrong????')
    }
}

var placeholderInserter;

function initialize_placeholder(data) {
    placeholderInserter = astutusUsbPlaceholderInserter.create('#label-rule-placeholder-table', '#label-rule-template');
    placeholderInserter.updatePlaceholderTable(data);
}

