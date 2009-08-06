# -*- coding: utf-8 -*-
# Copyright: Olivier Binda <olivier.binda@wanadoo.fr>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
# ---------------------------------------------------------------------------
# This file is a plugin for the "anki" flashcard application http://ichi2.net/anki/
# ---------------------------------------------------------------------------
import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4 import QtGui, QtCore


from ankiqt import mw,ui
from ankiqt.ui.utils import saveGeom, restoreGeom
from ankiqt.ui.graphs import AdjustableFigure

from graphs import *

class JxIntervalGraph(QDialog):

    def __init__(self, parent, *args):
        QDialog.__init__(self, parent, Qt.Window)
        ui.dialogs.open("JxGraphs", self)
        self.setAttribute(Qt.WA_DeleteOnClose)

    def reject(self):
        saveGeom(self, "Jxgraphs")
        ui.dialogs.close("JxGraphs")
        QDialog.reject(self)
	
class JxGraphWindow(object):

    nameMap = {
        'JLPT4Kanji': _("Kanji"),
        'Jouyou': _("Graded"),
	 'Freq4Kanji': _("KFreq"),
        'JLPT4Tango': _("Tango"),
        }

    def __init__(self, parent, deck):
        self.parent = parent
        self.deck = deck
        self.widgets = []
        self.dg = JxDeckGraphs(deck)
        self.diag = JxIntervalGraph(parent)
        self.diag.setWindowTitle(_("JxGraphs"))
        if parent.config.get('graphsGeom'):
            restoreGeom(self.diag, "Jxgraphs")
        else:
            if sys.platform.startswith("darwin"):
                self.diag.setMinimumSize(740, 680)
            else:
                self.diag.setMinimumSize(690, 715)

        scroll = QScrollArea(self.diag)
        topBox = QVBoxLayout(self.diag)
        topBox.addWidget(scroll)
        self.frame = QWidget(scroll)
        self.vbox = QVBoxLayout(self.frame)
        self.vbox.setMargin(0)
        self.vbox.setSpacing(0)
        self.frame.setLayout(self.vbox)
        self.range = [7, 14, 30, 90, 180, 365, 730, 1095, 1460, 1825]
        scroll.setWidget(self.frame)
        self.hbox = QHBoxLayout()
        topBox.addLayout(self.hbox)
        self.setupGraphs()
        self.setupButtons()
        self.showHideAll()
        self.diag.show()

	
    def setupGraphs(self):
		Jxdg = JxDeckGraphs(self.deck)

		kanji = AdjustableFigure(self.parent, 'JLPT4Kanji', Jxdg.graphTime2JLPT4Kanji, self.range) 
		kanji.addWidget(QLabel(_("<h1>JLPT Kanji Progress ('Kanji ?' card model)</h1>")))
		self.vbox.addWidget(kanji)
		self.widgets.append(kanji)
      
		graded = AdjustableFigure(self.parent, 'Jouyou', Jxdg.graphTime2Jouyou4Kanji, self.range) 
		graded.addWidget(QLabel(_("<h1>Jouyou Kanji Progress ('Kanji ?' card model)</h1>")))
		self.vbox.addWidget(graded)
		self.widgets.append(graded)

		KFreq = AdjustableFigure(self.parent, 'KFreq', Jxdg.graphTime2Frequency4Kanji, self.range) 
		KFreq.addWidget(QLabel(_("<h1>Kanji Accumulated Frequency ('Kanji ?' card model)</h1>")))
		self.vbox.addWidget(KFreq)
		self.widgets.append(KFreq)
		
      		# Time -> JLPT for Words graph
		WJLPT = AdjustableFigure(self.parent, 'JLPT4Tango', Jxdg.graphTime2JLPT4Tango, self.range) 
		WJLPT.addWidget(QLabel(_("<h1>JLPT Word Progress ('Recognition' card model)</h1>")))
		self.vbox.addWidget(WJLPT)
		self.widgets.append(WJLPT)

		TFreq = AdjustableFigure(self.parent, 'TFreq', Jxdg.graphTime2Frequency4Words, self.range) 
		TFreq.addWidget(QLabel(_("<h1>Tango Accumulated Frequency (('Recognition' card model)</h1>")))
		self.vbox.addWidget(TFreq)
		self.widgets.append(TFreq)
		
    def setupButtons(self):
        self.showhide = QPushButton(_("Show/Hide"))
        self.hbox.addWidget(self.showhide)
        self.showhide.connect(self.showhide, SIGNAL("clicked()"),self.onShowHide)
        refresh = QPushButton(_("Refresh"))
        self.hbox.addWidget(refresh)
        self.showhide.connect(refresh, SIGNAL("clicked()"),self.onRefresh)
        buttonBox = QDialogButtonBox(self.diag)
        buttonBox.setOrientation(Qt.Horizontal)
        close = buttonBox.addButton(QDialogButtonBox.Close)
        close.setDefault(True)
        self.diag.connect(buttonBox, SIGNAL("rejected()"), self.diag.close)
        help = buttonBox.addButton(QDialogButtonBox.Help)
        self.diag.connect(buttonBox, SIGNAL("helpRequested()"), self.onHelp)
        self.hbox.addWidget(buttonBox)

    def showHideAll(self):
        self.deck.startProgress(len(self.widgets))
        for w in self.widgets:
            self.deck.updateProgress(_("Processing..."))
            w.showHide()
        self.frame.adjustSize()
        self.deck.finishProgress()


    def onShowHideToggle(self, b, w):
        key = 'graphs.shown.' + w.name
        self.parent.config[key] = not self.parent.config.get(key, True)
        self.showHideAll()

    def onShowHide(self):
        mw.help.showText('JxDebug1')
        m = QMenu(self.parent)
        for graph in self.widgets:
            name = graph.name
            shown = self.parent.config.get('graphs.shown.' + name, True)
            action = QAction(self.parent)
            action.setCheckable(True)
            action.setChecked(shown)
            action.setText(self.nameMap[name])
            action.connect(action, SIGNAL("toggled(bool)"),
                           lambda b, g=graph: self.onShowHideToggle(b, g))
            m.addAction(action)
        m.exec_(self.showhide.mapToGlobal(QPoint(0,0)))

    def onHelp(self):
        QDesktopServices.openUrl(QUrl(ankiqt.appWiki + "Graphs"))

    def onRefresh(self):
        self.deck.startProgress(len(self.widgets))
        self.dg.stats = None
        for w in self.widgets:
            self.deck.updateProgress(_("Processing..."))
            w.updateFigure()
        self.deck.finishProgress()

def JxGraphProxy(self, *args):
	return JxintervalGraph(self,*args) #shouldn't have self
		
def JxintervalGraph(self,*args): #shouldn't have self 
    return JxGraphWindow(self,*args) # shouldn't have self
