# -*- coding: utf-8 -*-
# Copyright: Olivier Binda <olivier.binda@wanadoo.fr>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
# ---------------------------------------------------------------------------
# This file is a plugin for the "anki" flashcard application http://repose.cx/anki/
# ---------------------------------------------------------------------------
import sys,time, datetime
from os import environ,path
from PyQt4.QtGui import *

# support frozen distribs
if getattr(sys, "frozen", None):
    environ['MATPLOTLIBDATA'] = path.join(
        path.dirname(sys.argv[0]),
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

from PyQt4.QtCore import *
from PyQt4 import QtGui, QtCore
from anki.utils import ids2str
from loaddata import *
from ui_graphs import *

######################################################################
#
#                                             Graphs
#
######################################################################


#colours for graphs
colorJLPT4 = "#0fb380"
colorJLPT3 = "#5c2380"
colorJLPT2 = "#fa2320"
colorJLPT1 = "#2f2380"
colorJLPT0 = "#f6b380"

colorGrade={1:"#80b3ff",2:"#90c3df",3:"#444DDD",4:"#222CCC",5:"#000BBB",6:"#222999",7:"#444777",8:"#666555"}

class JxDeckGraphs(object):

    def __init__(self, deck, width=8, height=3, dpi=75):
        self.deck = deck
        self.stats = None
        self.width = width
        self.height = height
        self.dpi = dpi

    def calcStats (self):
        if not self.stats:
            days = {}
            daysYoung = {}
            daysMature =  {}
            months = {}
            next = {}
            lowestInDay = 0
            midnightOffset = time.timezone - self.deck.utcOffset
            now = list(time.localtime(time.time()))
            now[3] = 23; now[4] = 59
            self.endOfDay = time.mktime(now) - midnightOffset
            t = time.time()
           
            self.stats = {}
           

            todaydt = datetime.datetime(*list(time.localtime(time.time())[:3]))
            

            ######################################################################
            #
            #                      JLPT/Grade stats for Kanji
            #
            ######################################################################

            # Selects the models of the Kanji you want to do JLPT/Grade stats upon
            JLPTmids = self.deck.s.column0('''select id from models where tags like "%Kanji%"''')
            # Selects the cards ids of the right type (say guess Kanji).   
	    JLPTReviews = self.deck.s.all("""
select fields.value, reviewHistory.time, reviewHistory.lastInterval, reviewHistory.nextInterval, reviewHistory.ease from cards,cardModels,facts,fields,fieldModels,reviewHistory where
cardModels.id = cards.cardModelId and cards.factId = facts.id and facts.id = fields.factId and fields.fieldModelId = fieldModels.id and reviewHistory.cardId = cards.id and
cardModels.name = "Kanji ?" and fieldModels.name = "Kanji" and facts.modelId in %s order by reviewHistory.time
""" % ids2str(JLPTmids)) 
            # parse the info to build an "day -> Kanji known count" array
	    OLKnownTemp={0:0,1:0,2:0,3:0,4:0}
	    GradeKnownTemp={1:0,2:0,3:0,4:0,5:0,6:0,'HS':0,'Other':0}
	    OLKnown={}
	    GradeKnown={}
            for (OLKanji,OLtime,interval,nextinterval,ease) in JLPTReviews:
                 if OLKanji in Kanji2JLPT:
		     a = Kanji2JLPT[OLKanji]
	         else:
	             a = 0
		 if OLKanji in Kanji2Grade:
		     b = Kanji2Grade[OLKanji]
	         else:
	             b = 'Other'    
	         if ease == 1 and interval > 21:
	             OLKnownTemp[a] = OLKnownTemp[a] - 1  
		     GradeKnownTemp[b] = GradeKnownTemp[b] - 1  
		 elif interval <= 21 and nextinterval>21:
		     OLKnownTemp[a] = OLKnownTemp[a] + 1
		     GradeKnownTemp[b] = GradeKnownTemp[b] + 1
		 OLDay = int((OLtime-t) / 86400.0)+1
		 OLKnown[OLDay] = {0:OLKnownTemp[0],1:OLKnownTemp[1],2:OLKnownTemp[2],3:OLKnownTemp[3],4:OLKnownTemp[4]} 
		 GradeKnown[OLDay] = {1:GradeKnownTemp[1],2:GradeKnownTemp[2],3:GradeKnownTemp[3],4:GradeKnownTemp[4],
		 5:GradeKnownTemp[5],6:GradeKnownTemp[6],'HS':GradeKnownTemp['HS'],'Other':GradeKnownTemp['Other']} 
		 
            OLKnown[0] = {0:OLKnownTemp[0],1:OLKnownTemp[1],2:OLKnownTemp[2],3:OLKnownTemp[3],4:OLKnownTemp[4]}
	    GradeKnown[0] = {1:GradeKnownTemp[1],2:GradeKnownTemp[2],3:GradeKnownTemp[3],4:GradeKnownTemp[4],
		 5:GradeKnownTemp[5],6:GradeKnownTemp[6],'HS':GradeKnownTemp['HS'],'Other':GradeKnownTemp['Other']} 
            self.stats['OL'] = OLKnown 
            self.stats['Grade'] = GradeKnown  



            ######################################################################
            #
            #                      JLPT stats for Words
            #
            ######################################################################

            # Selects the models of the Kanji you want to do JLPT/Grade stats upon
            JLPTmids = self.deck.s.column0('''select id from models where tags like "%Japanese%"''')
            # Selects the cards ids of the right type (say guess Kanji).   
	    JLPTReviews = self.deck.s.all("""
select fields.value, reviewHistory.time, reviewHistory.lastInterval, reviewHistory.nextInterval, reviewHistory.ease from cards,cardModels,facts,fields,fieldModels,reviewHistory where
cardModels.id = cards.cardModelId and cards.factId = facts.id and facts.id = fields.factId and fields.fieldModelId = fieldModels.id and reviewHistory.cardId = cards.id and
cardModels.name = "Recognition" and fieldModels.name = "Expression" and facts.modelId in %s order by reviewHistory.time
""" % ids2str(JLPTmids)) 
            # parse the info to build an "day -> Word known count" array
	    OLKnownTemp={0:0,1:0,2:0,3:0,4:0}
	    OLKnown={}
            for (OLWord,OLtime,interval,nextinterval,ease) in JLPTReviews:
		 WordStripped=OLWord.strip(u" ")
		 if WordStripped.endswith((u"する",u"の",u"な",u"に")):
			if WordStripped.endswith(u"する"):
				WordStripped=WordStripped[0:-2]
			else:
				WordStripped=WordStripped[0:-1]
                 if WordStripped in Word2Data:
		     a = Word2Data[WordStripped]
	         else:
	             a = 0 
	         if ease == 1 and interval > 21:
	             OLKnownTemp[a] = OLKnownTemp[a] - 1  
		 elif interval <= 21 and nextinterval>21:
		     OLKnownTemp[a] = OLKnownTemp[a] + 1
		 OLDay = int((OLtime-t) / 86400.0)+1
		 OLKnown[OLDay] = {0:OLKnownTemp[0],1:OLKnownTemp[1],2:OLKnownTemp[2],3:OLKnownTemp[3],4:OLKnownTemp[4]} 
		 
            OLKnown[0] = {0:OLKnownTemp[0],1:OLKnownTemp[1],2:OLKnownTemp[2],3:OLKnownTemp[3],4:OLKnownTemp[4]}
            self.stats['Time2JLPT4Words'] = OLKnown 

    ######################################################################
    #
    #                               Graphs
    #
    ######################################################################

    def graphTime2JLPT4Kanji(self, days=30):
        self.calcStats()
        fig = Figure(figsize=(self.width, self.height), dpi=self.dpi)
        graph = fig.add_subplot(111)

        JOL = {}
	for c in range(0,10):
	        JOL[c] = []
        OLK = self.stats['OL']
	# have to sort the dictionnary
	keys = OLK.keys()
        keys.sort()
	for a in keys:
		for c in range(0,5):	
                   JOL[2 * c].append(a)
	           JOL[2 * c + 1].append(sum([OLK[a][k] for k in range(c,5)]))
        Arg =[JOL[k] for k in range(0,10)]
        self.filledGraph(graph, days, [colorJLPT0,colorJLPT1,colorJLPT2,colorJLPT3,colorJLPT4], *Arg)
	
	cheat = fig.add_subplot(111)
        b0 = cheat.bar(-1, 0, color = colorJLPT4)
        b1 = cheat.bar(-2, 0, color = colorJLPT3)
        b2 = cheat.bar(-3, 0, color = colorJLPT2)
        b3 = cheat.bar(-4, 0, color = colorJLPT1)
        b4 = cheat.bar(-5, 0, color = colorJLPT0)
	
        cheat.legend([b0, b1, b2, b3, b4], [
            _("JLPT4"),
            _("JLPT3"),
            _("JLPT2"),
	    _("JLPT1"), 
	    _("Other")], loc='upper left')
	
        graph.set_xlim(xmin = -days, xmax = 0)
        graph.set_ylim(ymax= max (a for a in JOL[1]) + 30)
        return fig

    def graphTime2Jouyou4Kanji(self, days=30):
        self.calcStats()
        fig = Figure(figsize=(self.width, self.height), dpi=self.dpi)
        graph = fig.add_subplot(111)

        JOL = {}
	for c in range(0,16): 
	        JOL[c] = []
	Translate={1:1,2:2,3:3,4:4,5:5,6:6,7:'HS',8:'Other'}
        
        OLK = self.stats['Grade']
	# have to sort the dictionnary
	keys = OLK.keys()
        keys.sort()
	
	for a in keys:
		for c in range(0,8):	
                   JOL[2 * c].append(a)
	           JOL[15-2 * c].append(sum([OLK[a][Translate[k]] for k in range(1,c+2)]))
        Arg =[JOL[k] for k in range(0,16)]
        self.filledGraph(graph, days, [colorGrade[8-k] for k in range(0,8)], *Arg)
	
	cheat = fig.add_subplot(111)
        b0 = cheat.bar(-1, 0, color = colorGrade[1])
        b1 = cheat.bar(-2, 0, color = colorGrade[2])
        b2 = cheat.bar(-3, 0, color = colorGrade[3])
        b3 = cheat.bar(-4, 0, color = colorGrade[4])
        b4 = cheat.bar(-5, 0, color = colorGrade[5])
	b5 = cheat.bar(-6, 0, color = colorGrade[6])
        b6 = cheat.bar(-7, 0, color = colorGrade[7])
        b7 = cheat.bar(-8, 0, color = colorGrade[8])
        cheat.legend([b0, b1, b2, b3, b4, b5, b6, b7], [
            _("Grade 1"),
            _("Grade 2"),
            _("Grade 3"),
	    _("Grade 4"), 
	    _("Grade 5"),
            _("Grade 6"),
	    _("J. High School"), 
	    _("Other")], loc='upper left')
	
        graph.set_xlim(xmin = -days, xmax = 0)
        graph.set_ylim(ymax= max (a for a in JOL[1]) + 30)
        return fig
	
    def graphTime2JLPT4Tango(self, days=30):
        self.calcStats()
        fig = Figure(figsize=(self.width, self.height), dpi=self.dpi)
        graph = fig.add_subplot(111)

        JOL = {}
	for c in range(0,10):
	        JOL[c] = []
        OLK = self.stats['Time2JLPT4Words'] 
	# have to sort the dictionnary
	keys = OLK.keys()
        keys.sort()
	for a in keys:
		for c in range(0,5):	
                   JOL[2 * c].append(a)
	           JOL[2 * c + 1].append(sum([OLK[a][k] for k in range(c,5)]))
        Arg =[JOL[k] for k in range(0,10)]
        self.filledGraph(graph, days, [colorJLPT0,colorJLPT1,colorJLPT2,colorJLPT3,colorJLPT4], *Arg)
	
	cheat = fig.add_subplot(111)
        b0 = cheat.bar(-1, 0, color = colorJLPT4)
        b1 = cheat.bar(-2, 0, color = colorJLPT3)
        b2 = cheat.bar(-3, 0, color = colorJLPT2)
        b3 = cheat.bar(-4, 0, color = colorJLPT1)
        b4 = cheat.bar(-5, 0, color = colorJLPT0)
	
        cheat.legend([b0, b1, b2, b3, b4], [
            _("JLPT 4"),
            _("JLPT 3"),
            _("JLPT 2"),
	    _("JLPT 1"), 
	    _("Other")], loc='upper left')
	
        graph.set_xlim(xmin = -days, xmax = 0)
        graph.set_ylim(ymax= max (a for a in JOL[1]) + 30)
        return fig

    def filledGraph(self, graph, days, colours=["b"], *args):
        if isinstance(colours, str):
            colours = [colours]
        thick = True
        for triplet in [(args[n], args[n + 1], colours[n / 2]) for n in range(0, len(args), 2)]:
            x = list(triplet[0])
            y = list(triplet[1])
            c = triplet[2]
            lowest = 99999
            highest = -lowest
            for i in range(len(x)):
                if x[i] < lowest:
                    lowest = x[i]
                if x[i] > highest:
                    highest = x[i]
            # ensure the filled area reaches the bottom
            x.insert(0,lowest - 1)
            y.insert(0,0)
            x.append(highest + 1)
            y.append(0)
            # plot
            lw = 0
            if days < 180:
                lw += 1
            if thick:
                lw += 1
            if days > 360:
                lw = 0
            graph.fill(x, y, c, lw = lw)
            thick = False

        graph.grid(True)
        graph.set_ylim(ymin=0, ymax=max(2, graph.get_ylim()[1]))



		
class JxGraphWindow(object):

    nameMap = {
        'JLPT4Kanji': _("Kanji"),
        'Jouyou': _("Graded"),
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
      
      		# Time -> JLPT for Words graph
		WJLPT = AdjustableFigure(self.parent, 'JLPT4Tango', Jxdg.graphTime2JLPT4Tango, self.range) 
		WJLPT.addWidget(QLabel(_("<h1>JLPT Word Progress ('Recognition' card model)</h1>")))
		self.vbox.addWidget(WJLPT)
		self.widgets.append(WJLPT)

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


		
def JxintervalGraph(self,*args): #shouldn't have self 
    return JxGraphWindow(self,*args) # shouldn't have self

def JxGraphProxy(self, *args):
	return JxintervalGraph(self,*args) #shouldn't have self

#from ui.utils import showText


	
	
	
	
	
	
	
