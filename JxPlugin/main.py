# -*- coding: utf-8 -*-
# Copyright: Olivier Binda <olivier.binda@wanadoo.fr>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
# ---------------------------------------------------------------------------
# This file is a plugin for the "anki" flashcard application http://repose.cx/anki/
# ---------------------------------------------------------------------------

from ankiqt import mw,ui
import os, sys, time

# support frozen distribs
if getattr(sys, "frozen", None):
    os.environ['MATPLOTLIBDATA'] = os.path.join(
        os.path.dirname(sys.argv[0]),
        "matplotlibdata")
try:
    from matplotlib.figure import Figure
except UnicodeEncodeError:
    # haven't tracked down the cause of this yet, but reloading fixes it
    try:
        from matplotlib.figure import Figure
    except ImportError:
        pass
except ImportError:
    pass
import os
import traceback
import sys

from ankiqt.ui.graphs import GraphWindow
from ankiqt.ui.graphs import AdjustableFigure

from anki.graphs import DeckGraphs

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4 import QtGui, QtCore

from ankiqt import mw, ui





from graphs import *







from ankiqt.ui.utils import askUser, getOnlyText
from ankiqt import *

from ui.utils import showText

from ankiqt.ui.utils import saveGeom, restoreGeom

	
	
	
	
	
	
######################################################################
#
#                                             Tools
#
######################################################################



from tools import *
from anki.utils import canonifyTags, addTags
	


from stats import *


from PyQt4.QtWebKit import QWebPage, QWebView
from PyQt4 import QtWebKit

from string import Template












###############################################################################################################
#
#    displays aditionnal info  in the answer (Words : JLPT, Kanji : JLPT/Grade/stroke order/related words.
#
###############################################################################################################
import math
import re

from answer import *




from loaddata import *
######################################################################
#
#                      Will run in init hook
#
######################################################################

from ui_menu import *

if __name__ == "__main__":
    print "Don't run me : I'm a plugin."
else:  
    #r = KanjiGraphLauncher(mw)
    mw.addHook('init', init_JxPlugin)
    print 'Lakedaemon plugin loaded'

