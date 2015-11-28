# -*- coding: utf-8 -*-

import glob
from os import mkdir
from os.path import isdir, abspath, dirname, join
from subprocess import call

dpi = 150

path = abspath(dirname(__file__))

svgs = glob.glob("*.svg")
pngsDir = join(path, 'PNGs')
if not isdir(pngsDir):
    mkdir(pngsDir)

for svg in svgs:
    png = join(pngsDir, svg[:-4]+'.png')
    # on win: call(['C:/Program Files/Inkscape/inkscape.exe',
    call(['inkscape',
          '--export-png={}'.format(png),
          '-d {}'.format(dpi),
          svg])