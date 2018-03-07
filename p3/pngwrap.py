#!/bin/python
# -*- coding: utf-8 -*-

from PIL import Image
import math
import sys

def txtprep(s):
    return w, ba

def save_as_png(path, s):
    n = len(s)
    s = ('%d:' % n) + s
    n = len(s)
    an = ((n - 1) | (0x3)) + 1
    w = int(math.ceil(math.sqrt(an/4)))
    ba = bytearray(w * w * 4)
    ba[:n] = s
    ba[n:] = s[:len(ba)-n]
    bi = 0
    img = Image.new('RGBA', (w, w))
    for i in xrange(w):
        for j in xrange(w):
            img.putpixel((i, j), (ba[bi], ba[bi+1], ba[bi+2], ba[bi+3]))
            bi += 4
    img.save(path)

def load_from_png(path):
    img = Image.open(path)
    nx, ny = img.size
    # img.mode == 'RGBA'
    ba = bytearray(nx * ny * 4)
    bi = 0
    for i in xrange(nx):
        for j in xrange(ny):
            ba[bi:bi+4] = img.getpixel((i, j))
            bi += 4
    img.close()
    s = str(ba)
    n = int(s.split(':')[0])
    s = s.strip('0123456789:')[:n]
    return s
    
src = sys.argv[1]
if src[-4:] == '.png':
    with open(src[:-4]+'.out', 'w') as f:
        f.write(load_from_png(src))
else:
    with open(src) as f:
        save_as_png(src+'.png', f.read())
