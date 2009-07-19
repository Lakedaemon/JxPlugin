# -*- coding: utf-8 -*-
# Copyright: Olivier Binda <olivier.binda@wanadoo.fr>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
# ---------------------------------------------------------------------------
# This file is a plugin for the "anki" flashcard application http://repose.cx/anki/
# ---------------------------------------------------------------------------
from string import upper

from PyQt4 import QtGui, QtCore
from PyQt4.QtWebKit import QWebPage, QWebView

from ankiqt import mw, ui

from loaddata import *
from answer import *
from stats import *
from ui_graphs import *
from tools import *


JxMenu = """ 
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN">
<html>
<head>
<title>JxPlugin Main Menu</title>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<link rel="stylesheet" type="text/css" href="ui.dropdownchecklist.css" /> 
<link rel="stylesheet" type="text/css" href="demo.css" /> 
<script type="text/javascript" src="jquery.js"></script> 
<script type="text/javascript" src="ui.core.js"></script> 
<script type="text/javascript" src="ui.dropdownchecklist.js"></script> 
<script type="text/javascript"> 
        $(document).ready(function(){
	$("#s1").dropdownchecklist({ firstItemChecksAll: true,width:100});
        });
</script> 
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

QueryKanji = """select fields.value from facts,cards,fields,fieldModels, models where 
		cards.factId = facts.id  and facts.id = fields.factId and fields.fieldModelId = fieldModels.id and facts.modelId = models.id and 
		fieldModels.name = "Kanji" and models.tags like "%Kanji%" and cards.reps > 0 order by firstAnswered"""
QueryKanjib = """select fields.value,cards.id from facts,cards,fields,fieldModels, models where 
		cards.factId = facts.id  and facts.id = fields.factId and fields.fieldModelId = fieldModels.id and facts.modelId = models.id and 
		fieldModels.name = "Kanji" and models.tags like "%Kanji%" and cards.reps > 0 group by fields.value order by firstAnswered """
		
QueryTango = """select fields.value from facts,cards,fields,fieldModels, models where 
		cards.factId = facts.id  and facts.id = fields.factId and fields.fieldModelId = fieldModels.id and facts.modelId = models.id and 
		fieldModels.name = "Expression" and models.tags like "%Japanese%" and cards.reps > 0 order by firstAnswered"""

QueryTangob = """select fields.value, cards.id from facts,cards,fields,fieldModels, models where 
		cards.factId = facts.id  and facts.id = fields.factId and fields.fieldModelId = fieldModels.id and facts.modelId = models.id and 
		fieldModels.name = "Expression" and models.tags like "%Japanese%" and cards.reps > 0 group by fields.value order by firstAnswered"""
		
def JxGraphs():
	ui.dialogs.get("JxGraphs", mw, mw.deck)



JxResourcesUrl = QUrl.fromLocalFile(os.path.join(mw.config.configPath, "plugins","JxPlugin","Resources")+os.sep)

def JxTools():
	FieldsBuffer = u""
	FieldsBuffer +=  u"""<optgroup label="Models">"""
	FieldsBuffer +=  u"""<option selected="selected">All</option>"""

	Rows = mw.deck.s.all(u"""select name, id from models order by name""")
	mw.help.showText(str(Rows))
	for (Name, Id) in Rows:
		FieldsBuffer +=  u"""<option id="%(Id)s" selected="selected">%(Name)s</option> """ % {"Name":Name,"Id":Id}
	FieldsBuffer +=  u"""</optgroup>"""
	FieldsBuffer +=  u"""<optgroup label="Fields">"""
	Rows = mw.deck.s.all(u"""select name, id from fieldModels order by name""")
	mw.help.showText(str(Rows))
	for (Name, Id) in Rows:
		FieldsBuffer +=  u"""<option id="%(Id)s" selected="selected">%(Name)s</option> """ % {"Name":Name,"Id":Id}
	FieldsBuffer +=  u"""</optgroup>"""
	JxHtml = u"""<br /><p>Adds a tag to redundant entries among entries that share the following fields AND models 
	<span style="vertical-align:middle;"><select style="display:inline;" id="s1" multiple="multiple"> 
%s
        </select></span>    <p> 
        <select id="s6" multiple="multiple"> 
			<optgroup label="Letters"> 
				<option>A</option> 
				<option>B</option> 
				<option selected="selected">C</option> 
			</optgroup> 
            <optgroup label="Numbers"> 
				<option>1</option> 
				<option>2</option> 
				<option selected="selected">3</option> 
			</optgroup> 
        </select> 
    </p> 
	<ul><li>the younger redundant entries get the "JxDuplicate" tag</li><li>the oldest redundant entry gets the "JxMasterDuplicate" tag</li></ul></p><center><a href=py:JxTagDuplicates()>Tag Duplicates</a></center>
	<h1>Python Web Plugin Test</h1><div style="text-align:center;">
	<object type="x-pyqt/widget" width="100" height="20"></object></div>
	<p>This is a Web plugin written in Python.</p><p><code> 
            $("#s1").dropdownchecklist();
        </code>  </p><p>     </p>  """ % FieldsBuffer
	
	Dict = {"JLPT":'',"Jouyou":'',"Zone":'',"Tools":'',"Content":JxHtml}
	Dict["Tools"] = 'id="active"'
	JxPage = Template(JxMenu).safe_substitute(Dict)
	JxWindow.setHtml(JxPage,JxResourcesUrl)

	
JxMap={"Kanji2JLPT":MapJLPTKanji,"Tango2JLPT":MapJLPTTango,"Kanji2Jouyou":MapJouyouKanji,
"Kanji2Zone":MapZoneKanji,"Tango2Zone":MapZoneTango}

def JxStats(Type):
	
	JxHtml = """<br/><center><b style="font-size:1.4em;">KANJI</b></center>"""
	JxHtml += """<center><a href=py:JxMissing('""" + Type + """','Kanji')>Missing</a>&nbsp;&nbsp;<a href=py:JxSeen('""" + Type +  """','Kanji')>Seen</a></center><br/>"""
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

JxQuery={"Kanji":QueryKanji,"Tango":QueryTango,"Kanjib":QueryKanjib,"Tangob":QueryTangob}


def JxMissing(Type,Set):
	JxHtml = Template("""<br /><center><b style="font-size:1.4em;">MISSING ${CAPSET}</b></center><center><a href=py:JxSeen("${Type}","${Set}")>Seen</a>&nbsp;<a href=py:JxStats("${Type}")>Stats</a></center>""").substitute(Type=Type,Set=Set,CAPSET=upper(Set)) 
	JxHtml += MissingHtml(JxMap[Set+"2"+Type],JxQuery[Set])
	
	Dict = {"JLPT":'',"Jouyou":'',"Zone":'',"Tools":'',"Content":JxHtml}
	Dict[Type] = 'id="active"'
	JxPage = Template(JxMenu).safe_substitute(Dict)
	
	JxWindow.setHtml(JxPage)

def JxSeen(Type,Set):
	JxHtml = Template("""<br /><center><b style="font-size:1.4em;">SEEN ${CAPSET}</b></center><center><a href=py:JxMissing("${Type}","${Set}")>Missing</a>&nbsp;<a href=py:JxStats("${Type}")>Stats</a></center>""").substitute(Type=Type,Set=Set,CAPSET=upper(Set)) 
	JxHtml += SeenHtml(JxMap[Set+"2"+Type],JxQuery[Set+"b"])
	
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
JxWindow.page().setLinkDelegationPolicy(QWebPage.DelegateAllLinks)
mw.connect(JxWindow, QtCore.SIGNAL('linkClicked (const QUrl&)'), onClick)

JxWindow.hide()



import sys
from PyQt4.QtCore import QSize, Qt
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *
class WebWidget(QWidget):

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setBrush(Qt.white)
        painter.setPen(Qt.black)
        painter.drawRect(self.rect().adjusted(0, 0, -1, -1))
        painter.setBrush(Qt.red)
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.width()/4, self.height()/4,
                         self.width()/2, self.height()/2)
        painter.end()
    
    def sizeHint(self):
        return QSize(100, 100)
	
def onJxMenu():
	JxStats('JLPT')

class WebPluginFactory(QWebPluginFactory):

    def __init__(self, parent = None):
        QWebPluginFactory.__init__(self, parent)
    
    def create(self, mimeType, url, names, values):
        if mimeType == "x-pyqt/widget":
            return JxField()
    
    def plugins(self):
        plugin = QWebPluginFactory.Plugin()
        plugin.name = "PyQt Widget"
        plugin.description = "An example Web plugin written with PyQt."
        mimeType = QWebPluginFactory.MimeType()
        mimeType.name = "x-pyqt/widget"
        mimeType.description = "PyQt widget"
        mimeType.fileExtensions = []
        plugin.mimeTypes = [mimeType]
        print "plugins"
        return [plugin]
	
class JxFieldb(QComboBox):
    def __init__(self, parent = None):
        QComboBox.__init__(self, parent)
        Rows = mw.deck.s.all(u"""select name, id from models""")
        self.SizeAdjustPolicy(QComboBox.AdjustToContents)
        for (Name, Id) in Rows:
		self.addItem(Name)
        self.show()
	
class JxField(QMenuBar):	
    def __init__(self, parent = None):
	QMenuBar.__init__(self, parent)
	Menu = QMenu("Fields",self)

	Rows = mw.deck.s.all(u"""select name, id from models""")
	for (Name, Id) in Rows:
              Menu.addAction(Name)
	self.addMenu(Menu)
	self.show()





QWebSettings.globalSettings().setAttribute(QWebSettings.JavascriptEnabled, True)
# with this you can enable QWidget inside a QWebView
QWebSettings.globalSettings().setAttribute(QWebSettings.PluginsEnabled, True)
factory = WebPluginFactory()
JxWindow.page().setPluginFactory(factory)	



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

mw.addHook('init', init_JxPlugin)
mw.registerPlugin("Japanese Extended Support", 666)
print 'Japanese Extended Plugin loaded'
