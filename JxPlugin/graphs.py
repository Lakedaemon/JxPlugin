# -*- coding: utf-8 -*-
# Copyright: Olivier Binda <olivier.binda@wanadoo.fr>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
# ---------------------------------------------------------------------------
# This file is a plugin for the "anki" flashcard application http://ichi2.net/anki/
# ---------------------------------------------------------------------------
import time
#import datetime


#from anki.utils import ids2str
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
                while Index + Delta < Length:
                        if Rows[Index + Delta][7] == Tuple[7]: 
                                Delta += Tau                
                        else:
                                break
                Fields = [(Rows[a][5],Rows[a][6],Rows[a][8]) for a in range(Index,Index + Tau)]# beware of unpacking 2 out of 3 values
                List = JxParseFactTags4Stats(Rows,Index)
                CardsIds = [Rows[a][0] for a in range(Index,Index + Delta,Tau)]
                CardId2Types.update([(Id,(List,CardsIds)) for Id in CardsIds])
                Index += Delta
                if Index < Length:
                        if Rows[Index][2] != Tuple[2]:
                                # resets the model types
                                ModelInfo = None
        del ModelInfo,Fields,Tuple,Tau
        JxProfile("Card Parsng Ended")
      
       
                
                
                
                
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
                    
def JxNewAlgorythm():
        global JxStateArray,JxStatsMap
        JxProfile("NewAlgorythm Begins")
        Rows = mw.deck.s.all("""
                select facts.id,reviewHistory.cardId, reviewHistory.time, reviewHistory.lastInterval, reviewHistory.nextInterval, reviewHistory.ease 
                from reviewHistory,cards,facts where facts.id=cards.factId and cards.id = reviewHistory.cardId 
                order by facts.id,reviewHistory.cardId,reviewHistory.time
                """) 
        JxProfile("Query ended")  
        JxStatsMap = {'Word':[MapJLPTTango,MapZoneTango],'Kanji':[MapJLPTKanji,MapZoneKanji,MapJouyouKanji,MapKankenKanji],'Grammar':[],'Sentence':[]}
        JxNowTime = time.time()
        # The Graphs we can have
        Length = len(Rows)
        Index = 0
        JxCardState = []
        JxCardStateArray = []
        JxStateArray = {}
        # We will initialize other stuff on the fly !
        while True:
                # 0:FactId 1:CardId, 2:Time, 3: lastInterval, 4: next interval, 5:ease
                (FactId,CardId,Time,Interval,NextInterval,Ease) = Rows[Index]                  
                # first, we have to build a list of the days where status changes happened for this card (+ - + - + - ...)
                if (Interval <= 21 and NextInterval > 21) or (Interval > 21 and Ease == 1):
                        #Card Status Change
                        Day = int((JxNowTime-Time) / 86400.0)
                        JxCardState.append(Day)
                Index += 1
                if Index == Length: 
                        # we have finished parsing the Entries.Flush the last Fact and break
                        JxCardStateArray.append(JxCardState[:])
                        JxFlushFacts(JxCardStateArray,CardId)
                        break
                        # we have finished parsing the Entries, flush the Status change
                elif CardId == Rows[Index][1]:
                        # Same Card : Though it does nothing, we put this here for speed purposes because it happens a lot.
                        pass
                elif FactId != Rows[Index][0]:                        
                        # Fact change : Though it happens a bit less often than cardId change, we have to put it there or it won't be caught, flush the status change.
                        JxCardStateArray.append(JxCardState[:])
                        JxFlushFacts(JxCardStateArray,CardId)
                        JxCardState = []
                        JxCardStateArray = []
                else:
                        # CardId change happens just a little bit more often than fact changes (if deck has more than 3 card models;..). Store and intit the card status change
                        JxCardStateArray.append(JxCardState[:])
                        JxCardState = []
        JxProfile("NewAlgorythm Ends")
        # return the array
        JxGraphsJSon = {}
        #global debug
        #debug=""
        for (Type,List) in JxStatsMap.iteritems():
                for (k, Map) in enumerate(List):
                        for (Key,String) in Map.Order +[('Other','Other')]:
                                try:
                                        List = JxStateArray[(Type,k,Key)]
                                except:
                                        List = [0]
                                        #debug += "<br/>(" + Type+','+str(k)+','+str(Key)+') :'+str(List)
                                JxGraphsJSon[(Type,k,Key)] =  JxJSon([(Day,sum(List[-Day:])) for Day in range(-len(List),1)]) 
        return JxGraphsJSon
        
def JxFlushFacts(JxCardStateArray,CardId):
        global JxStateArray,JxStatsMap
        """Flush the fact stats into the state array"""
        try:# get the card type and the number of shared cardsids by the fact
                (CardInfo,CardsNumber) = CardId2Types[CardId]
                CardWeight = 1.0/max(1,len(CardsNumber))
                for (Type,Name,Content) in CardInfo:
                        for (k, Map) in enumerate(JxStatsMap[Type]):
                                try:
                                        Key = Map.Value(Content)
                                except KeyError:
                                        Key = 'Other' 
                                if k != 1:
                                #if Map.To != 'Occurences':    #something is wrong there, why do I have to comment that ? 
                                        Change = CardWeight
                                elif Type == "Word":
                                        #elif Map.From == 'Tango':
                                        try:
                                                Change = 100.0 * Word2Frequency[Content] * CardWeight / SumWordOccurences 
                                        except KeyError:
                                                Change = 0
                                else:
                                        try:
                                                Change = 100.0 * Kanji2Frequency[Content] * CardWeight / SumKanjiOccurences
                                        except KeyError:
                                                Change = 0 
                                # we have to update the graph of each type
                                try:
                                        List = JxStateArray[(Type,k,Key)]
                                except KeyError:
                                        # got to initialize it
                                        List=[]
############################################################################################################# upgrade this part to support "over-ooptimist", "optimist", "realist", "pessimist" modes                                        
                                #now, we got to flush the fact. Let's go for the realist model first
                                for JxDaysList in JxCardStateArray:
                                        Status = True
                                        for JxDay in JxDaysList:
                                                try: 
                                                        if Status:
                                                                List[JxDay] += Change
                                                        else:
                                                                List[JxDay] -= Change
                                                except:# we have to update the size of List first
                                                        List = List + [0 for a in range(len(List),JxDay+1)]
                                                        # now, it should be okey
                                                        if Status:
                                                                List[JxDay] += Change
                                                        else:
                                                                List[JxDay] -= Change 
                                        Status = not(Status)
                                        # save the updated list                        
                                        JxStateArray[(Type,k,Key)] = List[:] 
##############################################################################################################
        except KeyError:# we do nothing, this Fact has no type.
                pass
        
               
def JxGraphs(): 
        #global JxStateArray
        JxProfile("JxGraphs()")   
        JxParseFacts4Stats() 
        JxGraphsJSon =JxNewAlgorythm()
        JxStatsMap = {'Word':[MapJLPTTango,MapZoneTango],'Kanji':[MapJLPTKanji,MapZoneKanji,MapJouyouKanji,MapKankenKanji],'Grammar':[],'Sentence':[]}


        from ui_menu import JxPreview
        from ui_menu import JxResourcesUrl
        JxHtml=u"""
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


<script type="text/javascript" src="jquery.flot.js"></script>

<script type="text/javascript" src="jquery.flot.stack.mod.min.js"></script>






<script> 
	jQuery().ready(function(){
               $('.ui-button').button({checkButtonset:true});
               
$.plot($("#KanjiJLPT"),   %(JSon:Kanji|0)s ,{grid:{show:true,aboveData:true},lines:{show:true,fill:1,fillcolor:false},series:{stack:true},legend:{container:$('#LegendJLPT')}});
$.plot($("#WordJLPT"),    %(JSon:Word|0)s  ,{grid:{show:true,aboveData:true},lines:{show:true,fill:1,fillcolor:false},series:{stack:true},legend:{show:false}});
$.plot($("#KanjiFreq"),   %(JSon:Kanji|1)s ,{grid:{show:true,aboveData:true},lines:{show:true,fill:1,fillcolor:false},series:{stack:true},legend:{container:$('#LegendFreq')},yaxis:{tickDecimals:0,tickFormatter:function (val, axis) {
    return val.toFixed(axis.tickDecimals) +' %%'}}});               
$.plot($("#WordFreq"),     %(JSon:Word|1)s ,{grid:{show:true,aboveData:true},lines:{show:true,fill:1,fillcolor:false},series:{stack:true},legend:{show:false},yaxis:{tickDecimals:0,tickFormatter:function (val, axis) {
    return val.toFixed(axis.tickDecimals) +' %%'}}});  
$.plot($("#KanjiJouyou"), %(JSon:Kanji|2)s ,{grid:{show:true,aboveData:true},lines:{show:true,fill:1,fillcolor:false},series:{stack:true},legend:{container:$('#LegendJouyou'),noColumns:8}});
$.plot($("#KanjiKanken"), %(JSon:Kanji|3)s ,{grid:{show:true,aboveData:true},lines:{show:true,fill:1,fillcolor:false},series:{stack:true},legend:{container:$('#LegendKanken'),noColumns:13}});
 
            
               
               
});
</script> 
</head>
<body>

<div style="text-align:center;float:left;margin-left:10px;"><strong>JLPT KANJI COUNT</strong><div id="KanjiJLPT" style="width:500px;height:250px;">JLPT KANJI COUNT</div></div>
<div style="text-align:center;float:right;margin-right:10px;"><strong>JLPT WORD COUNT</strong><div id="WordJLPT" style="width:500px;height:250px;">JLPT WORD COUNT</div></div>


<div style="width:100px;height:200px;margin:0 auto;padding:20px;padding-top:70px;text-align:center;"><strong>JLPT</strong>
<div id="LegendJLPT" align="center" style="width:100px;height:140px;padding-top:10px;">JLPT Legend</div></div>

<div style="clear:both;height:30px"/></div>

<div style="text-align:center;float:left;clear:left;margin-left:10px;"><strong>KANJI Accumulated Frequency</strong><div id="KanjiFreq" style="width:500px;height:250px;"></div></div>
<div style="text-align:center;float:right;clear:right;margin-right:10px;"><strong>WORDS Accumulated Frequency</strong><div id="WordFreq" style="width:500px;height:250px;"></div></div>

<div style="width:100px;height:200px;margin:0 auto;padding:20px;text-align:center;margin-top:40px;"><strong>FREQUENCY</strong>
<div id="LegendFreq" align="center" style="width:100px;height:140px;padding-top:10px;">Frequency Legend</div></div>

<div style="clear:both;height:30px"/></div>

<div style="width:500px;text-align:center;float:left;clear:left;margin-left:30px;"><strong>JOUYOU</strong>
<div id="LegendJouyou" align="center" style="width:360px;margin:0 auto;text-align:center;">Jouyou Legend</div>
<div id="KanjiJouyou" style="width:500px;height:250px;margin:0 auto;"></div></div>

<div style="width:500px;text-align:center;float:right;clear:right;margin-right:30px;"><strong>KANKEN</strong>
<div id="LegendKanken" align="center" style="width:460px;margin: 0 auto;text-align:center;">Kanken Legend</div>
<div id="KanjiKanken" style="width:500px;height:250px;margin:0 auto;"></div></div>


          </body></html>                 
                    
                    """% (dict([('JSon:'+Type+'|'+str(k),"[" + ",".join(['{ label: "'+ String +'",data :'+ JxGraphsJSon[(Type,k,Key)] +'}' for (Key,String) in (reversed(Map.Order+[('Other','Other')]))]) +"]") for (Type,List) in JxStatsMap.iteritems() for (k,Map) in enumerate(List)]))
        JxProfile("JxGraphs().Substitute done")
        JxPreview.setHtml(JxHtml ,JxResourcesUrl)
        JxProfile("JxGraphs().Preview.SetHtml")
        JxPreview.show()  
        JxProfile("JxGraphs().Show()")
        #global debug
        #mw.help.showText(JxShowProfile()+debug)





	
	
	
	
	
	
	
