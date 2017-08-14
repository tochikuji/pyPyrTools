import numpy as np
import pyrtools
from PIL import Image
from sys import argv


def normalize(img):
    return (img - img.min()) / (img.max() - img.min()) * 255


img = Image.open('../examples/einsteinCorrect.pgm')
img = np.asarray(img)
sfpyr = pyrtools.SCFpyr(img, int(argv[1]), int(argv[2]))
sfpyr.showPyr()
recon = sfpyr.reconPyr()
pyrtools.showIm(normalize(recon))
