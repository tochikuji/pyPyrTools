import numpy as np
import pyrtools
from PIL import Image

import sys


img = Image.open('../examples/einsteinCorrect.pgm')
img = np.asarray(img)
sfpyr = pyrtools.Spyr(img, int(sys.argv[1]), 'sp1Filters')
sfpyr.showPyr()
img = sfpyr.reconPyr()
pyrtools.showIm(img)
