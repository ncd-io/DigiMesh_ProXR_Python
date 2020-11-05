from __future__ import absolute_import
from __future__ import print_function, unicode_literals
from digi.xbee.devices import XBeeDevice
from digi.xbee.devices import RemoteXBeeDevice
from digi.xbee.devices import XBee64BitAddress


import codecs
import os
import sys
import threading
import glob
import time

import serial

from serial.tools.list_ports import comports
from serial.tools import hexlify_codec


from pprint import pprint

def serial_ports():
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/cu[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/cu.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

port_array = {}

print(" +--------------+")
print(" | ProXR Sample |")
print(" +--------------+\n")

print('Scanning for Serial Ports')
print('Please wait for the scan to complete')
print('Serial Port Options:')

for serial_port in serial_ports():
    sp_key = len(port_array)+1
    port_array.update({str(sp_key): serial_port})

for serial_port in port_array:
    print('[' + serial_port + ']: ' + port_array.get(serial_port))
print('')
target_port_key = input('Please enter the number of the desired Serial Port above: ')
port = port_array.get(target_port_key)

#instanciate object to communicate through
device = XBeeDevice(port, 115200)

try:

    #Open connection to the XBee modem and scan for other wireless devices
    device.open()
    print('Port open to modem, scanning for devices')
    xbee_network = device.get_network()
    xbee_network.set_discovery_timeout(15)
    xbee_network.clear()
    remote_array = []
    def callback_device_discovered(remote):
        remote_array.append(remote)
    xbee_network.add_device_discovered_callback(callback_device_discovered)
    xbee_network.start_discovery_process()

except:
    print('Failed to communicate with modem')
    exit(1)

while xbee_network.is_discovery_running():
    time.sleep(0.5)

#scan is complete so display devices to user
i = 1
for remote in remote_array:
    print('[',i,']: ',remote)
    i=i+1

remoteIndex = int(input('Please enter the number of the desired remote address above:'))

REMOTE_NODE_ID = remote_array[remoteIndex-1].get_64bit_addr()

remote_device = RemoteXBeeDevice(device, REMOTE_NODE_ID)

print('enter exit at anytime to stop the program')

#run this loop forever or until the user enters exit to stop the program
while True:
    command = input('Enter Command: ')
    if command == 'exit':
        if device is not None and device.is_open():
            print('closing connection to modem')
            device.close()
            print('exitiing application')
        break
    list = command.split(',')
    commandBytes = bytearray(map(int, list))

    try:
        device.send_data(remote_device, commandBytes, len(commandBytes))
        print('command sent')
    except:
        print('Transmission failed')
sys.exit(0)
