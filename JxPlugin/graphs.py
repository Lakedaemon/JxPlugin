# -*- coding: utf-8 -*-
# Copyright: Olivier Binda <olivier.binda@wanadoo.fr>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
# ---------------------------------------------------------------------------
# This file is a plugin for the "anki" flashcard application http://ichi2.net/anki/
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
#from ui_graphs import *
from answer import Tango2Dic

######################################################################
#
#                                             Graphs
#
######################################################################


#colours for graphs
colorGrade={1:"#CC9933",2:"#FF9933",3:"#FFCC33",4:"#FFFF33",5:"#CCCC99",6:"#CCFF99",7:"#CCFF33",8:"#CCCC33"}
colorFreq={1:"#3333CC",2:"#3366CC",3:"#3399CC",4:"#33CCCC",5:"#33FFCC"}
colorJLPT={4:"#996633",3:"#999933",2:"#99CC33",1:"#99FF33",0:"#FFFF33"}

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
	    GradeKnownTemp= {1:0,2:0,3:0,4:0,5:0,6:0,'HS':0,'Other':0}
	    AccumulatedTemp = {1:0,2:0,3:0,4:0,5:0}
	    OLKnown={}
	    GradeKnown={}
	    Accumulated={}

            for (OLKanji,OLtime,interval,nextinterval,ease) in JLPTReviews:
                 if OLKanji in Kanji2JLPT:
		     a = Kanji2JLPT[OLKanji]
                 else:
	             a = 0
                 if OLKanji in Kanji2Grade:
		     b = Kanji2Grade[OLKanji]
                 else:
	             b = 'Other'
                 if OLKanji in Kanji2Frequency:
		     b = Kanji2Zone[OLKanji]                   
		     Change = Kanji2Frequency[OLKanji]
                 else:
	             Change = 0	
	             b = 5		  
                 if ease == 1 and interval > 21:
	             OLKnownTemp[a] -= 1  
		     GradeKnownTemp[b] -=  1  
		     AccumulatedTemp[b] -= Change
                 elif interval <= 21 and nextinterval>21:
		     OLKnownTemp[a] += 1
		     GradeKnownTemp[b] += 1
		     AccumulatedTemp[b] += Change
                 OLDay = int((OLtime-t) / 86400.0)+1
                 OLKnown[OLDay] = {0:OLKnownTemp[0],1:OLKnownTemp[1],2:OLKnownTemp[2],3:OLKnownTemp[3],4:OLKnownTemp[4]} 
                 GradeKnown[OLDay] = {1:GradeKnownTemp[1],2:GradeKnownTemp[2],3:GradeKnownTemp[3],4:GradeKnownTemp[4],5:GradeKnownTemp[5],6:GradeKnownTemp[6],'HS':GradeKnownTemp['HS'],'Other':GradeKnownTemp['Other']} 
                 Accumulated[OLDay] = {1:AccumulatedTemp[1],2:AccumulatedTemp[2],3:AccumulatedTemp[3],4:AccumulatedTemp[4],5:AccumulatedTemp[5]}
            OLKnown[0] = {0:OLKnownTemp[0],1:OLKnownTemp[1],2:OLKnownTemp[2],3:OLKnownTemp[3],4:OLKnownTemp[4]}
            GradeKnown[0] = {1:GradeKnownTemp[1],2:GradeKnownTemp[2],3:GradeKnownTemp[3],4:GradeKnownTemp[4],5:GradeKnownTemp[5],6:GradeKnownTemp[6],'HS':GradeKnownTemp['HS'],'Other':GradeKnownTemp['Other']} 
            Accumulated[0]= {1:AccumulatedTemp[1],2:AccumulatedTemp[2],3:AccumulatedTemp[3],4:AccumulatedTemp[4],5:AccumulatedTemp[5]}
            self.stats['OL'] = OLKnown 
            self.stats['Grade'] = GradeKnown  
            self.stats['KAccumulated'] = Accumulated


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
	    AccumulatedTemp = {1:0,2:0,3:0,4:0,5:0}
	    Accumulated = {}
	    
            for (OLWord,OLtime,interval,nextinterval,ease) in JLPTReviews:
		WordStripped=Tango2Dic(OLWord)
		if WordStripped in Word2Data:
		     a = Word2Data[WordStripped]
		else:
	             a = 0 
		if OLWord in Word2Frequency:
		     b = Word2Zone[OLWord]                   
		     Change = Word2Frequency[OLWord]
		else:
	             Change = 0	
	             b = 5			     
		if ease == 1 and interval > 21:
	             OLKnownTemp[a] = OLKnownTemp[a] - 1 
		     AccumulatedTemp[b] -= Change		     
		elif interval <= 21 and nextinterval>21:
		     OLKnownTemp[a] = OLKnownTemp[a] + 1
		     AccumulatedTemp[b] += Change		     
		OLDay = int((OLtime-t) / 86400.0)+1
		OLKnown[OLDay] = {0:OLKnownTemp[0],1:OLKnownTemp[1],2:OLKnownTemp[2],3:OLKnownTemp[3],4:OLKnownTemp[4]} 
		Accumulated[OLDay] = {1:AccumulatedTemp[1],2:AccumulatedTemp[2],3:AccumulatedTemp[3],4:AccumulatedTemp[4],5:AccumulatedTemp[5]}
	     
            OLKnown[0] = {0:OLKnownTemp[0],1:OLKnownTemp[1],2:OLKnownTemp[2],3:OLKnownTemp[3],4:OLKnownTemp[4]}
            Accumulated[0]= {1:AccumulatedTemp[1],2:AccumulatedTemp[2],3:AccumulatedTemp[3],4:AccumulatedTemp[4],5:AccumulatedTemp[5]}	    
            self.stats['Time2JLPT4Words'] = OLKnown 
            self.stats['TAccumulated'] = Accumulated
            
            
            
    
	    
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

        
        
        self.filledGraph(graph, days, [colorJLPT[k] for k in range(0,5)], *Arg)
	
	cheat = fig.add_subplot(111)
        b0 = cheat.bar(-1, 0, color = colorJLPT[4])
        b1 = cheat.bar(-2, 0, color = colorJLPT[3])
        b2 = cheat.bar(-3, 0, color = colorJLPT[2])
        b3 = cheat.bar(-4, 0, color = colorJLPT[1])
        b4 = cheat.bar(-5, 0, color = colorJLPT[0])
	
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
	
        
             
        def JxSon(ListA,ListB):
                return "[" + ",".join(map(lambda (x,y): "[%s,%s]"%(x,y),zip(ListA,ListB))) + "]"               
        from ui_menu import JxPreview
        from ui_menu import JxResourcesUrl
        JxHtml="""
                    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN">
<html>
<head>
<title>JxPlugin Main Menu</title>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />



<!--                  jQuery & UI                          -->


<script type="text/javascript" src="js/jquery-1.3.2.min.js"></script>
<script type="text/javascript" src="js/jquery-ui-1.7.2.custom.min.js"></script> 


<!--                         Theme                          -->

<!--<link type="text/css" rel="stylesheet" href="http://jqueryui.com/themes/base/ui.all.css" /> -->
<link rel="Stylesheet" href="themes/sunny/jquery-ui.css" type="text/css" /> 


<!--                  Buttons                          -->





<script src="ui.button/ui.classnameoptions.js"></script> 
<script src="ui.button/ui.button.js"></script> 
<link rel="stylesheet" type="text/css" href="ui.button/ui-button.css" /> 
<script src="ui.button/ui.buttonset.js"></script> 



	<script type="text/javascript"  src="http://jqueryui.com/themeroller/themeswitchertool/"></script> 

<!--                     Selects                          -->

<link rel="stylesheet" type="text/css" href="ui.dropdownchecklist.css" /> 
<script type="text/javascript" src="ui.dropdownchecklist.js"></script>

<link rel="Stylesheet" href="ui.selectmenu/ui.selectmenu.css" type="text/css" /> 
<script type="text/javascript" src="ui.selectmenu/ui.selectmenu.js"></script> 





<script type="text/javascript" src="jquery.flot.js"></script>







<script> 
	jQuery().ready(function(){
		//var icon = "info"; 
               $('.ui-button').button({checkButtonset:true});
$.plot($("#placeholder"), %s , {   lines: {
    show: true,
    fill: 1,
    fillColor: false
  },yaxis: { max: 500 } });
});
</script> 
</head>
<body>

      <div id="placeholder" style="width:600px;height:300px"></div>
          </body></html>          
                    
                    
                    """% ("[" + ",".join([JxSon(JOL[2*k],JOL[2*k+1]) for k in [0]]) +"]")  
        #JxPreview.setHtml(JxHtml ,JxResourcesUrl)
        #JxPreview.show()
        
        
        
       
        
        
        
        
        
        
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

    def graphTime2Frequency4Kanji(self, days=30):
        self.calcStats()
        fig = Figure(figsize=(self.width, self.height), dpi=self.dpi)
        graph = fig.add_subplot(111)

        JOL = {}
        for c in range(0,10): 
	      JOL[c] = []
        
        OLK = self.stats['KAccumulated']
        # have to sort the dictionnary
        keys = OLK.keys()
        keys.sort()
	
	for a in keys:
		for c in range(0,5):	
                   JOL[2 * c].append(a)
                   JOL[9-2 * c].append(sum([OLK[a][k] for k in range(1,c+2)])*100.0/SumKanjiOccurences)
        Arg =[JOL[k] for k in range(0,10)]
        self.filledGraph(graph, days, [colorFreq[5-k] for k in range(0,5)], *Arg)
	
        cheat = fig.add_subplot(111)
        b0 = cheat.bar(-1, 0, color = colorFreq[1])
        b1 = cheat.bar(-2, 0, color = colorFreq[2])
        b2 = cheat.bar(-3, 0, color = colorFreq[3])
        b3 = cheat.bar(-4, 0, color = colorFreq[4])
        b4 = cheat.bar(-5, 0, color = colorFreq[5])
        cheat.legend([b0, b1, b2, b3, b4], [
            _("Highest"),
            _("High"),
            _("Fair"),
	    _("Low"), 
	    _("Lowest")], loc='upper left')
	
        graph.set_xlim(xmin = -days, xmax = 0)
        graph.set_ylim(ymax= max (a for a in JOL[1])*1.1 )
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
        self.filledGraph(graph, days, [colorJLPT[k] for k in range(0,5)], *Arg)
	
	cheat = fig.add_subplot(111)
        b0 = cheat.bar(-1, 0, color = colorJLPT[4])
        b1 = cheat.bar(-2, 0, color = colorJLPT[3])
        b2 = cheat.bar(-3, 0, color = colorJLPT[2])
        b3 = cheat.bar(-4, 0, color = colorJLPT[1])
        b4 = cheat.bar(-5, 0, color = colorJLPT[0])
	
        cheat.legend([b0, b1, b2, b3, b4], [
            _("JLPT 4"),
            _("JLPT 3"),
            _("JLPT 2"),
	    _("JLPT 1"), 
	    _("Other")], loc='upper left')
	
        graph.set_xlim(xmin = -days, xmax = 0)
        graph.set_ylim(ymax= max (a for a in JOL[1]) + 30)
        return fig

    def graphTime2Frequency4Words(self, days=30):
        self.calcStats()
       
        fig = Figure(figsize=(self.width, self.height), dpi=self.dpi)
        graph = fig.add_subplot(111)

        JOL = {}
        for c in range(0,10): 
	      JOL[c] = []
        
        OLK = self.stats['TAccumulated']
        # have to sort the dictionnary
        keys = OLK.keys()
        keys.sort()
	for a in keys:
#                sumJOL=0.0
		for c in range(0,5):	
                   JOL[2 * c].append(a)
                   value=sum([OLK[a][k] for k in range(1,c+2)])*100.0/SumWordOccurences
                   JOL[9-2 * c].append(value)
        
        Arg =[JOL[k] for k in range(0,10)]
        self.filledGraph(graph, days, [colorFreq[5-k] for k in range(0,5)], *Arg)

        cheat = fig.add_subplot(111)
        b0 = cheat.bar(-1, 0, color = colorFreq[1])
        b1 = cheat.bar(-2, 0, color = colorFreq[2])
        b2 = cheat.bar(-3, 0, color = colorFreq[3])
        b3 = cheat.bar(-4, 0, color = colorFreq[4])
        b4 = cheat.bar(-5, 0, color = colorFreq[5])
        cheat.legend([b0, b1, b2, b3, b4], [
            _("Highest"),
            _("High"),
            _("Fair"),
	    _("Low"), 
	    _("Lowest")], loc='upper left')
	
        graph.set_xlim(xmin = -days, xmax = 0)
        graph.set_ylim(ymax= max (a for a in JOL[1])*1.1)
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



		






	
	
	
	
	
	
	
