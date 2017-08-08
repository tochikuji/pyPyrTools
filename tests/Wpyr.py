import numpy as np
import pyrtools
from PIL import Image


img = Image.open('../examples/einsteinCorrect.pgm')
img = np.asarray(img)
pyr = pyrtools.Wpyr(img)
pyr.showPyr()
