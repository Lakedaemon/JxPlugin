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
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from anki.graphs import DeckGraphs
from PyQt4 import QtGui, QtCore
from ankiqt import mw, ui

from anki.utils import parseTags, tidyHTML, genID, ids2str, hexifyID, canonifyTags, joinTags, addTags
import datetime


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












from ankiqt.ui.utils import askUser, getOnlyText
from ankiqt import *
#import ankiqt.forms

from ui.utils import showText

from ankiqt.ui.utils import saveGeom, restoreGeom
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

from ui.utils import showText

def onJxGraphs():
	ui.dialogs.get("JxGraphs", mw, mw.deck)
	
	
	
	
	
	
	
	
	
	
	
	
	





from anki.utils import canonifyTags, addTags



def onJxDuplicates():

	Query = """select fields.value, facts.id, facts.created, facts.tags from fields,facts,fieldModels,models where 
		facts.id = fields.factId and fields.fieldModelId = fieldModels.id and facts.modelId = models.id and  
		fieldModels.name = "Expression" and models.tags like "%Japanese%" order by fields.value"""

	Html = "<table>".decode("utf-8")
	Rows = mw.deck.s.all(Query)
	MasterDuplicates=[]
	MasterTags="".decode("utf_8")
	Duplicates=[]
	Duplication = False
	(lastField,lastId,lastTime,lastTags) = [u"None",None,None,"".decode("utf-8")]
	for (Field,Id,Time,Tags) in Rows:
		if lastField == Field and lastTime > Time:
			Duplication = True
			# first duplicate younger
			Duplicates.append(lastId)
			MasterTags =  canonifyTags(addTags(MasterTags,Tags)) 
			(lastField,lastId,lastTime) = (Field,Id,Time)
			Html += "<tr><td>%s</td><td>%s</td></tr>" % (Field,lastTags+ u" JxDuplicate")
		elif lastField == Field:
			Duplication = True
			# second duplicate younger
			Duplicates.append(Id)
			MasterTags =  canonifyTags(addTags(MasterTags,Tags)) 
			Html += "<tr><td>%s</td><td>%s</td></tr>" % (Field,Tags+ u" JxDuplicate")
		else: 
			if Duplication:
				MasterDuplicates.append((lastId,canonifyTags(MasterTags)))
			Duplication = False
			MasterTags = Tags
			(lastField,lastId,lastTime,lastTags) = (Field,Id,Time,Tags)
	if Duplication:
		MasterDuplicates.append((lastId,canonifyTags(MasterTags)))
	Html += "</table><center> duplicates count :" + str(len(Duplicates)) +"</center>"
	mw.help.showText(str(MasterDuplicates)+Html)
	mw.deck.addTags(Duplicates,"JxDuplicate".decode("utf-8"))
	temp=[]
	for (Id,Tags) in MasterDuplicates:
		 mw.deck.s.statement("update facts set tags = :tags, modified = :t where id =:id",id=Id, t=time.time(),tags=Tags)
		 temp.append(Id)
	#mw.deck.updateFactTags(temp)
	mw.deck.addTags(temp,"JxMasterDuplicate".decode("utf-8"))
	mw.deck.deleteTags(temp,"JxDuplicate".decode("utf-8"))
			
######################################################################
#
#                      JxStats : Stats
#
######################################################################

def ComputeCount(Dict,Query):  #### try to clean up, now that you are better at python
	"""compute and Display an HTML report of the result of a Query against a Map"""
	# First compute the cardinal of every equivalence class in Stuff2Val
	Count = {"InQuery":0, "Inside":0, "L0":0}
	Values = set(Dict.values())
	for value in Values:
		Count["T" + str(value)] = 0
		Count["L" + str(value)] = 0		
	for key, value in Dict.iteritems():
		Count["T" + str(value)] += 1
	Count["InMap"] = sum(Count["T" + str(value)] for value in Values)
	Counted = {}
	for Stuff in mw.deck.s.column0(Query):
		Stuffed=Stuff.strip(u" ")
		if Stuffed.endswith((u"する",u"の",u"な",u"に")):
			if Stuffed.endswith(u"する"):
				Stuffed=Stuffed[0:-2]
			else:
				Stuffed=Stuffed[0:-1]
		if Stuffed not in Counted:
			Counted[Stuffed] = 0
			if Stuffed in Dict:
				a = "L" + str(Dict[Stuffed])
			else:
				a = "L0"
			Count[a] += 1
	Count["Inside"] = sum(Count["L" + str(value)] for value in Values)
	Count["InQuery"] = Count["Inside"] + Count["L0"]
	for value in Values:
		Count["P" + str(value)] = round(Count["L" + str(value)] * 100.0 / max(Count["T" + str(value)],1),2)
	Count["PInsideInMap"] = round(Count["Inside"] *100.0 / max(Count["InMap"],1),2)
	Count["PInsideInQuery"] = round(Count["Inside"] *100.0 / max(Count["InQuery"],1),2)
	return Count

def HtmlReport(Map,Query):
	Map.update(ComputeCount(Map["Dict"],Query))
	JStatsHTML = """
	<table width="100%%" align="center" style="margin:0 20 0 20;">
	<tr><td align="left"><b>%(To)s</b></td><th colspan=2 align="center"><b>%(From)s</b></th><td align="right"><b>Percent</b></td></tr>
	""" 
	for key,value in Map["Legend"].iteritems():
		JStatsHTML += """
		<tr><td align="left"><b>%s</b></td><td align="right">%%(L%s)s</td><td align="left"> / %%(T%s)s</td><td align="right">%%(P%s).1f %%%%</td></tr>
		""" % (value,key,key,key) 

	JStatsHTML += """
	<tr><td align="left"><b>Total</b></td><td align="right">%(Inside)s</td><td align="left"> / %(InMap)s</td><td align="right">%(PInsideInMap).1f %%</td></tr>
	<tr><td colspan=4><hr/></td/></tr>
	<tr><td align="left"><b> %(To)s/All</b></td><td align="right">%(Inside)s</td><td align="left"> / %(InQuery)s</td><td align="right">%(PInsideInQuery).1f %%</td></tr>
	</table>
	""" 
        return JStatsHTML % Map



def onJStats():
	"""Computes and displays all kind of Stats related to japanese"""
	
	JStatsHTML ="""<center><h1>KANJI</h1></center><h3></h3>"""
	
	JStatsHTML += HtmlReport(MapJLPTKanji,QueryKanji)
	
	JStatsHTML += """<br /><hr style="margin:0 20 0 20;"/>
	<center>JLPT : <a href=py:missJLPTKanji>Missing</a>&nbsp;&nbsp;<a href=py:seenJLPTKanji>Seen</a>&nbsp;&nbsp;&nbsp;
	Jouyou : <a href=py:missJouyouKanji>Missing</a>&nbsp;<a href=py:seenJouyouKanji>Seen</a></center>
	<hr style="margin:0 20 0 20;"/><br />"""
	
	JStatsHTML += HtmlReport(MapJouyouKanji,QueryKanji)
        	
	JStatsHTML += """<br /><hr style="margin:0 20 0 20;"/>
	<center>Jouyou : <a href=py:missJouyouKanji>Missing</a>&nbsp;&nbsp;<a href=py:seenJouyouKanji>Seen</a>&nbsp;&nbsp;&nbsp;
	Frequency : <a href=py:missZoneKanji>Missing</a>&nbsp;<a href=py:seenZoneKanji>Seen</a></center>
	<hr style="margin:0 20 0 20;"/><br />"""
	
	JStatsHTML += HtmlReport(MapZoneKanji,QueryKanji) 
	
	JStatsHTML +="""
	<center><h1>TANGO</h1></center>
	<h3></h3>
	"""
		
	JStatsHTML += HtmlReport(MapJLPTTango,QueryTango)
	
	JStatsHTML += """<br /><hr style="margin:0 20 0 20;"/>
	<center>JLPT : <a href=py:missJLPTTango>Missing</a>&nbsp;&nbsp;<a href=py:seenJLPTTango>Seen</a>&nbsp;&nbsp;&nbsp;
	Frequency : <a href=py:missZoneTango>Missing</a>&nbsp;<a href=py:seenZoneTango>Seen</a></center>
	<hr style="margin:0 20 0 20;"/><br />"""
	
	JStatsHTML += HtmlReport(MapZoneTango,QueryTango)

	mw.help.showText(JStatsHTML, py={
		"seenJLPTKanji": onSeenJLPTKanjiStats,
		"missJLPTKanji": onMissingJLPTKanjiStats,
		"seenJouyouKanji": onSeenJouyouKanjiStats,
		"missJouyouKanji": onMissingJouyouKanjiStats,
		"seenZoneKanji": onSeenZoneKanjiStats,
		"missZoneKanji": onMissingZoneKanjiStats,
		"seenJLPTTango": onSeenJLPTTangoStats,
		"missJLPTTango": onMissingJLPTTangoStats,
		"seenZoneTango": onSeenZoneTangoStats,
		"missZoneTango": onMissingZoneTangoStats,
		"try": onJxAdd
		})


from PyQt4.QtWebKit import QWebPage, QWebView
from PyQt4 import QtWebKit

from string import Template


def onJxAdd():
	JxHtml = Template(JxMenu).substitute(TangoZone=HtmlReport(MapZoneTango,QueryTango),KanjiZone=HtmlReport(MapJLPTKanji,QueryKanji),
		TangoJLPT=HtmlReport(MapJLPTTango,QueryTango),KanjiJLPT=HtmlReport(MapJLPTKanji,QueryKanji),
		KanjiJouyou=HtmlReport(MapJouyouKanji,QueryKanji))
	JxWindow.setHtml(JxHtml)
	JxWindow.show()
                            

def SeenHtml(Map,Query):
	Dict=Map["Dict"]
	Seen = {}
	Color = {0:True}
	Buffer = {0:""}
	for value in Dict.values():
		Buffer[value] = ""
		Color[value] = True	
	for Stuff in mw.deck.s.column0(Query):
		if Stuff not in Seen:
			try: 
				value = Dict[Stuff]	  
			except KeyError:
				value = 0
			Seen[Stuff] = a
			Color[value] = not(Color[value])			
			if Color[value]:
				Buffer[value] += Stuff
			else:
				Buffer[value] += """<span style="color:blue">"""+ Stuff +"""</span>"""
	HtmlBuffer = ""
	for key, string in Buffer.iteritems():
		if key == 0:
			HtmlBuffer += """<h2  align="center">Other</h2><p><font size=+2>%s</font></p>""" % string
		else:
			HtmlBuffer += """<h2  align="center">%s</h2><p><font size=+2>%s</font></p>""" % (Map["Legend"][key],string)
	return HtmlBuffer

def onSeenJLPTKanjiStats():
	JStatsHTML = SeenHtml(MapJLPTKanji,QueryKanji)
	mw.help.showText("""<h1  align="center">SEEN KANJI</h1><center><a href=py:miss>Missing</a>&nbsp;<a href=py:stats>Stats</a></center><hr />""" + JStatsHTML, py={
        "miss": onMissingJLPTKanjiStats,
        "stats": onJStats
        })
	
def onSeenJouyouKanjiStats():
	JStatsHTML = SeenHtml(MapJouyouKanji,QueryKanji)
	mw.help.showText("""<h1  align="center">SEEN KANJI</h1><center><a href=py:miss>Missing</a>&nbsp;<a href=py:stats>Stats</a></center><hr />""" + JStatsHTML, py={
        "miss": onMissingJouyouKanjiStats,
        "stats": onJStats
        })

def onSeenZoneKanjiStats():
	JStatsHTML = SeenHtml(MapZoneKanji,QueryKanji)
	mw.help.showText("""<h1  align="center">SEEN KANJI</h1><center><a href=py:miss>Missing</a>&nbsp;<a href=py:stats>Stats</a></center><hr />""" + JStatsHTML, py={
        "miss": onMissingZoneKanjiStats,
        "stats": onJStats
        })

def onSeenJLPTTangoStats():
	JStatsHTML = SeenHtml(MapJLPTTango,QueryTango)
	mw.help.showText("""<h1  align="center">SEEN WORDS</h1><center><a href=py:miss>Missing</a>&nbsp;<a href=py:stats>Stats</a></center><hr />""" + JStatsHTML, py={
        "miss": onMissingJLPTTangoStats,
        "stats": onJStats
        })

def onSeenZoneTangoStats():
	JStatsHTML = SeenHtml(MapZoneTango,QueryTango)
	mw.help.showText("""<h1  align="center">SEEN WORDS</h1><center><a href=py:miss>Missing</a>&nbsp;<a href=py:stats>Stats</a></center><hr />""" + JStatsHTML, py={
        "miss": onMissingZoneTangoStats,
        "stats": onJStats
        })

def MissingHtml(Map,Query):
	Dict=Map["Dict"]
	Seen = {}
	for Stuff in mw.deck.s.column0(Query):
		Seen[Stuff] = 0
		
	Color = {0:True}
	Buffer = {0:""}
	for value in Dict.values():
		Buffer[value] = ""
		Color[value] = True	
	for Stuff,Note in Dict.iteritems():
		if Stuff not in Seen:
			Color[Note] = not(Color[Note])			
			if Color[Note]:
				Buffer[Note] += Stuff
			else:
				Buffer[Note] += """<span style="color:blue">"""+ Stuff +"""</span>"""
	HtmlBuffer = ""
	for key, string in Buffer.iteritems():
		if key != 0:
			HtmlBuffer += """<h2  align="center">%s</h2><p><font size=+2>%s</font></p>""" % (Map["Legend"][key],string)
	return HtmlBuffer	


def onMissingJLPTKanjiStats():
	JStatsHTML = MissingHtml(MapJLPTKanji,QueryKanji)
	mw.help.showText("""<h1  align="center">MISSING KANJI</h1><center><a href=py:seen>Seen</a>&nbsp;<a href=py:stats>Stats</a></center><hr />""" + JStatsHTML, py={
        "seen": onSeenJLPTKanjiStats,
        "stats": onJStats
        })

def onMissingJouyouKanjiStats():
	JStatsHTML = MissingHtml(MapJouyouKanji,QueryKanji)
	mw.help.showText("""<h1  align="center">MISSING KANJI</h1><center><a href=py:seen>Seen</a>&nbsp;<a href=py:stats>Stats</a></center><hr />""" + JStatsHTML, py={
        "seen": onSeenJouyouKanjiStats,
        "stats": onJStats
        })
	
def onMissingZoneKanjiStats():
	JStatsHTML = MissingHtml(MapZoneKanji,QueryKanji)
	mw.help.showText("""<h1  align="center">MISSING KANJI</h1><center><a href=py:seen>Seen</a>&nbsp;<a href=py:stats>Stats</a></center><hr />""" + JStatsHTML, py={
        "seen": onSeenZoneKanjiStats,
        "stats": onJStats
        })
def onMissingJLPTTangoStats():
	JStatsHTML = MissingHtml(MapJLPTTango,QueryTango)
	mw.help.showText("""<h1  align="center">MISSING WORDS</h1><center><a href=py:seen>Seen</a>&nbsp;<a href=py:stats>Stats</a></center><hr />""" + JStatsHTML, py={
        "seen": onSeenJLPTTangoStats,
        "stats": onJStats
        })

def onMissingZoneTangoStats():
	JStatsHTML = MissingHtml(MapZoneTango,QueryTango)
	mw.help.showText("""<h1  align="center">MISSING WORDS</h1><center><a href=py:seen>Seen</a>&nbsp;<a href=py:stats>Stats</a></center><hr />""" + JStatsHTML, py={
        "seen": onSeenZoneTangoStats,
        "stats": onJStats
        })

###############################################################################################################
#
#    displays aditionnal info  in the answer (Words : JLPT, Kanji : JLPT/Grade/stroke order/related words.
#
###############################################################################################################
import math
import re
Map = {1:"JLPT 1",2:"JLPT 2",3:"JLPT 3",4:"JLPT 4",5:"Other"}

def Tango2Dic(string):
	String = string.strip(u" ")
	if String.endswith(u"する") and len(String)>2:
		return String[0:-2]
	elif (String.endswith(u"な") or String.endswith(u"の") or String.endswith(u"に")) and len(String)>1: #python24 fix for OS X                  
#	elif String.endswith((u"な",u"の",u"に")) and len(String)>1:    #python25
		return String[0:-1]
	else:
		return String

def JxDefaultAnswer(Buffer,String,Dict):
	if re.search(u"\${.*?}",Buffer):
		return String
	else: 
		return Buffer + String

def append_JxPlugin(Answer,Card):
    """Append additional information about kanji and words in answer."""
    
    Append = re.search(u"\${.*?}",Answer) == None

    for key in [u"Expression",u"単語",u"言葉"]:
	    try:
		Tango = Tango2Dic(Card.fact[key])
		break
	    except KeyError:
                Tango = None		    
		
    for key in [u"Kanji",u"漢字"]:
	    try:
		Kanji = Card.fact[key].strip()
		break
	    except KeyError:
		Kanji = None	


    JxAnswerDict = {}
    for key in [u"T2JLPT",u"T2Freq",u"Stroke",u"K2JLPT",u"K2Jouyou",u"K2Freq",u"K2Words"]:
	    JxAnswerDict[key] = u""

    JxAnswerDict[u"Stroke"] =  """<span class="LDKanjiStroke">%s</span>""" % Kanji
    JxAnswerDict[u"Css"] = """
    <style> 
    .Kanji { font-family: Meiryo,'Hiragino Kaku Gothic Pro','MS Mincho',Arial,sans-serif; font-weight: normal; text-decoration: none; font-size:2.5em;}
    .Kana { font-family: Meiryo,'Hiragino Kaku Gothic Pro','MS Mincho',Arial,sans-serif; font-weight: normal; text-decoration: none; font-size:1.8em; }
    .Romaji { font-family: Arial,sans-serif; font-weight: normal; text-decoration: none; font-size:1.5em;}
    .JLPT,.Jouyou,.Frequency { font-family: Arial,sans-serif; font-weight: normal; font-size:1.2em;}
    .LDKanjiStroke  { font-family: KanjiStrokeOrders; font-size: 10em;}
    td { padding: 2px 15px 2px 15px;}
    </style>"""


    if Append:
	    AnswerBuffer = u"""${Css}"""		
    
    # Word2JLPT
    try:
        JxAnswerDict[u"T2JLPT"] =  u"""<span class="JLPT">%s</span>""" % Map[Word2Data[Tango]]
	if Append:
		AnswerBuffer += u""" <div class="JLPT">${T2JLPT}</div>"""
    except KeyError:
	    pass

    # Word2Frequency
    try:
		JxAnswerDict[u"T2Freq"] = u"""<span class="Frequency">LFreq %s</span>"""  % int((math.log(Word2Frequency[Tango]+1,2)-math.log(MinWordFrequency+1,2))/(math.log(MaxWordFrequency+1,2)-math.log(MinWordFrequency+1,2))*100) 
		if Append:
			AnswerBuffer += """ <div class="Frequency">${T2Freq}</div>"""
    except KeyError:
		pass

    if Kanji != None:
		
		# Stroke Order
		if Append:
			AnswerBuffer += u"""<div style="float:left;">${Stroke}</div>"""
			
		# Kanji2JLPT
		try:
			JxAnswerDict[u"K2JLPT"] =  """<span class="JLPT">%s</span>""" % Map[Kanji2JLPT[Kanji]]
			if Append:
				AnswerBuffer += u""" <div class="JLPT">${K2JLPT}</div>"""
		except KeyError:
			pass
	
		# Kanji2Jouyou	
		try:
			JxAnswerDict[u"K2Jouyou"] =  """<span class="Jouyou">%s</span>""" % MapJouyouKanji["Legend"][Kanji2JLPT[Kanji]]
			if Append:
				AnswerBuffer += u""" <div class="Jouyou">${K2Jouyou}</div>"""
		except KeyError:
			pass

		# Word2Frequency
		try:    
			JxAnswerDict[u"K2Freq"] = u"""<span class="Frequency">LFreq %s</span>"""  % int((math.log(Kanji2Frequency[Kanji]+1,2)-math.log(MaxFrequency+1,2))*10+100)
			if Append:
				AnswerBuffer += """ <div class="Frequency">${K2Freq}</div>"""
		except KeyError:
			pass		
				
		# Finds all word facts whose expression uses the Kanji and returns a table with expression, reading, meaning
		query = """select expression.value, reading.value, meaning.value from 
		fields as expression, fields as reading, fields as meaning, 
		fieldModels as fmexpression, fieldModels as fmreading, fieldModels as fmmeaning where 
		expression.fieldModelId= fmexpression.id and fmexpression.name="Expression" and 
		reading.fieldModelId= fmreading.id and fmreading.name="Reading" and reading.factId=expression.factId and 
		meaning.fieldModelId= fmmeaning.id and fmmeaning.name="Meaning" and meaning.factId=expression.factId and 
		expression.value like "%%%s%%" """ % Kanji

		# HTML Buffer 
		info = "" 
		# Adds the words to the HTML Buffer 
		for (u,v,w) in mw.deck.s.all(query):
			info += """ <tr><td><span class="%s">%s </span></td><td><span class="%s">%s</span></td><td><span class="%s"> %s</td></tr>
			""" % ("Kanji",u.strip(),"Romaji" ,w.strip(),"Kana",v.strip())

		# if there Html Buffer isn't empty, adds it to the card info
		if len(info):
			JxAnswerDict[u"K2Words"] = """<table style="text-align:center;" align="center">%s</table>""" % info
			if Append:
				AnswerBuffer += """${K2Words}"""
		else:
			pass			

    if Append:
	    return Template(Answer+AnswerBuffer).safe_substitute(JxAnswerDict)
    else:
	    return Template(Answer).safe_substitute(JxAnswerDict)







######################################################################
#
#                      JLPT for Kanji
#
######################################################################

KanjiList_JLPT = {
4: '一七万三上下中九二五人今休会何先入八六円出分前北十千午半南友口古右名四国土外多大天女子学安小少山川左年店後手新日時書月木本来東校母毎気水火父生男白百目社空立耳聞花行西見言話語読買足車週道金長間雨電食飲駅高魚'.decode("utf-8"), 
3:
'不世主乗事京仕代以低住体作使便借働元兄光写冬切別力勉動区医去台合同味品員問回図地堂場声売夏夕夜太好妹姉始字室家寒屋工市帰広度建引弟弱強待心思急悪意所持教文料方旅族早明映春昼暑暗曜有服朝村林森業楽歌止正歩死民池注洋洗海漢牛物特犬理産用田町画界病発県真着知短研私秋究答紙終習考者肉自色英茶菜薬親計試説貸質赤走起転軽近送通進運遠都重野銀門開院集青音頭題顔風飯館首験鳥黒'.decode("utf-8"),
2: '腕湾和論録老労路連練恋列歴齢零礼冷例令類涙輪緑領量良療涼両了粒留流略率律陸裏利卵乱落絡頼翌浴欲陽踊要葉溶様容幼預与余予郵遊由勇優輸油約役戻毛面綿鳴迷命娘無夢務眠未満末枚埋磨防貿棒望暴忙忘帽坊亡豊訪法放抱宝報包暮募補捕保返辺編片変壁米閉並平兵粉仏沸払複腹福幅復副封部舞武負膚符浮普怖府布富婦夫付貧秒評表氷標筆必匹鼻美備飛非費被皮疲比批悲彼否番晩販般犯版板反判抜髪畑肌箱麦爆薄泊倍配背杯敗拝馬破波農脳能濃悩燃念熱猫認任乳難軟内鈍曇届突独毒得銅童導逃到筒等当灯湯盗投島塔凍党倒怒努途登渡徒塗殿伝点展鉄適的滴泥程庭底定停痛追賃珍沈直頂超調張庁兆貯著駐虫柱宙仲竹畜築遅置恥値談段暖断団炭探担単谷達濯宅第退袋替帯対打他損尊孫存卒続速測束息則側造贈蔵臓憎増像装草総窓相争燥操掃捜想層双組祖全然善選船線浅泉戦専占絶雪節設折接責績積石昔席税静製精清晴星整政成性姓勢制数吹震針辛身臣神申深寝信伸触職植蒸畳状条情常城賞象紹笑章省照焼消昇招承床将商召勝除助諸署緒初処順純準述術祝宿柔舟拾修州周収授受酒種守取若捨実湿失識式辞示治次寺児似歯資誌詞脂糸枝支指志師史司刺伺残賛算散参皿雑殺札察刷冊昨咲坂財罪材在際細祭済歳採才妻最再座砂査差混根婚困込骨腰告刻号香降鉱郊講荒航肯耕紅硬港構更康幸向厚効公候交誤御互雇湖枯故戸庫固呼個限現減原険軒賢肩権検券健件血結決欠劇迎芸警経景敬恵形型傾係軍群訓君靴掘隅偶具苦禁均勤玉極曲局胸狭況橋挟恐境叫協共競供漁許巨居旧給級球泣求救吸久逆客詰喫議疑技記規季祈機期机希寄基器喜危願岩岸含丸関観簡管看甘環汗換慣感干官完巻刊乾活割額革較角覚確格拡各害貝階絵皆灰械改快解介過貨課菓荷河果科可加価仮化温億黄王欧横押応奥央汚塩煙演延園越液鋭泳永栄営雲羽宇因印育域違衣胃移異易委囲偉依位案圧愛'.decode("utf-8"),
1:
'乙丁刀又勺士及己丈乏寸凡刃弓斤匁氏井仁丹幻凶刈冗弔斗尺屯孔升厄丙且弁功甲仙句巡矢穴丘玄巧矛汁尼迅奴囚凸凹斥弐吏企邦江吉刑充至芝扱旬旨尽缶仰后伏劣朴壮吐如匠妃朱伐舌羊朽帆妄芋沢佐攻系抗迫我抑択秀尾伴邸沖却災孝戒杉里妥肝妙序即寿励芳克没妊豆狂岐廷妨亜把呈尿忍呉伯扶忌肖迭吟汽坑抄壱但松郎房拠拒枠併析宗典祉免忠沿舎抵茂斉炎阻岳拘卓炉牧奇拍往屈径抽披沼肥拐拓尚征邪殴奉怪佳昆芽苗垂宜盲弦炊枢坪泡肪奔享拙侍叔岬侮抹茎劾泌肢附派施姿宣昭皇紀削為染契郡挑促俊侵括透津是奏威柄柳孤牲帝耐恒冒胞浄肺貞胆悔盾軌荘冠卸垣架砕俗洞亭赴盆疫訂怠哀臭洪狩糾峡厘胎窃恨峠叙逓甚姻幽卑帥逝拷某勅衷逐侯弧朕耗挙宮株核討従振浜素益逮陣秘致射貢浦称納紛託敏郷既華哲症倉索俳剤陥兼脅竜梅桜砲祥秩唆泰剣倫殊朗烈悟恩陛衰准浸虐徐脈俵栽浪紋逸隻鬼姫剛疾班宰娠桑飢郭宴珠唐恭悦粋辱桃扇娯俸峰紡胴挿剖唇匿畔翁殉租桟蚊栓宵酌蚕畝倣倹視票渉推崎盛崩脱患執密措描掲控渋掛排訳訟釈隆唱麻斎貫偽脚彩堀菊唯猛陳偏遇陰啓粘遂培淡剰虚帳惨据勘添斜涯眼瓶彫釣粛庶菌巣廊寂酔惜悼累陶粗蛇眺陵舶窒紳旋紺遍猟偵喝豚赦殻陪悠淑笛渇崇曹尉蛍庸渓堕婆脹痘統策提裁証援訴衆隊就塁遣雄廃創筋葬惑博弾塚項喪街属揮貴焦握診裂裕堅賀揺喚距圏軸絞棋揚雰殖随尋棟搭詐紫欺粧滋煮疎琴棚晶堤傍傘循幾掌渦猶慌款敢扉硫媒暁堪酢愉塀閑詠痢婿硝棺詔惰蛮塑虞幹義督催盟献債源継載幕傷鈴棄跡慎携誉勧滞微誠聖詳雅飾詩嫌滅滑頑蓄誇賄墓寛隔暇飼艇奨滝雷酬愚遭稚践嫁嘆碁漠該痴搬虜鉛跳僧溝睡猿摂飽鼓裸塊腸慈遮慨鉢禅絹傑禍酪賊搾廉煩愁楼褐頒嗣銑箇遵態閣摘維遺模僚障徴需端奪誘銭銃駆稲綱閥隠徳豪旗網酸罰腐僕塾漏彰概慢銘漫墜漂駄獄誓酷墨磁寧穀魂暦碑膜漬酵遷雌漆寡慕漸嫡謁賦監審影撃請緊踏儀避締撤盤養還慮緩徹衝撮誕歓縄範暫趣慰潟敵魅敷潮賠摩輝稼噴撲縁慶潜黙輩稿舗熟霊諾勲潔履憂潤穂賓寮澄弊餓窮幣槽墳閲憤戯嘱鋳窯褒罷賜錘墾衛融憲激壊興獲樹薦隣繁擁鋼縦膨憶諮謀壌緯諭糖懐壇奮穏謡憾凝獣縫憩錯縛衡薫濁錠篤隷嬢儒薪錬爵鮮厳聴償縮購謝懇犠翼繊擦覧謙頻轄鍛礁擬謹醜矯嚇霜謄濫離織臨闘騒礎鎖瞬懲糧覆翻顕鎮穫癒騎藩癖襟繕繭璽繰瀬覇簿鯨鏡髄霧麗羅鶏譜藻韻護響懸籍譲騰欄鐘醸躍露顧艦魔襲驚鑑'.decode("utf-8")
}


Kanji2JLPT = {}
for a in range(1,5):
    for b in KanjiList_JLPT[a]:
        Kanji2JLPT[b]=a


######################################################################
#
#                      Grade for Kanji
#
######################################################################
		    
KanjiList_Jouyou={
1:
'一九七二人入八力十下三千上口土夕大女子小山川五天中六円手文日月木水火犬王正出本右四左玉生田白目石立百年休先名字早気竹糸耳虫村男町花見貝赤足車学林空金雨青草音校森'.decode("utf-8"),
2:
'刀万丸才工弓内午少元今公分切友太引心戸方止毛父牛半市北古台兄冬外広母用矢交会合同回寺地多光当毎池米羽考肉自色行西来何作体弟図声売形汽社角言谷走近里麦画東京夜直国姉妹岩店明歩知長門昼前南点室後春星海活思科秋茶計風食首夏弱原家帰時紙書記通馬高強教理細組船週野雪魚鳥黄黒場晴答絵買朝道番間雲園数新楽話遠電鳴歌算語読聞線親頭曜顔'.decode("utf-8"),
3:
'丁予化区反央平申世由氷主仕他代写号去打皮皿礼両曲向州全次安守式死列羊有血住助医君坂局役投対決究豆身返表事育使命味幸始実定岸所放昔板泳注波油受物具委和者取服苦重乗係品客県屋炭度待急指持拾昭相柱洋畑界発研神秒級美負送追面島勉倍真員宮庫庭旅根酒消流病息荷起速配院悪商動宿帳族深球祭第笛終習転進都部問章寒暑植温湖港湯登短童等筆着期勝葉落軽運遊開階陽集悲飲歯業感想暗漢福詩路農鉄意様緑練銀駅鼻横箱談調橋整薬館題'.decode("utf-8"),
4:
'士不夫欠氏民史必失包末未以付令加司功札辺印争仲伝共兆各好成灯老衣求束兵位低児冷別努労告囲完改希折材利臣良芸初果刷卒念例典周協参固官底府径松毒泣治法牧的季英芽単省変信便軍勇型建昨栄浅胃祝紀約要飛候借倉孫案害帯席徒挙梅残殺浴特笑粉料差脈航訓連郡巣健側停副唱堂康得救械清望産菜票貨敗陸博喜順街散景最量満焼然無給結覚象貯費達隊飯働塩戦極照愛節続置腸辞試歴察旗漁種管説関静億器賞標熱養課輪選機積録観類験願鏡競議'.decode("utf-8"),
5:
'久仏支比可旧永句圧弁布刊犯示再仮件任因団在舌似余判均志条災応序快技状防武承価舎券制効妻居往性招易枝河版肥述非保厚故政査独祖則逆退迷限師個修俵益能容恩格桜留破素耕財造率貧基婦寄常張術情採授接断液混現略眼務移経規許設責険備営報富属復提検減測税程絶統証評賀貸貿過勢幹準損禁罪義群墓夢解豊資鉱預飼像境増徳慣態構演精総綿製複適酸銭銅際雑領導敵暴潔確編賛質興衛燃築輸績講謝織職額識護'.decode("utf-8"),
6:
'亡寸己干仁尺片冊収処幼庁穴危后灰吸存宇宅机至否我系卵忘孝困批私乱垂乳供並刻呼宗宙宝届延忠拡担拝枚沿若看城奏姿宣専巻律映染段洗派皇泉砂紅背肺革蚕値俳党展座従株将班秘純納胸朗討射針降除陛骨域密捨推探済異盛視窓翌脳著訪訳欲郷郵閉頂就善尊割創勤裁揮敬晩棒痛筋策衆装補詞貴裏傷暖源聖盟絹署腹蒸幕誠賃疑層模穀磁暮誤誌認閣障劇権潮熟蔵諸誕論遺奮憲操樹激糖縦鋼厳優縮覧簡臨難臓警'.decode("utf-8"),
'HS':
'乙了又与及丈刃凡勺互弔井升丹乏匁屯介冗凶刈匹厄双孔幻斗斤且丙甲凸丘斥仙凹召巨占囚奴尼巧払汁玄甘矛込弐朱吏劣充妄企仰伐伏刑旬旨匠叫吐吉如妃尽帆忙扱朽朴汚汗江壮缶肌舟芋芝巡迅亜更寿励含佐伺伸但伯伴呉克却吟吹呈壱坑坊妊妨妙肖尿尾岐攻忌床廷忍戒戻抗抄択把抜扶抑杉沖沢沈没妥狂秀肝即芳辛迎邦岳奉享盲依佳侍侮併免刺劾卓叔坪奇奔姓宜尚屈岬弦征彼怪怖肩房押拐拒拠拘拙拓抽抵拍披抱抹昆昇枢析杯枠欧肯殴況沼泥泊泌沸泡炎炊炉邪祈祉突肢肪到茎苗茂迭迫邸阻附斉甚帥衷幽為盾卑哀亭帝侯俊侵促俗盆冠削勅貞卸厘怠叙咲垣契姻孤封峡峠弧悔恒恨怒威括挟拷挑施是冒架枯柄柳皆洪浄津洞牲狭狩珍某疫柔砕窃糾耐胎胆胞臭荒荘虐訂赴軌逃郊郎香剛衰畝恋倹倒倣俸倫翁兼准凍剣剖脅匿栽索桑唆哲埋娯娠姫娘宴宰宵峰貢唐徐悦恐恭恵悟悩扇振捜挿捕敏核桟栓桃殊殉浦浸泰浜浮涙浪烈畜珠畔疾症疲眠砲祥称租秩粋紛紡紋耗恥脂朕胴致般既華蚊被託軒辱唇逝逐逓途透酌陥陣隻飢鬼剤竜粛尉彫偽偶偵偏剰勘乾喝啓唯執培堀婚婆寂崎崇崩庶庸彩患惨惜悼悠掛掘掲控据措掃排描斜旋曹殻貫涯渇渓渋淑渉淡添涼猫猛猟瓶累盗眺窒符粗粘粒紺紹紳脚脱豚舶菓菊菌虚蛍蛇袋訟販赦軟逸逮郭酔釈釣陰陳陶陪隆陵麻斎喪奥蛮偉傘傍普喚喫圏堪堅堕塚堤塔塀媒婿掌項幅帽幾廃廊弾尋御循慌惰愉惑雇扉握援換搭揚揺敢暁晶替棺棋棚棟款欺殖渦滋湿渡湾煮猶琴畳塁疎痘痢硬硝硫筒粧絞紫絡脹腕葬募裕裂詠詐詔診訴越超距軸遇遂遅遍酢鈍閑隅随焦雄雰殿棄傾傑債催僧慈勧載嗣嘆塊塑塗奨嫁嫌寛寝廉微慨愚愁慎携搾摂搬暇楼歳滑溝滞滝漠滅溶煙煩雅猿献痴睡督碁禍禅稚継腰艇蓄虞虜褐裸触該詰誇詳誉賊賄跡践跳較違遣酬酪鉛鉢鈴隔雷零靴頑頒飾飽鼓豪僕僚暦塾奪嫡寡寧腐彰徴憎慢摘概雌漆漸漬滴漂漫漏獄碑稲端箇維綱緒網罰膜慕誓誘踊遮遭酵酷銃銑銘閥隠需駆駄髪魂錬緯韻影鋭謁閲縁憶穏稼餓壊懐嚇獲穫潟轄憾歓環監緩艦還鑑輝騎儀戯擬犠窮矯響驚凝緊襟謹繰勲薫慶憩鶏鯨撃懸謙賢顕顧稿衡購墾懇鎖錯撮擦暫諮賜璽爵趣儒襲醜獣瞬潤遵償礁衝鐘壌嬢譲醸錠嘱審薪震錘髄澄瀬請籍潜繊薦遷鮮繕礎槽燥藻霜騒贈濯濁諾鍛壇鋳駐懲聴鎮墜締徹撤謄踏騰闘篤曇縄濃覇輩賠薄爆縛繁藩範盤罷避賓頻敷膚譜賦舞覆噴墳憤幣弊壁癖舗穂簿縫褒膨謀墨撲翻摩磨魔繭魅霧黙躍癒諭憂融慰窯謡翼羅頼欄濫履離慮寮療糧隣隷霊麗齢擁露'.decode("utf-8")
}

Kanji2Grade = {}
for a in (1,2,3,4,5,6,'HS'):
    for b in KanjiList_Jouyou[a]:
        Kanji2Grade[b]=a

		



######################################################################
#
#                      JLPT for words
#
######################################################################

import os
import codecs
import cPickle
import itertools

Word2Data = {}
JLPTWordLists={1:0,2:0,3:0,4:0} #utility ?

file = os.path.join(mw.config.configPath, "plugins\\JxPlugin\\Data", "JLPT.Word.List.csv")
file_pickle = os.path.join(mw.config.configPath, "plugins\\JxPlugin\\Data", "Word2Data.pickle")

def read_JLPT(file):
	"""Reads JLPT wordlists from file."""
	f = codecs.open(file, "r", "utf8")
	
	def keyfunc(line):
		if line=="\n":
			return False
		else:
			return True
	Html=""
	for key, group in itertools.groupby(f.readlines(), keyfunc):
		if key:
			group=list(group)
			data=[l.rstrip().split("	".decode("utf-8")) for l in group]
			for linol in data:
		            
			    if linol[1] == "":
				Html+= linol[0]+u" "    
			        Word2Data[linol[0].strip(u" ")] = int(linol[4])
		            else:
				Html+= linol[1]+u" "  
			        Word2Data[linol[1].strip(u" ")] = int(linol[4])
			    JLPTWordLists[int(linol[4])] = JLPTWordLists[int(linol[4])] + 1
	f.close()

if (os.path.exists(file_pickle) and 
	os.stat(file_pickle).st_mtime > os.stat(file).st_mtime):
	f = open(file_pickle, 'rb')
	Word2Data = cPickle.load(f)
	f.close()
else:
	read_JLPT(file)
	f = open(file_pickle, 'wb')
	cPickle.dump(Word2Data, f, cPickle.HIGHEST_PROTOCOL)
	f.close()
	


######################################################################
#
#                      Frequency for Kanji
#
######################################################################
Kanji2Frequency = {}

file = os.path.join(mw.config.configPath, "plugins\\JxPlugin\\Data", "KanjiFrequencyWikipedia.csv")

def read_Frequency(file):
	"""Reads Kanji frequency from file."""
	f = codecs.open(file, "r", "utf8")
	
	def keyfunc(line):
		if line=="\n":
			return False
		else:
			return True
	for key, group in itertools.groupby(f.readlines(), keyfunc):
		if key:
			group=list(group)
			data=[l.rstrip().split("	".decode("utf-8")) for l in group]
			for linol in data:
			    Kanji2Frequency[linol[0].strip(u" ")] = int(linol[1])
	f.close()

read_Frequency(file)
MaxFrequency = max(Kanji2Frequency.values())
Kanji2Zone ={}
for (key,value) in Kanji2Frequency.iteritems():
	a= (math.log(value+1,2)-math.log(MaxFrequency+1,2))*10+100
	if a > 62.26: #1/2
		Kanji2Zone[key] = 1
	elif a > 45: #1/5
		Kanji2Zone[key] = 2
	elif a > 30.32: #1/13
		Kanji2Zone[key] = 3
	elif a > 0.6: #1/100
		Kanji2Zone[key] = 4
	else:
		Kanji2Zone[key] = 5
		
######################################################################
#
#                      Frequency for Words
#
######################################################################
{}

file = os.path.join(mw.config.configPath, "plugins\\JxPlugin\\Data", "CorpusInternet.csv")

def read_Frequency(file,Dict):
	"""Reads Kanji frequency from file."""
	f = codecs.open(file, "r", "utf8")
	
	def keyfunc(line):
		if line=="\n":
			return False
		else:
			return True
	for key, group in itertools.groupby(f.readlines(), keyfunc):
		if key:
			group=list(group)
			data=[l.rstrip().split("	".decode("utf-8")) for l in group]
			for linol in data:
			    Dict[linol[0].strip(u" ")] = int(linol[1])
	f.close()
	return Dict
	
Word2Frequency = read_Frequency(file,{})
MaxWordFrequency = max(Word2Frequency.values())
MinWordFrequency = min(Word2Frequency.values())
Word2Zone ={}
for (key,value) in Word2Frequency.iteritems():
	a= (math.log(value+1,2)-math.log(MinWordFrequency+1,2))/(math.log(MaxWordFrequency+1,2)-math.log(MinWordFrequency+1,2))*100
	if a > 38: #1/2
		Word2Zone[key] = 1
	elif a > 30: #1/5
		Word2Zone[key] = 2
	elif a > 12: #1/13
		Word2Zone[key] = 3
	elif a > 4: #1/100
		Word2Zone[key] = 4
	else:
		Word2Zone[key] = 5
	
MapJLPTTango = {"From":"Tango","To":"JLPT","Legend":{1:"Lvl 1",2:"Lvl 2",3:"Lvl 3",4:"Lvl 4"},"Dict":Word2Data}
MapZoneTango = {"From":"Tango","To":"Frequency","Legend":{1:"Highest",2:"High",3:"Fair",4:"Low",5:"Lowest"},"Dict":Word2Zone}
MapJLPTKanji = {"From":"Kanji","To":"JLPT","Legend":{1:"Lvl 1",2:"Lvl 2",3:"Lvl 3",4:"Lvl 4"},"Dict":Kanji2JLPT}
MapZoneKanji = {"From":"Kanji","To":"Frequency","Legend":{1:"Highest",2:"High",3:"Fair",4:"Low",5:"Lowest"},"Dict":Kanji2Zone}
MapJouyouKanji = {"From":"Kanji","To":"Jouyou","Legend":{1:"Grade 1",2:"Grade 2",3:"Grade 3",4:"Grade 4",5:"Grade 5",6:"Grade 6","HS":"H.School"},"Dict":Kanji2Grade}

QueryKanji = """select fields.value from facts,cards,fields,fieldModels, models where 
		cards.factId = facts.id  and facts.id = fields.factId and fields.fieldModelId = fieldModels.id and facts.modelId = models.id and 
		fieldModels.name = "Kanji" and models.tags like "%Kanji%" and cards.reps > 0 order by firstAnswered"""
QueryTango = """select fields.value from facts,cards,fields,fieldModels, models where 
		cards.factId = facts.id  and facts.id = fields.factId and fields.fieldModelId = fieldModels.id and facts.modelId = models.id and 
		fieldModels.name = "Expression" and models.tags like "%Japanese%" and cards.reps > 0 order by firstAnswered"""

######################################################################
#
#                      Will run in init hook
#
######################################################################

JxMenu = """ 
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN">
<html>
<head>
<title>JxPlugin Main Menu</title>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<style type="text/css">

div#content {
	word-wrap: break-word;
}

ul#navlist {
        margin: 0;
        padding: 0;
        list-style-type: none;
        white-space: nowrap;
}

ul#navlist li {
        float: left;
        font-family: verdana, arial, sans-serif;
        font-size: 9px;
        font-weight: bold;
        margin: 0;
        padding: 5px 0 4px 0;
        background-color: #eef4f1;
        border-top: 1px solid #e0ede9;
        border-bottom: 1px solid #e0ede9;
}

#navlist a, #navlist a:link {
        margin: 0;
        padding: 5px 9px 4px 9px;
        color: #95bbae;
        border-right: 1px dashed #d1e3db;
        text-decoration: none;
}

ul#navlist li#active {
        color: #95bbae;
        background-color: #deebe5;
}

#navlist a:hover {
        color: #74a893;
        background-color: #d1e3db;
}

</style>
</head>
<body>
<div id="navcontainer">
<ul id="navlist">
<li ${JLPT}><a href=py:JxStats("JLPT")>JLPT</a></li>
<li ${Jouyou}><a href=py:JxStats("Jouyou")>Jouyou</a></li>
<li ${Zone}><a href=py:JxStats("Zone")>Frequency</a></li>
<li ${Tools}><a href=py:Tools>Tools</a></li>
</ul>
</div>
<div id="content" style="clear:both;">${Content}</div>
</body>
</html>
""".decode('utf-8')

def onJxMenu():
	JxStats('JLPT')

JxMap={"Kanji2JLPT":MapJLPTKanji,"Tango2JLPT":MapJLPTTango,"Kanji2Jouyou":MapJouyouKanji,
"Kanji2Zone":MapZoneKanji,"Tango2Zone":MapZoneTango}

def JxStats(Type):
	
	JxHtml = """<br/><center><b style="font-size:1.4em;">KANJI</b></center>"""
	JxHtml += """<center><a href=py:JxMissing('""" + Type + """','Kanji')>Missing</a>&nbsp;&nbsp;<a href=py:JxSeen('""" + Type + """','Kanji')>Seen</a></center><br/>"""
	JxHtml += HtmlReport(JxMap["Kanji2"+Type],QueryKanji)
	
	if Type!="Jouyou":
		JxHtml +="""<br /><center><b style="font-size:1.4em;">TANGO</b></center>"""
		JxHtml += """<center><a href=py:JxMissing('""" + Type + """','Tango')>Missing</a>&nbsp;&nbsp;<a href=py:JxSeen('""" + Type + """','Tango')>Seen</a></center><br />"""
		JxHtml += HtmlReport(JxMap["Tango2"+Type],QueryTango)
	
	Dict = {"JLPT":'',"Jouyou":'',"Zone":'',"Tools":'',"Content":JxHtml}
	Dict[Type] = 'id="active"'
	JxPage = Template(JxMenu).safe_substitute(Dict)
	
	JxWindow.setHtml(JxPage)
	JxWindow.show()

JxQuery={"Kanji":QueryKanji,"Tango":QueryTango}

import string

def JxMissing(Type,Set):
	JxHtml = Template("""<br /><center><b style="font-size:1.4em;">MISSING ${CAPSET}</b></center><center><a href=py:JxSeen("${Type}","${Set}")>Seen</a>&nbsp;<a href=py:JxStats("${Type}")>Stats</a></center>""").substitute(Type=Type,Set=Set,CAPSET=string.upper(Set)) 
	JxHtml += MissingHtml(JxMap[Set+"2"+Type],JxQuery[Set])
	
	Dict = {"JLPT":'',"Jouyou":'',"Zone":'',"Tools":'',"Content":JxHtml}
	Dict[Type] = 'id="active"'
	JxPage = Template(JxMenu).safe_substitute(Dict)
	
	JxWindow.setHtml(JxPage)

def JxSeen(Type,Set):
	JxHtml = Template("""<br /><center><b style="font-size:1.4em;">SEEN ${CAPSET}</b></center><center><a href=py:JxMissing("${Type}","${Set}")>Missing</a>&nbsp;<a href=py:JxStats("${Type}")>Stats</a></center>""").substitute(Type=Type,Set=Set,CAPSET=string.upper(Set)) 
	JxHtml += SeenHtml(JxMap[Set+"2"+Type],JxQuery[Set])
	
	Dict = {"JLPT":'',"Jouyou":'',"Zone":'',"Tools":'',"Content":JxHtml}
	Dict[Type] = 'id="active"'
	JxPage = Template(JxMenu).safe_substitute(Dict)
	
	JxWindow.setHtml(JxPage)
	
def onClick(url):
	String = unicode(url.toString())
	if String.startswith("py:"):
		String = String[3:]
		eval(String)

# I now have my own window =^.^=
JxWindow = QWebView(mw)
sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
sizePolicy.setHorizontalStretch(0)
sizePolicy.setVerticalStretch(0)
sizePolicy.setHeightForWidth(JxWindow.sizePolicy().hasHeightForWidth())
JxWindow.setSizePolicy(sizePolicy)
JxWindow.setMinimumSize(QtCore.QSize(310, 400))
JxWindow.setMaximumSize(QtCore.QSize(310, 16777215))
JxWindow.page().setLinkDelegationPolicy(QtWebKit.QWebPage.DelegateAllLinks)
mw.connect(JxWindow, QtCore.SIGNAL('linkClicked (const QUrl&)'), onClick)
JxWindow.hide()


def exit_JxPlugin():
	JxWindow.hide()

def init_JxPlugin():

#	Initialises the Anki GUI to present an option to invoke the plugin.


	
	widg ={}
	n = mw.mainWin.hboxlayout.count()
        for a in reversed(range(0,n)):
		widg[a+1]=mw.mainWin.hboxlayout.takeAt(a).widget()
		mw.mainWin.hboxlayout.removeWidget(widg[a+1])
        widg[0]=JxWindow	

	for a in range(0,n+1):
		mw.mainWin.hboxlayout.addWidget(widg[a])
	
	# creates menu entry
	mw.mainWin.actionJxGraphs = QtGui.QAction('JxGraphs', mw)
	mw.mainWin.actionJxGraphs.setStatusTip('Japanese GRAPHS')
	mw.mainWin.actionJxGraphs.setEnabled(False)
	mw.connect(mw.mainWin.actionJxGraphs, QtCore.SIGNAL('triggered()'), onJxGraphs)

	# creates menu entry
	mw.mainWin.actionJxStats = QtGui.QAction('JxStats', mw)
	mw.mainWin.actionJxStats.setStatusTip('Japanese STATS')
	mw.mainWin.actionJxStats.setEnabled(False)
	mw.connect(mw.mainWin.actionJxStats, QtCore.SIGNAL('triggered()'), onJStats)

	# creates menu entry
	mw.mainWin.actionJxDuplicates = QtGui.QAction('JxDuplicates', mw)
	mw.mainWin.actionJxDuplicates.setStatusTip('Japanese Duplicates')
	mw.mainWin.actionJxDuplicates.setEnabled(False)
	mw.connect(mw.mainWin.actionJxDuplicates, QtCore.SIGNAL('triggered()'), onJxDuplicates)

	# creates menu entry
	mw.mainWin.actionJxMenu = QtGui.QAction('JxMenu', mw)
	mw.mainWin.actionJxMenu.setStatusTip('Menuol')
	mw.mainWin.actionJxMenu.setEnabled(False)
	mw.connect(mw.mainWin.actionJxMenu, QtCore.SIGNAL('triggered()'), onJxMenu)

	# creates menu in the plugin sub menu
	#mw.mainWin.pluginMenu = mw.mainWin.menubar.addMenu('&JPlugin')
	#mw.mainWin.pluginMenu.addAction(mw.mainWin.actionJStats)

	#mw.mainWin.actionJStats.setShortcut(_("Ctrl+J"))


	# adds the plugin icon in the Anki Toolbar
	
	#mw.mainWin.toolBar.addSeparator()
	mw.mainWin.toolBar.addAction(mw.mainWin.actionJxGraphs)
	mw.mainWin.toolBar.addAction(mw.mainWin.actionJxStats)
	#mw.mainWin.toolBar.addAction(mw.mainWin.actionJxDuplicates)
	mw.mainWin.toolBar.addAction(mw.mainWin.actionJxMenu)
	
	# to enable or disable Jstats whenever a deck is opened/closed
	mw.deckRelatedMenuItems = mw.deckRelatedMenuItems + ("JxGraphs","JxStats","JxDuplicates","JxMenu",)
	
	# Ading features through hooks !
	mw.addHook('drawAnswer', append_JxPlugin) # additional info in answer cards
	mw.addHook('deckClosed', exit_JxPlugin) # additional info in answer cards
	
	ui.dialogs.registerDialog("JxGraphs", JxGraphProxy) # additional graphs


if __name__ == "__main__":
    print "Don't run me : I'm a plugin."
else:  
    #r = KanjiGraphLauncher(mw)
    mw.addHook('init', init_JxPlugin)
    print 'Lakedaemon plugin loaded'

