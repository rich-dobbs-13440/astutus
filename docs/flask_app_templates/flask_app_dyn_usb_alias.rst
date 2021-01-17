USB Aliases
===========

.. astutus_dyn_link:: "/astutus/usb/alias"

.. astutus_dyn_links_in_menus::

««HTML_TITLE»» USB Aliases - /astutus/alias ««END_HTML_TITLE»»

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


Device Aliases
--------------

««INCLUDE»» usb/device_aliases.html ««END_INCLUDE»»