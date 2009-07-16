# -*- coding: utf-8 -*-
# Copyright: Olivier Binda <olivier.binda@wanadoo.fr>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
# ---------------------------------------------------------------------------
# This file is a plugin for the "anki" flashcard application http://repose.cx/anki/
# ---------------------------------------------------------------------------
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4 import QtGui, QtCore


from ankiqt import mw,ui
from ankiqt.ui.utils import saveGeom, restoreGeom
from ankiqt.ui.graphs import AdjustableFigure

def JxGraphs():
	ui.dialogs.get("JxGraphs", mw, mw.deck)

class JxIntervalGraph(QDialog):

    def __init__(self, parent, *args):
        QDialog.__init__(self, parent, Qt.Window)
        ui.dialogs.open("JxGraphs", self)
        self.setAttribute(Qt.WA_DeleteOnClose)

    def reject(self):
        saveGeom(self, "Jxgraphs")
        ui.dialogs.close("JxGraphs")
        QDialog.reject(self)
