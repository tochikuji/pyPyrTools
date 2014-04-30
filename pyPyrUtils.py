import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import pylab
import scipy.linalg as spl
import scipy.signal as spsig
import scipy.stats as sps
import math
import struct
import re
from pyPyrCcode import *

def showIm(*args):
    if len(args) == 0:
        #print "showIm( matrix, range, zoom, label, colormap, colorbar )"
        print "showIm( matrix, range, label, colormap, colorbar )"
        print "  matrix is string. It should be the name of a 2D array."
        print "  range is a two element tuple.  It specifies the values that "
        print "    map to the min and max colormap values.  Passing a value "
        print "    of 'auto' (default) sets range=[min,max].  'auto2' sets "
        print "    range=[mean-2*stdev, mean+2*stdev].  'auto3' sets "
        print "    range=[p1-(p2-p1)/8, p2+(p2-p1)/8], where p1 is the 10th "
        print "    percientile value of the sorted matix samples, and p2 is "
        print "    the 90th percentile value."
        #print "  zoom specifies the number of matrix samples per screen pixel."
        #print "    It will be rounded to an integer, or 1 divided by an "
        #print "    integer.  A value of 'same' or 'auto' (default) causes the "
        #print "    zoom value to be chosen automatically to fit the image into"
        #print "    the current axes.  A value of 'full' fills the axis region "
        #print "    (leaving no room for labels)."
        print "  label - A string that is used as a figure title."
        print "  colormap must contain the string 'auto' (grey colormap will " 
        print "    be used), or a string that is the name of a colormap "
        print "    variable"
        print "  colorbar is a boolean that specifies whether or not a "
        print "    colorbar is displayed"
    if len(args) > 0:   # matrix entered
        matrix = args[0]
        # defaults for all other values in case they weren't entered
        imRange = ( np.amin(matrix), np.amax(matrix) )
        zoom = 1
        label = 1
        colorbar = False
        colormap = cm.Greys_r
    if len(args) > 1:   # range entered
        if isinstance(args[1], basestring):
            if args[1] is "auto":
                imRange = ( np.amin(matrix), np.amax(matrix) )
            elif args[1] is "auto2":
                imRange = ( matrix.mean()-2*matrix.std(), 
                            matrix.mean()+2*matrix.std() )
            elif args[1] is "auto3":
                #p1 = np.percentile(matrix, 10)  not in python 2.6.6?!
                #p2 = np.percentile(matrix, 90)
                p1 = sps.scoreatpercentile(np.hstack(matrix), 10)
                p2 = sps.scoreatpercentile(np.hstack(matrix), 90)
                imRange = p1-(p2-p1)/8, p2+(p2-p1)/8
            else:
                print "Error: range of %s is not recognized." % args[1]
                print "       please use a two element tuple or "
                print "       'auto', 'auto2' or 'auto3'"
                print "       enter 'showIm' for more info about options"
                return
        else:
            imRange = args[1][0], args[1][1]
    #if len(args) > 2:   # zoom entered
    #    # no equivalent to matlab's pixelAxes in matplotlib. need dpi
    #    # might work with tkinter, but then have to change everything
    #    zoom = 1
    if len(args) > 2:   # label entered
        label = args[2]
    if len(args) > 3:   # colormap entered
        if args[3] is "auto":
            colormap = cm.Greys_r
        else:  # got a variable name
            colormap = args[3]
    if len(args) > 4 and args[4]:   # colorbar entered and set to true
        colorbar = args[4]
        
    #imgplot = plt.imshow(matrix, colormap, origin='lower').set_clim(imRange)
    imgplot = plt.imshow(matrix, colormap).set_clim(imRange)
    #plt.gca().invert_yaxis()  # default is inverted y from matlab
    if label != 0 and label != 1:
        plt.title(label)
    if colorbar:
        plt.colorbar(imgplot, cmap=colormap)
    #pylab.show()
    plt.show()
    
# Compute maximum pyramid height for given image and filter sizes.
# Specifically: the number of corrDn operations that can be sequentially
# performed when subsampling by a factor of 2.
def maxPyrHt_old(imsz, filtsz):
    if isinstance(imsz, int):
        imsz = (imsz, 1)
    if isinstance(filtsz, int):
        filtsz = (filtsz, 1)

    if len(imsz) == 1 and len(filtsz) == 1:
        imsz = (imsz[0], 1)
        filtsz = (filtsz[0], 1)
    elif len(imsz) == 1 and not any(f == 1 for f in filtsz):
            print "Error: cannot have a 1D 'image' and 2D filter"
            exit(1)
    elif len(imsz) == 1:
        imsz = (imsz[0], 1)
    elif len(filtsz) == 1:
        filtsz = (filtsz[0], 1)

    if filtsz[0] == 1 or filtsz[1] == 1:
        filtsz = (max(filtsz), max(filtsz))

    if imsz == 0:
        height = 0
    elif isinstance(imsz, tuple):
        if any( i < f for i,f in zip(imsz, filtsz) ):
            height = 0
        else:
            #if any( i == 1 for i in imsz):
            if imsz[0] == 1:
                imsz = (1, int(math.floor(imsz[1]/2) ) )
            elif imsz[1] == 1:
                imsz = (int( math.floor(imsz[0]/2) ), 1)
            else:
                imsz = ( int( math.floor(imsz[0]/2) ), 
                         int( math.floor(imsz[1]/2) ))
            height = 1 + maxPyrHt(imsz, filtsz)
    else:
        if any(imsz < f for f in filtsz):
            height = 0;
        else:
            imsz = ( int( math.floor(imsz/2) ), 1 )
            height = 1 + maxPyrHt(imsz, filtsz)
            
    return height

def maxPyrHt(imsz, filtsz):
    if not isinstance(imsz, tuple) or not isinstance(filtsz, tuple):
        if imsz < filtsz:
            return 0
    else:
        if len(imsz) == 1:
            imsz = (imsz[0], 1)
        if len(filtsz) == 1:
            filtsz = (filtsz[0], 1)
        #if filtsz[1] == 1:  # new
        #    filtsz = (filtsz[1], filtsz[0])
        if imsz[0] < filtsz[0] or imsz[1] < filtsz[1]:
            return 0


    if not isinstance(imsz, tuple) and not isinstance(filtsz, tuple):
        imsz = imsz
        filtsz = filtsz
    elif imsz[0] == 1 or imsz[1] == 1:         # 1D image
        imsz = imsz[0] * imsz[1]
        filtsz = filtsz[0] * filtsz[1]
    elif filtsz[0] == 1 or filtsz[1] == 1:   # 2D image, 1D filter
        filtsz = (filtsz[0], filtsz[0])

    if not isinstance(imsz, tuple) and not isinstance(filtsz, tuple) and imsz < filtsz:
        height = 0
    elif not isinstance(imsz, tuple) and not isinstance(filtsz, tuple):
        height = 1 + maxPyrHt( np.floor(imsz/2.0), filtsz )
    else:
        height = 1 + maxPyrHt( (np.floor(imsz[0]/2.0), 
                                np.floor(imsz[1]/2.0)), 
                               filtsz )

    return height

# returns a vector of binomial coefficients of order (size-1)
def binomialFilter(size):
    if size < 2:
        print "Error: size argument must be larger than 1"
        exit(1)
    
    kernel = np.array([[0.5], [0.5]])

    for i in range(0, size-2):
        kernel = spsig.convolve(np.array([[0.5], [0.5]]), kernel)

    return np.asarray(kernel)

# Some standard 1D filter kernels. These are scaled such that their L2-norm 
#   is 1.0
#
# binomN              - binomial coefficient filter of order N-1
# haar                - Harr wavelet
# qmf8, qmf12, qmf16  - Symmetric Quadrature Mirror Filters [Johnston80]
# daub2, daub3, daub4 - Daubechies wavelet [Daubechies88]
# qmf5, qmf9, qmf13   - Symmetric Quadrature Mirror Filters [Simoncelli88, 
#                                                            Simoncelli90]
# [Johnston80] - J D Johnston, "A filter family designed for use in quadrature 
#    mirror filter banks", Proc. ICASSP, pp 291-294, 1980.
#
# [Daubechies88] - I Daubechies, "Orthonormal bases of compactly supported wavelets",
#    Commun. Pure Appl. Math, vol. 42, pp 909-996, 1988.
#
# [Simoncelli88] - E P Simoncelli,  "Orthogonal sub-band image transforms",
#     PhD Thesis, MIT Dept. of Elec. Eng. and Comp. Sci. May 1988.
#     Also available as: MIT Media Laboratory Vision and Modeling Technical 
#     Report #100.
#
# [Simoncelli90] -  E P Simoncelli and E H Adelson, "Subband image coding",
#    Subband Transforms, chapter 4, ed. John W Woods, Kluwer Academic 
#    Publishers,  Norwell, MA, 1990, pp 143--192.
#
# Rob Young, 4/13
#
def namedFilter(name):
    if len(name) > 5 and name[:5] == "binom":
        kernel = math.sqrt(2) * binomialFilter(int(name[5:]))
    elif name is "qmf5":
        kernel = np.array([[-0.076103], [0.3535534], [0.8593118], [0.3535534], [-0.076103]])
    elif name is "qmf9":
        kernel = np.array([[0.02807382], [-0.060944743], [-0.073386624], [0.41472545], [0.7973934], [0.41472545], [-0.073386624], [-0.060944743], [0.02807382]])
    elif name is "qmf13":
        kernel = np.array([[-0.014556438], [0.021651438], [0.039045125], [-0.09800052], [-0.057827797], [0.42995453], [0.7737113], [0.42995453], [-0.057827797], [-0.09800052], [0.039045125], [0.021651438], [-0.014556438]])
    elif name is "qmf8":
        kernel = math.sqrt(2) * np.array([[0.00938715], [-0.07065183], [0.06942827], [0.4899808], [0.4899808], [0.06942827], [-0.07065183], [0.00938715]])
    elif name is "qmf12":
        kernel = math.sqrt(2) * np.array([[-0.003809699], [0.01885659], [-0.002710326], [-0.08469594], [0.08846992], [0.4843894], [0.4843894], [0.08846992], [-0.08469594], [-0.002710326], [0.01885659], [-0.003809699]])
    elif name is "qmf16":
        kernel = math.sqrt(2) * np.array([[0.001050167], [-0.005054526], [-0.002589756], [0.0276414], [-0.009666376], [-0.09039223], [0.09779817], [0.4810284], [0.4810284], [0.09779817], [-0.09039223], [-0.009666376], [0.0276414], [-0.002589756], [-0.005054526], [0.001050167]])
    elif name is "haar":
        kernel = np.array([[1], [1]]) / math.sqrt(2)
    elif name is "daub2":
        kernel = np.array([[0.482962913145], [0.836516303738], [0.224143868042], [-0.129409522551]]);
    elif name is "daub3":
        kernel = np.array([[0.332670552950], [0.806891509311], [0.459877502118], [-0.135011020010], [-0.085441273882], [0.035226291882]])
    elif name is "daub4":
        kernel = np.array([[0.230377813309], [0.714846570553], [0.630880767930], [-0.027983769417], [-0.187034811719], [0.030841381836], [0.032883011667], [-0.010597401785]])
    elif name is "gauss5":  # for backward-compatibility
        kernel = math.sqrt(2) * np.array([[0.0625], [0.25], [0.375], [0.25], [0.0625]])
    elif name is "gauss3":  # for backward-compatibility
        kernel = math.sqrt(2) * np.array([[0.25], [0.5], [0.25]])
    else:
        print "Error: Bad filter name: %s" % (name)
        exit(1)
    return np.array(kernel)

def strictly_decreasing(L):
    return all(x>y for x, y in zip(L, L[1:]))

def compareRecon(recon1, recon2):
    if recon1.shape != recon2.shape:
        return 0

    for i in range(recon1.shape[0]):
        for j in range(recon2.shape[1]):
            if math.fabs(recon1[i,j] - recon2[i,j]) > math.pow(10,-11):
                print "i=%d j=%d %f %f diff=%f" % (i, j, recon1[i,j], recon2[i,j], math.fabs(recon1[i,j]-recon2[i,j]))
                return 0

    return 1

def comparePyr(matPyr, pyPyr):
    # compare two pyramids - return 0 for !=, 1 for == 
    # correct number of elements?
    matSz = sum(matPyr.shape)
    pySz = 1
    #for key in pyPyr.pyrSize.keys():
    for idx in range(len(pyPyr.pyrSize)):
        #sz = pyPyr.pyrSize[key]
        sz = pyPyr.pyrSize[idx]
        if len(sz) == 1:
            pySz += sz[0]
        else:
            pySz += sz[0] * sz[1]

    if(matSz != pySz):
        print "size difference: %d != %d, returning 0" % (matSz, pySz)
        return 0

    # values are the same?
    matStart = 0
    #for key, value in pyPyr.pyrSize.iteritems():
    for idx in range(len(pyPyr.pyrSize)):
        #bandSz = value
        bandSz = pyPyr.pyrSize[idx]
        if len(bandSz) == 1:
            matLen = bandSz[0]
        else:
            matLen = bandSz[0] * bandSz[1]
        matTmp = matPyr[matStart:matStart + matLen]
        matTmp = np.reshape(matTmp, bandSz, order='F')
        matStart = matStart+matLen
        #if (matTmp != pyPyr.pyr[key]).any():
        if (matTmp != pyPyr.pyr[idx]).any():
            print "some pyramid elements not identical: checking..."
            #for i in range(value[0]):
            #    for j in range(value[1]):
            for i in range(bandSz[0]):
                for j in range(bandSz[1]):
                    #if matTmp[i,j] != pyPyr.pyr[key][i,j]:
                    if matTmp[i,j] != pyPyr.pyr[idx][i,j]:
                        #print "%d %d : %.20f" % (i,j,
                        #                         math.fabs(matTmp[i,j]- 
                        #                                  pyPyr.pyr[key][i,j]))
                        #if ( math.fabs(matTmp[i,j] - pyPyr.pyr[key][i,j]) > 
                        if ( math.fabs(matTmp[i,j] - pyPyr.pyr[idx][i,j]) > 
                             math.pow(10,-9) ):
                            print "failed level:%d element:%d %d value:%.15f %.15f" % (idx, i, j, matTmp[i,j], pyPyr.pyr[idx][i,j])
                            return 0
            print "same to at least 10^-9"

    return 1

def mkRamp(*args):
    # mkRamp(SIZE, DIRECTION, SLOPE, INTERCEPT, ORIGIN)
    # Compute a matrix of dimension SIZE (a [Y X] 2-vector, or a scalar)
    # containing samples of a ramp function, with given gradient DIRECTION
    # (radians, CW from X-axis, default = 0), SLOPE (per pixel, default = 
    # 1), and a value of INTERCEPT (default = 0) at the ORIGIN (default =
    # (size+1)/2, [1 1] = upper left). All but the first argument are
    # optional
    
    if len(args) == 0:
        print "mkRamp(SIZE, DIRECTION, SLOPE, INTERCEPT, ORIGIN)"
        print "first argument is required"
        exit(1)
    else:
        sz = args[0]
        if isinstance(sz, (int)):
            sz = (sz, sz)
        elif not isinstance(sz, (tuple)):
            print "first argument must be a two element tuple or an integer"
            exit(1)

    # OPTIONAL args:

    if len(args) > 1:
        direction = args[1]
    else:
        direction = 0

    if len(args) > 2:
        slope = args[2]
    else:
        slope = 1

    if len(args) > 3:
        intercept = args[3]
    else:
        intercept = 0

    if len(args) > 4:
        origin = args[4]
    else:
        origin = ( float(sz[0]-1)/2.0, float(sz[1]-1)/2.0 )

    #--------------------------

    xinc = slope * math.cos(direction)
    yinc = slope * math.sin(direction)

    [xramp, yramp] = np.meshgrid( xinc * (np.array(range(sz[1]))-origin[1]),
                                  yinc * (np.array(range(sz[0]))-origin[0]) )

    res = intercept + xramp + yramp

    return res.copy()

# Steerable pyramid filters.  Transform described  in:
#
# @INPROCEEDINGS{Simoncelli95b,
#	TITLE = "The Steerable Pyramid: A Flexible Architecture for
#		 Multi-Scale Derivative Computation",
#	AUTHOR = "E P Simoncelli and W T Freeman",
#	BOOKTITLE = "Second Int'l Conf on Image Processing",
#	ADDRESS = "Washington, DC", MONTH = "October", YEAR = 1995 }
#
# Filter kernel design described in:
#
#@INPROCEEDINGS{Karasaridis96,
#	TITLE = "A Filter Design Technique for 
#		Steerable Pyramid Image Transforms",
#	AUTHOR = "A Karasaridis and E P Simoncelli",
#	BOOKTITLE = "ICASSP",	ADDRESS = "Atlanta, GA",
#	MONTH = "May",	YEAR = 1996 }
def sp0Filters():
    filters = {}
    filters['harmonics'] = np.array([0])
    filters['lo0filt'] =  ( 
        np.array([[-4.514000e-04, -1.137100e-04, -3.725800e-04, -3.743860e-03, 
                   -3.725800e-04, -1.137100e-04, -4.514000e-04], 
                  [-1.137100e-04, -6.119520e-03, -1.344160e-02, -7.563200e-03, 
                    -1.344160e-02, -6.119520e-03, -1.137100e-04],
                  [-3.725800e-04, -1.344160e-02, 6.441488e-02, 1.524935e-01, 
                    6.441488e-02, -1.344160e-02, -3.725800e-04], 
                  [-3.743860e-03, -7.563200e-03, 1.524935e-01, 3.153017e-01, 
                    1.524935e-01, -7.563200e-03, -3.743860e-03], 
                  [-3.725800e-04, -1.344160e-02, 6.441488e-02, 1.524935e-01, 
                    6.441488e-02, -1.344160e-02, -3.725800e-04],
                  [-1.137100e-04, -6.119520e-03, -1.344160e-02, -7.563200e-03, 
                    -1.344160e-02, -6.119520e-03, -1.137100e-04], 
                  [-4.514000e-04, -1.137100e-04, -3.725800e-04, -3.743860e-03,
                    -3.725800e-04, -1.137100e-04, -4.514000e-04]]) )
    filters['lofilt'] = (
        np.array([[-2.257000e-04, -8.064400e-04, -5.686000e-05, 8.741400e-04, 
                   -1.862800e-04, -1.031640e-03, -1.871920e-03, -1.031640e-03,
                   -1.862800e-04, 8.741400e-04, -5.686000e-05, -8.064400e-04,
                   -2.257000e-04],
                  [-8.064400e-04, 1.417620e-03, -1.903800e-04, -2.449060e-03, 
                    -4.596420e-03, -7.006740e-03, -6.948900e-03, -7.006740e-03,
                    -4.596420e-03, -2.449060e-03, -1.903800e-04, 1.417620e-03,
                    -8.064400e-04],
                  [-5.686000e-05, -1.903800e-04, -3.059760e-03, -6.401000e-03,
                    -6.720800e-03, -5.236180e-03, -3.781600e-03, -5.236180e-03,
                    -6.720800e-03, -6.401000e-03, -3.059760e-03, -1.903800e-04,
                    -5.686000e-05],
                  [8.741400e-04, -2.449060e-03, -6.401000e-03, -5.260020e-03, 
                   3.938620e-03, 1.722078e-02, 2.449600e-02, 1.722078e-02, 
                   3.938620e-03, -5.260020e-03, -6.401000e-03, -2.449060e-03, 
                   8.741400e-04], 
                  [-1.862800e-04, -4.596420e-03, -6.720800e-03, 3.938620e-03,
                    3.220744e-02, 6.306262e-02, 7.624674e-02, 6.306262e-02,
                    3.220744e-02, 3.938620e-03, -6.720800e-03, -4.596420e-03,
                    -1.862800e-04],
                  [-1.031640e-03, -7.006740e-03, -5.236180e-03, 1.722078e-02, 
                    6.306262e-02, 1.116388e-01, 1.348999e-01, 1.116388e-01, 
                    6.306262e-02, 1.722078e-02, -5.236180e-03, -7.006740e-03,
                    -1.031640e-03],
                  [-1.871920e-03, -6.948900e-03, -3.781600e-03, 2.449600e-02,
                    7.624674e-02, 1.348999e-01, 1.576508e-01, 1.348999e-01,
                    7.624674e-02, 2.449600e-02, -3.781600e-03, -6.948900e-03,
                    -1.871920e-03],
                  [-1.031640e-03, -7.006740e-03, -5.236180e-03, 1.722078e-02,
                    6.306262e-02, 1.116388e-01, 1.348999e-01, 1.116388e-01,
                    6.306262e-02, 1.722078e-02, -5.236180e-03, -7.006740e-03,
                    -1.031640e-03], 
                  [-1.862800e-04, -4.596420e-03, -6.720800e-03, 3.938620e-03,
                    3.220744e-02, 6.306262e-02, 7.624674e-02, 6.306262e-02,
                    3.220744e-02, 3.938620e-03, -6.720800e-03, -4.596420e-03,
                    -1.862800e-04],
                  [8.741400e-04, -2.449060e-03, -6.401000e-03, -5.260020e-03,
                   3.938620e-03, 1.722078e-02, 2.449600e-02, 1.722078e-02, 
                   3.938620e-03, -5.260020e-03, -6.401000e-03, -2.449060e-03,
                   8.741400e-04],
                  [-5.686000e-05, -1.903800e-04, -3.059760e-03, -6.401000e-03,
                    -6.720800e-03, -5.236180e-03, -3.781600e-03, -5.236180e-03,
                    -6.720800e-03, -6.401000e-03, -3.059760e-03, -1.903800e-04,
                    -5.686000e-05],
                  [-8.064400e-04, 1.417620e-03, -1.903800e-04, -2.449060e-03,
                    -4.596420e-03, -7.006740e-03, -6.948900e-03, -7.006740e-03,
                    -4.596420e-03, -2.449060e-03, -1.903800e-04, 1.417620e-03,
                    -8.064400e-04], 
                  [-2.257000e-04, -8.064400e-04, -5.686000e-05, 8.741400e-04,
                   -1.862800e-04, -1.031640e-03, -1.871920e-03, -1.031640e-03,
                    -1.862800e-04, 8.741400e-04, -5.686000e-05, -8.064400e-04,
                    -2.257000e-04]]) )
    filters['mtx'] = np.array([ 1.000000 ])
    filters['hi0filt'] = ( 
        np.array([[5.997200e-04, -6.068000e-05, -3.324900e-04, -3.325600e-04, 
                   -2.406600e-04, -3.325600e-04, -3.324900e-04, -6.068000e-05, 
                   5.997200e-04],
                  [-6.068000e-05, 1.263100e-04, 4.927100e-04, 1.459700e-04, 
                    -3.732100e-04, 1.459700e-04, 4.927100e-04, 1.263100e-04, 
                    -6.068000e-05],
                  [-3.324900e-04, 4.927100e-04, -1.616650e-03, -1.437358e-02, 
                    -2.420138e-02, -1.437358e-02, -1.616650e-03, 4.927100e-04, 
                    -3.324900e-04], 
                  [-3.325600e-04, 1.459700e-04, -1.437358e-02, -6.300923e-02, 
                    -9.623594e-02, -6.300923e-02, -1.437358e-02, 1.459700e-04, 
                    -3.325600e-04],
                  [-2.406600e-04, -3.732100e-04, -2.420138e-02, -9.623594e-02, 
                    8.554893e-01, -9.623594e-02, -2.420138e-02, -3.732100e-04, 
                    -2.406600e-04],
                  [-3.325600e-04, 1.459700e-04, -1.437358e-02, -6.300923e-02, 
                    -9.623594e-02, -6.300923e-02, -1.437358e-02, 1.459700e-04, 
                    -3.325600e-04], 
                  [-3.324900e-04, 4.927100e-04, -1.616650e-03, -1.437358e-02, 
                    -2.420138e-02, -1.437358e-02, -1.616650e-03, 4.927100e-04, 
                    -3.324900e-04], 
                  [-6.068000e-05, 1.263100e-04, 4.927100e-04, 1.459700e-04, 
                    -3.732100e-04, 1.459700e-04, 4.927100e-04, 1.263100e-04, 
                    -6.068000e-05], 
                  [5.997200e-04, -6.068000e-05, -3.324900e-04, -3.325600e-04, 
                   -2.406600e-04, -3.325600e-04, -3.324900e-04, -6.068000e-05, 
                   5.997200e-04]]) )
    filters['bfilts'] = ( 
        np.array([-9.066000e-05, -1.738640e-03, -4.942500e-03, -7.889390e-03, 
                   -1.009473e-02, -7.889390e-03, -4.942500e-03, -1.738640e-03, 
                   -9.066000e-05, -1.738640e-03, -4.625150e-03, -7.272540e-03, 
                   -7.623410e-03, -9.091950e-03, -7.623410e-03, -7.272540e-03, 
                   -4.625150e-03, -1.738640e-03, -4.942500e-03, -7.272540e-03, 
                   -2.129540e-02, -2.435662e-02, -3.487008e-02, -2.435662e-02, 
                   -2.129540e-02, -7.272540e-03, -4.942500e-03, -7.889390e-03, 
                   -7.623410e-03, -2.435662e-02, -1.730466e-02, -3.158605e-02, 
                   -1.730466e-02, -2.435662e-02, -7.623410e-03, -7.889390e-03,
                   -1.009473e-02, -9.091950e-03, -3.487008e-02, -3.158605e-02, 
                   9.464195e-01, -3.158605e-02, -3.487008e-02, -9.091950e-03, 
                   -1.009473e-02, -7.889390e-03, -7.623410e-03, -2.435662e-02, 
                   -1.730466e-02, -3.158605e-02, -1.730466e-02, -2.435662e-02, 
                   -7.623410e-03, -7.889390e-03, -4.942500e-03, -7.272540e-03, 
                   -2.129540e-02, -2.435662e-02, -3.487008e-02, -2.435662e-02, 
                   -2.129540e-02, -7.272540e-03, -4.942500e-03, -1.738640e-03, 
                   -4.625150e-03, -7.272540e-03, -7.623410e-03, -9.091950e-03, 
                   -7.623410e-03, -7.272540e-03, -4.625150e-03, -1.738640e-03,
                   -9.066000e-05, -1.738640e-03, -4.942500e-03, -7.889390e-03,
                   -1.009473e-02, -7.889390e-03, -4.942500e-03, -1.738640e-03,
                   -9.066000e-05]) )
    filters['bfilts'] = filters['bfilts'].reshape(len(filters['bfilts']),1)
    return filters

def sp1Filters():
    filters = {}
    filters['harmonics'] = np.array([ 1 ])
    filters['mtx'] = np.eye(2)
    filters['lo0filt'] = ( 
        np.array([[-8.701000e-05, -1.354280e-03, -1.601260e-03, -5.033700e-04, 
                    2.524010e-03, -5.033700e-04, -1.601260e-03, -1.354280e-03, 
                    -8.701000e-05],
                  [-1.354280e-03, 2.921580e-03, 7.522720e-03, 8.224420e-03, 
                    1.107620e-03, 8.224420e-03, 7.522720e-03, 2.921580e-03, 
                    -1.354280e-03],
                  [-1.601260e-03, 7.522720e-03, -7.061290e-03, -3.769487e-02,
                    -3.297137e-02, -3.769487e-02, -7.061290e-03, 7.522720e-03,
                    -1.601260e-03],
                  [-5.033700e-04, 8.224420e-03, -3.769487e-02, 4.381320e-02,
                    1.811603e-01, 4.381320e-02, -3.769487e-02, 8.224420e-03,
                    -5.033700e-04], 
                  [2.524010e-03, 1.107620e-03, -3.297137e-02, 1.811603e-01, 
                   4.376250e-01, 1.811603e-01, -3.297137e-02, 1.107620e-03, 
                   2.524010e-03],
                  [-5.033700e-04, 8.224420e-03, -3.769487e-02, 4.381320e-02, 
                    1.811603e-01, 4.381320e-02, -3.769487e-02, 8.224420e-03,
                    -5.033700e-04],
                  [-1.601260e-03, 7.522720e-03, -7.061290e-03, -3.769487e-02,
                    -3.297137e-02, -3.769487e-02, -7.061290e-03, 7.522720e-03,
                    -1.601260e-03],
                  [-1.354280e-03, 2.921580e-03, 7.522720e-03, 8.224420e-03, 
                    1.107620e-03, 8.224420e-03, 7.522720e-03, 2.921580e-03,
                    -1.354280e-03], 
                  [-8.701000e-05, -1.354280e-03, -1.601260e-03, -5.033700e-04, 
                    2.524010e-03, -5.033700e-04, -1.601260e-03, -1.354280e-03, 
                    -8.701000e-05]]) )
    filters['lofilt'] = (
        np.array([[-4.350000e-05, 1.207800e-04, -6.771400e-04, -1.243400e-04, 
                    -8.006400e-04, -1.597040e-03, -2.516800e-04, -4.202000e-04,
                    1.262000e-03, -4.202000e-04, -2.516800e-04, -1.597040e-03,
                    -8.006400e-04, -1.243400e-04, -6.771400e-04, 1.207800e-04,
                    -4.350000e-05], 
                  [1.207800e-04, 4.460600e-04, -5.814600e-04, 5.621600e-04, 
                   -1.368800e-04, 2.325540e-03, 2.889860e-03, 4.287280e-03, 
                   5.589400e-03, 4.287280e-03, 2.889860e-03, 2.325540e-03, 
                   -1.368800e-04, 5.621600e-04, -5.814600e-04, 4.460600e-04, 
                   1.207800e-04],
                  [-6.771400e-04, -5.814600e-04, 1.460780e-03, 2.160540e-03, 
                    3.761360e-03, 3.080980e-03, 4.112200e-03, 2.221220e-03, 
                    5.538200e-04, 2.221220e-03, 4.112200e-03, 3.080980e-03, 
                    3.761360e-03, 2.160540e-03, 1.460780e-03, -5.814600e-04, 
                    -6.771400e-04],
                  [-1.243400e-04, 5.621600e-04, 2.160540e-03, 3.175780e-03, 
                    3.184680e-03, -1.777480e-03, -7.431700e-03, -9.056920e-03,
                    -9.637220e-03, -9.056920e-03, -7.431700e-03, -1.777480e-03,
                    3.184680e-03, 3.175780e-03, 2.160540e-03, 5.621600e-04, 
                    -1.243400e-04],
                  [-8.006400e-04, -1.368800e-04, 3.761360e-03, 3.184680e-03, 
                    -3.530640e-03, -1.260420e-02, -1.884744e-02, -1.750818e-02,
                    -1.648568e-02, -1.750818e-02, -1.884744e-02, -1.260420e-02,
                    -3.530640e-03, 3.184680e-03, 3.761360e-03, -1.368800e-04,
                    -8.006400e-04],
                  [-1.597040e-03, 2.325540e-03, 3.080980e-03, -1.777480e-03, 
                    -1.260420e-02, -2.022938e-02, -1.109170e-02, 3.955660e-03, 
                    1.438512e-02, 3.955660e-03, -1.109170e-02, -2.022938e-02, 
                    -1.260420e-02, -1.777480e-03, 3.080980e-03, 2.325540e-03, 
                    -1.597040e-03],
                  [-2.516800e-04, 2.889860e-03, 4.112200e-03, -7.431700e-03, 
                    -1.884744e-02, -1.109170e-02, 2.190660e-02, 6.806584e-02, 
                    9.058014e-02, 6.806584e-02, 2.190660e-02, -1.109170e-02, 
                    -1.884744e-02, -7.431700e-03, 4.112200e-03, 2.889860e-03, 
                    -2.516800e-04],
                  [-4.202000e-04, 4.287280e-03, 2.221220e-03, -9.056920e-03, 
                    -1.750818e-02, 3.955660e-03, 6.806584e-02, 1.445500e-01, 
                    1.773651e-01, 1.445500e-01, 6.806584e-02, 3.955660e-03, 
                    -1.750818e-02, -9.056920e-03, 2.221220e-03, 4.287280e-03, 
                    -4.202000e-04],
                  [1.262000e-03, 5.589400e-03, 5.538200e-04, -9.637220e-03, 
                   -1.648568e-02, 1.438512e-02, 9.058014e-02, 1.773651e-01, 
                   2.120374e-01, 1.773651e-01, 9.058014e-02, 1.438512e-02, 
                   -1.648568e-02, -9.637220e-03, 5.538200e-04, 5.589400e-03, 
                   1.262000e-03],
                  [-4.202000e-04, 4.287280e-03, 2.221220e-03, -9.056920e-03, 
                    -1.750818e-02, 3.955660e-03, 6.806584e-02, 1.445500e-01, 
                    1.773651e-01, 1.445500e-01, 6.806584e-02, 3.955660e-03, 
                    -1.750818e-02, -9.056920e-03, 2.221220e-03, 4.287280e-03, 
                    -4.202000e-04],
                  [-2.516800e-04, 2.889860e-03, 4.112200e-03, -7.431700e-03, 
                    -1.884744e-02, -1.109170e-02, 2.190660e-02, 6.806584e-02, 
                    9.058014e-02, 6.806584e-02, 2.190660e-02, -1.109170e-02, 
                    -1.884744e-02, -7.431700e-03, 4.112200e-03, 2.889860e-03, 
                    -2.516800e-04],
                  [-1.597040e-03, 2.325540e-03, 3.080980e-03, -1.777480e-03, 
                    -1.260420e-02, -2.022938e-02, -1.109170e-02, 3.955660e-03, 
                    1.438512e-02, 3.955660e-03, -1.109170e-02, -2.022938e-02, 
                    -1.260420e-02, -1.777480e-03, 3.080980e-03, 2.325540e-03, 
                    -1.597040e-03],
                  [-8.006400e-04, -1.368800e-04, 3.761360e-03, 3.184680e-03, 
                    -3.530640e-03, -1.260420e-02, -1.884744e-02, -1.750818e-02,
                    -1.648568e-02, -1.750818e-02, -1.884744e-02, -1.260420e-02,
                    -3.530640e-03, 3.184680e-03, 3.761360e-03, -1.368800e-04,
                    -8.006400e-04],
                  [-1.243400e-04, 5.621600e-04, 2.160540e-03, 3.175780e-03, 
                    3.184680e-03, -1.777480e-03, -7.431700e-03, -9.056920e-03,
                    -9.637220e-03, -9.056920e-03, -7.431700e-03, -1.777480e-03,
                    3.184680e-03, 3.175780e-03, 2.160540e-03, 5.621600e-04,
                    -1.243400e-04],
                  [-6.771400e-04, -5.814600e-04, 1.460780e-03, 2.160540e-03, 
                    3.761360e-03, 3.080980e-03, 4.112200e-03, 2.221220e-03, 
                    5.538200e-04, 2.221220e-03, 4.112200e-03, 3.080980e-03, 
                    3.761360e-03, 2.160540e-03, 1.460780e-03, -5.814600e-04, 
                    -6.771400e-04],
                  [1.207800e-04, 4.460600e-04, -5.814600e-04, 5.621600e-04, 
                   -1.368800e-04, 2.325540e-03, 2.889860e-03, 4.287280e-03, 
                   5.589400e-03, 4.287280e-03, 2.889860e-03, 2.325540e-03, 
                   -1.368800e-04, 5.621600e-04, -5.814600e-04, 4.460600e-04, 
                   1.207800e-04],
                  [-4.350000e-05, 1.207800e-04, -6.771400e-04, -1.243400e-04, 
                    -8.006400e-04, -1.597040e-03, -2.516800e-04, -4.202000e-04,
                    1.262000e-03, -4.202000e-04, -2.516800e-04, -1.597040e-03,
                    -8.006400e-04, -1.243400e-04, -6.771400e-04, 1.207800e-04,
                    -4.350000e-05] ]) )
    filters['hi0filt'] = (
        np.array([[-9.570000e-04, -2.424100e-04, -1.424720e-03, -8.742600e-04, 
                    -1.166810e-03, -8.742600e-04, -1.424720e-03, -2.424100e-04,
                    -9.570000e-04],
                  [-2.424100e-04, -4.317530e-03, 8.998600e-04, 9.156420e-03, 
                    1.098012e-02, 9.156420e-03, 8.998600e-04, -4.317530e-03, 
                    -2.424100e-04],
                  [-1.424720e-03, 8.998600e-04, 1.706347e-02, 1.094866e-02, 
                    -5.897780e-03, 1.094866e-02, 1.706347e-02, 8.998600e-04, 
                    -1.424720e-03],
                  [-8.742600e-04, 9.156420e-03, 1.094866e-02, -7.841370e-02, 
                    -1.562827e-01, -7.841370e-02, 1.094866e-02, 9.156420e-03, 
                    -8.742600e-04],
                  [-1.166810e-03, 1.098012e-02, -5.897780e-03, -1.562827e-01, 
                    7.282593e-01, -1.562827e-01, -5.897780e-03, 1.098012e-02, 
                    -1.166810e-03],
                  [-8.742600e-04, 9.156420e-03, 1.094866e-02, -7.841370e-02, 
                    -1.562827e-01, -7.841370e-02, 1.094866e-02, 9.156420e-03, 
                    -8.742600e-04],
                  [-1.424720e-03, 8.998600e-04, 1.706347e-02, 1.094866e-02, 
                    -5.897780e-03, 1.094866e-02, 1.706347e-02, 8.998600e-04, 
                    -1.424720e-03],
                  [-2.424100e-04, -4.317530e-03, 8.998600e-04, 9.156420e-03, 
                    1.098012e-02, 9.156420e-03, 8.998600e-04, -4.317530e-03, 
                    -2.424100e-04],
                  [-9.570000e-04, -2.424100e-04, -1.424720e-03, -8.742600e-04, 
                    -1.166810e-03, -8.742600e-04, -1.424720e-03, -2.424100e-04,
                    -9.570000e-04]]) )
    filters['bfilts'] = (
        np.array([[6.125880e-03, -8.052600e-03, -2.103714e-02, -1.536890e-02, 
                   -1.851466e-02, -1.536890e-02, -2.103714e-02, -8.052600e-03, 
                   6.125880e-03, -1.287416e-02, -9.611520e-03, 1.023569e-02, 
                   6.009450e-03, 1.872620e-03, 6.009450e-03, 1.023569e-02, 
                   -9.611520e-03, -1.287416e-02, -5.641530e-03, 4.168400e-03, 
                   -2.382180e-02, -5.375324e-02, -2.076086e-02, -5.375324e-02,
                   -2.382180e-02, 4.168400e-03, -5.641530e-03, -8.957260e-03, 
                   -1.751170e-03, -1.836909e-02, 1.265655e-01, 2.996168e-01, 
                   1.265655e-01, -1.836909e-02, -1.751170e-03, -8.957260e-03, 
                   0.000000e+00, 0.000000e+00, 0.000000e+00, 0.000000e+00, 
                   0.000000e+00, 0.000000e+00, 0.000000e+00, 0.000000e+00, 
                   0.000000e+00, 8.957260e-03, 1.751170e-03, 1.836909e-02, 
                   -1.265655e-01, -2.996168e-01, -1.265655e-01, 1.836909e-02, 
                   1.751170e-03, 8.957260e-03, 5.641530e-03, -4.168400e-03, 
                   2.382180e-02, 5.375324e-02, 2.076086e-02, 5.375324e-02, 
                   2.382180e-02, -4.168400e-03, 5.641530e-03, 1.287416e-02, 
                   9.611520e-03, -1.023569e-02, -6.009450e-03, -1.872620e-03, 
                   -6.009450e-03, -1.023569e-02, 9.611520e-03, 1.287416e-02, 
                   -6.125880e-03, 8.052600e-03, 2.103714e-02, 1.536890e-02, 
                   1.851466e-02, 1.536890e-02, 2.103714e-02, 8.052600e-03, 
                   -6.125880e-03],
                  [-6.125880e-03, 1.287416e-02, 5.641530e-03, 8.957260e-03, 
                    0.000000e+00, -8.957260e-03, -5.641530e-03, -1.287416e-02, 
                    6.125880e-03, 8.052600e-03, 9.611520e-03, -4.168400e-03, 
                    1.751170e-03, 0.000000e+00, -1.751170e-03, 4.168400e-03, 
                    -9.611520e-03, -8.052600e-03, 2.103714e-02, -1.023569e-02, 
                    2.382180e-02, 1.836909e-02, 0.000000e+00, -1.836909e-02, 
                    -2.382180e-02, 1.023569e-02, -2.103714e-02, 1.536890e-02, 
                    -6.009450e-03, 5.375324e-02, -1.265655e-01, 0.000000e+00, 
                    1.265655e-01, -5.375324e-02, 6.009450e-03, -1.536890e-02, 
                    1.851466e-02, -1.872620e-03, 2.076086e-02, -2.996168e-01, 
                    0.000000e+00, 2.996168e-01, -2.076086e-02, 1.872620e-03, 
                    -1.851466e-02, 1.536890e-02, -6.009450e-03, 5.375324e-02, 
                    -1.265655e-01, 0.000000e+00, 1.265655e-01, -5.375324e-02, 
                    6.009450e-03, -1.536890e-02, 2.103714e-02, -1.023569e-02, 
                    2.382180e-02, 1.836909e-02, 0.000000e+00, -1.836909e-02, 
                    -2.382180e-02, 1.023569e-02, -2.103714e-02, 8.052600e-03, 
                    9.611520e-03, -4.168400e-03, 1.751170e-03, 0.000000e+00, 
                    -1.751170e-03, 4.168400e-03, -9.611520e-03, -8.052600e-03, 
                    -6.125880e-03, 1.287416e-02, 5.641530e-03, 8.957260e-03, 
                    0.000000e+00, -8.957260e-03, -5.641530e-03, -1.287416e-02, 
                    6.125880e-03]]).T )
    filters['bfilts'] = -filters['bfilts']

    return filters

def sp3Filters():
    filters = {}
    filters['harmonics'] = np.array([1, 3])
    filters['mtx'] = (
        np.array([[0.5000, 0.3536, 0, -0.3536],
                  [-0.0000, 0.3536, 0.5000, 0.3536],
                  [0.5000, -0.3536, 0, 0.3536],
                  [-0.0000, 0.3536, -0.5000, 0.3536]]))
    filters['hi0filt'] = (
        np.array([[-4.0483998600E-4, -6.2596000498E-4, -3.7829999201E-5,
                    8.8387000142E-4, 1.5450799838E-3, 1.9235999789E-3,
                    2.0687500946E-3, 2.0898699295E-3, 2.0687500946E-3,
                    1.9235999789E-3, 1.5450799838E-3, 8.8387000142E-4,
                    -3.7829999201E-5, -6.2596000498E-4, -4.0483998600E-4],
                  [-6.2596000498E-4, -3.2734998967E-4, 7.7435001731E-4,
                    1.5874400269E-3, 2.1750701126E-3, 2.5626500137E-3,
                    2.2892199922E-3, 1.9755100366E-3, 2.2892199922E-3,
                    2.5626500137E-3, 2.1750701126E-3, 1.5874400269E-3,
                    7.7435001731E-4, -3.2734998967E-4, -6.2596000498E-4],
                  [-3.7829999201E-5, 7.7435001731E-4, 1.1793200392E-3,
                    1.4050999889E-3, 2.2253401112E-3, 2.1145299543E-3,
                    3.3578000148E-4, -8.3368999185E-4, 3.3578000148E-4,
                    2.1145299543E-3, 2.2253401112E-3, 1.4050999889E-3,
                    1.1793200392E-3, 7.7435001731E-4, -3.7829999201E-5],
                  [8.8387000142E-4, 1.5874400269E-3, 1.4050999889E-3,
                   1.2960999738E-3, -4.9274001503E-4, -3.1295299996E-3,
                   -4.5751798898E-3, -5.1014497876E-3, -4.5751798898E-3,
                   -3.1295299996E-3, -4.9274001503E-4, 1.2960999738E-3,
                   1.4050999889E-3, 1.5874400269E-3, 8.8387000142E-4],
                  [1.5450799838E-3, 2.1750701126E-3, 2.2253401112E-3,
                   -4.9274001503E-4, -6.3222697936E-3, -2.7556000277E-3,
                   5.3632198833E-3, 7.3032598011E-3, 5.3632198833E-3,
                   -2.7556000277E-3, -6.3222697936E-3, -4.9274001503E-4,
                   2.2253401112E-3, 2.1750701126E-3, 1.5450799838E-3],
                  [1.9235999789E-3, 2.5626500137E-3, 2.1145299543E-3,
                   -3.1295299996E-3, -2.7556000277E-3, 1.3962360099E-2,
                   7.8046298586E-3, -9.3812197447E-3, 7.8046298586E-3,
                   1.3962360099E-2, -2.7556000277E-3, -3.1295299996E-3,
                   2.1145299543E-3, 2.5626500137E-3, 1.9235999789E-3],
                  [2.0687500946E-3, 2.2892199922E-3, 3.3578000148E-4,
                   -4.5751798898E-3, 5.3632198833E-3, 7.8046298586E-3,
                   -7.9501636326E-2, -0.1554141641, -7.9501636326E-2,
                   7.8046298586E-3, 5.3632198833E-3, -4.5751798898E-3,
                   3.3578000148E-4, 2.2892199922E-3, 2.0687500946E-3],
                  [2.0898699295E-3, 1.9755100366E-3, -8.3368999185E-4,
                   -5.1014497876E-3, 7.3032598011E-3, -9.3812197447E-3,
                   -0.1554141641, 0.7303866148, -0.1554141641, 
                   -9.3812197447E-3, 7.3032598011E-3, -5.1014497876E-3,
                   -8.3368999185E-4, 1.9755100366E-3, 2.0898699295E-3],
                  [2.0687500946E-3, 2.2892199922E-3, 3.3578000148E-4,
                   -4.5751798898E-3, 5.3632198833E-3, 7.8046298586E-3,
                   -7.9501636326E-2, -0.1554141641, -7.9501636326E-2,
                   7.8046298586E-3, 5.3632198833E-3, -4.5751798898E-3,
                   3.3578000148E-4, 2.2892199922E-3, 2.0687500946E-3],
                  [1.9235999789E-3, 2.5626500137E-3, 2.1145299543E-3,
                   -3.1295299996E-3, -2.7556000277E-3, 1.3962360099E-2,
                   7.8046298586E-3, -9.3812197447E-3, 7.8046298586E-3,
                   1.3962360099E-2, -2.7556000277E-3, -3.1295299996E-3,
                   2.1145299543E-3, 2.5626500137E-3, 1.9235999789E-3],
                  [1.5450799838E-3, 2.1750701126E-3, 2.2253401112E-3,
                   -4.9274001503E-4, -6.3222697936E-3, -2.7556000277E-3,
                   5.3632198833E-3, 7.3032598011E-3, 5.3632198833E-3,
                   -2.7556000277E-3, -6.3222697936E-3, -4.9274001503E-4,
                   2.2253401112E-3, 2.1750701126E-3, 1.5450799838E-3],
                  [8.8387000142E-4, 1.5874400269E-3, 1.4050999889E-3,
                   1.2960999738E-3, -4.9274001503E-4, -3.1295299996E-3,
                   -4.5751798898E-3, -5.1014497876E-3, -4.5751798898E-3,
                   -3.1295299996E-3, -4.9274001503E-4, 1.2960999738E-3,
                   1.4050999889E-3, 1.5874400269E-3, 8.8387000142E-4],
                  [-3.7829999201E-5, 7.7435001731E-4, 1.1793200392E-3,
                    1.4050999889E-3, 2.2253401112E-3, 2.1145299543E-3,
                    3.3578000148E-4, -8.3368999185E-4, 3.3578000148E-4,
                    2.1145299543E-3, 2.2253401112E-3, 1.4050999889E-3,
                    1.1793200392E-3, 7.7435001731E-4, -3.7829999201E-5],
                  [-6.2596000498E-4, -3.2734998967E-4, 7.7435001731E-4,
                    1.5874400269E-3, 2.1750701126E-3, 2.5626500137E-3,
                    2.2892199922E-3, 1.9755100366E-3, 2.2892199922E-3,
                    2.5626500137E-3, 2.1750701126E-3, 1.5874400269E-3,
                    7.7435001731E-4, -3.2734998967E-4, -6.2596000498E-4],
                  [-4.0483998600E-4, -6.2596000498E-4, -3.7829999201E-5,
                    8.8387000142E-4, 1.5450799838E-3, 1.9235999789E-3,
                    2.0687500946E-3, 2.0898699295E-3, 2.0687500946E-3,
                    1.9235999789E-3, 1.5450799838E-3, 8.8387000142E-4,
                    -3.7829999201E-5, -6.2596000498E-4, -4.0483998600E-4]]))
    filters['lo0filt'] = (
        np.array([[-8.7009997515E-5, -1.3542800443E-3, -1.6012600390E-3,
                    -5.0337001448E-4, 2.5240099058E-3, -5.0337001448E-4,
                    -1.6012600390E-3, -1.3542800443E-3, -8.7009997515E-5],
                  [-1.3542800443E-3, 2.9215801042E-3, 7.5227199122E-3,
                    8.2244202495E-3, 1.1076199589E-3, 8.2244202495E-3,
                    7.5227199122E-3, 2.9215801042E-3, -1.3542800443E-3],
                  [-1.6012600390E-3, 7.5227199122E-3, -7.0612900890E-3,
                    -3.7694871426E-2, -3.2971370965E-2, -3.7694871426E-2,
                    -7.0612900890E-3, 7.5227199122E-3, -1.6012600390E-3],
                  [-5.0337001448E-4, 8.2244202495E-3, -3.7694871426E-2,
                    4.3813198805E-2, 0.1811603010, 4.3813198805E-2,
                    -3.7694871426E-2, 8.2244202495E-3, -5.0337001448E-4],
                  [2.5240099058E-3, 1.1076199589E-3, -3.2971370965E-2,
                   0.1811603010, 0.4376249909, 0.1811603010,
                   -3.2971370965E-2, 1.1076199589E-3, 2.5240099058E-3],
                  [-5.0337001448E-4, 8.2244202495E-3, -3.7694871426E-2,
                    4.3813198805E-2, 0.1811603010, 4.3813198805E-2,
                    -3.7694871426E-2, 8.2244202495E-3, -5.0337001448E-4],
                  [-1.6012600390E-3, 7.5227199122E-3, -7.0612900890E-3,
                    -3.7694871426E-2, -3.2971370965E-2, -3.7694871426E-2,
                    -7.0612900890E-3, 7.5227199122E-3, -1.6012600390E-3],
                  [-1.3542800443E-3, 2.9215801042E-3, 7.5227199122E-3,
                    8.2244202495E-3, 1.1076199589E-3, 8.2244202495E-3,
                    7.5227199122E-3, 2.9215801042E-3, -1.3542800443E-3],
                  [-8.7009997515E-5, -1.3542800443E-3, -1.6012600390E-3,
                    -5.0337001448E-4, 2.5240099058E-3, -5.0337001448E-4,
                    -1.6012600390E-3, -1.3542800443E-3, -8.7009997515E-5]]))
    filters['lofilt'] = (
        np.array([[-4.3500000174E-5, 1.2078000145E-4, -6.7714002216E-4,
                    -1.2434000382E-4, -8.0063997302E-4, -1.5970399836E-3,
                    -2.5168000138E-4, -4.2019999819E-4, 1.2619999470E-3,
                    -4.2019999819E-4, -2.5168000138E-4, -1.5970399836E-3,
                    -8.0063997302E-4, -1.2434000382E-4, -6.7714002216E-4,
                    1.2078000145E-4, -4.3500000174E-5],
                  [1.2078000145E-4, 4.4606000301E-4, -5.8146001538E-4,
                   5.6215998484E-4, -1.3688000035E-4, 2.3255399428E-3,
                   2.8898599558E-3, 4.2872801423E-3, 5.5893999524E-3,
                   4.2872801423E-3, 2.8898599558E-3, 2.3255399428E-3,
                   -1.3688000035E-4, 5.6215998484E-4, -5.8146001538E-4,
                   4.4606000301E-4, 1.2078000145E-4],
                  [-6.7714002216E-4, -5.8146001538E-4, 1.4607800404E-3,
                    2.1605400834E-3, 3.7613599561E-3, 3.0809799209E-3,
                    4.1121998802E-3, 2.2212199401E-3, 5.5381999118E-4,
                    2.2212199401E-3, 4.1121998802E-3, 3.0809799209E-3,
                    3.7613599561E-3, 2.1605400834E-3, 1.4607800404E-3,
                    -5.8146001538E-4, -6.7714002216E-4],
                  [-1.2434000382E-4, 5.6215998484E-4, 2.1605400834E-3,
                    3.1757799443E-3, 3.1846798956E-3, -1.7774800071E-3,
                    -7.4316998944E-3, -9.0569201857E-3, -9.6372198313E-3,
                    -9.0569201857E-3, -7.4316998944E-3, -1.7774800071E-3,
                    3.1846798956E-3, 3.1757799443E-3, 2.1605400834E-3,
                    5.6215998484E-4, -1.2434000382E-4],
                  [-8.0063997302E-4, -1.3688000035E-4, 3.7613599561E-3,
                    3.1846798956E-3, -3.5306399222E-3, -1.2604200281E-2,
                    -1.8847439438E-2, -1.7508180812E-2, -1.6485679895E-2,
                    -1.7508180812E-2, -1.8847439438E-2, -1.2604200281E-2,
                    -3.5306399222E-3, 3.1846798956E-3, 3.7613599561E-3,
                    -1.3688000035E-4, -8.0063997302E-4],
                  [-1.5970399836E-3, 2.3255399428E-3, 3.0809799209E-3,
                    -1.7774800071E-3, -1.2604200281E-2, -2.0229380578E-2,
                    -1.1091699824E-2, 3.9556599222E-3, 1.4385120012E-2,
                    3.9556599222E-3, -1.1091699824E-2, -2.0229380578E-2,
                    -1.2604200281E-2, -1.7774800071E-3, 3.0809799209E-3,
                    2.3255399428E-3, -1.5970399836E-3],
                  [-2.5168000138E-4, 2.8898599558E-3, 4.1121998802E-3,
                    -7.4316998944E-3, -1.8847439438E-2, -1.1091699824E-2,
                    2.1906599402E-2, 6.8065837026E-2, 9.0580143034E-2,
                    6.8065837026E-2, 2.1906599402E-2, -1.1091699824E-2,
                    -1.8847439438E-2, -7.4316998944E-3, 4.1121998802E-3,
                    2.8898599558E-3, -2.5168000138E-4],
                  [-4.2019999819E-4, 4.2872801423E-3, 2.2212199401E-3,
                    -9.0569201857E-3, -1.7508180812E-2, 3.9556599222E-3,
                    6.8065837026E-2, 0.1445499808, 0.1773651242,
                    0.1445499808, 6.8065837026E-2, 3.9556599222E-3,
                    -1.7508180812E-2, -9.0569201857E-3, 2.2212199401E-3,
                    4.2872801423E-3, -4.2019999819E-4],
                  [1.2619999470E-3, 5.5893999524E-3, 5.5381999118E-4,
                   -9.6372198313E-3, -1.6485679895E-2, 1.4385120012E-2,
                   9.0580143034E-2, 0.1773651242, 0.2120374441,
                   0.1773651242, 9.0580143034E-2, 1.4385120012E-2,
                   -1.6485679895E-2, -9.6372198313E-3, 5.5381999118E-4,
                   5.5893999524E-3, 1.2619999470E-3],
                  [-4.2019999819E-4, 4.2872801423E-3, 2.2212199401E-3,
                    -9.0569201857E-3, -1.7508180812E-2, 3.9556599222E-3,
                    6.8065837026E-2, 0.1445499808, 0.1773651242,
                    0.1445499808, 6.8065837026E-2, 3.9556599222E-3,
                    -1.7508180812E-2, -9.0569201857E-3, 2.2212199401E-3,
                    4.2872801423E-3, -4.2019999819E-4],
                  [-2.5168000138E-4, 2.8898599558E-3, 4.1121998802E-3,
                    -7.4316998944E-3, -1.8847439438E-2, -1.1091699824E-2,
                    2.1906599402E-2, 6.8065837026E-2, 9.0580143034E-2,
                    6.8065837026E-2, 2.1906599402E-2, -1.1091699824E-2,
                    -1.8847439438E-2, -7.4316998944E-3, 4.1121998802E-3,
                    2.8898599558E-3, -2.5168000138E-4],
                  [-1.5970399836E-3, 2.3255399428E-3, 3.0809799209E-3,
                    -1.7774800071E-3, -1.2604200281E-2, -2.0229380578E-2,
                    -1.1091699824E-2, 3.9556599222E-3, 1.4385120012E-2,
                    3.9556599222E-3, -1.1091699824E-2, -2.0229380578E-2,
                    -1.2604200281E-2, -1.7774800071E-3, 3.0809799209E-3,
                    2.3255399428E-3, -1.5970399836E-3],
                  [-8.0063997302E-4, -1.3688000035E-4, 3.7613599561E-3,
                    3.1846798956E-3, -3.5306399222E-3, -1.2604200281E-2,
                    -1.8847439438E-2, -1.7508180812E-2, -1.6485679895E-2,
                    -1.7508180812E-2, -1.8847439438E-2, -1.2604200281E-2,
                    -3.5306399222E-3, 3.1846798956E-3, 3.7613599561E-3,
                    -1.3688000035E-4, -8.0063997302E-4],
                  [-1.2434000382E-4, 5.6215998484E-4, 2.1605400834E-3,
                    3.1757799443E-3, 3.1846798956E-3, -1.7774800071E-3,
                    -7.4316998944E-3, -9.0569201857E-3, -9.6372198313E-3,
                    -9.0569201857E-3, -7.4316998944E-3, -1.7774800071E-3,
                    3.1846798956E-3, 3.1757799443E-3, 2.1605400834E-3,
                    5.6215998484E-4, -1.2434000382E-4],
                  [-6.7714002216E-4, -5.8146001538E-4, 1.4607800404E-3,
                    2.1605400834E-3, 3.7613599561E-3, 3.0809799209E-3,
                    4.1121998802E-3, 2.2212199401E-3, 5.5381999118E-4,
                    2.2212199401E-3, 4.1121998802E-3, 3.0809799209E-3,
                    3.7613599561E-3, 2.1605400834E-3, 1.4607800404E-3,
                    -5.8146001538E-4, -6.7714002216E-4],
                  [1.2078000145E-4, 4.4606000301E-4, -5.8146001538E-4,
                   5.6215998484E-4, -1.3688000035E-4, 2.3255399428E-3,
                   2.8898599558E-3, 4.2872801423E-3, 5.5893999524E-3,
                   4.2872801423E-3, 2.8898599558E-3, 2.3255399428E-3,
                   -1.3688000035E-4, 5.6215998484E-4, -5.8146001538E-4,
                   4.4606000301E-4, 1.2078000145E-4],
                  [-4.3500000174E-5, 1.2078000145E-4, -6.7714002216E-4,
                    -1.2434000382E-4, -8.0063997302E-4, -1.5970399836E-3,
                    -2.5168000138E-4, -4.2019999819E-4, 1.2619999470E-3,
                    -4.2019999819E-4, -2.5168000138E-4, -1.5970399836E-3,
                    -8.0063997302E-4, -1.2434000382E-4, -6.7714002216E-4,
                    1.2078000145E-4, -4.3500000174E-5]]))
    filters['bfilts'] = (
        np.array([[-8.1125000725E-4, 4.4451598078E-3, 1.2316980399E-2,
                    1.3955879956E-2,  1.4179450460E-2, 1.3955879956E-2,
                    1.2316980399E-2, 4.4451598078E-3, -8.1125000725E-4,
                    3.9103501476E-3, 4.4565401040E-3, -5.8724298142E-3,
                    -2.8760801069E-3, 8.5267601535E-3, -2.8760801069E-3,
                    -5.8724298142E-3, 4.4565401040E-3, 3.9103501476E-3,
                    1.3462699717E-3, -3.7740699481E-3, 8.2581602037E-3,
                    3.9442278445E-2, 5.3605638444E-2, 3.9442278445E-2,
                    8.2581602037E-3, -3.7740699481E-3, 1.3462699717E-3,
                    7.4700999539E-4, -3.6522001028E-4, -2.2522680461E-2,
                    -0.1105690673, -0.1768419296, -0.1105690673,
                    -2.2522680461E-2, -3.6522001028E-4, 7.4700999539E-4,
                    0.0000000000, 0.0000000000, 0.0000000000,
                    0.0000000000, 0.0000000000, 0.0000000000,
                    0.0000000000, 0.0000000000, 0.0000000000,
                    -7.4700999539E-4, 3.6522001028E-4, 2.2522680461E-2,
                    0.1105690673, 0.1768419296, 0.1105690673,
                    2.2522680461E-2, 3.6522001028E-4, -7.4700999539E-4,
                    -1.3462699717E-3, 3.7740699481E-3, -8.2581602037E-3,
                    -3.9442278445E-2, -5.3605638444E-2, -3.9442278445E-2,
                    -8.2581602037E-3, 3.7740699481E-3, -1.3462699717E-3,
                    -3.9103501476E-3, -4.4565401040E-3, 5.8724298142E-3,
                    2.8760801069E-3, -8.5267601535E-3, 2.8760801069E-3,
                    5.8724298142E-3, -4.4565401040E-3, -3.9103501476E-3,
                    8.1125000725E-4, -4.4451598078E-3, -1.2316980399E-2,
                    -1.3955879956E-2, -1.4179450460E-2, -1.3955879956E-2,
                    -1.2316980399E-2, -4.4451598078E-3, 8.1125000725E-4],
                  [0.0000000000, -8.2846998703E-4, -5.7109999034E-5,
                   4.0110000555E-5, 4.6670897864E-3, 8.0871898681E-3,
                   1.4807609841E-2, 8.6204400286E-3, -3.1221499667E-3,
                   8.2846998703E-4, 0.0000000000, -9.7479997203E-4,
                   -6.9718998857E-3, -2.0865600090E-3, 2.3298799060E-3,
                   -4.4814897701E-3, 1.4917500317E-2, 8.6204400286E-3,
                   5.7109999034E-5, 9.7479997203E-4, 0.0000000000,
                   -1.2145539746E-2, -2.4427289143E-2, 5.0797060132E-2,
                   3.2785870135E-2, -4.4814897701E-3, 1.4807609841E-2,
                   -4.0110000555E-5, 6.9718998857E-3, 1.2145539746E-2,
                   0.0000000000, -0.1510555595, -8.2495503128E-2,
                   5.0797060132E-2, 2.3298799060E-3, 8.0871898681E-3,
                   -4.6670897864E-3, 2.0865600090E-3, 2.4427289143E-2,
                   0.1510555595, 0.0000000000, -0.1510555595,
                   -2.4427289143E-2, -2.0865600090E-3, 4.6670897864E-3,
                   -8.0871898681E-3, -2.3298799060E-3, -5.0797060132E-2,
                   8.2495503128E-2, 0.1510555595, 0.0000000000,
                   -1.2145539746E-2, -6.9718998857E-3, 4.0110000555E-5,
                   -1.4807609841E-2, 4.4814897701E-3, -3.2785870135E-2,
                   -5.0797060132E-2, 2.4427289143E-2, 1.2145539746E-2,
                   0.0000000000, -9.7479997203E-4, -5.7109999034E-5,
                   -8.6204400286E-3, -1.4917500317E-2, 4.4814897701E-3,
                   -2.3298799060E-3, 2.0865600090E-3, 6.9718998857E-3,
                   9.7479997203E-4, 0.0000000000, -8.2846998703E-4,
                   3.1221499667E-3, -8.6204400286E-3, -1.4807609841E-2,
                   -8.0871898681E-3, -4.6670897864E-3, -4.0110000555E-5,
                   5.7109999034E-5, 8.2846998703E-4, 0.0000000000],
                  [8.1125000725E-4, -3.9103501476E-3, -1.3462699717E-3,
                   -7.4700999539E-4, 0.0000000000, 7.4700999539E-4,
                   1.3462699717E-3, 3.9103501476E-3, -8.1125000725E-4,
                   -4.4451598078E-3, -4.4565401040E-3, 3.7740699481E-3,
                   3.6522001028E-4, 0.0000000000, -3.6522001028E-4,
                   -3.7740699481E-3, 4.4565401040E-3, 4.4451598078E-3,
                   -1.2316980399E-2, 5.8724298142E-3, -8.2581602037E-3,
                   2.2522680461E-2, 0.0000000000, -2.2522680461E-2,
                   8.2581602037E-3, -5.8724298142E-3, 1.2316980399E-2,
                   -1.3955879956E-2, 2.8760801069E-3, -3.9442278445E-2,
                   0.1105690673, 0.0000000000, -0.1105690673,
                   3.9442278445E-2, -2.8760801069E-3, 1.3955879956E-2,
                   -1.4179450460E-2, -8.5267601535E-3, -5.3605638444E-2,
                   0.1768419296, 0.0000000000, -0.1768419296,
                   5.3605638444E-2, 8.5267601535E-3, 1.4179450460E-2,
                   -1.3955879956E-2, 2.8760801069E-3, -3.9442278445E-2,
                   0.1105690673, 0.0000000000, -0.1105690673,
                   3.9442278445E-2, -2.8760801069E-3, 1.3955879956E-2,
                   -1.2316980399E-2, 5.8724298142E-3, -8.2581602037E-3,
                   2.2522680461E-2, 0.0000000000, -2.2522680461E-2,
                   8.2581602037E-3, -5.8724298142E-3, 1.2316980399E-2,
                   -4.4451598078E-3, -4.4565401040E-3, 3.7740699481E-3,
                   3.6522001028E-4, 0.0000000000, -3.6522001028E-4,
                   -3.7740699481E-3, 4.4565401040E-3, 4.4451598078E-3,
                   8.1125000725E-4, -3.9103501476E-3, -1.3462699717E-3,
                   -7.4700999539E-4, 0.0000000000, 7.4700999539E-4,
                   1.3462699717E-3, 3.9103501476E-3, -8.1125000725E-4],
                  [3.1221499667E-3, -8.6204400286E-3, -1.4807609841E-2,
                   -8.0871898681E-3, -4.6670897864E-3, -4.0110000555E-5,
                   5.7109999034E-5, 8.2846998703E-4, 0.0000000000,
                   -8.6204400286E-3, -1.4917500317E-2, 4.4814897701E-3,
                   -2.3298799060E-3, 2.0865600090E-3, 6.9718998857E-3,
                   9.7479997203E-4, -0.0000000000, -8.2846998703E-4,
                   -1.4807609841E-2, 4.4814897701E-3, -3.2785870135E-2,
                   -5.0797060132E-2, 2.4427289143E-2, 1.2145539746E-2,
                   0.0000000000, -9.7479997203E-4, -5.7109999034E-5,
                   -8.0871898681E-3, -2.3298799060E-3, -5.0797060132E-2,
                   8.2495503128E-2, 0.1510555595, -0.0000000000,
                   -1.2145539746E-2, -6.9718998857E-3, 4.0110000555E-5,
                   -4.6670897864E-3, 2.0865600090E-3, 2.4427289143E-2,
                   0.1510555595, 0.0000000000, -0.1510555595,
                   -2.4427289143E-2, -2.0865600090E-3, 4.6670897864E-3,
                   -4.0110000555E-5, 6.9718998857E-3, 1.2145539746E-2,
                   0.0000000000, -0.1510555595, -8.2495503128E-2,
                   5.0797060132E-2, 2.3298799060E-3, 8.0871898681E-3,
                   5.7109999034E-5, 9.7479997203E-4, -0.0000000000,
                   -1.2145539746E-2, -2.4427289143E-2, 5.0797060132E-2,
                   3.2785870135E-2, -4.4814897701E-3, 1.4807609841E-2,
                   8.2846998703E-4, -0.0000000000, -9.7479997203E-4,
                   -6.9718998857E-3, -2.0865600090E-3, 2.3298799060E-3,
                   -4.4814897701E-3, 1.4917500317E-2, 8.6204400286E-3,
                   0.0000000000, -8.2846998703E-4, -5.7109999034E-5,
                   4.0110000555E-5, 4.6670897864E-3, 8.0871898681E-3,
                   1.4807609841E-2, 8.6204400286E-3, -3.1221499667E-3]]).T)
    return filters

def sp5Filters():
    filters = {}
    filters['harmonics'] = np.array([1, 3, 5])
    filters['mtx'] = (
        np.array([[0.3333, 0.2887, 0.1667, 0.0000, -0.1667, -0.2887],
                  [0.0000, 0.1667, 0.2887, 0.3333, 0.2887, 0.1667],
                  [0.3333, -0.0000, -0.3333, -0.0000, 0.3333, -0.0000],
                  [0.0000, 0.3333, 0.0000, -0.3333, 0.0000, 0.3333],
                  [0.3333, -0.2887, 0.1667, -0.0000, -0.1667, 0.2887],
                  [-0.0000, 0.1667, -0.2887, 0.3333, -0.2887, 0.1667]]))
    filters['hi0filt'] = (
        np.array([[-0.00033429, -0.00113093, -0.00171484,
                    -0.00133542, -0.00080639, -0.00133542,
                    -0.00171484, -0.00113093, -0.00033429],
                  [-0.00113093, -0.00350017, -0.00243812,
                    0.00631653, 0.01261227, 0.00631653,
                    -0.00243812,-0.00350017, -0.00113093],
                  [-0.00171484, -0.00243812, -0.00290081,
                    -0.00673482, -0.00981051, -0.00673482,
                    -0.00290081, -0.00243812, -0.00171484],
                  [-0.00133542, 0.00631653, -0.00673482,
                    -0.07027679, -0.11435863, -0.07027679,
                    -0.00673482, 0.00631653, -0.00133542],
                  [-0.00080639, 0.01261227, -0.00981051,
                    -0.11435863, 0.81380200, -0.11435863,
                    -0.00981051, 0.01261227, -0.00080639],
                  [-0.00133542, 0.00631653, -0.00673482,
                    -0.07027679, -0.11435863, -0.07027679,
                    -0.00673482, 0.00631653, -0.00133542],
                  [-0.00171484, -0.00243812, -0.00290081,
                    -0.00673482, -0.00981051, -0.00673482,
                    -0.00290081, -0.00243812, -0.00171484],
                  [-0.00113093, -0.00350017, -0.00243812,
                    0.00631653, 0.01261227, 0.00631653,
                    -0.00243812, -0.00350017, -0.00113093],
                  [-0.00033429, -0.00113093, -0.00171484,
                    -0.00133542, -0.00080639, -0.00133542,
                    -0.00171484, -0.00113093, -0.00033429]]))
    filters['lo0filt'] = (
        np.array([[0.00341614, -0.01551246, -0.03848215, -0.01551246,
                  0.00341614],
                 [-0.01551246, 0.05586982, 0.15925570, 0.05586982,
                   -0.01551246],
                 [-0.03848215, 0.15925570, 0.40304148, 0.15925570,
                   -0.03848215],
                 [-0.01551246, 0.05586982, 0.15925570, 0.05586982,
                   -0.01551246],
                 [0.00341614, -0.01551246, -0.03848215, -0.01551246,
                  0.00341614]]))
    filters['lofilt'] = (
        2 * np.array([[0.00085404, -0.00244917, -0.00387812, -0.00944432,
                       -0.00962054, -0.00944432, -0.00387812, -0.00244917,
                       0.00085404],
                      [-0.00244917, -0.00523281, -0.00661117, 0.00410600,
                        0.01002988, 0.00410600, -0.00661117, -0.00523281,
                        -0.00244917],
                      [-0.00387812, -0.00661117, 0.01396746, 0.03277038,
                        0.03981393, 0.03277038, 0.01396746, -0.00661117,
                        -0.00387812],
                      [-0.00944432, 0.00410600, 0.03277038, 0.06426333,
                        0.08169618, 0.06426333, 0.03277038, 0.00410600,
                        -0.00944432],
                      [-0.00962054, 0.01002988, 0.03981393, 0.08169618,
                        0.10096540, 0.08169618, 0.03981393, 0.01002988,
                        -0.00962054],
                      [-0.00944432, 0.00410600, 0.03277038, 0.06426333,
                        0.08169618, 0.06426333, 0.03277038, 0.00410600,
                        -0.00944432],
                      [-0.00387812, -0.00661117, 0.01396746, 0.03277038,
                        0.03981393, 0.03277038, 0.01396746, -0.00661117,
                        -0.00387812],
                      [-0.00244917, -0.00523281, -0.00661117, 0.00410600,
                        0.01002988, 0.00410600, -0.00661117, -0.00523281,
                        -0.00244917],
                      [0.00085404, -0.00244917, -0.00387812, -0.00944432,
                       -0.00962054, -0.00944432, -0.00387812, -0.00244917,
                       0.00085404]]))
    filters['bfilts'] = (
        np.array([[0.00277643, 0.00496194, 0.01026699, 0.01455399, 0.01026699,
                   0.00496194, 0.00277643, -0.00986904, -0.00893064, 
                   0.01189859, 0.02755155, 0.01189859, -0.00893064,
                   -0.00986904, -0.01021852, -0.03075356, -0.08226445,
                   -0.11732297, -0.08226445, -0.03075356, -0.01021852,
                   0.00000000, 0.00000000, 0.00000000, 0.00000000, 0.00000000,
                   0.00000000, 0.00000000, 0.01021852, 0.03075356, 0.08226445,
                   0.11732297, 0.08226445, 0.03075356, 0.01021852, 0.00986904,
                   0.00893064, -0.01189859, -0.02755155, -0.01189859, 
                   0.00893064, 0.00986904, -0.00277643, -0.00496194,
                   -0.01026699, -0.01455399, -0.01026699, -0.00496194,
                   -0.00277643],
                  [-0.00343249, -0.00640815, -0.00073141, 0.01124321,
                    0.00182078, 0.00285723, 0.01166982, -0.00358461,
                    -0.01977507, -0.04084211, -0.00228219, 0.03930573,
                    0.01161195, 0.00128000, 0.01047717, 0.01486305,
                    -0.04819057, -0.12227230, -0.05394139, 0.00853965,
                    -0.00459034, 0.00790407, 0.04435647, 0.09454202,
                    -0.00000000, -0.09454202, -0.04435647, -0.00790407,
                    0.00459034, -0.00853965, 0.05394139, 0.12227230,
                    0.04819057, -0.01486305, -0.01047717, -0.00128000,
                    -0.01161195, -0.03930573, 0.00228219, 0.04084211,
                    0.01977507, 0.00358461, -0.01166982, -0.00285723,
                    -0.00182078, -0.01124321, 0.00073141, 0.00640815,
                    0.00343249],
                  [0.00343249, 0.00358461, -0.01047717, -0.00790407,
                   -0.00459034, 0.00128000, 0.01166982, 0.00640815,
                   0.01977507, -0.01486305, -0.04435647, 0.00853965,
                   0.01161195, 0.00285723, 0.00073141, 0.04084211, 0.04819057,
                   -0.09454202, -0.05394139, 0.03930573, 0.00182078,
                   -0.01124321, 0.00228219, 0.12227230, -0.00000000,
                   -0.12227230, -0.00228219, 0.01124321, -0.00182078,
                   -0.03930573, 0.05394139, 0.09454202, -0.04819057,
                   -0.04084211, -0.00073141, -0.00285723, -0.01161195,
                   -0.00853965, 0.04435647, 0.01486305, -0.01977507,
                   -0.00640815, -0.01166982, -0.00128000, 0.00459034,
                   0.00790407, 0.01047717, -0.00358461, -0.00343249],
                  [-0.00277643, 0.00986904, 0.01021852, -0.00000000,
                    -0.01021852, -0.00986904, 0.00277643, -0.00496194,
                    0.00893064, 0.03075356, -0.00000000, -0.03075356,
                    -0.00893064, 0.00496194, -0.01026699, -0.01189859,
                    0.08226445, -0.00000000, -0.08226445, 0.01189859,
                    0.01026699, -0.01455399, -0.02755155, 0.11732297,
                    -0.00000000, -0.11732297, 0.02755155, 0.01455399,
                    -0.01026699, -0.01189859, 0.08226445, -0.00000000,
                    -0.08226445, 0.01189859, 0.01026699, -0.00496194,
                    0.00893064, 0.03075356, -0.00000000, -0.03075356,
                    -0.00893064, 0.00496194, -0.00277643, 0.00986904,
                    0.01021852, -0.00000000, -0.01021852, -0.00986904,
                    0.00277643],
                  [-0.01166982, -0.00128000, 0.00459034, 0.00790407,
                    0.01047717, -0.00358461, -0.00343249, -0.00285723,
                    -0.01161195, -0.00853965, 0.04435647, 0.01486305,
                    -0.01977507, -0.00640815, -0.00182078, -0.03930573,
                    0.05394139, 0.09454202, -0.04819057, -0.04084211,
                    -0.00073141, -0.01124321, 0.00228219, 0.12227230,
                    -0.00000000, -0.12227230, -0.00228219, 0.01124321,
                    0.00073141, 0.04084211, 0.04819057, -0.09454202,
                    -0.05394139, 0.03930573, 0.00182078, 0.00640815,
                    0.01977507, -0.01486305, -0.04435647, 0.00853965,
                    0.01161195, 0.00285723, 0.00343249, 0.00358461,
                    -0.01047717, -0.00790407, -0.00459034, 0.00128000,
                    0.01166982],
                  [-0.01166982, -0.00285723, -0.00182078, -0.01124321,
                    0.00073141, 0.00640815, 0.00343249, -0.00128000,
                    -0.01161195, -0.03930573, 0.00228219, 0.04084211,
                    0.01977507, 0.00358461, 0.00459034, -0.00853965,
                    0.05394139, 0.12227230, 0.04819057, -0.01486305,
                    -0.01047717, 0.00790407, 0.04435647, 0.09454202,
                    -0.00000000, -0.09454202, -0.04435647, -0.00790407,
                    0.01047717, 0.01486305, -0.04819057, -0.12227230,
                    -0.05394139, 0.00853965, -0.00459034, -0.00358461,
                    -0.01977507, -0.04084211, -0.00228219, 0.03930573,
                    0.01161195, 0.00128000, -0.00343249, -0.00640815,
                    -0.00073141, 0.01124321, 0.00182078, 0.00285723,
                    0.01166982]]).T) 
    return filters

# convert level and band to dictionary index
def LB2idx(lev,band,nlevs,nbands):
    if lev == 0:
        idx = 0
    elif lev == nlevs-1:
        # (Nlevels - ends)*Nbands + ends -1 (because zero indexed)
        idx = (((nlevs-2)*nbands)+2)-1
    else:
        # (level-first level) * nbands + first level + current band 
        #idx = (nbands*(lev-1))+1+band
        idx = (nbands*(lev-1))+1-band + 1
    return idx

# given and index into dictionary return level and band
def idx2LB(idx, nlevs, nbands):
    if idx == 0:
        return ('hi', -1)
    elif idx == ((nlevs-2)*nbands)+1:
        return ('lo', -1)
    else:
        lev = math.ceil(idx/nbands)
        band = (idx % nbands) + 1
        if band == nbands:
            band = 0
        return (lev, band)

# find next largest size in list
def nextSz(size, sizeList):
    ## make sure sizeList is strictly increasing
    if sizeList[0] > sizeList[len(sizeList)-1]:
        sizeList = sizeList[::-1]
    outSize = (0,0)
    idx = 0;
    while outSize == (0,0) and idx < len(sizeList):
        if sizeList[idx] > size:
            outSize = sizeList[idx]
        idx += 1
    return outSize

def mkImpulse(*args):
    # create an image that is all zeros except for an impulse
    if(len(args) == 0):
        print "mkImpulse(size, origin, amplitude)"
        print "first input parameter is required"
        return
    
    if(isinstance(args[0], int)):
        sz = (args[0], args[0])
    elif(isinstance(args[0], tuple)):
        sz = args[0]
    else:
        print "size parameter must be either an integer or a tuple"
        return

    if(len(args) > 1):
        origin = args[1]
    else:
        origin = ( np.ceil(sz[0]/2.0), np.ceil(sz[1]/2.0) )

    if(len(args) > 2):
        amplitude = args[2]
    else:
        amplitude = 1

    res = np.zeros(sz);
    res[origin[0], origin[1]] = amplitude

    return res

# Compute a steering matrix (maps a directional basis set onto the
# angular Fourier harmonics).  HARMONICS is a vector specifying the
# angular harmonics contained in the steerable basis/filters.  ANGLES 
# (optional) is a vector specifying the angular position of each filter.  
# REL_PHASES (optional, default = 'even') specifies whether the harmonics 
# are cosine or sine phase aligned about those positions.
# The result matrix is suitable for passing to the function STEER.
# mtx = steer2HarmMtx(harmonics, angles, evenorodd)
def steer2HarmMtx(*args):

    if len(args) == 0:
        print "Error: first parameter 'harmonics' is required."
        return
    
    if len(args) > 0:
        harmonics = np.array(args[0])

    # optional parameters
    numh = (2*harmonics.shape[0]) - (harmonics == 0).sum()
    if len(args) > 1:
        angles = args[1]
    else:
        angles = np.pi * np.array(range(numh)) / numh
        
    if len(args) > 2:
        if isinstance(args[2], basestring):
            if args[2] == 'even' or args[2] == 'EVEN':
                evenorodd = 0
            elif args[2] == 'odd' or args[2] == 'ODD':
                evenorodd = 1
            else:
                print "Error: only 'even' and 'odd' are valid entries for the third input parameter."
                return
        else:
            print "Error: third input parameter must be a string (even/odd)."
    else:
        evenorodd = 0

    # Compute inverse matrix, which maps to Fourier components onto 
    #   steerable basis
    imtx = np.zeros((angles.shape[0], numh))
    col = 0
    for h in harmonics:
        args = h * angles
        if h == 0:
            imtx[:, col] = np.ones(angles.shape)
            col += 1
        elif evenorodd:
            imtx[:, col] = np.sin(args)
            imtx[:, col+1] = np.negative( np.cos(args) )
            col += 2
        else:
            imtx[:, col] = np.cos(args)
            imtx[:, col+1] = np.sin(args)
            col += 2

    r = np.rank(imtx)
    if r != numh and r != angles.shape[0]:
        print "Warning: matrix is not full rank"

    mtx = np.linalg.pinv(imtx)
    
    return mtx

# [X, Y] = rcosFn(WIDTH, POSITION, VALUES)
#
# Return a lookup table (suitable for use by INTERP1) 
# containing a "raised cosine" soft threshold function:
# 
#    Y =  VALUES(1) + (VALUES(2)-VALUES(1)) *
#              cos^2( PI/2 * (X - POSITION + WIDTH)/WIDTH )
#
# WIDTH is the width of the region over which the transition occurs
# (default = 1). POSITION is the location of the center of the
# threshold (default = 0).  VALUES (default = [0,1]) specifies the
# values to the left and right of the transition.
def rcosFn(*args):
    
    if len(args) > 0:
        width = args[0]
    else:
        width = 1

    if len(args) > 1:
        position = args[1]
    else:
        position = 0

    if len(args) > 2:
        values = args[2]
    else:
        values = (0,1)

    #---------------------------------------------

    sz = 256   # arbitrary!

    X = np.pi * np.array(range(-sz-1,2)) / (2*sz)

    Y = values[0] + (values[1]-values[0]) * np.cos(X)**2;

    # make sure end values are repeated, for extrapolation...
    Y[0] = Y[1]
    Y[sz+2] = Y[sz+1]
    
    X = position + (2*width/np.pi) * (X + np.pi/4)

    return (X,Y)

# Compute a matrix of dimension SIZE (a [Y X] 2-vector, or a scalar)
# containing samples of the polar angle (in radians, CW from the
# X-axis, ranging from -pi to pi), relative to angle PHASE (default =
# 0), about ORIGIN pixel (default = (size+1)/2).
def mkAngle(*args):

    if len(args) > 0:
        sz = args[0]
        if not isinstance(sz, tuple):
            sz = (sz, sz)
    else:
        print "Error: first input parameter 'size' is required!"
        print "makeAngle(size, phase, origin)"
        return

    # ------------------------------------------------------------
    # Optional args:

    if len(args) > 1:
        phase = args[1]
    else:
        phase = 'not set'

    if len(args) > 2:
        origin = args[2]
    else:
        origin = (sz[0]+1/2, sz[1]+1/2)

    #------------------------------------------------------------------

    (xramp, yramp) = np.meshgrid(np.array(range(1,sz[1]+1))-origin[1], 
                                 (np.array(range(1,sz[0]+1)))-origin[0])
    xramp = np.array(xramp)
    yramp = np.array(yramp)

    res = np.arctan2(yramp, xramp)
    
    if phase != 'not set':
        res = ((res+(np.pi-phase)) % (2*np.pi)) - np.pi

    return res

# [HFILT] = modulateFlipShift(LFILT)
# QMF/Wavelet highpass filter construction: modulate by (-1)^n,
# reverse order (and shift by one, which is handled by the convolution
# routines).  This is an extension of the original definition of QMF's
# (e.g., see Simoncelli90).
def modulateFlip(*args):

    if len(args) == 0:
        print "Error: filter input parameter required."
        return

    lfilt = args[0]
    
    sz = len(lfilt)
    sz2 = np.ceil(sz/2.0);

    ind = np.array(range(sz-1,-1,-1))
    print ind

    hfilt = lfilt[ind].T * (-1)**((ind+1)-sz2)

    return hfilt

# RES = blurDn(IM, LEVELS, FILT)
# Blur and downsample an image.  The blurring is done with filter
# kernel specified by FILT (default = 'binom5'), which can be a string
# (to be passed to namedFilter), a vector (applied separably as a 1D
# convolution kernel in X and Y), or a matrix (applied as a 2D
# convolution kernel).  The downsampling is always by 2 in each
# direction.
# The procedure is applied recursively LEVELS times (default=1).
# Eero Simoncelli, 3/97.  Ported to python by Rob Young 4/14
# function res = blurDn(im, nlevs, filt)
def blurDn(*args):
    if len(args) == 0:
        print "Error: image input parameter required."
        return

    im = np.array(args[0])
    
    # optional args
    if len(args) > 1:
        nlevs = args[1]
    else:
        nlevs = 1

    if len(args) > 2:
        filt = args[2]
        if isinstance(filt, basestring):
            filt = namedFilter(filt)
    else:
        filt = namedFilter('binom5')
    filt = [x/sum(filt) for x in filt]
    filt = np.array(filt)
    
    if nlevs > 1:
        im = blurDn(im, nlevs-1, filt)

    if nlevs >= 1:
        if len(im.shape) == 1 or im.shape[0] == 1 or im.shape[1] == 1:
            # 1D image
            if len(filt.shape) > 1 and (filt.shape[1]!=1 and filt.shape[2]!=1):
                # >1D filter
                print 'Error: Cannot apply 2D filter to 1D signal'
                return
            # orient filter and image correctly
            if im.shape[0] == 1:
                if len(filt.shape) == 1 or filt.shape[1] == 1:
                    filt = filt.T
            else:
                if filt.shape[0] == 1:
                    filt = filt.T
                
            res = corrDn(im.shape[0], im.shape[1], im, filt.shape[0], 
                         filt.shape[1], filt, 'reflect1', 2, 2)
            if len(im.shape) == 1 or im.shape[1] == 1:
                res = np.reshape(res, (np.ceil(im.shape[0]/2.0), 1))
            else:
                res = np.reshape(res, (1, np.ceil(im.shape[1]/2.0)))
        elif len(filt.shape) == 1 or filt.shape[0] == 1 or filt.shape[1] == 1:
            # 2D image and 1D filter
            res = corrDn(im.shape[0], im.shape[1], im.T, filt.shape[0], 
                         filt.shape[1], filt, 'reflect1', 2, 1).T
            #res = np.reshape(res, (im.shape[1], np.ceil(im.shape[0]/2.0))).T
            print res
            res = corrDn(res.shape[1], res.shape[0], res, filt.shape[0], 
                         filt.shape[1], filt, 'reflect1', 2, 1)
            #res = np.reshape(res, (np.ceil(im.shape[0]/2.0),
            #                       np.ceil(im.shape[1]/2.0)))
            print res
        else:  # 2D image and 2D filter
            res = corrDn(im.shape[0], im.shape[1], im, filt.shape[0], 
                         filt.shape[1], filt, 'reflect1', 2, 2)
    else:
        res = im
            
    return res

# Convolution of two matrices, with boundaries handled via reflection
# about the edge pixels.  Result will be of size of LARGER matrix.
# 
# The origin of the smaller matrix is assumed to be its center.
# For even dimensions, the origin is determined by the CTR (optional) 
# argument:
#      CTR   origin
#       0     DIM/2      (default)
#       1   (DIM/2)+1  
def rconv2(*args):

    if len(args) < 2:
        print "Error: two matrices required as input parameters"
        return

    if len(args) == 2:
        ctr = 0

    if ( args[0].shape[0] >= args[1].shape[0] and 
         args[0].shape[1] >= args[1].shape[1] ):
        large = args[0]
        small = args[1]
    elif ( args[0].shape[0] <= args[1].shape[0] and 
           args[0].shape[1] <= args[1].shape[1] ):
        large = args[1]
        small = args[0]
    else:
        print 'one arg must be larger than the other in both dimensions!'
        return

    ly = large.shape[0]
    lx = large.shape[1]
    sy = small.shape[0]
    sx = small.shape[1]

    ## These values are one less than the index of the small mtx that falls on 
    ## the border pixel of the large matrix when computing the first 
    ## convolution response sample:
    sy2 = np.floor((sy+ctr-1)/2)
    sx2 = np.floor((sx+ctr-1)/2)

    # pad with reflected copies
    #nw = large[sy-sy2:2:-1, sx-sx2:2:-1]
    #n = large[sy-sy2:2:-1, :]
    #ne = large[sy-sy2:2:-1, lx-1:lx-sx2:-1]
    #w = large[:, sx-sx2:2:-1]
    #e = large[:, lx-1:lx-sx2:-1]
    #sw = large[ly-1:ly-sy2:-1, sx-sx2:2:-1]
    #s = large[ly-1:ly-sy2:-1, :]
    #se = large[ly-1:ly-sy2:-1, lx-1:lx-sx2:-1]
    nw = large[sy-sy2-1:0:-1, sx-sx2-1:0:-1]
    n = large[sy-sy2-1:0:-1, :]
    ne = large[sy-sy2-1:0:-1, lx-2:lx-sx2-2:-1]
    w = large[:, sx-sx2-1:0:-1]
    e = large[:, lx-2:lx-sx2-2:-1]
    sw = large[ly-2:ly-sy2-2:-1, sx-sx2-1:0:-1]
    s = large[ly-2:ly-sy2-2:-1, :]
    se = large[ly-2:ly-sy2-2:-1, lx-2:lx-sx2-2:-1]

    n = np.column_stack((nw, n, ne))
    c = np.column_stack((w,large,e))
    s = np.column_stack((sw, s, se))

    clarge = np.concatenate((n, c), axis=0)
    clarge = np.concatenate((clarge, s), axis=0)
    
    return spsig.convolve(clarge, small, 'valid')

# compute minimum and maximum values of input matrix, returning them as tuple
def range2(*args):
    if not np.isreal(args[0]).all():
        print 'Error: matrix must be real-valued'

    return (args[0].min(), args[0].max())

# Sample variance of a matrix.
#  Passing MEAN (optional) makes the calculation faster.
def var2(*args):
    if len(args) == 1:
        mn = args[0].mean()
    
    if(np.isreal(args[0]).all()):
        res = sum(sum((args[0]-mn)**2)) / max(np.prod(args[0].shape)-1, 1)
    else:
        res = sum((args[0]-mn).real**2) + 1j*sum((args[0]-mn).imag)**2
        res = res /  max(np.prod(args[0].shape)-1, 1)

    return res

# Sample kurtosis (fourth moment divided by squared variance) 
# of a matrix.  Kurtosis of a Gaussian distribution is 3.
#  MEAN (optional) and VAR (optional) make the computation faster.
def kurt2(*args):
    if len(args) == 0:
        print 'Error: input matrix is required'

    if len(args) < 2:
        mn = args[0].mean()
    else:
        mn = args[1]

    if len(args) < 3:
        v = var2(args[0])
    else:
        v = args[2]

    if np.isreal(args[0]).all():
        res = (np.abs(args[0]-mn)**4).mean() / v**2
    else:
        res = ( (((args[0]-mn).real**4).mean() / v.real**2) + 
                ((np.i * (args[0]-mn).imag**4).mean() / v.imag**2) )

    return res

# Report image (matrix) statistics.
# When called on a single image IM1, report min, max, mean, stdev, 
# and kurtosis.
# When called on two images (IM1 and IM2), report min, max, mean, 
# stdev of the difference, and also SNR (relative to IM1).
def imStats(*args):

    if len(args) == 0:
        print 'Error: at least one input image is required'
        return
    elif len(args) == 1 and not np.isreal(args[0]).all():
        print 'Error: input images must be real-valued matrices'
        return
    elif len(args) == 2 and ( not np.isreal(args[0]).all() or not np.isreal(args[1]).all()):
        print 'Error: input images must be real-valued matrices'
        return
    elif len(args) > 2:
        print 'Error: maximum of two input images allowed'
        return

    if len(args) == 2:
        difference = args[0] - args[1]
        (mn, mx) = range2(difference)
        mean = difference.mean()
        v = var2(difference)
        if v < np.finfo(np.double).tiny:
            snr = np.inf
        else:
            snr = 10 * np.log10(var2(args[0])/v)
        print 'Difference statistics:'
        print '  Range: [%d, %d]' % (mn, mx)
        print '  Mean: %f,  Stdev (rmse): %f,  SNR (dB): %f' % (mean, np.sqrt(v), snr)
    else:
        (mn, mx) = range2(args[0])
        mean = args[0].mean()
        var = var2(args[0])
        stdev = np.sqrt(var.real) + np.sqrt(var.imag)
        kurt = kurt2(args[0], mean, stdev**2)
        print 'Image statistics:'
        print '  Range: [%f, %f]' % (mn, mx)
        print '  Mean: %f,  Stdev: %f,  Kurtosis: %f' % (mean, stdev, kurt)
        
# makes image the same as read in by matlab
def correctImage(img):
    tmpcol = img[:,0]
    for i in range(img.shape[1]-1):
        img[:,i] = img[:,i+1]
    img[:, img.shape[1]-1] = tmpcol
    return img
