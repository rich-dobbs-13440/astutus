Developer Notes
===============



Plan:

* Create some REST API to drive adoption of Rasberry Pi into ecosystem.

* This requires a persistence layer, so do SQLAlchemy next

* Transfer python package to RaspPi.

* Web inteface to control lights

* Pick out colors of lights with sensor

* Web interface - how to get styling??? Try to use Sphinx to generate styled pages
  with appropriate forms???



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

    * Capture modified version of sudoers and document change.

Running Flask from a package
----------------------------


import astutus.web.flask_app
astutus.web.flask_app.run_with_standard_options()

This doesn't seem to work.  Instead just use main()


>>> import astutus.web.flask_app
>>> db.create_all()
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
NameError: name 'db' is not defined
>>> astutus.web.flask_app.db.create_all()

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

  Bus (\d+) Device (\d+): ID ([0-9,a-e]{4}):([0-9,a-e]{4}) (.*)


https://askubuntu.com/questions/373096/how-do-i-permanently-change-permissions-for-dev-ttys0#373269

There's no need to change system file's permissions. The serial devices have the following default permissions:

crw-rw---- 1 root dialout ... /dev/ttyS0
So all you have to do is add the user to the dialout group:

sudo adduser $USER dialout