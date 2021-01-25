Device Identification
=====================

Devices are identified for a particular USB device vendor and product,
regardless of where it is located in relationship to other devices.  The
identity of a device can vary depending on the contents of values for the device.
For example, the same vendor and product values are used for both
Logitech mouses and keyboard receivers, but there are other values inside the
/sys/devices/... structure to differentiate them.

In the long term, we hope to distribute a broad set device names with
this system.  In the short term, the default values are fairly useful,
and you can update configurations for your system by editing the
device_configurations.json file.

Soon, these links should allow you to make local customizations.

.. astutus_dyn_include:: app/usb/device_configurations.html


.. toctree::
    :hidden:

    device_id_item


.. astutus_dyn_link:: "/astutus/app/usb/configuration.html"

.. astutus_dyn_bookmark:: USB Device ID - /astutus/app/usb/device_configurations