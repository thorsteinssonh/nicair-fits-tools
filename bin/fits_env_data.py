#! /usr/bin/python
import sys
import pyfits

h = pyfits.open(sys.argv[1])

print h[0].header['DATE'], h[1].header['VOLTAGE'], h[1].header['GPSLAT'] > 0, h[1].header['HUMIDITY'], h[1].header['TSENSOR0'], h[1].header['TSENSOR1'], h[1].header['TSENSOR2'], h[1].header['TSENSOR3'], h[1].header['TSENSOR4'], h[1].header['TSENSOR5'], h[1].header['TSENSOR6']





