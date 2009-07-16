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
#import ankiqt.forms

from ui.utils import showText

from ankiqt.ui.utils import saveGeom, restoreGeom

	
	
	
	
	
	
######################################################################
#
#                                             Tools
#
######################################################################



from tools import *
from anki.utils import canonifyTags, addTags
	

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





from PyQt4.QtWebKit import QWebPage, QWebView
from PyQt4 import QtWebKit

from string import Template



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







from loaddata import *
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
<li><a href=py:JxGraphs()>Graphs</a></li>
<li ${Tools}><a href=py:JxTools()>Tools</a></li>
</ul>
</div>
<div id="content" style="clear:both;">${Content}</div>
</body>
</html>
""".decode('utf-8')

def JxTools():
	JxHtml = """<br /><p>Adds a tag to redundant entries for the field "Expression" in the "Japanese" model of the current deck : <ul><li>the younger redundant entries get the "JxDuplicate" tag</li><li>the oldest redundant entry gets the "JxMasterDuplicate" tag</li></ul></p><center><a href=py:JxTagDuplicates()>Tag Duplicates</a></center>""" 
	
	Dict = {"JLPT":'',"Jouyou":'',"Zone":'',"Tools":'',"Content":JxHtml}
	Dict["Tools"] = 'id="active"'
	JxPage = Template(JxMenu).safe_substitute(Dict)
	
	JxWindow.setHtml(JxPage)

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
	mw.mainWin.actionJxMenu = QtGui.QAction('JxMenu', mw)
	mw.mainWin.actionJxMenu.setStatusTip('Menuol')
	mw.mainWin.actionJxMenu.setEnabled(False)
	mw.connect(mw.mainWin.actionJxMenu, QtCore.SIGNAL('triggered()'), onJxMenu)

	# creates menu in the plugin sub menu
	#mw.mainWin.pluginMenu = mw.mainWin.menubar.addMenu('&JPlugin')
	#mw.mainWin.pluginMenu.addAction(mw.mainWin.actionJStats)

	#mw.mainWin.actionJStats.setShortcut(_("Ctrl+J"))


	# adds the plugin icon in the Anki Toolbar
	
	mw.mainWin.toolBar.addAction(mw.mainWin.actionJxMenu)
	
	# to enable or disable Jstats whenever a deck is opened/closed
	mw.deckRelatedMenuItems = mw.deckRelatedMenuItems + ("JxMenu",)
	
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

