import numpy
from PIL import Image
import scipy.stats
import matplotlib.pyplot as plt


def showIm(*args):
    # check and set input parameters
    if len(args) == 0:
        print("showIm( matrix, range, zoom, label, nshades )")
        print("  matrix is string. It should be the name of a 2D array.")
        print("  range is a two element tuple.  It specifies the values that ")
        print("    map to the min and max colormap values.  Passing a value ")
        print("    of 'auto' (default) sets range=[min,max].  'auto2' sets ")
        print("    range=[mean-2*stdev, mean+2*stdev].  'auto3' sets ")
        print("    range=[p1-(p2-p1)/8, p2+(p2-p1)/8], where p1 is the 10th ")
        print("    percientile value of the sorted matix samples, and p2 is ")
        print("    the 90th percentile value.")
        print("  zoom specifies the number of matrix samples per screen pixel.")
        print("    It will be rounded to an integer, or 1 divided by an ")
        print("    integer.")
        #print "    A value of 'same' or 'auto' (default) causes the "
        #print "    zoom value to be chosen automatically to fit the image into"
        #print "    the current axes."
        #print "    A value of 'full' fills the axis region "
        #print "    (leaving no room for labels)."
        print("  label - A string that is used as a figure title.")
        print("  NSHADES (optional) specifies the number of gray shades, ")
        print("    and defaults to the size of the current colormap. ")

    if len(args) > 0:   # matrix entered
        matrix = numpy.array(args[0])

    if len(args) > 1:   # range entered
        if isinstance(args[1], str):
            if args[1] is "auto":
                imRange = ( numpy.amin(matrix), numpy.amax(matrix) )
            elif args[1] is "auto2":
                imRange = ( matrix.mean()-2*matrix.std(), 
                            matrix.mean()+2*matrix.std() )
            elif args[1] is "auto3":
                #p1 = numpy.percentile(matrix, 10)  not in python 2.6.6?!
                #p2 = numpy.percentile(matrix, 90)
                p1 = scipy.stats.scoreatpercentile(numpy.hstack(matrix), 10)
                p2 = scipy.stats.scoreatpercentile(numpy.hstack(matrix), 90)
                imRange = (p1-(p2-p1)/8.0, p2+(p2-p1)/8.0)
            else:
                print("Error: range of %s is not recognized." % args[1])
                print("       please use a two element tuple or ")
                print("       'auto', 'auto2' or 'auto3'")
                print("       enter 'showIm' for more info about options")
                return
        else:
            imRange = args[1][0], args[1][1]
    else:
        imRange = ( numpy.amin(matrix), numpy.amax(matrix) )

    if len(args) > 2:   # zoom entered
        zoom = args[2]
    else:
        zoom = 1

    if len(args) > 3:   # label entered
        label = args[3]
    else:
        label = ''

    if len(args) > 4:   # colormap entered
        nshades = args[4]
        print("colormap parameter is not supported.")
        print("Such specification does not make any sense.")
    else:
        nshades = 256  # NOQA

    # show image
    # create canvas (mpl)
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.set_title(label)

    width = matrix.shape[0] * zoom
    height = matrix.shape[1] * zoom

    # normalize image to [0, 255]
    pmin, pmax = matrix.min(), matrix.max()
    matrix = (matrix - pmin) / (pmax - pmin) * 255
    img = Image.fromarray(matrix.astype(numpy.uint8))

    # zoom
    if zoom != 1:
        img.thumbnail((width, height), Image.BICUBIC)

    ax.imshow(img, cmap='gray')
    plt.show()
