Developer Notes from Before January 27, 2021
============================================

.. note::

  These notes have been edited to remove some of no longer useful information.
  In some cases, the original notes have been incorporated into the application.
  In other cases, the notes reflected the understanding at the time which
  turned out to be wrong

Plan For Starting the Application:

* Note: To control relays, need to be able to select them by topology it turns out.
  Almost nothing that I'm interested in has a persistent unique identifier like a
  serial number attached to it.

* |done| Create USB utilities to understand how to USB and PCI work.

* |done| Create a print_tree routine to visualize topology

* |done| Factor out utilities to make it feasible to uniquely identify relays.

* |done| Create some REST API to drive adoption of Rasberry Pi into ecosystem.

* |done| This requires a persistence layer, so do SQLAlchemy next

* |done| Transfer python package to RaspPi.

* Web inteface to control lights

* Pick out colors of lights with sensor

* |done| Use Sphinx to generate styling for dynamic pages.



Regarding Using the nmap Utility
--------------------------------

To get more information from nmap, it should be run using sudo.

Found this searching the web:

    While OP might have a good reason for wanting to do exactly this, it usually is a bad idea (password can be read by ps, and so on) and I wanted to provide a more secure alternative.

    A better solution if you want to run something with sudo without putting in your password is to allow your user to do exactly that one command without password.

    Open sudoers file with sudo visudo and add the following line (obviously replace the username at the beginning and the command at the end):

    alice ALL = NOPASSWD: /full/path/to/command

    This is explained more here: https://askubuntu.com/a/39294

TODO:

    * Capture modified version of sudoers
    * Document changes needed to get it to work without a password.
    * Detect and prompt user to install it if it is not available.


Pytest
------

pytest -s -p no:logging

pytest -vv -s --log-cli-level=DEBUG --log-cli-format="%(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)" --log-cli-date-format="%Y-%m-%d %H:%M:%S"

Fix it up so path is full.

Olio
----

Linter rstcheck is not installed.

Serial Communication with USB Relay
-----------------------------------


.. code-block:: console

  (venv) rich@wendy:~/src/github.com/rich-dobbs-13440/astutus/pytests$ lsusb -d 1a86:7523
  Bus 010 Device 022: ID 1a86:7523 QinHeng Electronics HL-340 USB-Serial adapter
  Bus 010 Device 021: ID 1a86:7523 QinHeng Electronics HL-340 USB-Serial adapter

  (venv) rich@wendy:~/src/github.com/rich-dobbs-13440/astutus/pytests$ sudo python3

  >>> port = serial.Serial("/dev/ttyUSB1")
  >>> port.baudrate = 9600
  >>> port.bytesize = 8
  >>> port.parity = 'N'
  >>> port.stopbits = 1
  >>> off = bytearray(b'\xA0\x01\x01\xA2')
  >>> on = bytearray(b'\xA0\x01\x00\xA1')
  >>> num = port.write(off)
  >>> num = port.write(on)
  >>> num = port.write(off)
  >>> num = port.write(on)
  >>> port.close()
  >>> exit()

  (venv) rich@wendy:~/src/github.com/rich-dobbs-13440/astutus/pytests$ ls -l /dev/ttyUSB0
  crw-rw---- 1 root dialout 188, 0 Dec 23 14:21 /dev/ttyUSB0

  (venv) rich@wendy:~/src/github.com/rich-dobbs-13440/astutus/pytests$ ls -l /sys/dev/char/188:0
  lrwxrwxrwx 1 root root 0 Dec 23 15:15 /sys/dev/char/188:0 -> ../../devices/pci0000:00/0000:00:07.0/0000:05:00.0/usb10/10-1/10-1.2/10-1.2.3/10-1.2.3:1.0/ttyUSB0/tty/ttyUSB0

  (venv) rich@wendy:~/src/github.com/rich-dobbs-13440/astutus/pytests$ ls -l /dev/ttyUSB0
  crw-rw---- 1 root dialout 188, 0 Dec 23 14:21 /dev/ttyUSB0
  (venv) rich@wendy:~/src/github.com/rich-dobbs-13440/astutus/pytests$ ls -l /sys/dev/char/188:0
  lrwxrwxrwx 1 root root 0 Dec 23 15:15 /sys/dev/char/188:0 -> ../../devices/pci0000:00/0000:00:07.0/0000:05:00.0/usb10/10-1/10-1.2/10-1.2.3/10-1.2.3:1.0/ttyUSB0/tty/ttyUSB0
  (venv) rich@wendy:~/src/github.com/rich-dobbs-13440/astutus/pytests$ ls  ../../devices/pci0000:00/0000:00:07.0/0000:05:00.0/usb10/10-1/10-1.2/10-1.2.3/10-1.2.3:1.0/devnum
  ls: cannot access '../../devices/pci0000:00/0000:00:07.0/0000:05:00.0/usb10/10-1/10-1.2/10-1.2.3/10-1.2.3:1.0/devnum': No such file or directory
  (venv) rich@wendy:~/src/github.com/rich-dobbs-13440/astutus/pytests$ cd /sys/devices/pci0000:00(venv) rich@wendy:/sys/devices/pci0000:00$ ls
  0000:00:00.0  0000:00:05.0  0000:00:11.0  0000:00:13.0  0000:00:14.2  0000:00:14.5  0000:00:18.0  0000:00:18.3  firmware_node  power
  0000:00:02.0  0000:00:06.0  0000:00:12.0  0000:00:13.2  0000:00:14.3  0000:00:16.0  0000:00:18.1  0000:00:18.4  pci_bus        uevent
  0000:00:04.0  0000:00:07.0  0000:00:12.2  0000:00:14.0  0000:00:14.4  0000:00:16.2  0000:00:18.2  0000:00:18.5  PNP0C14:00
  (venv) rich@wendy:/sys/devices/pci0000:00$ cd 0000:00:07.0
  (venv) rich@wendy:/sys/devices/pci0000:00/0000:00:07.0$ ls
  0000:05:00.0          consistent_dma_mask_bits  device           enable         local_cpus      msi_bus    remove    revision                subsystem_device
  broken_parity_status  current_link_speed        dma_mask_bits    firmware_node  max_link_speed  numa_node  rescan    secondary_bus_number    subsystem_vendor
  class                 current_link_width        driver           irq            max_link_width  pci_bus    reset     subordinate_bus_number  uevent
  config                d3cold_allowed            driver_override  local_cpulist  modalias        power      resource  subsystem               vendor
  (venv) rich@wendy:/sys/devices/pci0000:00/0000:00:07.0$ cd 0000\:05\:00.0/
  (venv) rich@wendy:/sys/devices/pci0000:00/0000:00:07.0/0000:05:00.0$ ls
  broken_parity_status      current_link_speed  dma_mask_bits    irq             max_link_width  numa_node  rescan     revision          uevent
  class                     current_link_width  driver           local_cpulist   modalias        pools      reset      subsystem         usb10
  config                    d3cold_allowed      driver_override  local_cpus      msi_bus         power      resource   subsystem_device  usb11
  consistent_dma_mask_bits  device              enable           max_link_speed  msi_irqs        remove     resource0  subsystem_vendor  vendor
  (venv) rich@wendy:/sys/devices/pci0000:00/0000:00:07.0/0000:05:00.0$ cd usb10
  (venv) rich@wendy:/sys/devices/pci0000:00/0000:00:07.0/0000:05:00.0/usb10$ ls
  10-0:1.0            bcdDevice            bmAttributes        busnum         devpath    interface_authorized_default  product    speed
  10-1                bConfigurationValue  bMaxPacketSize0     configuration  driver     ltm_capable                   quirks     subsystem
  authorized          bDeviceClass         bMaxPower           descriptors    ep_00      manufacturer                  removable  uevent
  authorized_default  bDeviceProtocol      bNumConfigurations  dev            idProduct  maxchild                      remove     urbnum
  avoid_reset_quirk   bDeviceSubClass      bNumInterfaces      devnum         idVendor   power                         serial     version
  (venv) rich@wendy:/sys/devices/pci0000:00/0000:00:07.0/0000:05:00.0/usb10$ cd busnum
  bash: cd: busnum: Not a directory
  (venv) rich@wendy:/sys/devices/pci0000:00/0000:00:07.0/0000:05:00.0/usb10$ cat busnum
  10
  (venv) rich@wendy:/sys/devices/pci0000:00/0000:00:07.0/0000:05:00.0/usb10$ cat devnum
  1
  (venv) rich@wendy:/sys/devices/pci0000:00/0000:00:07.0/0000:05:00.0/usb10$


  (venv) rich@wendy:/sys/devices$ grep -r . -e "1a86" 2>/dev/null


  Bus (\d+) Device (\d+)

  Bus (\d+) Device (\d+): ID ([0-9,af]{4}):([0-9,a-f]{4}) (.*)


https://askubuntu.com/questions/373096/how-do-i-permanently-change-permissions-for-dev-ttys0#373269

There's no need to change system file's permissions. The serial devices have the following default permissions:

crw-rw---- 1 root dialout ... /dev/ttyS0
So all you have to do is add the user to the dialout group:

sudo adduser $USER dialout





.. code-block:: console

  rich@wendy:~$ lsusb --tree
  /:  Bus 11.Port 1: Dev 1, Class=root_hub, Driver=xhci_hcd/2p, 5000M
  /:  Bus 10.Port 1: Dev 1, Class=root_hub, Driver=xhci_hcd/2p, 480M
      |__ Port 1: Dev 2, If 0, Class=Hub, Driver=hub/4p, 480M
          |__ Port 1: Dev 3, If 0, Class=Human Interface Device, Driver=usbhid, 12M
          |__ Port 1: Dev 3, If 1, Class=Human Interface Device, Driver=usbhid, 12M
          |__ Port 2: Dev 4, If 0, Class=Hub, Driver=hub/4p, 480M
              |__ Port 1: Dev 11, If 0, Class=Vendor Specific Class, Driver=ch341, 12M
              |__ Port 4: Dev 9, If 0, Class=Vendor Specific Class, Driver=r8152, 480M
              |__ Port 2: Dev 13, If 2, Class=Audio, Driver=snd-usb-audio, 12M
              |__ Port 2: Dev 13, If 0, Class=Audio, Driver=snd-usb-audio, 12M
              |__ Port 2: Dev 13, If 3, Class=Human Interface Device, Driver=usbhid, 12M
              |__ Port 2: Dev 13, If 1, Class=Audio, Driver=snd-usb-audio, 12M
              |__ Port 3: Dev 15, If 0, Class=Imaging, Driver=usbfs, 480M
          |__ Port 3: Dev 14, If 0, Class=Vendor Specific Class, Driver=ch341, 12M
          |__ Port 4: Dev 7, If 0, Class=Audio, Driver=snd-usb-audio, 480M
          |__ Port 4: Dev 7, If 3, Class=Video, Driver=uvcvideo, 480M
          |__ Port 4: Dev 7, If 1, Class=Audio, Driver=snd-usb-audio, 480M
          |__ Port 4: Dev 7, If 2, Class=Video, Driver=uvcvideo, 480M
  /:  Bus 09.Port 1: Dev 1, Class=root_hub, Driver=xhci_hcd/2p, 5000M
  /:  Bus 08.Port 1: Dev 1, Class=root_hub, Driver=xhci_hcd/2p, 480M
      |__ Port 1: Dev 2, If 0, Class=Human Interface Device, Driver=usbhid, 12M
      |__ Port 1: Dev 2, If 1, Class=Human Interface Device, Driver=usbhid, 12M
      |__ Port 1: Dev 2, If 2, Class=Human Interface Device, Driver=usbhid, 12M
  /:  Bus 07.Port 1: Dev 1, Class=root_hub, Driver=ohci-pci/4p, 12M
  /:  Bus 06.Port 1: Dev 1, Class=root_hub, Driver=ohci-pci/2p, 12M
  /:  Bus 05.Port 1: Dev 1, Class=root_hub, Driver=ohci-pci/5p, 12M
  /:  Bus 04.Port 1: Dev 1, Class=root_hub, Driver=ohci-pci/5p, 12M
  /:  Bus 03.Port 1: Dev 1, Class=root_hub, Driver=ehci-pci/4p, 480M
  /:  Bus 02.Port 1: Dev 1, Class=root_hub, Driver=ehci-pci/5p, 480M
  /:  Bus 01.Port 1: Dev 1, Class=root_hub, Driver=ehci-pci/5p, 480M


  rich@wendy:~$ lsusb
  Bus 003 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
  Bus 007 Device 001: ID 1d6b:0001 Linux Foundation 1.1 root hub
  Bus 006 Device 001: ID 1d6b:0001 Linux Foundation 1.1 root hub
  Bus 002 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
  Bus 005 Device 001: ID 1d6b:0001 Linux Foundation 1.1 root hub
  Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
  Bus 004 Device 001: ID 1d6b:0001 Linux Foundation 1.1 root hub
  Bus 011 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
  Bus 010 Device 007: ID 046d:082c Logitech, Inc. HD Webcam C615
  Bus 010 Device 014: ID 1a86:7523 QinHeng Electronics HL-340 USB-Serial adapter
  Bus 010 Device 020: ID 0bda:8153 Realtek Semiconductor Corp. RTL8153 Gigabit Ethernet Adapter
  Bus 010 Device 030: ID 14cd:125d Super Top
  Bus 010 Device 022: ID 0e6f:0232 Logic3
  Bus 010 Device 031: ID 04e8:6860 Samsung Electronics Co., Ltd Galaxy series, misc. (MTP mode)
  Bus 010 Device 016: ID 05e3:0610 Genesys Logic, Inc. 4-port hub
  Bus 010 Device 003: ID 046d:c52f Logitech, Inc. Unifying Receiver
  Bus 010 Device 002: ID 05e3:0610 Genesys Logic, Inc. 4-port hub
  Bus 010 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
  Bus 009 Device 003: ID 0bda:8153 Realtek Semiconductor Corp. RTL8153 Gigabit Ethernet Adapter
  Bus 009 Device 002: ID 05e3:0612 Genesys Logic, Inc. Hub
  Bus 009 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
  Bus 008 Device 007: ID 046d:c52b Logitech, Inc. Unifying Receiver
  Bus 008 Device 006: ID 046d:c52b Logitech, Inc. Unifying Receiver
  Bus 008 Device 003: ID 05e3:0610 Genesys Logic, Inc. 4-port hub
  Bus 008 Device 002: ID 046d:c52b Logitech, Inc. Unifying Receiver
  Bus 008 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub



  FileNotFoundError: [Errno 2] No such file or directory: '/tmp/try-astutus/astutus/packaging/dist/venv/lib/python3.8/site-packages/astutus/web/static/_docs/source/developer_notes.html'




Deprecation Warning
-------------------

2020-12-28 18:36 Warning showed up in Pytest with most recent venv:

.. code-block:: console

    ================================================================================================ warnings summary =================================================================================================
  ../venv/lib/python3.8/site-packages/future/standard_library/__init__.py:65
    /home/rich/src/github.com/rich-dobbs-13440/astutus/venv/lib/python3.8/site-packages/future/standard_library/__init__.py:65: DeprecationWarning: the imp module is deprecated in favour of importlib; see the module's documentation for alternative uses
      import imp

  -- Docs: https://docs.pytest.org/en/stable/warnings.html





Different Selector Syntax Idea
------------------------------

pci(0x1002:0x5a1b)/pci(0x1b21:0x1042)/usb(1d6b:0002)/usb(05e3:0610)/usb(1a86:7523)

Convert node to list

Do a match based on that.

Add a capability to astutus-usb-tree to list out paths for a selected node.

Do it in JSON format, that can be plopped into aliases and then modified.

Breadcrump Navigation
---------------------

.. code-block::  html

    <div role="navigation" aria-label="breadcrumbs navigation">
    <ul class="wy-breadcrumbs">
    <li><a href="/astutus/doc/index.html" class="icon icon-home"></a> &raquo;</li>
    <li><a href="../maintanence/guidelines.html">Guidelines for Maintaining the System</a> &raquo;</li>
    <li><a href="template_index.html">Flask Application Templates</a> &raquo;</li>
    <li>USB Tree</li>
    <li class="wy-breadcrumbs-aside">
    <a href="../_sources/flask_app_templates/flask_app_dyn_usb.rst.txt" rel="nofollow"> View page source</a>
    </li>
    </ul>
    <hr/>
    </div>

Favicon For Website
-------------------

https://favicon.io/

First, use the download button to download the files listed below.
Place the files in the root directory of your website:

  * android-chrome-192x192.png
  * android-chrome-512x512.png
  * apple-touch-icon.png
  * favicon-16x16.png
  * favicon-32x32.png
  * favicon.ico
  * site.webmanifest

Next, copy the following link tags and paste them into the head of your HTML.

.. code-block::  html

  <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
  <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
  <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
  <link rel="manifest" href="/site.webmanifest">


Installing On Raspberry Pi
--------------------------

.. code-block:: console

  Could not find a version that satisfies the requirement treelib (from astutus) (from versions: )
  No matching distribution found for treelib (from astutus)

  Collecting SQLAlchemy>=0.8.0 (from flask-sqlalchemy->astutus)
  Could not find a version that satisfies the requirement SQLAlchemy>=0.8.0 (from flask-sqlalchemy->astutus) (from versions: )
  No matching distribution found for SQLAlchemy>=0.8.0 (from flask-sqlalchemy->astutus)

  Collecting pyyaml>=3.13 (from serial->astutus)
  Could not find a version that satisfies the requirement pyyaml>=3.13 (from serial->astutus) (from versions: )
  No matching distribution found for pyyaml>=3.13 (from serial->astutus)


  pip3 install --no-index --find-links=. astutus

Dynamic TOC Tree
----------------

Here is structure of toc generated on the page for the toctree directive:

.. code-block:: html

  <div class="toctree-wrapper compound">
      <p class="caption"><span class="caption-text">Contents:</span></p>
      <ul>
        <li class="toctree-l1"><a class="reference internal" href="flask_app_dyn_usb_device.html">USB Device Tree</a></li>
        <li class="toctree-l1"><a class="reference internal" href="flask_app_dyn_usb_alias.html">USB Aliases</a></li>
        <li class="toctree-l1"><a class="reference internal" href="flask_app_dyn_usb_configuration.html">Device Configurations</a></li>
        </ul>
      </div>