Label Rules
===========

Label rules are used to identify aliases for USB and PCI devices.

Aliases allow providing meaningful human names to USB devices and the
PCI buses and devices connecting them despite the challenges of the USB implementation:

    * Physical devices consist of multiple USB components.
    * USB components present different logical USB devices to the host computer
      depending on what physical devices they are plugged into, and the cables
      connecting the devices.
    * Most USB devices do not have unique identifiers such as true serial numbers.
    * The sys/device file structure is not persistent or consistent against
      system reboot timing and plug-and-play.


.. astutus_dyn_include:: app/usb/label_rules.html


.. toctree::
    :hidden:

    label_rule_editor

.. astutus_dyn_link:: /astutus/app/usb/labelrule/index.html

.. astutus_dyn_destination:: app/usb/labelrule/styled_index.html

.. astutus_dyn_bookmark:: USB Aliases - /astutus/app/usb/labelrule
