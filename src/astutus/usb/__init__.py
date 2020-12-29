"""

USB products are troublesome.  The physical USB device that you purchase
consists of various physical and logical USB components.  The same
physical components are used by various manufacturers to implement
a large array of devices.  In many, if not most cases, the physical
components do not have stable, unique identifiers, such as serial numbers.
Although, the cost to provide this capabilities is mere pennies in
2020, the large array of USB devices that have already been purchased
will never have this feature.  Instead, a more convoluted approach must
be taken.

Each USB device is identified by a unique **busnum** and **devnum**
while in operation.  Unfortunately, the same device is likely to have
a different **busnum** and **devnum** if it is unplugged and plugged
into a different port, or even the same one at a later time.  In addition,
if a computer is rebooted, the **devnum** is likely to change, and the
**busnum** may also change, depending on the exact start up time.  The
order can even be effected by the exact versions of drivers associated
with particular devices.

In addition, each USB device is typically associated with a location
in the directory structure of /sys/devices under the Unix family of
operating system.  AFAIK, with most computers this is connected to the
devices in the PCI bus system.  Unfortunately, the labeling of this
hierachy is not stable upon reboot.  The parts of the system that are
initialized early are likely to be stably labeled, but due to timing
of various start up activities, the lower reaches of the PCI bus
tree are likely to be inconsistently labeled.  So the /sys/devices
hierachary can not be used to uniquely identify USB devices.

Next, the same physical device can have a different logical identity
depending on what it is plugged into.  Take a device that is a 3.1 USB
hub.  If it is plugged into a USB 1.1 port, the logical 3.0 port
won't be present.  Or if it is plugged into a USB 3.0 port, but
a USB 1.1 device is plugged into it, it will show up as USB 3.0
logical device, a USB 2.0 logical device, and a USB 1.1. logical
device.

Despite these challenges, it is often possible to uniquely identify
a particular USB device in a system based on how it connects with
the computer of interest and how different physical devices are
connected.

This module provides the capabilities to identify particular
nodes for visualization as well as selection of nodes as
needed for device control.


"""

from astutus.usb.device_aliases import DeviceAliases  # noqa
from astutus.usb.device_aliases import find_pci_paths  # noqa
from astutus.usb.lcus_1_usb_relay import UsbRelayLcus1  # noqa
from astutus.usb.tree import DeviceConfigurations  # noqa
from astutus.usb.tree import print_tree  # noqa
from astutus.usb.usb_impl import find_busnum_and_devnum_for_sym_link  # noqa
from astutus.usb.usb_impl import find_busnum_and_devnum_for_sys_device  # noqa
from astutus.usb.usb_impl import find_busnum_and_devnum_for_tty  # noqa
from astutus.usb.usb_impl import find_paths_for_vendor_and_product  # noqa
from astutus.usb.usb_impl import find_sym_link_for_tty  # noqa
from astutus.usb.usb_impl import find_tty_description_from_pci_path  # noqa
from astutus.usb.usb_impl import find_tty_for_busnum_and_devnum  # noqa
from astutus.usb.usb_impl import find_vendor_info_from_busnum_and_devnum  # noqa
