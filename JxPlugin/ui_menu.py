# -*- coding: utf-8 -*-
# Copyright: Olivier Binda <olivier.binda@wanadoo.fr>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
# ---------------------------------------------------------------------------
# This file is a plugin for the "anki" flashcard application http://ichi2.net/anki/
# ---------------------------------------------------------------------------
from string import upper
import itertools

from ankiqt import mw

import globalobjects
from loaddata import *
from answer import *
from stats import *
from tools import *
import jmdic
#import kanjidic


JxResourcesUrl = QUrl.fromLocalFile(os.path.join(mw.config.configPath, "plugins","JxPlugin","Resources") + os.sep)

JxStatsMenu ={
'JLPT':[('Kanji',HtmlReport,('Kanji',0)),('Words',HtmlReport,('Word',0))],
'Frequency':[('Kanji',HtmlReport,('Kanji',2)),('Kanji',JxWidgetAccumulatedReport,('Kanji',1)),('Word',HtmlReport,('Word',2)),
('Words',JxWidgetAccumulatedReport,('Word',1))],
'Kanken':[('Kanji',HtmlReport,('Kanji',4))],
'Jouyou':[('Kanji',HtmlReport,('Kanji',3))]}


def onClick(url):
        String = unicode(url.toString())
	if String.startswith("py:"):
	        String = String[3:]
	        eval(String)
	else:
	        from PyQt4.QtGui import QDesktopServices
	        QDesktopServices.openUrl(QUrl(url))	

def JxHelp():
        from html import Jx_Html_HelpAutomaticMapping
        JxPreview.setHtml(Jx_Html_HelpAutomaticMapping,JxResourcesUrl)
        JxPreview.activateWindow()
        JxPreview.show()


def JxStats(Type):
        JxHtml=""
	for (Title,Func,Couple) in JxStatsMenu[Type]:
	        if Func == HtmlReport:
	                JxHtml += '<br/><center><b style="font-size:1.4em;">' + Title.upper() + "</b></center>"
	                JxHtml += """<center>
	                <a href=py:JxShowIn('""" + Couple[0] + "'," + str(Couple[1]) +  """,'Known')>Known</a>&nbsp;&nbsp;
	                <a href=py:JxShowIn('""" + Couple[0] + "'," + str(Couple[1]) +  """,'Seen')>Seen</a>&nbsp;&nbsp;
	                <a href=py:JxShowIn('""" + Couple[0] + "'," + str(Couple[1]) +  """,'InDeck')>Deck</a>&nbsp;&nbsp;
	                <a href=py:JxShowOut('""" + Couple[0] + "'," + str(Couple[1])+ """)>Missing</a>
	                </center><br/>"""
                JxHtml += Func(Couple[0],Couple[1])
        return JxHtml





def JxShowIn(Type,k,Label):
        Map = JxStatsMap[Type][k]
        Dict = None
        if Type == 'Kanji':
                Dict = Jx_Kanji_Occurences
        elif Type == 'Word':
                Dict = Jx_Word_Occurences
        if Dict:
                for (Key,String) in Map.Order + [('Other','Other')]: 
                        JxPartitionLists[(Type,k,Key,Label)].sort(lambda x,y:JxVal(Dict,y[0])-JxVal(Dict,x[0]))
        from html import Jx_Html_DisplayStuff
        JxHtml = Jx_Html_DisplayStuff + JxShowPartition(Type,k,Label)+ """</body></html>"""
        JxPreview.setHtml(JxHtml,JxResourcesUrl)
        JxPreview.activateWindow()
        JxPreview.setWindowTitle("Cards Report")
        JxPreview.show()
        
	
def JxShowOut(Type,k):
        Map = JxStatsMap[Type][k]
        Dict = None
        if Type == 'Kanji':
                Dict = Jx_Kanji_Occurences
        elif Type == 'Word':
                Dict = Jx_Word_Occurences
        for (Key,String) in Map.Order: 
                Done =  [Stuff for Label in ['Known','Seen','InDeck'] for (Stuff,Value) in JxPartitionLists[(Type,k,Key,Label)]]
                JxPartitionLists[(Type,k,Key,'Missing')] = [Stuff for (Stuff,Value) in Map.Dict.iteritems() if Value == Key and Stuff not in Done]
                if Dict:               
                        JxPartitionLists[(Type,k,Key,'Missing')].sort(lambda x,y:JxVal(Dict,y)-JxVal(Dict,x))
        from html import Jx_Html_DisplayStuff
        JxHtml = Jx_Html_DisplayStuff + JxShowMissingPartition(Type,k) + """</body></html>"""
        JxPreview.setHtml(JxHtml,JxResourcesUrl)
        JxPreview.activateWindow()
        JxPreview.setWindowTitle("Cards Report")
        JxPreview.show()  
		
from controls import Jx_Control_Tags       

                



def onJxMenu():
        from graphs import JxParseFacts4Stats
        JxParseFacts4Stats() 
        ComputeCount()        
        Jx_Control_Tags.Update()
        from html import Jx_Html_Menu
	JxHtml = Template(Jx_Html_Menu).safe_substitute({'JLPT':JxStats('JLPT'),'Frequency':JxStats('Frequency'),'Kanken':JxStats('Kanken'),
                'Jouyou':JxStats('Jouyou')})
        JxWindow.setHtml(JxHtml,JxResourcesUrl)
        JxWindow.show()







def JxBrowse():
	from controls import Jx__Model_CardModel_String	
	JxAnswerSettings = Jx__Model_CardModel_String("JxAnswerSettings")
	JxPreview.page().mainFrame().addToJavaScriptWindowObject("JxAnswerSettings",JxAnswerSettings)	
	JxPreview.setWindowTitle(u"Css and Template Browser")
        from html import Jx_Html_Preview
	JxPreview.setHtml(Jx_Html_Preview,JxResourcesUrl)
	JxPreview.activateWindow()
	JxPreview.show()

def onJxGraphs():
        from graphs import JxParseFacts4Stats, JxNewAlgorythm
        if not CardId2Types:
                JxParseFacts4Stats() 
        JxGraphsJSon =JxNewAlgorythm()
        from html import Jx_Html_Graphs
        JxHtml = Jx_Html_Graphs % (dict([('JSon:'+Type+'|'+str(k),"[" + ",".join(['{ label: "'+ String +'",data :'+ JxGraphsJSon[(Type,k,Key)] +'}' for (Key,String) in (reversed(Map.Order+[('Other','Other')]))]) +"]") for (Type,List) in JxStatsMap.iteritems() for (k,Map) in enumerate(List)]))
        JxPreview.setHtml(JxHtml ,JxResourcesUrl)
        JxPreview.setWindowTitle(u"Japanese related Graphs")
        JxPreview.activateWindow()
        JxPreview.show() 




def init_JxPlugin():
        """Initialises the Anki GUI to present an option to invoke the plugin."""
        from PyQt4 import QtGui, QtCore

	# put JxWindow at the left of the main window
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
	mw.mainWin.actionJxMenu.setStatusTip('Stats, Tools ans Settings for Japanese')
        mw.mainWin.actionJxMenu.setEnabled(not not mw.deck)
	mw.connect(mw.mainWin.actionJxMenu, QtCore.SIGNAL('triggered()'), onJxMenu)

	# creates graph entry
	mw.mainWin.actionJxGraphs = QtGui.QAction('JxGraphs', mw)
	mw.mainWin.actionJxGraphs.setStatusTip('Graphs for Japanese')
	mw.mainWin.actionJxGraphs.setEnabled(not not mw.deck)
	mw.connect(mw.mainWin.actionJxGraphs, QtCore.SIGNAL('triggered()'), onJxGraphs)

	# adds the plugin icons in the Anki Toolbar
	
	mw.mainWin.toolBar.addAction(mw.mainWin.actionJxMenu)
	mw.mainWin.toolBar.addAction(mw.mainWin.actionJxGraphs)
	
	# to enable or disable Jstats whenever a deck is opened/closed
	mw.deckRelatedMenuItems = mw.deckRelatedMenuItems + ("JxMenu","JxGraphs",)
	
	# Ading features through hooks !
	mw.addHook('drawAnswer', append_JxPlugin) # additional info in answer cards
	mw.addHook('deckClosed', JxWindow.hide) # hides the main Jxplugin window when the current deck is closed	

# adds JxPlugin to the list of plugin to process in Anki 
mw.addHook('init', init_JxPlugin)
mw.registerPlugin("Japanese Extended Support", 666)
print 'Japanese Extended Plugin loaded'

 
# The main JxPlugin Windows # funny, you cannot import stuff after these statements
from controls import JxWindow
from controls import JxPreview        
        
        
        
        
        

	
