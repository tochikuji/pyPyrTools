import numpy as np
import pyrtools
from PIL import Image

import sys


img = Image.open('../examples/einsteinCorrect.pgm')
img = np.asarray(img)
sfpyr = pyrtools.SFpyr(img, int(sys.argv[1]), int(sys.argv[2]))
sfpyr.showPyr()
recon = sfpyr.reconPyr()
pyrtools.showIm(recon)
