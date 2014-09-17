#! /usr/bin/python
import sys
import pyfits
from os import listdir
from datetime import datetime

dir = sys.argv[1]
files = listdir(dir)


time_file_pairs = []
for f in files:
    if ".fits" in f:
        t = datetime.strptime(f[20:],"%Y-%m-%dT%H%M%S.fits")
        time_file_pairs.append((t,f))

time_file_pairs = sorted(time_file_pairs)

for i in range(0,len(time_file_pairs),20):
    try:
        f = time_file_pairs[i][1]
        h = pyfits.open(dir+"/"+f)
        print h[0].header['DATE'], h[1].header['VOLTAGE'], h[1].header['GPSLAT'] > 0, h[1].header['HUMIDITY'], h[1].header['TSENSOR0'], h[1].header['TSENSOR1'], h[1].header['TSENSOR2'], h[1].header['TSENSOR3'], h[1].header['TSENSOR4'], h[1].header['TSENSOR5'], h[1].header['TSENSOR6']
        h.close()
    except:
        pass


