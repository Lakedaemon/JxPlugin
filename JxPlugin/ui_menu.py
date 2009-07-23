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
<script language="javascript" type="text/javascript" src="firebug-lite-compressed.js"></script>
<script type="text/javascript" src="jquery.js"></script> 
<script type="text/javascript" src="ui.core.js"></script> 
<script type="text/javascript" src="ui.dropdownchecklist.js"></script>
<script type="text/javascript" src="jquery.jeditable.js"></script> 
<script type="text/javascript" src="editinplace.js"></script>

<script type="text/javascript"> 

$(document).ready(function(){	
		$("#s1").dropdownchecklist({ firstItemChecksAll: true,width:100});
});
</script>
<script type="text/javascript"> 
	
	
	 	$(document).ready(function(){
    $('.editable').AVeditable(function(element){
      // function that will be called when the
      // user finishes editing and clicks outside of editable area
      Jx_Model.String = element.innerHTML;
    });

 
   });
</script>
<script type="text/javascript"> 
   
   	       OLHasho={'Dolor sit':'Doeeelor sit',selected:'Dolor sit'};

	$(document).ready(function(){	
	
	
$('.edit_Model').editable(function(value, settings) { 
	       Jx_Model.String = value;
	       
	       OLHash=   JxTac.Fields(value);   
		       $('.edit_CardModel').remove();
		       		       $('.oltest').append("<b class='edit_CardModel'>ouh</b>");
				       
				       
				       $('.edit_CardModel').editable(function(value, settings) { 
	       JxString.String = value;
       
	       
     console.log(this);
     console.log(value);
     console.log(settings);
     return(value);
  }, { 
     onblur : 'submit',
    indicator : '<img src="img/indicator.gif">',
    data   : OLHash,
    type   : "select",
    placeholder : "OL",
    style  : "inherit",
    tooltip   : "Click to edit model !",
    submitdata : function() {
      return {id : 2};
    }
  });     
				       
				       
				       
				       
				       
	       //$('.edit_CardModel').trigger("blur");	       
	       	   //    $('.edit_CardModel').trigger("submit");
     console.log(this);
     console.log(value);
     console.log(settings);
     return(value);
  }, { 
     onblur : 'submit',
    indicator : '<img src="img/indicator.gif">',
    data   : "${DeckModels}",
    type   : "select",
    placeholder : "${DeckModelselected}",
    style  : "inherit",
    tooltip   : "Click to edit model !",
    submitdata : function() {
      return {id : 2};
    }
  });    
  });  
    
    
    </script>
<script type="text/javascript"> 
   
   	       OLHash={'Lorum':'gahhhhh'};

	$(document).ready(function(){	
    
    
    
    
    
$('.edit_CardModel').editable(function(value, settings) { 
	       JxString.String = value;
       
	       
     console.log(this);
     console.log(value);
     console.log(settings);
     return(value);
  }, { 
     onblur : 'submit',
    indicator : '<img src="img/indicator.gif">',
    data   : OLHash,
    type   : "select",
    placeholder : "OL",
    style  : "inherit",
    tooltip   : "Click to edit model !",
    submitdata : function() {
      return {id : 2};
    }
  });     
    
    
    
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
	<ul><li id="gah">young ones get "JxDuplicate"</li><li>the oldest one gets "JxMasterDuplicate"</li></ul>

	<h3 style="text-align:center;">ANSWER FIELDS</h3>
	<p>The card model <b class="oltest"><b class="edit_CardModel" id="div_1"></b></b> of deck model <b class="edit_Model" id="div_1"></b> has the display settings : <i id="JxString" class="editable" contenteditable="true">yo essai</i></p>
	 """ % FieldsBuffer
	
	Dict = {"JLPT":'',"Jouyou":'',"Zone":'',"Tools":'',"Content":JxHtml}
	Dict["Tools"] = 'id="active"'
	Dict["DeckModels"] = u"{%s}" % string.join([u"'"+ a + u"':'" + a + u"'" for a in JxPopulateModels],",")
	Dict["DeckModelselected"] = u"%s" % JxPopulateModels[0]	
	JxPage = Template(JxMenu).safe_substitute(Dict)
	
	Jx_Model=QObject(JxBase)
	Jx_Model.setObjectName("Jx_Model")	
	Jx_Model.setProperty("String",QVariant(""))
	JxWindow.page().mainFrame().addToJavaScriptWindowObject("Jx_Model",Jx_Model)
	JxString=QObject(JxBase)
	JxString.setObjectName("JxString")	
	JxString.setProperty("String",QVariant(""))
	JxWindow.page().mainFrame().addToJavaScriptWindowObject("JxString",JxString)
	JxTac = Jxj("JxTac")
	JxTac.setProperty("String",QVariant("oups"))
	JxWindow.page().mainFrame().addToJavaScriptWindowObject("JxTac",JxTac)	
	JxWindow.page().mainFrame().evaluateJavaScript("alert(JxTac.Fields('Tango'))")	
#	JxWindow.page().mainFrame().evaluateJavaScript("JxString.String='beurkeu'")
#	mw.help.showText(JxString.property("String").toString())
	mw.connect( JxWindow.page().mainFrame(),QtCore.SIGNAL('javaScriptWindowObjectCleared()'), Rah);


	JxWindow.setHtml(JxPage,JxResourcesUrl)
#	mw.help.showText(JxString.property("String").toString())


    
JxBase=QObject()
    
class Jxj(QObject):
	def __init__(self,name,parent=JxBase):
		QObject.__init__(self,parent)
		self.setObjectName(name)	
#		@QtCore.pyqtProperty("QString")
#		self. = u"Tano"
#		self.OK.setObjectName("OK") 
	@QtCore.pyqtSlot(str,result=str)
	def Fields(self,model):
		Query = u"""select fieldModels.name from fieldModels,models where 
			models.id = fieldModels.modelId and models.name="%s"
			group by fieldModels.name order by fieldModels.name""" % u"Tango"
		Rows = mw.deck.s.column0(Query)
		return u"{" + string.join([u"'" + Stuff + u"':'" + Stuff  + u"'" for Stuff in Rows],u",") + u"}"
	
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




#JxString=QObject()
def Rah():
	Jx_Model = JxBase.findChild(QObject,'Jx_Model')
	JxWindow.page().mainFrame().addToJavaScriptWindowObject("Jx_Model",Jx_Model)	
	JxString = JxBase.findChild(QObject,'JxString')
	JxWindow.page().mainFrame().addToJavaScriptWindowObject("JxString",JxString)
	JxTac = JxBase.findChild(QObject,'JxTac')
	if JxTac: 
		mw.help.showText("found")
	else:
		mw.help.showText("not found")
	JxWindow.page().mainFrame().addToJavaScriptWindowObject("JxTac",JxTac)		
#def Rah():
#	JxWindow.page().mainFrame().addToJavaScriptWindowObject("JxString",JxString)
