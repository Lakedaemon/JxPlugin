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
from metacode import *

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
<script type="text/javascript" src="jquery.jeditable.js"></script> 
<script type="text/javascript" src="Settings.js"></script>


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
        padding: 5px 8px 4px 7px;
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
<li><a href=py:JxWindow.hide()>X</a></li>
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
	FieldsBuffer +=  u"""<option id="Model" selected="selected">All</option>"""
	FieldsBuffer +=  u"""<optgroup label="Models">"""
	JxPopulateModels = []
	Rows = mw.deck.s.column0(u"""select name from models group by name order by name""")
	for Name in Rows:
		FieldsBuffer +=  u"""<option id="%(Id)s" selected="selected">%(Name)s</option> """ % {"Name":Name,"Id":u"Model."+ Name}
		JxPopulateModels.append(Name)
		
	FieldsBuffer +=  u"""</optgroup>"""
	FieldsBuffer +=  u"""<optgroup label="Fields">"""
	Rows = mw.deck.s.column0(u"""select name from fieldModels group by name order by name""")
	for Name in Rows:
		FieldsBuffer +=  u"""<option id="%(Id)s" selected="selected">%(Name)s</option> """ % {"Name":Name,"Id":u"Field."+ Name}
	FieldsBuffer +=  u"""</optgroup>"""
	JxHtml = u"""<br />
	
	<h3 style="text-align:center;">DEBUG</h3>
	<a href="py:mw.help.showText(JxBase.findChild(QObject,'Jx_Model').property('String').toString() +' et ' +  JxBase.findChild(QObject,'JxString').property('String').toString())">rahhh</a>
	
	<h3 style="text-align:center;">TAG REDUNDANT ENTRIES IN A SET</h3>
	<center>
	<span style="vertical-align:middle;"><select style="display:inline;" id="s1" multiple="multiple">%s</select></span> 
	&nbsp;&nbsp;&nbsp;<a href=py:JxTagDuplicates(JxGetInfo())>Tag them !</a>
	</center>
	<ul><li>young ones get "JxDuplicate"</li><li>the oldest one gets "JxMasterDuplicate"</li></ul>

	<h3 style="text-align:center;">ANSWER FIELDS</h3>
	<p>In the <b class="edit_Model" id="div_1"></b> deck model, the <b class="oltest"><b class="edit_CardModel" id="div_1"></b></b> card model; <b id="JxString" class="edit_Mode"></b> the answer settings with  : <center><i class="edit_DisplayString"></i></center></p>

	<h3 style="text-align:center;">AUTOMATIC MAPPING</h3>
	Your decks are using the following mappings : <b class="edit_CardTemplate"> essai </b>
	<center><table>
	<tr><th>Entry</th><th></th><th>Source Template</th><th></th><th>Target Template</th></tr>
	<tr><td class="edit_NameTemplate"></td><td>:</td><td class="edit_SourceTemplate"></td><td>&hArr;</td><td class="edit_TargetTemplate"></td></tr>
	</table></center>	
	
	 """ % FieldsBuffer
	
	Dict = {"JLPT":'',"Jouyou":'',"Zone":'',"Tools":'',"Content":JxHtml}
	Dict["Tools"] = 'id="active"'
	Dict["DeckModels"] = u"{%s}" % string.join([u"'"+ a + u"':'" + a + u"'" for a in JxPopulateModels],",")
	Dict["DeckModelselected"] = u"%s" % JxPopulateModels[0]	
	JxPage = Template(JxMenu).safe_substitute(Dict)
	

	JxAnswerSettings = Jx__Model_CardModel_String("JxAnswerSettings")
	JxWindow.page().mainFrame().addToJavaScriptWindowObject("JxAnswerSettings",JxAnswerSettings)	
#	JxWindow.page().mainFrame().evaluateJavaScript("alert(JxAnswerSettings.Fieldselected('Tango'))")	
	JxTemplateOverride = Jx__Entry_Source_Target("JxTemplateOverride")
	JxWindow.page().mainFrame().addToJavaScriptWindowObject("JxTemplateOverride",JxTemplateOverride)	
	mw.connect( JxWindow.page().mainFrame(),QtCore.SIGNAL('javaScriptWindowObjectCleared()'), Rah);


	JxWindow.setHtml(JxPage,JxResourcesUrl)
#	mw.help.showText(JxString.property("String").toString())





#
#






JxTable = {
u"Word recall":
	{"""%(Reading)s""":
		"""${Css}<div style="float:left"><div>${T2JLPT}</div><div>${T2Freq}</div></div><div><center>${Expression}<br />${Reading}</center></div>"""},
u"Word recognition":
	{"""%(Reading)s<br>%(Meaning)s""":"""${Css}<div style="float:left;"><div>${T2JLPT}</div><div>${T2Freq}</div></div><div><center>${Reading}<br \>${Meaning}</center></div>"""},
u"Kanji character":
	{"""%(Kanji)s""":
		"""${Css}<div style="float:left">${Stroke}<div>${K2JLPT}</div><div>${K2Jouyou}</div><div>${K2Freq}</div></div><center>${K2Words}</center>"""},
u"Kanji meaning":
	{"""%(Meaning)s""":
		"""${Css}<div style="float:left">${Stroke}<div>${K2JLPT}</div><div>${K2Jouyou}</div><div>${K2Freq}</div></div><center>${Meaning}</center><center>${K2Words}</center>"""},
u"Kanji readings":
	{"""%(OnYomi)s<br>%(KunYomi)s""":
		"""${Css}<div style="float:left">${Stroke}<div>${K2JLPT}</div><div>${K2Jouyou}</div><div>${K2Freq}</div></div><center>${OnYomi}<br />${KunYomi}</center><center>${K2Words}</center>"""},
}
    
JxBase=QObject()

class Jx__Entry_Source_Target(QObject):
	def __init__(self,name,parent=JxBase):
		QObject.__init__(self,parent)
		self.setObjectName(name)
		self.Entry = JxTable.keys()[0]
		
	def Jx__Entry_fset(self,value):
		self._Entry = str(value)
		if self._Entry != u"Add Entry":
			self._Name = self._Entry
			self._Source = JxTable[self._Entry].keys()[0]
			self._Target = JxTable[self._Entry].values()[0]
		else:
			self._Name = self.MakeNameUnique(u"Name<br>(must be unique)")
			self._Source = self.MakeSourceUnique(u"Add Source<br>(must be unique)")
			self._Target = u"Add Target"
			JxTable[self._Name] = {self._Source:self._Target}
			self._Entry = self. _Name			
	@Jx__Prop
	def Entry():return {'fset': lambda self,value:self.Jx__Entry_fset(value)}

	def Jx__Name_fset(self,value):
		self._Name=str(value)
		if self._Name != self._Entry:
			del JxTable[self._Entry]
		JxTable[self._Name] = {self._Source:self._Target}
		self._Entry = self._Name
	@Jx__Prop
	def Name():return {'fset': lambda self,value:self.Jx__Name_fset(value)}

	def Jx__Source_fset(self,value):
		self._Source=str(value)
		JxTable[self._Name] = {self._Source:self._Target}
	@Jx__Prop
	def Source():return {'fset': lambda self,value:self.Jx__Source_fset(value)}
	
	def Jx__Target_fset(self,value):
		self._Target = str(value)
		JxTable[self._Name] = {self._Source:self._Target}
	@Jx__Prop
	def Target():return {'fset': lambda self,value:self.Jx__Target_fset(value)}
	
	@QtCore.pyqtSlot(result=str)	
	def GetEntries(self):
		Hash = []
		for name in JxTable.keys():
			Hash.append(u"'" + name + u"':'" + name + u"'")
		Hash.append(u"'Add Entry':'Add Entry'")
		Hash.append(u"'selected':'" + self._Entry + u"'")
		return u"{" + u",".join(Hash) + u"}"

	@QtCore.pyqtSlot(str,result=str)	
	def MakeNameUnique(self,value):
		"""Make sure to return a unique name field"""
		String = str(value)
		TempDict = set(name for name in JxTable.keys() if name !=self._Entry)
		JxUnicityBuffer = u""
		a = 0
		while JxUnicityBuffer + String in TempDict:
			JxUnicityBuffer = u"%s! " % a	
			a += 1
		return JxUnicityBuffer + String

	@QtCore.pyqtSlot(str,result=str)	
	def MakeSourceUnique(self,value):
		"""Make sure to return a unique source field"""
		String = str(value)
		TempDict = set(Dict.keys()[0] for (name,Dict) in JxTable.iteritems() if name !=self._Entry)
		JxUnicityBuffer = u""
		a = 0
		while JxUnicityBuffer + String in TempDict:
			JxUnicityBuffer = u"%s! " % a	
			a += 1
		return JxUnicityBuffer + String

class Jx__Model_CardModel_String(QObject):
	def __init__(self,name,parent=JxBase):
		QObject.__init__(self,parent)
		self.setObjectName(name)
		self.UpdateModels()

	def Jx__Model_fset(self,value):
		self._Model = value
		self.UpdateCardModels()
	@Jx__Prop
	def Model():return {'fset': lambda self,value:self.Jx__Model_fset(value)}

	def Jx__CardModel_fset(self,value):
		self._CardModel = value
		self.UpdateDisplayString()
	@Jx__Prop
	def CardModel():return {'fset': lambda self,value:self.Jx__CardModel_fset(value)}
	
	# to do : implement writing display string in the database if it's different
	@Jx__Prop
	def DisplayString():pass
	
	@QtCore.pyqtSlot(result=str)
	def GetModels(self):
		return u"{" + string.join([u"'" + Stuff + u"':'" + Stuff  + u"'" for Stuff in self.Models],u",") + u",'selected':'"  + self.Model + u"'}"
	@QtCore.pyqtSlot(result=str)
	def GetCardModels(self):
		return u"{" + string.join([u"'" + Stuff + u"':'" + Stuff  + u"'" for Stuff in self.CardModels],u",") + u",'selected':'"  + self.CardModel + u"'}"
	def UpdateModels(self):
		self.Models = mw.deck.s.column0(u"""select name from models group by name order by name""")
		if len(self.Models) == 0:
			self.Model = u""
		else:
			self.Model = self.Models[0]
	def UpdateCardModels(self):#beware "models.name" and "cardModels.name" aren't fields with the "unique" feature
		Query = u"""select cardModels.name from cardModels,models where 
		models.id = cardModels.modelId and models.name="%s"
		group by cardModels.name order by cardModels.name""" % self._Model
		self.CardModels = mw.deck.s.column0(Query)
		if len(self.CardModels) == 0:
			self.CardModel = u""
		else:
			self.CardModel = self.CardModels[0]
	def UpdateDisplayString(self):
		Query = u"""select cardModels.aformat from cardModels,models where 
		models.id = cardModels.modelId and models.name="%(Model)s" and cardModels.name="%(CardModel)s"
		""" % {'Model':self._Model,'CardModel':self._CardModel}
		s=mw.deck.s.scalar(Query)
		if s in JxLink:
			so=JxLink[s]
			s=so
#		s = s.replace("<", "&lt;")
#		s = s.replace(">", "&gt;")
		self.DisplayString = s
			
			
			
		

JxJavaScript = u"""
	function getInfo(){
	return (document.getElementById("%(Id)s").selected)?document.getElementById("%(Id)s").innerHTML:"";
	}
	getInfo();
	"""
# To Do : Implement Tags too	
def JxGetInfo():
	Models = []
	Rows = mw.deck.s.column0(u"""select name from models group by name order by name""")
	for Name in Rows:
		Value = JxWindow.page().mainFrame().evaluateJavaScript(JxJavaScript % {"Id":u"Model." + Name}).toString()
		if Value != u"":
			Models.append(Value)
	Fields = []
	Rows = mw.deck.s.column0(u"""select name from fieldModels group by name order by name""")
	for Name in Rows:
		Value = JxWindow.page().mainFrame().evaluateJavaScript(JxJavaScript % {"Id":u"Field." + Name}).toString()
		if Value != u"":
			Fields.append(Value)	
	
	return """select fields.value, facts.id, facts.created, facts.tags from fields,facts,fieldModels,models where 
		facts.id = fields.factId and fields.fieldModelId = fieldModels.id and facts.modelId = models.id and  
		fieldModels.name in (%(Fields)s) and models.name in  (%(Models)s) group by facts.id order by fields.value """ % ({"Fields":JxList2SQL(Fields),"Models":JxList2SQL(Models)})
	#mw.help.showText(str(Models)+str(Fields)+Query)		#Debug




	
	
	
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
JxWindow.setMinimumSize(QtCore.QSize(1010, 400))
JxWindow.setMaximumSize(QtCore.QSize(1010, 16777215))
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






# needed to run javascript inside JxWindow
QWebSettings.globalSettings().setAttribute(QWebSettings.JavascriptEnabled, True)
QWebSettings.globalSettings().setAttribute(QWebSettings.JavascriptCanOpenWindows, True)
def JxJavaScriptPrint2Console(Message,Int, Source):
	mw.help.showText("Line "+ str(Int) + " SourceID " + Source + "/n" + Message)
JxWindow.javaScriptConsoleMessage=JxJavaScriptPrint2Console
# QWidget inside QWebView experiment
#class WebPluginFactory(QWebPluginFactory):
#
#    def __init__(self, parent = None):
#        QWebPluginFactory.__init__(self, parent)
#    
#    def create(self, mimeType, url, names, values):
#        if mimeType == "x-pyqt/widget":
#            return JxField()
    
#    def plugins(self):
#        plugin = QWebPluginFactory.Plugin()
#        plugin.name = "PyQt Widget"
#        plugin.description = "An example Web plugin written with PyQt."
#        mimeType = QWebPluginFactory.MimeType()
#        mimeType.name = "x-pyqt/widget"
#        mimeType.description = "PyQt widget"
#        mimeType.fileExtensions = []
#        plugin.mimeTypes = [mimeType]
#        print "plugins"
#        return [plugin]
	
#class JxFieldb(QComboBox):
#    def __init__(self, parent = None):
#        QComboBox.__init__(self, parent)
#        Rows = mw.deck.s.all(u"""select name, id from models""")
#        self.SizeAdjustPolicy(QComboBox.AdjustToContents)
#        for (Name, Id) in Rows:
#		self.addItem(Name)
#        self.show()
	
#class JxField(QMenuBar):	
#    def __init__(self, parent = None):
#	QMenuBar.__init__(self, parent)
#	Menu = QMenu("Fields",self)
#
#	Rows = mw.deck.s.all(u"""select name, id from models""")
#	for (Name, Id) in Rows:
#              Menu.addAction(Name)
#	self.addMenu(Menu)
#	self.show()

# with this you can enable QWidget inside a QWebView
#QWebSettings.globalSettings().setAttribute(QWebSettings.PluginsEnabled, True)
#factory = WebPluginFactory()
#JxWindow.page().setPluginFactory(factory)	



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


JxAnswerSettings={}

def Rah():
	JxAnswerSettings = JxBase.findChild(Jx__Model_CardModel_String,'JxAnswerSettings')	
	JxWindow.page().mainFrame().addToJavaScriptWindowObject("JxAnswerSettings",JxAnswerSettings)	
	JxTemplateOverride = JxBase.findChild(Jx__Entry_Source_Target,'JxTemplateOverride')	
	JxWindow.page().mainFrame().addToJavaScriptWindowObject("JxTemplateOverride",JxTemplateOverride)	
	
