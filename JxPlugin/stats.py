# -*- coding: utf-8 -*-
# Copyright: Olivier Binda <olivier.binda@wanadoo.fr>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
# ---------------------------------------------------------------------------
# This file is a plugin for the "anki" flashcard application http://ichi2.net/anki/
# ---------------------------------------------------------------------------
from time import time
from os import path
from ankiqt import mw
#from ankiqt.ui.utils import getSaveFile, askUser
from answer import Tango2Dic
from loaddata import *
from graphs import CardId2Types
from globalobjects import JxStatsMap
from cache import load_cache, save_cache
######################################################################
#
#                      JxStats : Stats
#
######################################################################
        
JxStatsArray = {}
JxPartitionLists = {}
def ComputeCount(): 
        global JxStatsArray,JxPartitionLists,NoType
        Rows = mw.deck.s.all("""select cards.factId,cards.id,cards.reps,cards.Interval from cards order by cards.factId""")  
        # we can compute known/seen/in deck/total stats for each value of each map depending of the type
        NoType = 0 # known/seen/in deck
        CardState = []
        for (Type,List) in JxStatsMap.iteritems():
                for (k, Map) in enumerate(List):
                        for (Key,String) in Map.Order+[('Other','Other')]:
                                if k != 1:
                                        JxStatsArray[(Type,k,Key)] = (0,0,0,len([Item for (Item,Value) in Map.Dict.iteritems() if Value == Key])) 
                                elif Type =='Word':
                                        JxStatsArray[(Type,k,Key)] = (0,0,0,sum([Jx_Word_Occurences[Item] for (Item,Value) in Map.Dict.iteritems() if Value == Key]))
                                else:
                                        JxStatsArray[(Type,k,Key)] = (0,0,0,sum([Jx_Kanji_Occurences[Item] for (Item,Value) in Map.Dict.iteritems() if Value == Key])) 
                                for Label in ['Known','Seen','InDeck']:
                                        JxPartitionLists[(Type,k,Key,Label)] = []
        Length = len(Rows)
        Index = 0
        while True:
                (FactId,CardId,CardRep,Interval) = Rows[Index]
                # set the card's status                       
                if Interval > 21 and CardRep:
                        CardState.append(0)
                elif CardRep:
                        CardState.append(1)
                else:
                        CardState.append(2)
                Index += 1
                if Index == Length: 
                        # we have finished parsing the Entries.Flush the last Fact and break
                        JxFlushFactStats(CardState,CardId)
                        break
                        # we have finished parsing the Entries, flush the Status change
                elif FactId == Rows[Index][0]:
                        # Same Fact : Though it does nothing, we put this here for speed purposes because it happens a lot.
                        pass
                else:                        
                        # Fact change
                        JxFlushFactStats(CardState,CardId)
                        CardState = []

###############################################################################
def compute_count(): 
    """Computes the stats"""
    
    global JxStatsArray,JxPartitionLists,NoType
    
    JxCache = load_cache()
    try:
        Query = """select cards.factId, cards.id, cards.reps, cards.interval from cards, 
	cards as mCards where mCards.modified>%s and cards.factId=mCards.factId 
	group by cards.id order by cards.factId""" % JxCache['TimeCached']
        JxStatsArray = JxCache['Stats']
        JxPartitionLists = JxCache['Partitions']
        NoType = JxCache['NoType']
    except:
        Query = """select factId, id, reps, interval from cards order by factId"""
        NoType = 0 # known/seen/in deck
        for (Type,List) in JxStatsMap.iteritems():
            for (k, Map) in enumerate(List):
                for (Key,String) in Map.Order+[('Other','Other')]:
                    if k != 1:
                        JxStatsArray[(Type,k,Key)] = (0, 0, 0, 
			        len([Item for (Item,Value) in Map.Dict.iteritems() if Value == Key])) 
                    elif Type =='Word':
                        JxStatsArray[(Type,k,Key)] = (0, 0, 0, sum([Jx_Word_Occurences[Item] 
				for (Item,Value) in Map.Dict.iteritems() if Value == Key]))
                    else:
                        JxStatsArray[(Type,k,Key)] = (0, 0, 0, sum([Jx_Kanji_Occurences[Item] 
			        for (Item,Value) in Map.Dict.iteritems() if Value == Key])) 
                    for Label in ['Known','Seen','InDeck']:
                        JxPartitionLists[(Type,k,Key,Label)] = []	
			
    # we compute known/seen/in deck/total stats for each value of each map and each type
    Rows = mw.deck.s.all(Query)  
    CardState = []
    Length = len(Rows)
    Index = 0
    while True and Index<Length:
        (FactId,CardId,CardRep,Interval) = Rows[Index]
        # set the card's status                       
        if Interval > 21 and CardRep:
            CardState.append(0)
        elif CardRep:
            CardState.append(1)
        else:
            CardState.append(2)
        Index += 1
        if Index == Length: 
            # we have finished parsing the Entries.Flush the last Fact and break
            JxFlushFactStats(CardState,CardId)
            break
            # we have finished parsing the Entries, flush the Status change
        elif FactId == Rows[Index][0]:
            # Same Fact : Though it does nothing, we put this here for speed purposes because it happens a lot.
            pass
        else:                        
            # Fact change
            JxFlushFactStats(CardState,CardId)
            CardState = []
	    
    # now cache the updated stats  
    JxCache['Stats'] = JxStatsArray
    JxCache['Partitions'] = JxPartitionLists
    JxCache['NoType'] = NoType
    JxCache['TimeCached'] = time() # among the few things that coul corrupt the cache : 
    # new entries in the database before the cache was saved...sigh...
    save_cache(JxCache)
			
			

def JxVal(Dict,x):
        try:
                return  Dict[x]
        except KeyError:
                return -1
  
        
def JxFlushFactStats(CardState,CardId):
        """Flush the fact stats"""
        global JxStatsArray,JxPartitionLists,JxStatsMap, NoType
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
                                                Change = Jx_Word_Occurences[Content] * CardWeight
                                        except KeyError:
                                                Change = 0
                                else:
                                        try:
                                                Change = Jx_Kanji_Occurences[Content] * CardWeight
                                        except KeyError:
                                                Change = 0 
                                # we have to update the stats of each type
                                (Known,Seen,InDeck,Total) = JxStatsArray[(Type,k,Key)] 
                                (OldKnown,OldSeen,OldInDeck) = (Known,Seen,InDeck)
############################################################################################################# upgrade this part to support "over-optimist", "optimist", "realist", "pessimist" modes                                        
                                #now, we got to flush the fact. Let's go for the realist model first
                                for State in CardState:
                                        InDeck += Change
                                        if State < 2:
                                                Seen += Change
                                        if State == 0:
                                                Known += Change
                                # save the updated list                        #### this is probably a bit slow
                                JxStatsArray[(Type,k,Key)] = (Known,Seen,InDeck,Total)
                                if (Known-OldKnown) * 2 >= InDeck-OldInDeck: #Majority
                                        JxPartitionLists[(Type,k,Key,'Known')].append((Content,CardId))
                                elif (Known-OldKnown + Seen - OldSeen) > 0: # At least once
                                        JxPartitionLists[(Type,k,Key,'Seen')].append((Content,CardId))
                                else:
                                        JxPartitionLists[(Type,k,Key,'InDeck')].append((Content,CardId))
                                        
##############################################################################################################     
        except KeyError: # this fact has no type
                NoType +=1
         


def HtmlReport(Type,k):
        global JxStatsArray
        from graphs import JxParseFacts4Stats
        Map = JxStatsMap[Type][k]
	JxStatsHtml = """<style>
	.BackgroundHeader {background-color: #eee8d4;}
	.Background {background-color: #fff9e5;}
        .JxStats td{align:center;text-align:center;}
        .JxStats tr > td:first-child,.JxStats tr > th:first-child{
        border-right:1px solid black;
        border-left:1px solid black;
        }
        .BorderRight{border-right:1px solid black;}
        .Border td,.Border th{border-top:1px solid black;border-bottom:1px solid black;}
        </style>
	<table class="JxStats" width="100%%" align="center" style="margin:0 20 0 20;border:0px solid black;" cellspacing="0px"; cellpadding="4px">
	<tr class="Border BackgroundHeader"><th><b>%s</b></th><th><b>%%</b></th><th><b>Known</b></th><th><b>Seen</b></th><th><b>Deck</b></th><th class="BorderRight"><b>Total</b></th></tr>
	""" % Map.To
        (SumKnown, SumSeen, SumInDeck, SumTotal)=(0,0,0,0)
	for (Key,Value) in Map.Order:
                (Known,Seen,InDeck,Total) = JxStatsArray[(Type,k,Key)]
                (SumKnown, SumSeen, SumInDeck, SumTotal) = (SumKnown + Known, SumSeen + Seen, SumInDeck + InDeck, SumTotal + Total)
		JxStatsHtml += """
		<tr class="Background"><td><b>%s</b></td><td><b style="font-size:small">%.0f%%</b></td><td>%.0f</td><td>%.0f</td><td>%.0f</td><td class="BorderRight">%.0f</td></tr>
		""" % (Value,Known*100.0/max(1,Total),Known,Seen,InDeck,Total)
        JxStatsHtml += """
        <tr class="Border BackgroundHeader"><td><b>%s</b></td><td><b style="font-size:small">%.0f%%</b></td><td>%.0f</td><td>%.0f</td><td>%.0f</td><td class="BorderRight">%.0f</td></tr>
		""" % ('Total',SumKnown*100.0/max(1,SumTotal),SumKnown,SumSeen,SumInDeck,SumTotal)        
        (Known,Seen,InDeck,Total) = JxStatsArray[(Type,k,'Other')]
        if (Known,Seen,InDeck,Total) != (0,0,0,0):
                JxStatsHtml += """<tr><td style="border:0px solid black;"><b>%s</b></td><td></td><td>%.0f</td><td>%.0f</td><td>%.0f</td><td></td></tr>""" % ('Other',Known,Seen,InDeck)                

        JxStatsHtml += "</table>"
        return JxStatsHtml

def JxFormat(Float):
        if Float < 0.01:                            # 0.001 -> 0
                return "0"
        if Float < 0.1:                             # 0.016 -> 0.02
                return "%.1g" % Float       
        if Float <1:                                # 0.168 -> 0.17
                return "%.2g" % Float                            
        else:                                       # 4.00 -> 4          4.10 -> 4           4.1678 -> 4.17           15.28 -> 15.3
                return "%.3g" % Float               
 
def JxWidgetAccumulatedReport(Type,k):
        global JxStatsArray
        from graphs import JxParseFacts4Stats
        Map = JxStatsMap[Type][k]
	JxStatsHtml = """<style>
	.BackgroundHeader {background-color: #817865;}
	.Background {background-color: #fece2f;}
        .JxStats td{align:center;text-align:center;}
        .JxStats tr > td:first-child,.JxStats tr > th:first-child{
        border-right:1px solid black;
        border-left:1px solid black;
        }
        .BorderRight{border-right:1px solid black;}
        .Border td,.Border th{border-top:1px solid black;border-bottom:1px solid black;}
        </style>
        <br/>
	<table class="JxStats" width="100%%" align="center" style="margin:0 20 0 20;border:0px solid black;" cellspacing="0px"; cellpadding="4px">
	<tr class="Border BackgroundHeader"><th><b>Accumulated</b></th><th><b>Known</b></th><th><b>Seen</b></th><th><b>Deck</b></th><th class="BorderRight"><b>Total</b></th></tr>
	""" 
        JxSumTotal = sum([JxStatsArray[(Type,k,Key)][3] for (Key,Value) in Map.Order])
        (SumKnown, SumSeen, SumInDeck, SumTotal)=(0,0,0,0)
	for (Key,Value) in Map.Order:
                (Known,Seen,InDeck,Total) = JxStatsArray[(Type,k,Key)]
                (SumKnown, SumSeen, SumInDeck, SumTotal) = (SumKnown + Known, SumSeen + Seen, SumInDeck + InDeck, SumTotal + Total)
		JxStatsHtml += """
		<tr class="Background"><td><b>%s</b></td><td>%s%%</td><td>%s%%</td><td>%s%%</td><td class="BorderRight">%.0f%%</td></tr>
		""" % (Value,JxFormat(Known*100.0/max(1,JxSumTotal)),JxFormat(Seen*100.0/max(1,JxSumTotal)),JxFormat(InDeck*100.0/max(1,JxSumTotal)),Total*100.0/max(1,JxSumTotal))
        JxStatsHtml += """
        <tr class="Border BackgroundHeader"><td><b>%s</b></td><td>%s%%</td><td>%s%%</td><td>%s%%</td><td class="BorderRight">%s%%</td></tr>
		""" % ('Total',JxFormat(SumKnown*100.0/max(1,JxSumTotal)),JxFormat(SumSeen*100.0/max(1,JxSumTotal)),JxFormat(SumInDeck*100.0/max(1,JxSumTotal)),100)        
        (Known,Seen,InDeck,Total) = JxStatsArray[(Type,k,'Other')]              

        JxStatsHtml += "</table>"
        return JxStatsHtml       
	
def JxShowPartition(Type,k,Label):
        global JxPartitionLists
        """Returns an Html report of the seen stuff of Type/k/Label"""
        Map = JxStatsMap[Type][k]
	Color = dict([(Key,True) for (Key,String) in Map.Order + [('Other','Other')]])
	Buffer = dict([(Key,"") for (Key,String) in Map.Order + [('Other','Other')]])
	for (Key,String) in Map.Order + [('Other','Other')]:
	        for (Stuff,Id) in JxPartitionLists[(Type,k,Key,Label)]:
			Color[Key] = not(Color[Key])			
			if Color[Key]:
				Buffer[Key] += u"""<a style="text-decoration:none;color:black;" href="py:JxAddo(u'%(Stuff)s','%(Id)s')">%(Stuff)s</a>""" % {"Stuff":Stuff,"Id":Id}
			else:
				Buffer[Key] += u"""<a style="text-decoration:none;color:blue;" href="py:JxAddo(u'%(Stuff)s','%(Id)s')">%(Stuff)s</a>""" % {"Stuff":Stuff,"Id":Id}
	HtmlBuffer = u""
	for (Key,Value) in Map.Order:
                if Buffer[Key]:
			HtmlBuffer += u"""<h2  align="center">%s</h2><p><font size=+2>%s</font></p>""" % (Value,Buffer[Key])
        if Buffer['Other']:
			HtmlBuffer += u"""<h2  align="center">Other</h2><p><font size=+2>%s</font></p>""" % Buffer['Other']
	return HtmlBuffer

def JxShowMissingPartition(Type,k):
        global JxPartitionLists
        """Returns an Html report of the seen stuff corresponding to Map and Query """
        Map = JxStatsMap[Type][k]
	Color = dict([(Key,True) for (Key,String) in Map.Order])
	Buffer = dict([(Key,"") for (Key,String) in Map.Order])
	for (Key,String) in Map.Order:
	        for Stuff in JxPartitionLists[(Type,k,Key,'Missing')]:
			Color[Key] = not(Color[Key])			
			if Color[Key]:
				Buffer[Key] += u"""<a style="text-decoration:none;color:black;" href="py:JxDoNothing(u'%(Stuff)s')">%(Stuff)s</a>""" % {"Stuff":Stuff}
			else:
				Buffer[Key] += u"""<a style="text-decoration:none;color:blue;" href="py:JxDoNothing(u'%(Stuff)s')">%(Stuff)s</a>""" % {"Stuff":Stuff}
	HtmlBuffer = u""
	for (Key,Value) in Map.Order:
                if Buffer[Key]:
			HtmlBuffer += u"""<h2  align="center">%s</h2><p><font size=+2>%s</font></p>""" % (Value,Buffer[Key])
	return HtmlBuffer
     
def JxDoNothing(Stuff):
	pass

	
	
User = []



def JxAddo(Stuff,Id):
	if (Stuff,Id) not in User:
	    User.append((Stuff,Id))
	JxShow()

def JxClear():
	User[0:] = []
	JxShow()

def JxRemove(Stuff,Id):
	User.remove((Stuff,Id))
	JxShow()
	
def JxShow():
	JxHtml = u"""<style> li {font-size:x-large;}</style>
	<center><a href=py:Clear>Clear</a>&nbsp;&nbsp;<a href=py:Export2csv>Export (.csv)</a>&nbsp;&nbsp;<a href=py:Export2Anki>Export (.anki)</a></center>
	<ol>"""	
	for (Entry,Id) in User:
		JxHtml += u"""<li style="display:inline;"><a style="color:black;text-decoration:none;"  href=Jx:JxRemove(u'%(Entry)s','%(Id)s')>%(Entry)s</a></li>""" % {"Entry":Entry,"Id":Id}
	JxHtml += u"""</ol>"""
	py = {u"Export2csv":JxExport2csv,u"Export2Anki":JxExport2Anki,u"Clear":JxClear}
	mw.help.showText(JxHtml,py)


# "hack" to overload mw.help.anchorClicked
def JxAnchorClicked(url):
        # prevent the link being handled
        mw.help.widget.setSource(QUrl(""))
        addr = unicode(url.toString())
        if addr.startswith("hide:"):
            if len(addr) > 5:
                # hide for good
                mw.help.config[addr] = True
            mw.help.hide()
            if "hide" in mw.help.handlers:
                mw.help.handlers["hide"]()
        elif addr.startswith("py:"):
            key = addr[3:]
            if key in mw.help.handlers:
                mw.help.handlers[key]()
	elif addr.startswith("Jx:"):
            key = addr[3:]
            eval(key)
        else:
            # open in browser
            QDesktopServices.openUrl(QUrl(url))
        if mw.help.focus:
            mw.help.focus.setFocus()
	    
from PyQt4.QtCore import SIGNAL, QUrl
mw.help.widget.connect(mw.help.widget, SIGNAL("anchorClicked(QUrl)"),
                            JxAnchorClicked)    


def JxExport2csv():
	JxPath = unicode(getSaveFile(mw,  _("Choose file to export to"), "","Tab separated text file (.csv)", ".csv"))
	if not JxPath:
		return
	if not JxPath.lower().endswith(".csv"):
		JxPath += ".csv"
	if path.exists(JxPath):
		# check for existence after extension
		if not ui.utils.askUser("This file exists. Are you sure you want to overwrite it?"):
		       return
	import string
#	Query = u"""select cards.id from facts,cards,fields,fieldModels, models where 
#		cards.factId = facts.id  and facts.id = fields.factId and fields.fieldModelId = fieldModels.id and facts.modelId = models.id and 
#		fieldModels.name = "Expression" and models.tags like "%%Japanese%%" and fields.value in (%s) group by cards.id""" % string.join([unicode("'" + Stuff + "',") for Stuff in User])[0:-1]

#	Ids = mw.deck.s.column0(Query)
	Ids=[]
	for (Stuff,Id) in User:
	     Ids.append(Id)
	from anki.exporting import TextFactExporter
	JxExport = TextFactExporter(mw.deck)
	JxExport.limitCardIds = Ids
	JxExport.exportInto(JxPath)
	mw.help.showText("Successfully exported " + str(len(Ids)) + " facts")
	
def JxExport2Anki():
	JxPath = unicode(getSaveFile(mw,  _("Choose file to export to"), "","Anki Deck (*.anki)", ".anki"))
	if not JxPath:
		return
	if not JxPath.lower().endswith(".anki"):
		JxPath += ".anki"
	if path.exists(JxPath):
		# check for existence after extension
		if not ui.utils.askUser("This file exists. Are you sure you want to overwrite it?"):
		       return
	import string
#	Query = u"""select cards.id from facts,cards,fields,fieldModels, models where 
#		cards.factId = facts.id  and facts.id = fields.factId and fields.fieldModelId = fieldModels.id and facts.modelId = models.id and 
#		fieldModels.name = "Expression" and models.tags like "%%Japanese%%" and fields.value in (%s) group by cards.id""" % string.join([unicode("'" + Stuff + "',") for Stuff in User])[0:-1]

#	Ids = mw.deck.s.column0(Query)
	Ids=[]
	for (Stuff,Id) in User:
	     Ids.append(Id)
	from anki.exporting import AnkiExporter
	JxExport = AnkiExporter(mw.deck)
	JxExport.limitCardIds = Ids
	JxExport.exportInto(JxPath)
	
