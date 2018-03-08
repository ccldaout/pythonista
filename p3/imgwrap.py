#!/bin/python
# -*- coding: utf-8 -*-

from PIL import Image
import math
import sys
import tarfile
from StringIO import StringIO

def str2image(data):
    data_n = len(data)

    n = len(data) + 4
    an = ((n - 1) | (0x3)) + 1
    img_w = int(math.ceil(math.sqrt(an/4)))

    b = bytearray(img_w * img_w * 4)
    b[0] = 0xff & ((data_n      ) >> 24)
    b[1] = 0xff & ((data_n <<  8) >> 24)
    b[2] = 0xff & ((data_n << 16) >> 24)
    b[3] = 0xff & ((data_n << 24) >> 24)
    b[4:4+data_n] = data

    img = Image.new('RGBA', (img_w, img_w))
    bi = 0
    for i in xrange(img_w):
        for j in xrange(img_w):
            img.putpixel((i, j), tuple(b[bi:bi+4]))
            bi += 4

    return img

def image2str(img):
    # img.mode == 'RGBA'
    nx, ny = img.size
    b = bytearray(nx * ny * 4)
    bi = 0
    for i in xrange(nx):
        for j in xrange(ny):
            b[bi:bi+4] = img.getpixel((i, j))
            bi += 4

    data_n = (b[0]<<24)|(b[1]<<16)|(b[2]<<8)|b[3]
    return b[4:4+data_n]
    
def tar2image(files):
    sf = StringIO()
    ar = tarfile.open(fileobj=sf, mode='w')
    for f in files:
        ar.add(f)
    ar.close()
    img = str2image(sf.getvalue())
    sf.close()
    return img

def image2tar(img):
    data = image2str(img)
    sf = StringIO(data)
    ar = tarfile.open(fileobj=sf, mode='r')
    return ar

def tar2png(files, png_name):
    img = tar2image(files)
    img.save(png_name)

def png2tar(png_name):
    img = Image.open(png_name)
    return image2tar(img)
