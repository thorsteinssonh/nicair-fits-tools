#! /usr/bin/python
# -*- coding: latin-1 -*-

import os
import sys
import numpy
import pyfits
from pydecorate import DecoratorAGG
import aggdraw
from datetime import datetime
import math

NICAIR_SENSOR_BIASES = {
'nicair2-002':{'TILTXBIAS':35.3,'TILTYBIAS':-0.5},
'nicair2-003':{'TILTXBIAS':34.2,'TILTYBIAS':0.5},
'nicair2-004':{'TILTXBIAS':35.3,'TILTYBIAS':-0.5},
}

PERLAN={'POSITION':(-21.918883, 64.129184, 60.0),'NAME':"Perlan",'TICK_DISTANCE':10.0} # (-16.837, 64.869, 760.0),'NAME':"Holuhraun")
SJOMAN={'POSITION':(-21.902533, 64.139257, 42.0),'NAME':"Sjomannaskoli",'TICK_DISTANCE':20.0} # (-16.837, 64.869, 760.0),'NAME':"Holuhraun")
SALURI={'POSITION':(-21.909109,64.111823, 37.0),'NAME':"Salurinn",'TICK_DISTANCE':20.0} # (-16.837, 64.869, 760.0),'NAME':"Holuhraun")

CAMERA_TARGETS = {
'nicair2-002':PERLAN,
'nicair2-003':SJOMAN,
'nicair2-004':SJOMAN
}

CAMERA_HEIGHT_OVERRIDE = {
'nicair2-002':61.0,
'nicair2-003':61.0,
'nicair2-004':61.0
}

try:
    font = aggdraw.Font("black","/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",size=10)
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
except IOError:
    font = aggdraw.Font("black","/usr/share/fonts/truetype/ttf-dejavu/DejaVuSerif.ttf",size=10)
    font_path = "/usr/share/fonts/truetype/ttf-dejavu/DejaVuSerif.ttf"

def distance_longlat(longlat1,longlat2):
    R = 6371.0
    phi1 = longlat1[1]*math.pi/180.0
    phi2 = longlat2[1]*math.pi/180.0
    lam1 = longlat1[0]*math.pi/180.0
    lam2 = longlat2[0]*math.pi/180.0
    dphi = phi2 - phi1
    dlam = lam2 - lam1

    a = math.sin(dphi/2.0)**2.0 + math.cos(phi1)*math.cos(phi2)*(math.sin(dlam/2.0)**2.0)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = R * c
    return d

def draw_text(img, xy, txt='', color="black", size=12, opacity=255, align="ul", rotation=0.0):
    # set font
    try:
        f = aggdraw.Font(color, "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", size=size, opacity=opacity)
    except IOError:
        f = aggdraw.Font(color, "/usr/share/fonts/truetype/ttf-dejavu/DejaVuSerif.ttf", size=size, opacity=opacity)
    drawer = aggdraw.Draw(img)
    # text widht,height
    w,h = drawer.textsize(txt, f)
    # set align and margin
    if align == "ul":
        adjusted_xy = xy
    elif align == "cl":
        adjusted_xy = (xy[0], xy[1]-h/2)
    elif align == "bl":
        adjusted_xy = (xy[0], xy[1]-h)
    elif align == "ur":
        adjusted_xy = (xy[0]-w, xy[1])
    elif align == "cr":
        adjusted_xy = (xy[0]-w, xy[1]-h/2)
    elif align == "br":
        adjusted_xy = (xy[0]-w, xy[1]-h)
    else:
        adjusted_xy = xy
    # set tansform for rotation
    if rotation != 0.0:
        rot_rad = rotation*math.pi/180.0
        affine = (math.cos(rot_rad),
                  math.sin(rot_rad),
                  adjusted_xy[0],
                  -math.sin(rot_rad),
                  math.cos(rot_rad),                 
                  adjusted_xy[1])
        drawer.settransform(affine)
        drawer.text((0.0,0.0), txt, f)
    else:
        drawer.text(adjusted_xy, txt, f)
    drawer.flush()

def draw_texts(img, texts):
    for k in range(len(texts[0])):
        draw_text(img, texts[0][k], **(texts[1][k]))

def draw_line(img, xy1, xy2, color="black", width=1, opacity=255):
    drawer = aggdraw.Draw(img)
    p = aggdraw.Pen(color,width, opacity)
    drawer.line((xy1[0],xy1[1],xy2[0],xy2[1]),p)
    drawer.flush()

def draw_lines(img, lines):
    for k in range(len(lines[0])):
        draw_line(img, lines[0][k], lines[1][k], **(lines[2][k]))

def prepare_graticule(nx, ny, distance=None, vfov=None, tilt=None, 
                      tick_distance=100.0, height=0.0, target_height=0.0, target_name=""):
    # tick size
    tick_size = 20
    # km per pixel calculation
    km_p_px = distance*math.tan(vfov*math.pi/180.0)/ny
    print "no pixels per 100m:", 0.1/km_p_px
    # calculate horizon center
    tilt_x = tilt[0]
    tilt_y = tilt[1]
    hcent = ( nx/2.0, ((vfov/2.0 + tilt_x)/vfov)*ny )
    # volcano baseline point (w.r.t. hcent)
    dh = height - target_height
    bcent = ( 0.0, dh/1000.0/km_p_px )
    lines = [[],[],[]]
    texts = [[],[]]
    # horizon
    lines[0].append( (-nx, 0.0) )
    lines[1].append( ( nx, 0.0) )
    lines[2].append( {} )
    texts[0].append( (-nx/3.0, 0.0) )
    texts[1].append( {"txt":"camera alt:%.0fm"%(height), "rotation":tilt_y} )
    # vertical
    lines[0].append( (0.0, -ny) )
    lines[1].append( (0.0, bcent[1]) )
    lines[2].append( {} )
    # target base-line
    print "bcent:", bcent
    lines[0].append( (bcent[0]-2*tick_size, bcent[1]) )
    lines[1].append( (bcent[0]+2*tick_size, bcent[1]) )
    lines[2].append( {"color":"black", "width":2} )
    texts[0].append( (bcent[0]+2*tick_size+5, bcent[1]) )
    texts[1].append( {"txt":"targ:%s|alt:%.0fm"%(target_name, target_height),"color":"black","align":"cl", "rotation":tilt_y} )
    # tick marks (100m space)
    tick_space = tick_distance/1000.0/km_p_px
    modulus_margin_distance = target_height % tick_distance
    modulus_margin_space = (modulus_margin_distance)/1000.0/km_p_px
    for i in range(1, abs(int(2*(bcent[1]+hcent[1])/tick_space))):
        lines[0].append( (bcent[0]-tick_size, bcent[1]+modulus_margin_space-i*tick_space) )
        lines[1].append( (bcent[0]+tick_size, bcent[1]+modulus_margin_space-i*tick_space) )
        lines[2].append( {"color":"black"} )
        texts[0].append( (bcent[0]+tick_size+5, bcent[1]+modulus_margin_space-i*tick_space) )
        texts[1].append( {"txt":"%.0fm"%(target_height-modulus_margin_distance+i*tick_distance), "align":"cl", "color":"black", "rotation":tilt_y} )
    # center and rotate by tilt angles
    tilt_y_rad = tilt_y*math.pi/180.0
    for i in range(len(lines[0])):
        x1 = lines[0][i][0]
        x2 = lines[1][i][0]
        y1 = lines[0][i][1]
        y2 = lines[1][i][1]
        # apply rotation
        r = (x1**2 + y1**2)**0.5
        theta = math.atan2(x1,y1)
        x1 = r*math.sin(theta+tilt_y_rad)
        y1 = r*math.cos(theta+tilt_y_rad)
        r = (x2**2 + y2**2)**0.5
        theta = math.atan2(x2,y2)
        x2 = r*math.sin(theta+tilt_y_rad)
        y2 = r*math.cos(theta+tilt_y_rad)
        # apply center
        lines[0][i] = ( x1 + hcent[0], y1 + hcent[1] )
        lines[1][i] = ( x2 + hcent[0], y2 + hcent[1] )
    for i in range(len(texts[0])):
        x1 = texts[0][i][0]
        y1 = texts[0][i][1]
        # apply rotation
        r = (x1**2 + y1**2)**0.5
        theta = math.atan2(x1,y1)
        x1 = r*math.sin(theta+tilt_y_rad)
        y1 = r*math.cos(theta+tilt_y_rad)
        # apply center
        texts[0][i] = ( x1 + hcent[0], y1 + hcent[1] )
        
    return lines, texts

from trollimage.image import Image
from trollimage.colormap import spectral as rainbow
rainbow.reverse()

def plot(data, text, minmax=None, transpose=False, 
         filename=None, position=(-16.743860721,64.915348712,712.4), 
         tilt=None, target_position=None, target_name="", vfov=18.5, tick_distance=50.0):

    if transpose:
        data = data.transpose()

    if minmax is None:
        rainbow.set_range(data.min(),data.max())
    else:
        rainbow.set_range(minmax[0],minmax[1])


    img = Image(data, mode="L")
    img.colorize(rainbow)
    img = img.pil_image()
    
    # Decoration
    dc = DecoratorAGG(img)
    dc.align_bottom()
    #dc.add_logo("/home/sat/dev/pydecorate/logos/VI_Logo_Transp.png")
    #dc.add_logo("Nicarnica-Aviation-22-oct-300x102.png")
    try:
        dc.add_logo("/home/master/bin/futurevolc_logo.png", height=47)
        dc.add_logo("/home/master/bin/nicarnica_logo.png")
        dc.add_logo("/home/master/bin/vi_logo.png")
    except IOError:
        dc.add_logo("bin/futurevolc_logo.png", height=47)
        dc.add_logo("bin/nicarnica_logo.png")
        dc.add_logo("bin/vi_logo.png")

    dc.add_text(text, font=font)
    tick_space = 5.0
    #dc.add_scale(rainbow, extend=True, unit='°C', tick_marks=tick_space, minor_tick_marks=tick_space)

    # target distance and km/px
    ny = data.shape[0]
    nx = data.shape[1]
    distance = distance_longlat(target_position,position)
    
    # plot grid
    lines, texts = prepare_graticule(nx, ny, distance=distance, vfov=vfov, 
                                     tilt=tilt, tick_distance=tick_distance,
                                     height=position[2],target_height=target_position[2],
                                     target_name=target_name)
    draw_lines(img, lines)
    draw_texts(img, texts)

    if filename == None:
        img.show()
    else:
        img.save(filename, "JPEG", quality=90)


records = pyfits.open(str(sys.argv[1]))
records.info()

# obs time
tstr = records[0].header['DATE']
t = datetime.strptime(tstr,"%Y-%m-%dT%H%M%S.%f")
print type(t), t

# system / camera id
camsystem = records[0].header['SYSTEM']
camserial = records[0].header['PRODID']

for i, x in enumerate(records):
    if i>0:
        print x.header['OBSUNIT']

if CAMERA_HEIGHT_OVERRIDE[camserial]:
    gps_position = ( records[1].header['GPSLONG'], records[1].header['GPSLAT'], CAMERA_HEIGHT_OVERRIDE[camserial] )
else:
    gps_position = ( records[1].header['GPSLONG'], records[1].header['GPSLAT'], records[1].header['GPSALT'] )
voltage = records[1].header['VOLTAGE']
if voltage == "NAN":
    voltage = -99
temperature = records[1].header['TSENSOR1']
if temperature == "NAN":
    temperature = -99
humidity = records[1].header['HUMIDITY']
if humidity == "NAN":
    humidity = -99

for r in records:
    if 'OBSUNIT' in r.header:
        if r.header['OBSUNIT'] == "BRIGHT":
            # position
            tilt_x = r.header['TILTX'] + NICAIR_SENSOR_BIASES[camserial]['TILTXBIAS']
            tilt_y = r.header['TILTY'] + NICAIR_SENSOR_BIASES[camserial]['TILTYBIAS']
            # wavelength
            wavel = r.header['IRFILTER']
            # data
            data = r.data
            davg = numpy.average(data)
            dstd = numpy.std(data)
            dmin = davg - 1.5*dstd
            dmax = davg + 2.5*dstd
            outname = "webcam_"+camserial+"_BT%.0f"%(float(wavel)*10)+"_{0:%Y%m%d_%H%M%S}".format(t)+".jpg"
            text_label = camserial+" TIR %s"%(wavel)+" V{1:.1f}/T{2:.1f}/H{3:.0f}/DMM{4:.0f}\n{0:%Y.%m.%d %H:%M:%S}\nTESTING|UNCALIBRATED".format(t,voltage, temperature, humidity,dmax-dmin) 
            plot(data, text_label, 
                 minmax=(dmin,dmax), filename=outname,
                 position=gps_position,
                 tilt=(tilt_x, tilt_y),
                 target_position=CAMERA_TARGETS[camserial]['POSITION'],
                 target_name=CAMERA_TARGETS[camserial]['NAME'],
                 tick_distance=CAMERA_TARGETS[camserial]['TICK_DISTANCE'])





