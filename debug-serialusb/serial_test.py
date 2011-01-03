from __future__ import print_function

import optparse
import sys

import serial

BAUD = 9600
MAX_TRANS_SIZE = 60
ERROR_CHAR = '*'
NONBLOCKING_TIMEOUT = 2.5       # seconds

def serial_tx_only(port,baudrate=BAUD):
    ser = serial.Serial(port, baudrate=baudrate)

    size = 1
    val = 1
    while True:
        print('size = {0}'.format(size))
        s = str(val)*size
        print('writing packet - len,val: {0},{1}'.format(len(s),s))
        ser.write(s)
        print('wrote packet')
        print('got back {0}'.format(ser.readline().strip()))

        size *= 2
        val += 1
        if size > MAX_TRANS_SIZE:
            size = 1
            val = 1

def serial_echo(port, baudrate=BAUD):
    ser = serial.Serial(port, baudrate=baudrate)
    while True:
        print(ser.read(), end='')

def serial_roundtrip(port, baudrate=BAUD):
    ser = serial.Serial(port, baudrate=baudrate)

    size = 1
    while True:
        print('Handshake: "{0}"'.format(ser.readline().strip()))
        print('size = {0}'.format(size))
        s = ser.read(size)
        print('read buffer ({0}B):    "{1}"'.format(len(s), s))
        nbytes = ser.write(s)
        if nbytes == len(s):
            print('sent buffer back ({0}B)'.format(nbytes))
        else:
            raise RuntimeError('nbytes {0} != size {1}'.format(nbytes, size))

        s = nonblocking_read(ser, size)
        print('read buffer response: "{1}"'.format(len(s), s))
        if ERROR_CHAR in s or len(s) < size:
            raise RuntimeError('not enough bytes (expected {0}): "{1}"'.format(
                    size, s))

        print()

        size *= 2
        if size > MAX_TRANS_SIZE:
            size = 1

def nonblocking_read(ser, nbytes=1):
    old = ser.timeout
    try:
        ser.timeout = NONBLOCKING_TIMEOUT
        return ser.read(nbytes)
    finally:
        ser.timeout = old

if __name__ == '__main__':
    parser = optparse.OptionParser(usage='usage: %prog [options] port')
    parser.add_option('-b', '--baud-rate', default=BAUD,
                      help='Baud rate (Kbps), default {0}'.format(BAUD))
    parser.add_option('-t', '--only-send', default=False,
                      help='Only send bytes')
    parser.add_option('-e', '--echo', default=None,
                      help='Echo bytes received from port ECHO')

    opts, args = parser.parse_args()

    def usage(msg, fatal=True):
        if fatal: print ('Error: ', end='')
        print(msg)
        parser.print_help()
        if fatal: sys.exit(1)

    if opts.only_send and opts.echo:
        usage('Cannot specify both -e and -t options')

    if opts.only_send:
        serial_tx_only(port, baudrate=opts.baud_rate)
    elif opts.echo:
        print('echoing output from port {0}'.format(opts.echo))
        serial_echo(opts.echo, baudrate=opts.baud_rate)
    elif len(args) != 1:
        usage('Must specify exactly one serial port.')
    else:
        print('testing virtual comm port {0}'.format(args[0]))
        serial_roundtrip(args[0], baudrate=opts.baud_rate)