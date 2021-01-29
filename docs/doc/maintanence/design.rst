Application Design
==================

Device Tree AJAX
----------------

The USB device tree is implemented mostly in HTML and Javascript using AJAX concepts.
Consequently, it is not easily explained using Python docstrings and Sphinx Apidoc
tactics.  Rather than including comments in the HTML and Javascript, which has
performance implications, the design of this part of the system will be shared here.


Page Loading
............

The HTML page loads quickly - about a tenth of a secon, with no functionality, with only
data that has been gathered during the process of identifying the tree, and consequently,
not the final look. Near the bottom of the page, the update process is triggered with this code:

.. code-block:: javascript

    updateAllDescriptions();

This function call triggers the process of updating all of the descriptions and fetching
such information as needed to use the page.  The update proceeds from the top of the page
down to the bottom, so that the part of the browser page that is immediately visible is
updated first, in perhaps half a second.

The function that actually updates the description for a particular button is:

.. code-block:: javascript

    updateButtonData(buttons[buttonIdx]);

The updateButtonData function initiates an asynchronous HTTP call to the Flask web application,
and then returns.  The callback triggered when the web server responds processes the response
which contains the information required so that the next button's update can be triggered.
In addition, the remained of the information necessary for updating the button's description
is obtained by calling:

.. code-block:: javascript

    updateNodeData(button, data_for_dir);

The updateNodeData function call makes another asynchronous HTTP call to the Flask web application
to collect the remained of the needed information.  In the callback triggered when the web
server responds provides the remainder of the information for updating the labels associated
with each USB device and attaches an onclick handler to each button associate with every device.

The information returned by the asynchonous HTTP calls is stored in HTML5 data attributes.

The asynchronous HTTP calls are implemented using vanilla Javascript calls, rather than
by using JQuery.


On Click Action
...............

When a button is clicked, a popup is displayed on the web page.

Currently the popup directly displays the Add Alias form, since that was the first command implemented.

In the future, the popup will display a menu, and other forms will popup upon selection of the form.


Add Alias Form
..............

The following functions are associated with the Add Alias form:

.. code-block:: javascript

    function handleAliasAddForm(placementElement, data)

    function handleAddAliasFormCancel()

    function updatePlaceholderTable(table_id, data)

    function rememberTemplateSelection( selectionStart, selectionEnd)

    function handleInsertButtonClick(value)

    function onTreeButtonClick(button)


General Page Functionality
..........................

The following functions are used for the overall page functionality:

.. code-block:: javascript

    function isElementInViewport(el)

    function toggleVisibility(checkbox, cssClass, displayValue)

    function onBackgroundColorChange(colorInput)
