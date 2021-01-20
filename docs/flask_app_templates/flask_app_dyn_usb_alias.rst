USB Aliases
===========

.. astutus_dyn_bookmark:: USB Aliases - /astutus/alias

««DESTINATION»» usb/dyn_alias.html ««END_DESTINATION»»

Aliases allow providing meaningful human names to USB devices despite
the challenges of the USB implementation:

    * Physical devices consist of multiple USB components.
    * USB components present different logical USB devices to the host computer
      depending on what physical devices they are plugged into, and the cables
      connecting the devices.
    * Most USB devices do not have unique identifiers such as true serial numbers.
    * The sys/device file structure is not persistent or consistent against
      system reboot timing and plug-and-play.

  Typically, you will define aliases interactively, by clicking on the buttons
  in the device tree.  But you might find this page useful for seeing all
  of the aliases that you have defined, and editing specific aliases.


.. astutus_dyn_include:: usb/device_aliases.html

.. astutus_dyn_link:: "/astutus/usb/alias"

.. toctree::
    :hidden:

    flask_app_dyn_usb_alias_item

.. astutus_dyn_include:: usb/alias_items_list_js.html

.. astutus_dyn_links_in_menus:: dynamic alias_items_list <path>