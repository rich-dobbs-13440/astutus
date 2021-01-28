# import usb.core
# import usb.util
# import sys


# class find_class(object):
#     def __init__(self, class_):
#         self._class = class_

#     def __call__(self, device):
#         # first, let's check the device
#         if device.bDeviceClass == self._class:
#             return True
#         # ok, transverse all devices to find an
#         # interface that matches our class
#         for cfg in device:
#             # find_descriptor: what's it?
#             intf = usb.util.find_descriptor(
#                                         cfg,
#                                         bInterfaceClass=self._class
#                                 )
#             if intf is not None:
#                 return True

#         return False


# def test_find_all():
#     devices = usb.core.find(find_all=True)
#     # loop through devices, printing vendor and product ids in decimal and hex
#     for device in devices:
#         sys.stdout.write(
#             'Decimal VendorID=' + str(device.idVendor) + ' & ProductID=' + str(device.idProduct) + '\n')
#         sys.stdout.write(
#             'Hexadecimal VendorID=' + hex(device.idVendor) + ' & ProductID=' + hex(device.idProduct) + '\n\n')


# def test_find_all_attributes():
#     devices = usb.core.find(find_all=True)
#     for device in devices:
#         print(f"device: {device}")


# def test_find_all_summary():
#     devices = usb.core.find(find_all=True)
#     for device in devices:
#         print(f"manufacturer: {device.manufacturer}")
#         print(f"product: {device.product}")
#         print(f"serial_number: {device.serial_number}")
#         print("===========================================")


# def test_find_some_summary():
#     excluded_manufacturers = [
#         "Linux 4.15.0-20-generic xhci-hcd",
#         "Linux 4.15.0-20-generic ohci_hcd",
#         "Linux 4.15.0-20-generic ehci_hcd",
#         "Logitech",
#         "PDP",
#         "Realtek",
#         "GenesysLogic",
#     ]
#     excluded_products = [
#         "HD Webcam C615",
#     ]
#     devices = usb.core.find(find_all=True)
#     count = 0
#     for device in devices:
#         count += 1
#         if device.manufacturer in excluded_manufacturers:
#             continue
#         if device.product in excluded_products:
#             continue
#         print(f"device: {device}")
#     print(f"Count of devices: {count}")

# print(f"manufacturer: {device.manufacturer}")
# print(f"product: {device.product}")
# print(f"serial_number: {device.serial_number}")
# print("===========================================")

# def test_usbpy():
#     # find our device
#     dev = usb.core.find(idVendor=0xfffe, idProduct=0x0001)

#     # was it found?
#     if dev is None:
#         raise ValueError('Device not found')

#     # set the active configuration. With no arguments, the first
#     # configuration will be the active one
#     dev.set_configuration()

#     # get an endpoint instance
#     cfg = dev.get_active_configuration()
#     intf = cfg[(0, 0)]

#     def matcher(e):
#         return usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT

#     ep = usb.util.find_descriptor(
#         intf,
#         # match the first OUT endpoint
#         custom_match=matcher
#     )

#     assert ep is not None

#     # write the data
#     ep.write('test')
