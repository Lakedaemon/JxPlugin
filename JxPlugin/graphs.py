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
from answer import Tango2Dic,JxType,JxTypeJapanese, GuessType,JxProfile,Jx_Profile,JxShowProfile,JxInitProfile



#colours for graphs
colorGrade={1:"#CC9933",2:"#FF9933",3:"#FFCC33",4:"#FFFF33",5:"#CCCC99",6:"#CCFF99",7:"#CCFF33",8:"#CCCC33"}
colorFreq={1:"#3333CC",2:"#3366CC",3:"#3399CC",4:"#33CCCC",5:"#33FFCC"}
colorJLPT={4:"#996633",3:"#999933",2:"#99CC33",1:"#99FF33",0:"#FFFF33"}





######################################################################
#
#          Routines for building the Card2Type Dictionnary
#
######################################################################
CardId2Types={}

def JxParseFacts4Stats():
        global ModelInfo,Fields,Tuple,Tau
        JxProfile("Before Query")
        # We are going to use 1 select and do most of the work in python (there might be other ways, but I have no time to delve into sqllite and sql language...haven't found any good tutorial about functions out there). 
        Query = """select cards.id, facts.tags, models.id, models.tags, models.name, fieldModels.name, fields.value, facts.id, fieldModels.ordinal
        from cards,facts,fields,fieldModels, models where 
        cards.factId = facts.id and facts.id = fields.factId and fields.fieldModelId = fieldModels.id and facts.modelId = models.id 
        order by models.id,facts.id,cards.id,fieldModels.ordinal"""
        Rows = mw.deck.s.all(Query)
        JxProfile("Parse Cards start")
        Length = len(Rows)
        ModelInfo = None
        Index = 0
        while Index < Length:
                #(0:CardId, 1:FactTags, 2:ModelId, 3:ModelTags, 4:ModelName, 5:FieldName, 6:FieldContent, 7: FactId, 8: FieldOrdinal)
                Tuple = Rows[Index]                
                Tau = 1
                while Index + Tau < Length:# For OS X users. We need python 2.5 for "short and" and "short or".  
                        if Rows[Index + Tau][0] == Tuple[0]:
                                Tau += 1
                        else:
                                break
                Delta = Tau
                while Index + Delta< Length:
                        if Rows[Index + Delta][7] == Tuple[7]: 
                                Delta += Tau                
                        else:
                                break
                Fields = [(Rows[a][5],Rows[a][6],Rows[a][8]) for a in range(Index,Index + Tau)]# beware of unpacking 2 out of 3 values
                List = JxParseFactTags4Stats(Rows,Index)
                CardId2Types.update([(Rows[a][0],List) for a in range(Index,Index + Delta,Tau)])
                Index += Delta
                if Index < Length:
                        if Rows[Index][2] != Tuple[2]:
                                # resets the model types
                                ModelInfo = None
        del ModelInfo,Fields,Tuple,Tau
        JxProfile("Card Parsng Ended")
      
        mw.help.showText(  JxShowProfile())         
                
                
                
                
def JxParseFactTags4Stats(Rows,Index):               
                # first check the tags of the fact
                Types = set()
                JxFactTags = set(Tuple[1].split(" "))
                for (Key,List) in JxType:
                        if JxFactTags.intersection(List):
                                Types.update([Key])
                if Types: 
                        return JxAffectFields4Stats(Fields,Types)
                # no relevant Fact tags, parse the model
                return JxParseModel4Stats(Rows,Index)
                 
def JxParseModel4Stats(Rows,Index):
        global ModelInfo
        # first check the model types
        if ModelInfo == None:# got to parse the model tags and maybee the model name
                ModelInfo = (set(),[])
                JxModelTags = set(Tuple[3].split(" "))
                for (Key,List) in JxType:
                        if JxModelTags.intersection(List):
                                ModelInfo[0].update([Key]) 
                if not(ModelInfo[0]):# model name now
                        for (Key,List) in JxType:
                                if Tuple[4] in List:
                                        ModelInfo[0].update([Key])
                                        break # no need to parse further
                if not(ModelInfo[0]):# Fields name now
                        for (Name,Content,Ordinal) in Fields:
                                for (Type,TypeList) in JxType:
                                        if Name in TypeList:
                                                ModelInfo[0].update([Type])
                                                ModelInfo[1].append((Type,Name,Ordinal,True))
                                                break # no need to parse this Field further
                if not(ModelInfo[0]): # Japanese Model ?
                        Set = set(Tuple[1].split(" ") + Tuple[3].split(" ") + [Tuple[4]] + [Rows[a][5] for a in range(Index,Index + Tau)])   
                        if Set.intersection(JxTypeJapanese):
                                ModelInfo[0].update(['Kanji','Word','Sentence','Grammar'])   
                if not(ModelInfo[0]):
                        pass 
                        # this set might still be related to japanese if it's content includes Kana (as I expect the japanese user of Anki NOT to use the JxPlugin, 
                        # I test for Kana in case there are koreans or chinese users learning japanese, it'll be hard finding the relevant field for those though
                        # I expect that anybody wantng to learn japanese will want to display kana readings)
                        # Anyway, I need Jmdict.xml to do anything about this
                        
                # now, we got to set the action and build a Hint
                elif not(ModelInfo[1]):
                        # first, we try to affect relevant fields for each type (first try fields with the name similar to the type)
                        for (Type,TypeList) in JxType:
                                if Type in ModelInfo[0]:
                                        for (Name,Content,Ordinal) in Fields:
                                                if Name in TypeList:
                                                        ModelInfo[1].append((Type,Name,Ordinal,True)) 
                                                        break
                        if len(ModelInfo[1]) < len(ModelInfo[0]):
                                # for the still missing fields, we try to find an "Expression" field next and update the List
                                if ModelInfo[1]:
                                        (Done,Arga,Argb,Argc) = zip(*ModelInfo[1])
                                else : 
                                        Done = []
                                TempList = []
                                for (Type,TypeList) in JxType:
                                        if Type in ModelInfo[0] and Type in Done:
                                                TempList.append(ModelInfo[1].pop(0))
                                        elif Type in ModelInfo[0]:
                                                for (Name,Content,Ordinal) in Fields:
                                                        if Name == "Expression":
                                                                if len(ModelInfo[0])==1:
                                                                        TempList.append((Type,"Expression",Ordinal,True))
                                                                else:
                                                                        TempList.append((Type,"Expression",Ordinal,False))                                                                        
                                                                break 
                                ModelInfo = (ModelInfo[0],TempList)
                
                        #if len(ModelInfo[1]) < len(ModelInfo[0]):
                        #        # there is nothing we can do about that at the model level
                        #        pass
        
                
        # now that we have ModelInfo, we can set/guess (True/False) the value of the fields and return a list of (type/name/content)
        
        if not(ModelInfo[0]) :
                return []
        # use the Hint if there is one
        List = []
        for (Type,Name,Ordinal,Boolean) in ModelInfo[1]:
                Content = Rows[Index + Ordinal][6]
                if Boolean:
                        List.append((Type,Name,Content))
                elif Type in GuessType(Content):
                        List.append((Type,Name,Content))
                                
        if len(List) < len(ModelInfo[0]):
                # we need Jmdict.xml to do something sensible about that
                # field names and "Expression" have failed, we could still try to guess with the fields content
                # but for the time being, we will pass because I don't know how to choose between two fields that might only have kanas (maybee query other cards to decide between the fields, might be doable for sentences (ponctuation helps) and Kanji (only 1 Kanji character))
                pass
                
        return List           

def JxAffectFields4Stats(FieldNameContentList,Types):# could be optimized for Rows and stats, maybee...but that way, it can be usd by both routines
        # we now try to affect relevant fields for each type (first try fields with the name similar to the type)
        List=[]
        for (Type,TypeList) in JxType:
                if Type in Types:
                        for (Name,Content) in FieldNameContentList:
                                if Name in TypeList:
                                        List.append((Type,Name,Content)) 
                                        break
                                             
        if len(List)<len(Types):
                # there are still missing fields for the types, we could try the "Expression" field next and update the List
                if len(List)>0:
                        (Done,Field) = zip(*List)
                else : 
                        Done=[]
                TempList=[]
                for (Type,TypeList) in JxType:
                        if Type in Types and Type in Done:
                                TempList.append(List.pop(0))
                        elif Type in Types:
                                for (Name,Content) in FieldNameContentList:
                                        if Name == u"Expression":
                                                TempList.append((Type,Name,Content)) 
                                                break 
                List = TempList
                                                
        if len(List)<len(Types):
                # field names and "Expression" have failed, we could still try to guess with the fields content
                # but for the time being, we will pass because I don't know how to choose between two fields that might only have kanas (maybee query other cards to decide between the fields, might be doable for sentences (ponctuation helps) and Kanji (only 1 Kanji character))
                pass
   
        return List
######################################################################
#
#                               Graphs
#
######################################################################

def JxJSon(CouplesList):
        return "[" + ",".join(map(lambda (x,y): "[%s,%s]"%(x,y),CouplesList)) + "]" 

def JxStatsUpdate(Key,Ease,Value):
        if Ease == 1 and Interval > 21:
                JxState[Value[Type + "|" + str(k)]] -= 1  
        elif Interval <= 21 and NextInterval >21:
                JxState[Value[Type]] += 1
                
def JxGraphsa():        
            
        JxParseFacts4Stats() 
        Rows = mw.deck.s.all("""
                select reviewHistory.cardId, reviewHistory.time, reviewHistory.lastInterval, reviewHistory.nextInterval, reviewHistory.ease 
                from reviewHistory order by reviewHistory.time
                """) 
        
        t = time.time()
        from copy import deepcopy # very important or the dictionnary stays linked !!
        # Parse the info with respect to the CardId2Types dictionnary

        JxStateArray = {}
        JxState = {}
        JxStatsMap = {'Word':[MapJLPTTango,MapZoneTango],'Kanji':[MapJLPTKanji,MapJouyouKanji,MapKankenKanji,MapZoneKanji],'Grammar':[],'Sentence':[]}
        for (Type,List) in JxStatsMap.iteritems():
                for (k,Map) in enumerate(List):
                        KeyGraph = Type + "|" + str(k)
                        JxState[KeyGraph] = dict([(Key,0) for (Key,String) in Map.Order] + [('Other',0)])
        JxNowTime = time.time()
        for (CardId,Time,Interval,NextInterval,Ease) in Rows:
                if CardId in CardId2Types:
                        for (Type,Name,Content) in CardId2Types[CardId]:
                                for (k, Map) in enumerate(JxStatsMap[Type]):
                                        KeyGraph = Type + "|" + str(k)
                                        try:
                                                Key = Map.Value(Content)
                                        except KeyError:
                                                Key = 'Other'
                                        if Ease == 1 and Interval > 21:
                                                JxState[KeyGraph][Key] = JxState[KeyGraph][Key]-1
                                        elif Interval <= 21 and NextInterval >21:
                                                JxState[KeyGraph][Key] = JxState[KeyGraph][Key]+1                                   
                JxDay = int((Time-JxNowTime) / 86400.0)+1
                JxStateArray[JxDay] = deepcopy(JxState)
        JxStateArray[0] = deepcopy(JxState)   
        
       
       
        # Transform the results into JSon strings
        JxDays = JxStateArray.keys()
        JxDays.sort()
        
        JxGraphsJSon = {}
        for (Type,List) in JxStatsMap.iteritems():
                for (k,Map) in enumerate(List):
                        KeyGraph = Type + "|" + str(k)                              
                        JxGraphsJSon[KeyGraph] = dict([(Key,JxJSon([(Day,JxStateArray[Day][KeyGraph][Key]) for Day in JxDays])) for (Key,String) in Map.Order] + [('Other',JxJSon([(Day,JxStateArray[Day][KeyGraph]['Other']) for Day in JxDays]))])           
       
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


<!--                     Graphs                          -->


<script type="text/javascript" src="jquery.newflot.js"></script>
<script type="text/javascript" src="jquery.flot.stack.js"></script>






<script> 
	jQuery().ready(function(){
		//var icon = "info"; 
               $('.ui-button').button({checkButtonset:true});
$.plot($("#placeholderb"), %(JSon)s , {   lines: {
    show: true,
    fill: 1,
    fillColor: false
  },yaxis: { max: 500 } });
});
</script> 
</head>
<body>

      <div id="placeholderb" style="width:600px;height:300px"></div>
      
          <div id="placeholder" style="width:600px;height:300px"></div> 
 
    <p>1000 kg. CO<sub>2</sub> emissions per year per capita for various countries (source: <a href="http://en.wikipedia.org/wiki/List_of_countries_by_carbon_dioxide_emissions_per_capita">Wikipedia</a>).</p> 
 
    <p>Flot supports selections. You can enable
       rectangular selection
       or one-dimensional selection if the user should only be able to
       select on one axis. Try left-clicking and drag on the plot above
       where selection on the x axis is enabled.</p> 
 
    <p>You selected: <span id="selection"></span></p> 
 
    <p>The plot command returns a Plot object you can use to control
       the selection. Try clicking the buttons below.</p> 
 
    <p><input id="clearSelection" type="button" value="Clear selection" /> 
       <input id="setSelection" type="button" value="Select year 1994" /></p> 
 
    <p>Selections are really useful for zooming. Just replot the
       chart with min and max values for the axes set to the values
       in the "plotselected" event triggered. Try enabling the checkbox
       below and select a region again.</p> 
 
    <p><input id="zoom" type="checkbox">Zoom to selection.</input></p> 
      
      <script id="source" language="javascript" type="text/javascript"> 
$(function () {
    var data = %(JSon)s
 
    var options = {
        lines: { show: true },
        points: { show: true },
        legend: { noColumns: 2 },
        xaxis: { tickDecimals: 0 },
        yaxis: { min: 0 },
        selection: { mode: "x" }
    };
 
    var placeholder = $("#placeholder");
 
    placeholder.bind("plotselected", function (event, ranges) {
        $("#selection").text(ranges.xaxis.from.toFixed(1) + " to " + ranges.xaxis.to.toFixed(1));
 
        var zoom = $("#zoom").attr("checked");
        if (zoom)
            plot = $.plot(placeholder, data,
                          $.extend(true, {}, options, {
                              xaxis: { min: ranges.xaxis.from, max: ranges.xaxis.to }
                          }));
    });
    
    var plot = $.plot(placeholder, data, options);
 
    $("#clearSelection").click(function () {
        plot.clearSelection();
    });
 
    $("#setSelection").click(function () {
        plot.setSelection({ x1: 1994, x2: 1995 });
    });
});
</script> 
      
      
          </body></html>          
                    
                    
                    """% {'JSon':"[" + ",".join(['{ label: "Grade '+ str(k) +'", stack:true,data :'+ JxGraphsJSon['Word|0'][k] +'}' for (k,String) in (MapJLPTKanji.Order+[('Other','Other')])]) +"]"}  
        JxPreview.setHtml(JxHtml ,JxResourcesUrl)
        JxPreview.show()  
        #mw.help.showText(JxGraphsJSon['Word|1'][1])
        #mw.help.showText(debug)























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
		     c = Kanji2Zone[OLKanji]                   
		     Change = Kanji2Frequency[OLKanji]
                 else:
	             Change = 0	
	             c = 5		  
                 if ease == 1 and interval > 21:
	             OLKnownTemp[a] -= 1  
		     GradeKnownTemp[b] -=  1  
		     AccumulatedTemp[c] -= Change
                 elif interval <= 21 and nextinterval>21:
		     OLKnownTemp[a] += 1
		     GradeKnownTemp[b] += 1
		     AccumulatedTemp[c] += Change
                 OLDay = int((OLtime-t) / 86400.0)+1
                 OLKnown[OLDay] = {0:OLKnownTemp[0],1:OLKnownTemp[1],2:OLKnownTemp[2],3:OLKnownTemp[3],4:OLKnownTemp[4]} 
                 GradeKnown[OLDay] = {1:GradeKnownTemp[1],2:GradeKnownTemp[2],3:GradeKnownTemp[3],4:GradeKnownTemp[4],5:GradeKnownTemp[5],6:GradeKnownTemp[6],'HS':GradeKnownTemp['HS'],'Other':GradeKnownTemp['Other']} 
                 Accumulated[OLDay] = {1:AccumulatedTemp[1],2:AccumulatedTemp[2],3:AccumulatedTemp[3],4:AccumulatedTemp[4],5:AccumulatedTemp[5]}
            OLKnown[0] = {0:OLKnownTemp[0],1:OLKnownTemp[1],2:OLKnownTemp[2],3:OLKnownTemp[3],4:OLKnownTemp[4]}
            GradeKnown[0] = {1:GradeKnownTemp[1],2:GradeKnownTemp[2],3:GradeKnownTemp[3],4:GradeKnownTemp[4],5:GradeKnownTemp[5],6:GradeKnownTemp[6],'HS':GradeKnownTemp['HS'],'Other':GradeKnownTemp['Other']} 
            Accumulated[0]= {1:AccumulatedTemp[1],2:AccumulatedTemp[2],3:AccumulatedTemp[3],4:AccumulatedTemp[4],5:AccumulatedTemp[5]}
            self.stats['OL'] = OLKnown.copy() 
            self.stats['Grade'] = GradeKnown.copy()  
            self.stats['KAccumulated'] = Accumulated.copy()


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
	             OLKnownTemp[a] -=  1 
		     AccumulatedTemp[b] -= Change		     
		elif interval <= 21 and nextinterval>21:
		     OLKnownTemp[a] +=  1
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



		






	
	
	
	
	
	
	
