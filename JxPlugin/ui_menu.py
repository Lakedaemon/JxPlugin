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
#import jmdic
#import kanjidic


JxResourcesUrl = QUrl.fromLocalFile(os.path.join(mw.config.configPath, "plugins","JxPlugin","Resources") + os.sep)

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

from database import display_stats, display_astats
JxStatsMenu ={
'JLPT':[('Kanji',display_stats,'K-JLPT'),('Words',display_stats,'W-JLPT')],
'Frequency':[('Kanji',display_stats,'K-Freq'),('Kanji',display_astats,'K-AFreq'),('Word',display_stats,'W-Freq'),
('Words',display_astats,'W-AFreq')],
'Kanken':[('Kanji',display_stats,'Kanken')],
'Jouyou':[('Kanji',display_stats,'Jouyou')]}

def JxStats(Type):
        html=""
	for (title,func,stat) in JxStatsMenu[Type]:
	        if func == display_stats:
	                html += '<br/><center><b style="font-size:1.4em;">' + title.upper() + "</b></center>"
	                html += """<center>
	                <a href=py:JxShowIn('""" + stat +  """',1)>Known</a>&nbsp;&nbsp;
	                <a href=py:JxShowIn('""" + stat +  """',0)>Seen</a>&nbsp;&nbsp;
	                <a href=py:JxShowIn('""" + stat +  """',-1)>Deck</a>&nbsp;&nbsp;
	                <a href=py:JxShowOut('""" + stat + """')>Missing</a>
	                </center><br/>"""
                html += func(stat)
        return html




def JxShowIn(stat,label):
    from database import display_partition
    from html import Jx_Html_DisplayStuff
    html = Jx_Html_DisplayStuff + display_partition(stat,label)+ """</body></html>"""
    JxPreview.setHtml(html,JxResourcesUrl)
    JxPreview.activateWindow()
    JxPreview.setWindowTitle("Facts Report")
    JxPreview.show()
        
	
def JxShowOut(stat):
    from database import display_complement
    from html import Jx_Html_DisplayStuff
    html = Jx_Html_DisplayStuff + display_complement(stat)+ """</body></html>"""
    JxPreview.setHtml(html,JxResourcesUrl)
    JxPreview.activateWindow()
    JxPreview.setWindowTitle("Facts Report")
    JxPreview.show()
		
from controls import Jx_Control_Tags       

                
  
def onJxMenu():
    from database import jxdeck
    jxdeck.update()
    #build_JxDeck()
    Jx_Control_Tags.Update()
    from html import Jx_Html_Menu
    JxHtml = Template(Jx_Html_Menu).safe_substitute({'JLPT':JxStats('JLPT'),'Frequency':JxStats('Frequency'),'Kanken':JxStats('Kanken'), 'Jouyou':JxStats('Jouyou')})
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
    from database import JxGraphs_into_json
    JxGraphsJSon = JxGraphs_into_json()
    from html import Jx_Html_Graphs
    tasks = {'W-JLPT':MapJLPTTango, 'K-JLPT':MapJLPTKanji, 'Jouyou':MapJouyouKanji, 'Kanken':MapKankenKanji} 
    dic = dict([('JSon:' + graph,"[" + ",".join(['{ label: "'+ string +'",data :'+ JxGraphsJSon[(graph,key)] +'}' for (key,string) in (reversed(mapping.Order+[('Other','Other')]))]) +"]") for (graph,mapping) in tasks.iteritems()])
    tasks = {'W-AFreq':MapZoneTango, 'K-AFreq':MapZoneKanji}
    dic.update([('JSon:' + graph,"[" + ",".join(['{ label: "'+ string +'",data :'+ JxGraphsJSon[(graph,key)] +'}' for (key,string) in (reversed(mapping.Order))]) +"]") for (graph,mapping) in tasks.iteritems()])
    JxHtml = Jx_Html_Graphs % dic
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
	
	# Adding features through hooks !
	mw.addHook('drawAnswer', append_JxPlugin) # additional info in answer cards
	mw.addHook('deckClosed', JxWindow.hide) # hides the main Jxplugin window when the current deck is closed	

# adds JxPlugin to the list of plugin to process in Anki 
mw.addHook('init', init_JxPlugin)
mw.registerPlugin("Japanese Extended Support", 666)

# let's overload the loadDeck function as there isn't any hook
oldLoadDeck = mw.loadDeck

def newLoadDeck(deckPath, sync=True, interactive=True, uprecent=True,media=None):
    code = oldLoadDeck(deckPath, sync, interactive, uprecent,media)
    if code and mw.deck:
        from database import build_JxDeck
        build_JxDeck()
    return code

mw.loadDeck = newLoadDeck
# The main JxPlugin Windows # funny, you cannot import stuff after these statements
from controls import JxWindow
from controls import JxPreview        


# make sure there is Cache and User directories
def ensure_dir_exists(dir):
    """creates a dir subdirectory of plugins/JxPlugin/ if it doesn't exist"""
    path = os.path.join(mw.config.configPath, "plugins","JxPlugin",dir)
    if not(os.path.isdir(path)):
        try:
            os.mkdir(path)
        except OSError:
            # big troubles ahead... raise an error message
            pass
            from ankiqt.ui.utils import showWarning
            showWarning("Couldn't create the '" + dir + "' directory.")

map(ensure_dir_exists,['User','Cache'])
        
        

	
