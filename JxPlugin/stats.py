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
	
