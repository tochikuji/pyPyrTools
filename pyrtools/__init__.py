import ctypes
import os

import pyrtools.JBhelpers
from pyrtools.binomialFilter import binomialFilter
from pyrtools.blurDn import blurDn
from pyrtools.blur import blur
from pyrtools.cconv2 import cconv2
from pyrtools.clip import clip
from pyrtools.comparePyr import comparePyr
from pyrtools.compareRecon import compareRecon
from pyrtools.corrDn import corrDn
from pyrtools.entropy2 import entropy2
from pyrtools.factorial import factorial
from pyrtools.Gpyr import Gpyr
from pyrtools.histoMatch import histoMatch
from pyrtools.histo import histo
from pyrtools.idx2LB import idx2LB
from pyrtools.imGradient import imGradient
from pyrtools.imStats import imStats
from pyrtools.kurt2 import kurt2
from pyrtools.LB2idx import LB2idx
from pyrtools.Lpyr import Lpyr
from pyrtools.maxPyrHt import maxPyrHt
from pyrtools.mkAngle import mkAngle
from pyrtools.mkAngularSine import mkAngularSine
from pyrtools.mkDisc import mkDisc
from pyrtools.mkFract import mkFract
from pyrtools.mkGaussian import mkGaussian
from pyrtools.mkImpulse import mkImpulse
from pyrtools.mkRamp import mkRamp
from pyrtools.mkR import mkR
from pyrtools.mkSine import mkSine
from pyrtools.mkSquare import mkSquare
from pyrtools.mkZonePlate import mkZonePlate
from pyrtools.modulateFlip import modulateFlip
from pyrtools.namedFilter import namedFilter
from pyrtools.nextSz import nextSz
from pyrtools.pointOp import pointOp
from pyrtools.pyramid import pyramid
from pyrtools.range2 import range2
from pyrtools.rconv2 import rconv2
from pyrtools.rcosFn import rcosFn
from pyrtools.round import round
from pyrtools.roundVal import roundVal
from pyrtools.SCFpyr import SCFpyr
from pyrtools.SFpyr import SFpyr
from pyrtools.shift import shift
from pyrtools.showIm import showIm
from pyrtools.skew2 import skew2
from pyrtools.sp0Filters import sp0Filters
from pyrtools.sp1Filters import sp1Filters
from pyrtools.sp3Filters import sp3Filters
from pyrtools.sp5Filters import sp5Filters
from pyrtools.Spyr import Spyr
from pyrtools.SpyrMulti import SpyrMulti
from pyrtools.steer2HarmMtx import steer2HarmMtx
from pyrtools.steer import steer
from pyrtools.strictly_decreasing import strictly_decreasing
from pyrtools.upBlur import upBlur
from pyrtools.upConv import upConv
from pyrtools.var2 import var2
from pyrtools.Wpyr import Wpyr
from pyrtools.zconv2 import zconv2

# load the C library
lib = ctypes.cdll.LoadLibrary(os.path.dirname(os.path.realpath(__file__)) +
                              '/wrapConv.so')
