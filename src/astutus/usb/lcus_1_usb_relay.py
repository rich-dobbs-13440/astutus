# sudo adduser $USER dialout

# Need to reboot or log off then back on????

#   (venv) rich@wendy:~/src/github.com/rich-dobbs-13440/astutus/pytests$ lsusb -d 1a86:7523
#   Bus 010 Device 022: ID 1a86:7523 QinHeng Electronics HL-340 USB-Serial adapter
#   Bus 010 Device 021: ID 1a86:7523 QinHeng Electronics HL-340 USB-Serial adapter

#   (venv) rich@wendy:~/src/github.com/rich-dobbs-13440/astutus/pytests$ sudo python3

#   >>> port = serial.Serial("/dev/ttyUSB1")
#   >>> port.baudrate = 9600
#   >>> port.bytesize = 8
#   >>> port.parity = 'N'
#   >>> port.stopbits = 1
#   >>> off = bytearray(b'\xA0\x01\x01\xA2')
#   >>> on = bytearray(b'\xA0\x01\x00\xA1')
#   >>> num = port.write(off)
#   >>> num = port.write(on)
#   >>> num = port.write(off)
#   >>> num = port.write(on)
#   >>> port.close()
#   >>> exit()
import serial


class SerialPort:

    def __init__(self, *, tty_dev, baudrate, bytesize=8, parity='N', stopbits=1):
        self.tty_dev = tty_dev
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.parity = parity
        self.stopbits = stopbits
        self.port = None

    def open(self):
        port = serial.Serial(self.tty_dev)
        port.baudrate = self.baudrate
        port.bytesize = self.bytesize
        port.parity = self.parity
        port.stopbits = self.stopbits
        self.port = port

    def close(self):
        self.port.close()
        self.port = None

    def write(self, bytes: bytearray):
        return self.port.write(bytes)


class UsbRelayLcus1():

    OFF_SIGNAL = bytearray(b'\xA0\x01\x01\xA2')
    ON_SIGNAL = bytearray(b'\xA0\x01\x00\xA1')

    def __init__(self, tty_dev):
        self.tty_dev = tty_dev
        self.serial_port = SerialPort(tty_dev=tty_dev, baudrate=9600, parity='N', stopbits=1)

    def __enter__(self):
        self.serial_port.open()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.serial_port.close()

    def turn_on(self):
        self.serial_port.write(self.ON_SIGNAL)

    def turn_off(self):
        self.serial_port.write(self.OFF_SIGNAL)
