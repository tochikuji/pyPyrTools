import numpy
import pyrtools
import matplotlib.pyplot as plt
import sys
from PIL import Image


imgpath = sys.argv[1]
img = Image.open(imgpath)
img = numpy.asarray(img)

lpyr = pyrtools.Lpyr(img)
lpyr.showPyr()

spyr = pyrtools.SFpyr(img)
spyr.showPyr()
