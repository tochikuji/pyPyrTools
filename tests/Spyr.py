import numpy as np
import pyrtools
from PIL import Image


img = Image.open('../examples/einsteinCorrect.pgm')
img = np.asarray(img)
sfpyr = pyrtools.Spyr(img, 4, 'sp3Filters')
sfpyr.showPyr()
