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

	<h3 style="text-align:center;">AUTOMATIC MAPPING</h3>
	<form name="Translator"> 
	
	<center><textarea name="Source" style="width: 70%%;height:50px;text-align:center;" onChange = "JxTemplateOverride.Source = JxTemplateOverride.MakeUnique(document.forms.Translator.Source.value,1)"></textarea></center>
	
	<br />
	
     	<table width="80%%" align="center"><tr><td style="text-align:center;"><a href = "javascript:void(0)" onClick="$('.Entry').html(JxTemplateOverride.ReduceForm());
	document.forms.Translator.Target.value=JxTemplateOverride.Target;
	document.forms.Translator.Source.value=JxTemplateOverride.Source;">Delete</a></td><td class="Entry" style="text-align:center">&nbsp;</td><td style="text-align:center;"><a href = "javascript:void(0)" onclick="Rename()">Rename</a></td></tr></table>
	
	<br />
	
	<center><textarea name="Target" style="width: 90%%;height:100px;text-align:center;" onChange = "JxTemplateOverride.Target = document.forms.Translator.Target.value" ></textarea></center>
	
	<br />
	
	<table align="center"  width="70%%"><tr><td style="text-align:center;"><a href="py:JxBrowse()">Preview</a></td><td style="text-align:center;"><a href="javascript:void(0);">Help</a></td></tr></table>
	
	</form>


	<h3 style="text-align:center;">TAG REDUNDANT ENTRIES IN A SET</h3>
	<center>
	<span style="vertical-align:middle;"><select style="display:inline;" id="s1" multiple="multiple">%s</select></span> 
	&nbsp;&nbsp;&nbsp;<a href=py:JxTagDuplicates(JxGetInfo())>Tag them !</a>
	</center>
	<ul><li>young ones get "JxDuplicate"</li><li>the oldest one gets "JxMasterDuplicate"</li></ul>
	

	
	 """ % FieldsBuffer
	
	Dict = {"JLPT":'',"Jouyou":'',"Zone":'',"Tools":'',"Content":JxHtml}
	Dict["Tools"] = 'id="active"'
	Dict["DeckModels"] = u"{%s}" % string.join([u"'"+ a + u"':'" + a + u"'" for a in JxPopulateModels],",")
	Dict["DeckModelselected"] = u"%s" % JxPopulateModels[0]	
	JxPage = Template(JxMenu).safe_substitute(Dict)
	

	#JxAnswerSettings = Jx__Model_CardModel_String("JxAnswerSettings")
	#JxWindow.page().mainFrame().addToJavaScriptWindowObject("JxAnswerSettings",JxAnswerSettings)	

	JxWindow.page().mainFrame().addToJavaScriptWindowObject("JxTemplateOverride",JxTemplateOverride)	
	mw.connect( JxWindow.page().mainFrame(),QtCore.SIGNAL('javaScriptWindowObjectCleared()'), Rah);

	JxWindow.setHtml(JxPage,JxResourcesUrl)



import os
#import codecs
import cPickle
import itertools

def JxReadFile(File):
	"""Reads a tab separated file text and returns a list of tupples."""
	List = []
	File = codecs.open(File, "r", "utf8")
	for Line in File:
		List.append(tuple(Line.strip('\n').split('\t')))
	f.close()
	return List




JxBase=QObject()



	











class Jx__Entry_Source_Target(QObject):
	"""Data class for the HtmlJavascript Entry/Name/Source/Target Widget"""
	def __init__(self,name,parent=JxBase):
		QObject.__init__(self,parent)
		self.setObjectName(name)
		self.File = os.path.join(mw.config.configPath, "plugins","JxPlugin","User", "JxTable.txt")
		self.InitTables()
		if len(self.Table)>0:
			self.Entry = 0
		else:
			self._Entry = 0
			self._Name = u""
			self._Source = u""
			self._Target = u""			
	def Jx__Entry_fset(self,value):
		self._Entry = int(value)
		N = len(self.Table)
		if self._Entry != N:
			(self._Name,self._Source,self._Target) = self.Table[self._Entry]
		else:
			(self._Name,self._Source,self._Target) = (self.MakeUnique(u"New Entry",0), self.MakeUnique(u"""Add Source
				(must be unique)""",1), u"Add Target")
			self.Table.append((self._Name,self._Source,self._Target))
			JxLink[self._Source]=self._Target
			
			
	@Jx__Prop
	def Entry():return {'fset': lambda self,value:self.Jx__Entry_fset(value)}

	def Jx__Name_fset(self,value):
		self._Name=str(value)
		(OldName,OldSource,OldTarget) = self.Table[self._Entry]
		if self._Name != OldName:
			self.Table[self._Entry]=(self._Name,OldSource,OldTarget)
			self.SaveTable()
	@Jx__Prop
	def Name():return {'fset': lambda self,value:self.Jx__Name_fset(value)}

	def Jx__Source_fset(self,value):
		self._Source=str(value)
		(OldName,OldSource,OldTarget) = self.Table[self._Entry]
		if self._Source != OldSource:
			self.Table[self._Entry]=(OldName,self._Source,OldTarget)
			self.SaveTable()
			del JxLink[OldSource]
			JxLink[self._Source]=self._Target
	@Jx__Prop
	def Source():return {'fset': lambda self,value:self.Jx__Source_fset(value)}
		
	def Jx__Target_fset(self,value):
		self._Target = str(value)
		(OldName,OldSource,OldTarget) = self.Table[self._Entry]
		if self._Target != OldTarget:
			self.Table[self._Entry]=(OldName,OldSource,self._Target)
			self.SaveTable()
			JxLink[OldSource]=self._Target
	@Jx__Prop
	def Target():return {'fset': lambda self,value:self.Jx__Target_fset(value)}

	@QtCore.pyqtSlot(result=str)	
	def GetForm(self):
		Form = u"""<select name="Entry" onchange="
		JxTemplateOverride.Entry = document.forms.Translator.Entry.options.selectedIndex;
		document.forms.Translator.Target.value = JxTemplateOverride.Target;
		document.forms.Translator.Source.value = JxTemplateOverride.Source;
		$('.Entry').html(JxTemplateOverride.GetForm())">"""
		N = len(self.Table)
		for Entry in range(0, N):
			Select = u""	
			if Entry == self._Entry: 
				Select = u" selected"
			Form += u"""<option value="%(Entry)s"%(Selected)s>%(Text)s</option>""" % {u'Entry':Entry, u'Text':self.Table[Entry][0] , u'Selected':Select} 
		Form += u"""<option value="%s">New Entry</option>""" % N 
		if len(self.Table) !=0:
			return Form + u"""</select>"""
		else:
			return u"""<button name="Entry" onclick="
			JxTemplateOverride.Entry = 0;
			document.forms.Translator.Target.value = JxTemplateOverride.Target;
			document.forms.Translator.Source.value = JxTemplateOverride.Source;
			$('.Entry').html(JxTemplateOverride.GetForm())">New Entry</button>"""
		
	@QtCore.pyqtSlot(str,int,result=str)	
	def MakeUnique(self,value,Int):
		"""Make sure to return a unique field"""
		String = str(value)
		TempDict = set(self.Table[Entry][Int] for Entry in range(0,len(self.Table)) if Entry != self._Entry)
		if Int == 0:
			TempDict.	add(u"New Entry")
		JxUnicityBuffer = u""
		a = 1
		while String + JxUnicityBuffer in TempDict:
			JxUnicityBuffer = u" %s" % a	
			a += 1
		return String + JxUnicityBuffer
	@QtCore.pyqtSlot(result=str)	
	def ReduceForm(self):
		if len(self.Table)>0:
			del JxLink[self._Source]
			self.Table.pop(self._Entry)
			self.SaveTable()

		if len(self.Table)>0:
			self.Entry = 0
		else:
			self._Entry = 0
			self._Name = u""
			self._Source = u""
			self._Target = u""
		return self.GetForm()
		
	def SaveTable(self):
		File = codecs.open(self.File, "wb", "utf8")  
		for (Name,Source,Target) in self.Table:
			File.write(u"%s	%s	%s\n"%(Name,Source,Target))
		File.close()
	def InitTables(self):
		if os.path.exists(self.File):
			self.Table = JxReadFile(self.File)
		else : 
			from default import Jx__Entry_Source_Target__Default
			self.Table = Jx__Entry_Source_Target__Default
			self.SaveTable()
		JxLink = {}
		for (Name, Source,Target) in self.Table:
			JxLink[Source] = Target



JxTemplateOverride = Jx__Entry_Source_Target("JxTemplateOverride")




class Jx__Model_CardModel_String(QObject):
	"""Data class for the HtmlJavascript Model/Card/String Widget"""
	def __init__(self,name,parent=JxBase):
		QObject.__init__(self,parent)
		self.setObjectName(name)
		self.UpdateModels()

	def Jx__Model_fset(self,value):
		self._Model = str(value)
		self.UpdateCardModels()
	@Jx__Prop
	def Model():return {'fset': lambda self,value:self.Jx__Model_fset(value)}

	def Jx__CardModel_fset(self,value):
		self._CardModel = str(value)
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
	def GetFormModels(self):		
		Form = u"""<select name="Model" onChange="
		var index = document.forms.Browser.Model.options.selectedIndex;
		JxAnswerSettings.Model = document.forms.Browser.Model.options[index].text;
		$('.CardModel').html(JxAnswerSettings.GetFormCardModels());
		$('.Answer').html(JxAnswerSettings.DisplayString);		
		">"""
		for Stuff in self.Models:
			Select = u""	
			if Stuff == self._Model: 
				Select = u" selected"
			Form += u"""<option value="%(Entry)s"%(Selected)s>%(Text)s</option>""" % {u'Entry':Stuff, u'Text':Stuff , u'Selected':Select} 
		return Form + u"""</select>"""
	@QtCore.pyqtSlot(result=str)
	def GetFormCardModels(self):		
		Form = u"""<select name="CardModel" onChange="
		var index = document.forms.Browser.CardModel.options.selectedIndex;
		JxAnswerSettings.CardModel = document.forms.Browser.CardModel.options[index].text;
		$('.Answer').html(JxAnswerSettings.DisplayString);	
		">"""
		for Stuff in self.CardModels:
			Select = u""	
			if Stuff == self._CardModel: 
				Select = u" selected"
			Form += u"""<option value="%(Entry)s"%(Selected)s>%(Text)s</option>""" % {u'Entry':Stuff, u'Text':Stuff , u'Selected':Select} 
		return Form + u"""</select>"""
			
			
			
		
	
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
	else:
		QDesktopServices.openUrl(QUrl(link))

# I now have my own window =^.^=
JxWindow = QWebView(mw)
sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
sizePolicy.setHorizontalStretch(0)
sizePolicy.setVerticalStretch(0)
sizePolicy.setHeightForWidth(JxWindow.sizePolicy().hasHeightForWidth())
JxWindow.setSizePolicy(sizePolicy)
JxWindow.setMinimumSize(QtCore.QSize(410, 400))
JxWindow.setMaximumSize(QtCore.QSize(410, 16777215))
JxWindow.page().setLinkDelegationPolicy(QWebPage.DelegateAllLinks)
mw.connect(JxWindow, QtCore.SIGNAL('linkClicked (const QUrl&)'), onClick)

JxWindow.hide()

#def sizeHint(self):
#        return QSize(100,100)

class Jx__Browser(QWebView):
	"""A modless QWebkit Window for Stuff that requires lot of space/focus."""
	def __init__(self,parent=None):
		QWebView.__init__(self,parent)
		sizePolicyd = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)	
		sizePolicyd.setHorizontalStretch(QSizePolicy.GrowFlag+QSizePolicy.ShrinkFlag)
		sizePolicyd.setVerticalStretch(QSizePolicy.GrowFlag+QSizePolicy.ShrinkFlag)
		#sizePolicyd.setHeightForWidth(self.sizePolicy().sizeHint())#hasHeightForWidth())
		self.setSizePolicy(sizePolicyd)
		self.setMinimumSize(QtCore.QSize(400, 200))
		#self.setMaximumSize(QtCore.QSize(210, 16777215))
		self.page().setLinkDelegationPolicy(QWebPage.DelegateAllLinks)
		mw.connect(self, QtCore.SIGNAL('linkClicked (const QUrl&)'), onClick)	
		self.hide()

			
	def sizeHint(self):
		return(QSize(800,600))
	
	
	
# I now have 2windows =^.^=
JxPreview = Jx__Browser()




def JxBrowse():
		
	JxAnswerSettings = Jx__Model_CardModel_String("JxAnswerSettings")
	JxPreview.page().mainFrame().addToJavaScriptWindowObject("JxAnswerSettings",JxAnswerSettings)	
	mw.connect( JxPreview.page().mainFrame(),QtCore.SIGNAL('javaScriptWindowObjectCleared()'), Rah);
	JxPreview.setWindowTitle(u"Answer Template Browser")
	JxPreview.setHtml(u"""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN">
<html>
<head>
<title>JxPlugin Main Menu</title>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<link rel="stylesheet" type="text/css" href="demo.css" /> 
<script type="text/javascript" src="jquery.js"></script> 
<script type="text/javascript" src="jquery.jeditable.js"></script> 
<script type="text/javascript" src="Browser.js"></script></head><body><form name="Browser">
<div><table align="center" width="80%"><tr><td style="text-align:center;">Deck Model : <span class="Model">&nbsp;</span></td><td style="text-align:center;">Card Model : <span class="CardModel">&nbsp;</span></td></tr></table></div><hr />
<div class="Answer"></div></form></body></html>""",JxResourcesUrl)
	JxPreview.show()
	
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
#def JxJavaScriptPrint2Console(Message,Int, Source):
#	mw.help.showText("Line "+ str(Int) + " SourceID " + Source + "/n" + Message)
#JxWindow.javaScriptConsoleMessage=JxJavaScriptPrint2Console	


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
	JxPreview.page().mainFrame().addToJavaScriptWindowObject("JxAnswerSettings",JxAnswerSettings)	
	JxTemplateOverride = JxBase.findChild(Jx__Entry_Source_Target,'JxTemplateOverride')	
	JxWindow.page().mainFrame().addToJavaScriptWindowObject("JxTemplateOverride",JxTemplateOverride)	
	
