#! /usr/bin/python
# -*- coding: latin-1 -*-

import sys

from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.dates import DAILY, YEARLY, DateFormatter, rrulewrapper, RRuleLocator, drange

date = []
voltage = []
gps_on = []
humidity = []
temp0 = []
temp1 = []
temp2 = []
temp3 = []
temp4 = []

f = open(sys.argv[1])
lines = f.readlines()
for l in lines:
    splt = l.split(" ")
    date_str = splt[0]

    date.append( datetime.strptime(date_str,"%Y-%m-%dT%H%M%S.%f") )
    voltage.append( float(splt[1]) )
    gps_on.append( (splt[2] == "True") )
    humidity.append( float(splt[3]) )
    temp0.append( float(splt[4]) )
    temp1.append( float(splt[5]) )
    temp2.append( float(splt[6]) )
    temp3.append( float(splt[7]) )
    temp4.append( float(splt[8]) )

fig, (ax0, ax1, ax2, ax3) = plt.subplots(nrows=4, sharex=True)
formatter = DateFormatter('%d/%m/%y')
rule = rrulewrapper(DAILY)
loc = RRuleLocator(rule)

ax0.plot(date,voltage, ".")
ax0.xaxis.set_major_formatter(formatter)
ax0.xaxis.set_major_locator(loc)
ax0.set_title("voltage (V)")

ax1.plot(date,temp0, ".")
ax1.plot(date,temp1, ".")
ax1.plot(date,temp2, ".")
ax1.plot(date,temp3, ".")
ax1.plot(date,temp4, ".")
ax1.xaxis.set_major_formatter(formatter)
ax1.xaxis.set_major_locator(loc)
ax1.set_title("temperature (degC)")

ax2.plot(date, humidity, ".")
ax2.xaxis.set_major_formatter(formatter)
ax2.xaxis.set_major_locator(loc)
ax2.set_title("humidity (%)")

ax3.plot(date, gps_on, ".")
ax3.xaxis.set_major_formatter(formatter)
ax3.xaxis.set_major_locator(loc)
ax3.set_title("gps on (bool)")
ax3.set_ylim((-0.1,1.1))

labels = ax3.get_xticklabels()
plt.setp(labels, rotation=30, fontsize=10)
plt.show()

