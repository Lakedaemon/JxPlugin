# -*- coding: utf-8 -*-
# Copyright: Olivier Binda <olivier.binda@wanadoo.fr>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
# ---------------------------------------------------------------------------
# This file is a plugin for the "anki" flashcard application http://repose.cx/anki/
# ---------------------------------------------------------------------------
from os import path
from ankiqt import mw
from ankiqt.ui.utils import getSaveFile, askUser

######################################################################
#
#                      JxStats : Stats
#
######################################################################

def ComputeCount(Dict,Query): 
	"""compute and Display an HTML report of the result of a Query against a Map"""
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

def SeenHtml(Map,Query):
	Dict=Map["Dict"]
	Seen = {}
	Color = {0:True}
	Buffer = {0:u""}
	for value in Dict.values():
		Buffer[value] = u""
		Color[value] = True	
	for (Stuff,Id) in mw.deck.s.all(Query):
		if Stuff not in Seen:
			try: 
				value = Dict[Stuff]	  
			except KeyError:
				value = 0
			Seen[Stuff] = 0
			Color[value] = not(Color[value])			
			if Color[value]:
				Buffer[value] += u"""<a style="text-decoration:none;color:black;" href=py:JxAddo(u"%(Stuff)s",u"%(Id)s")>%(Stuff)s</a>""" % {"Stuff":Stuff,"Id":Id}
			else:
				Buffer[value] += u"""<a style="text-decoration:none;color:blue;" href=py:JxAddo(u"%(Stuff)s",u"%(Id)s")>%(Stuff)s</a>""" % {"Stuff":Stuff,"Id":Id}
	HtmlBuffer = ""
	for key, string in Buffer.iteritems():
		if key == 0:
			HtmlBuffer += u"""<h2  align="center">Other</h2><p><font size=+2>%s</font></p>""" % string
		else:
			HtmlBuffer += u"""<h2  align="center">%s</h2><p><font size=+2>%s</font></p>""" % (Map["Legend"][key],string)
	return HtmlBuffer

def MissingHtml(Map,Query):
	Dict=Map["Dict"]
	Seen = {}
	for Stuff in mw.deck.s.column0(Query):
		Seen[Stuff] = 0
		
	Color = {0:True}
	Buffer = {0:""}
	for value in Dict.values():
		Buffer[value] = u""
		Color[value] = True	
	for Stuff,Note in Dict.iteritems():
		if Stuff not in Seen:
			Color[Note] = not(Color[Note])			
			if Color[Note]:
				Buffer[Note] += u"""<a style="text-decoration:none;color:black;" href=py:JxDoNothing(u"%(Stuff)s")>%(Stuff)s</a>""" % {"Stuff":Stuff}
			else:
				Buffer[Note] += u"""<a style="text-decoration:none;color:blue;" href=py:JxDoNothing(u"%(Stuff)s")>%(Stuff)s</a>""" % {"Stuff":Stuff}
	HtmlBuffer = u""
	for key, string in Buffer.iteritems():
		if key != 0:
			HtmlBuffer += u"""<h2  align="center">%s</h2><p><font size=+2>%s</font></p>""" % (Map[u"Legend"][key],string)
	return HtmlBuffer	
	
User = []

def JxDoNothing(Stuff):
	pass

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
		JxHtml += u"""<li style="display:inline;"><a style="color:black;text-decoration:none;"  href=Jx:JxRemove(u'%(Entry)s',u'%(Id)s')>%(Entry)s</a></li>""" % {"Entry":Entry,"Id":Id}
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
	
