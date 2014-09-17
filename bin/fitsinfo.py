#! /usr/bin/python
import sys
import pyfits

h = pyfits.open(sys.argv[1])
h.info()
print "FRAMENO:", h[0].header['FRAMENO']
print "EXPOSURE:", h[0].header['EXPOSURE'], "microseconds"
print "----------------------------------------------------------------"
for i in range(1,len(h)):
	print i, h[i].header['OBSUNIT']

