import numpy as np
import pyrtools
from PIL import Image


img = Image.open('../examples/einsteinCorrect.pgm')
img = np.asarray(img)
sfpyr = pyrtools.SFpyr(img, 4, 4)
sfpyr.showPyr()
recon = sfpyr.reconPyr()
pyrtools.showIm(recon)
