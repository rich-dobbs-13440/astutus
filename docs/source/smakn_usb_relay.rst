SMAKN LCUS-1 USB Relay
======================

SMAKN LCUS-1 type USB relay module USB intelligent control switch USB switch $15.60

.. code-block:: console

    device: DEVICE ID 1a86:7523 on Bus 010 Address 016 =================
    bLength                :   0x12 (18 bytes)
    bDescriptorType        :    0x1 Device
    bcdUSB                 :  0x110 USB 1.1
    bDeviceClass           :   0xff Vendor-specific
    bDeviceSubClass        :    0x0
    bDeviceProtocol        :    0x0
    bMaxPacketSize0        :    0x8 (8 bytes)
    idVendor               : 0x1a86
    idProduct              : 0x7523
    bcdDevice              :  0x264 Device 2.64
    iManufacturer          :    0x0 
    iProduct               :    0x2 USB Serial
    iSerialNumber          :    0x0 
    bNumConfigurations     :    0x1
    CONFIGURATION 1: 98 mA ===================================
    bLength              :    0x9 (9 bytes)
    bDescriptorType      :    0x2 Configuration
    wTotalLength         :   0x27 (39 bytes)
    bNumInterfaces       :    0x1
    bConfigurationValue  :    0x1
    iConfiguration       :    0x0 
    bmAttributes         :   0x80 Bus Powered
    bMaxPower            :   0x31 (98 mA)
        INTERFACE 0: Vendor Specific ===========================
        bLength            :    0x9 (9 bytes)
        bDescriptorType    :    0x4 Interface
        bInterfaceNumber   :    0x0
        bAlternateSetting  :    0x0
        bNumEndpoints      :    0x3
        bInterfaceClass    :   0xff Vendor Specific
        bInterfaceSubClass :    0x1
        bInterfaceProtocol :    0x2
        iInterface         :    0x0 
        ENDPOINT 0x82: Bulk IN ===============================
        bLength          :    0x7 (7 bytes)
        bDescriptorType  :    0x5 Endpoint
        bEndpointAddress :   0x82 IN
        bmAttributes     :    0x2 Bulk
        wMaxPacketSize   :   0x20 (32 bytes)
        bInterval        :    0x0
        ENDPOINT 0x2: Bulk OUT ===============================
        bLength          :    0x7 (7 bytes)
        bDescriptorType  :    0x5 Endpoint
        bEndpointAddress :    0x2 OUT
        bmAttributes     :    0x2 Bulk
        wMaxPacketSize   :   0x20 (32 bytes)
        bInterval        :    0x0
        ENDPOINT 0x81: Interrupt IN ==========================
        bLength          :    0x7 (7 bytes)
        bDescriptorType  :    0x5 Endpoint
        bEndpointAddress :   0x81 IN
        bmAttributes     :    0x3 Interrupt
        wMaxPacketSize   :    0x8 (8 bytes)
        bInterval        :    0x1

    >>> test_pyusb.test_find_some_summary()
    device: DEVICE ID 1a86:7523 on Bus 010 Address 017 =================
    bLength                :   0x12 (18 bytes)
    bDescriptorType        :    0x1 Device
    bcdUSB                 :  0x110 USB 1.1
    bDeviceClass           :   0xff Vendor-specific
    bDeviceSubClass        :    0x0
    bDeviceProtocol        :    0x0
    bMaxPacketSize0        :    0x8 (8 bytes)
    idVendor               : 0x1a86
    idProduct              : 0x7523
    bcdDevice              :  0x264 Device 2.64
    iManufacturer          :    0x0 
    iProduct               :    0x2 USB Serial
    iSerialNumber          :    0x0 
    bNumConfigurations     :    0x1
    CONFIGURATION 1: 98 mA ===================================
    bLength              :    0x9 (9 bytes)
    bDescriptorType      :    0x2 Configuration
    wTotalLength         :   0x27 (39 bytes)
    bNumInterfaces       :    0x1
    bConfigurationValue  :    0x1
    iConfiguration       :    0x0 
    bmAttributes         :   0x80 Bus Powered
    bMaxPower            :   0x31 (98 mA)
        INTERFACE 0: Vendor Specific ===========================
        bLength            :    0x9 (9 bytes)
        bDescriptorType    :    0x4 Interface
        bInterfaceNumber   :    0x0
        bAlternateSetting  :    0x0
        bNumEndpoints      :    0x3
        bInterfaceClass    :   0xff Vendor Specific
        bInterfaceSubClass :    0x1
        bInterfaceProtocol :    0x2
        iInterface         :    0x0 
        ENDPOINT 0x82: Bulk IN ===============================
        bLength          :    0x7 (7 bytes)
        bDescriptorType  :    0x5 Endpoint
        bEndpointAddress :   0x82 IN
        bmAttributes     :    0x2 Bulk
        wMaxPacketSize   :   0x20 (32 bytes)
        bInterval        :    0x0
        ENDPOINT 0x2: Bulk OUT ===============================
        bLength          :    0x7 (7 bytes)
        bDescriptorType  :    0x5 Endpoint
        bEndpointAddress :    0x2 OUT
        bmAttributes     :    0x2 Bulk
        wMaxPacketSize   :   0x20 (32 bytes)
        bInterval        :    0x0
        ENDPOINT 0x81: Interrupt IN ==========================
        bLength          :    0x7 (7 bytes)
        bDescriptorType  :    0x5 Endpoint
        bEndpointAddress :   0x81 IN
        bmAttributes     :    0x3 Interrupt
        wMaxPacketSize   :    0x8 (8 bytes)
        bInterval        :    0x1

.. code-block:: console

    (venv) rich@wendy:~/src/github.com/rich-dobbs-13440/astutus/pytests$ lsusb
    Bus 003 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
    Bus 007 Device 001: ID 1d6b:0001 Linux Foundation 1.1 root hub
    Bus 006 Device 001: ID 1d6b:0001 Linux Foundation 1.1 root hub
    Bus 002 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
    Bus 005 Device 001: ID 1d6b:0001 Linux Foundation 1.1 root hub
    Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
    Bus 004 Device 001: ID 1d6b:0001 Linux Foundation 1.1 root hub
    Bus 011 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
    Bus 010 Device 007: ID 046d:082c Logitech, Inc. HD Webcam C615
    Bus 010 Device 005: ID 0e6f:0232 Logic3 
    Bus 010 Device 008: ID 0bda:8153 Realtek Semiconductor Corp. RTL8153 Gigabit Ethernet Adapter
    Bus 010 Device 020: ID 1a86:7523 QinHeng Electronics HL-340 USB-Serial adapter
    Bus 010 Device 021: ID 1a86:7523 QinHeng Electronics HL-340 USB-Serial adapter
    Bus 010 Device 004: ID 05e3:0610 Genesys Logic, Inc. 4-port hub
    Bus 010 Device 003: ID 046d:c52f Logitech, Inc. Unifying Receiver
    Bus 010 Device 002: ID 05e3:0610 Genesys Logic, Inc. 4-port hub
    Bus 010 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
    Bus 009 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
    Bus 008 Device 002: ID 046d:c52b Logitech, Inc. Unifying Receiver
    Bus 008 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
    (venv) rich@wendy:~/src/github.com/rich-dobbs-13440/astutus/pytests$ 