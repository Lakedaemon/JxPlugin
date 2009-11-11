# -*- coding: utf-8 -*-
# Copyright: Olivier Binda <olivier.binda@wanadoo.fr>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
# ---------------------------------------------------------------------------
# This file is a plugin for the "anki" flashcard application http://ichi2.net/anki/
# ---------------------------------------------------------------------------
#from time import time
from os import path

from ankiqt import mw
from ankiqt.ui.utils import getSaveFile, askUser

#### global

User = []


####  Export partitions stuff

def JxDoNothing(Stuff):
	pass

def JxAddo(myType,atom):
    if (myType,atom) not in User:
	User.append((myType,atom))
    JxShow()

def JxClear():
    User[0:] = []
    JxShow()

def JxRemove(myType,atom):
    User.remove((myType,atom))
    JxShow()
	
def JxShow():
	JxHtml = u"""<style> li {font-size:x-large;}</style>
	<center><a href=py:Clear>Clear</a>&nbsp;&nbsp;<a href=py:Export2csv>Export (.csv)</a>&nbsp;&nbsp;<a href=py:Export2Anki>Export (.anki)</a></center>
	<ol>"""	
	for (myType,atom) in User:
		JxHtml += u"""<li style="display:inline;"><a style="color:black;text-decoration:none;"  href=Jx:JxRemove(u'%(Type)s','%(Atom)s')>%(Atom)s</a></li>""" % {"Type":myType,"Atom":atom}
	JxHtml += u"""</ol>"""
	py = {u"Export2csv":JxExport2csv,u"Export2Anki":JxExport2Anki,u"Clear":JxClear}
	mw.help.showText(JxHtml,py)

def JxExport2csv():
	JxPath = unicode(getSaveFile(mw,  _("Choose file to export to"), "","Tab separated text file (.csv)", ".csv"))
	if not JxPath:
		return
	if not JxPath.lower().endswith(".csv"):
		JxPath += ".csv"
	if path.exists(JxPath):
		# check for existence after extension
		if not askUser("This file exists. Are you sure you want to overwrite it?"):
		       return
	Ids=[]
	from database import eDeck
	for (myType,atom) in User:
	    try:
	        Ids.extend(eDeck.atoms[myType][atom].keys())
	    except:
	        pass
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
		if not askUser("This file exists. Are you sure you want to overwrite it?"):
		       return
	Ids=[]
	from database import eDeck
	for (myType,atom) in User:
	    try:
	        Ids.extend(eDeck.atoms[myType][atom].keys())
	    except:
	        pass
	from anki.exporting import AnkiExporter
	JxExport = AnkiExporter(mw.deck)
	JxExport.limitCardIds = Ids
	JxExport.exportInto(JxPath)
	
