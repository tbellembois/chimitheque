# -*- coding: utf-8; -*-
#
# (c) 2011-2015 Thomas Bellembois thomas.bellembois@ens-lyon.fr
#
# This file is part of Chimithèque.
#
# Chimithèque is free software; you can redistribute it and/or modify
# it under the terms of the Cecill as published by the CEA, CNRS and INRIA
# either version 2 of the License, or (at your option) any later version.
#
# Chimithèque is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the Cecill along with Chimithèque.
# If not, see <http://www.cecill.info/licences/>.
#
# SVN Revision:
# -------------
# $Id: test.py 194 2015-02-23 16:27:16Z tbellemb $
#
import time

from chimitheque_logger import chimitheque_logger

mylogger = chimitheque_logger()


def index():

    import ctypes
    import os

    dir_path = os.path.dirname(os.path.realpath(__file__))
    lib = ctypes.cdll.LoadLibrary(os.path.join(dir_path, 'gochimithequeutils.so'))
    print "Loaded go generated SO library"

    l2ef = lib.LinearToEmpiricalFormula
    l2ef.restype = ctypes.c_char_p
    l2ef.argtypes = [ctypes.c_char_p]

    result = l2ef(ctypes.c_char_p(u"(CH3)2C[C6H2(Br)2OH]2"))
    print result

    return dict()
