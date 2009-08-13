# -*- coding: utf-8 -*-
# Copyright: Olivier Binda <olivier.binda@wanadoo.fr>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
# ---------------------------------------------------------------------------
# This file is a plugin for the "anki" flashcard application http://ichi2.net/anki/
# ---------------------------------------------------------------------------
from string import upper

from PyQt4 import QtGui, QtCore
from PyQt4.QtWebKit import QWebPage, QWebView
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from ankiqt import mw

import globalobjects
from loaddata import *
from answer import *
from stats import *
from tools import *
from metacode import *


import os
import cPickle
import itertools

		
JxResourcesUrl = QUrl.fromLocalFile(os.path.join(mw.config.configPath, "plugins","JxPlugin","Resources") + os.sep)

def JxHelp():
        from html import Jx_Html_HelpAutomaticMapping
        JxPreview.setHtml(Jx_Html_HelpAutomaticMapping,JxResourcesUrl)
        JxPreview.show()


def JxReadFile(File):
	"""Reads a tab separated file text and returns a list of tupples."""
	List = []
	try:
		File = codecs.open(File, "rb", "utf8")
		for Line in File:
			List.append(tuple(map(lambda x:x.replace('<Tab/>','\t'),Line.strip('\n').split('\t'))))
		f.close()
	except:
		pass
	return List





JxBase = QObject()




	

class Jx__Settings(QObject):
	"""Data class for the settings of the JxPlugin"""
	def __init__(self,name="JxSettings",parent=JxBase):
		QObject.__init__(self,parent)
		self.setObjectName(name)
                self.File = os.path.join(mw.config.configPath, "plugins","JxPlugin", "Settings.pickle")
                self.Load()
         
        @pyqtSignature("QString", result="QString")	
	def Get(self,Key):
                return self.Dict[u"%s" % Key]
                
        @pyqtSignature("QString, QString")	
	def Set(self,Key,Value):
                self.Dict[u"%s" % Key] = Value
                self.Update()
                  
        def Load(self):
                if os.path.exists(self.File):
                          File = open(self.File, 'rb')
                          self.Dict = cPickle.load(File)
                          File.close()
                else:
                          from default import  Jx__Css__Default
                          self.Dict={"Mode":"Override","Css":Jx__Css__Default}
                          self.Update()
        def Update(self):
                File = open(self.File, 'wb')
                cPickle.dump(self.Dict, File, cPickle.HIGHEST_PROTOCOL)
                File.close()

JxSettings = Jx__Settings()




class Jx__Entry_Source_Target(QObject):
	"""Data class for the HtmlJavascript Entry/Name/Source/Target Widget"""
	def __init__(self,name,parent=JxBase):
		QObject.__init__(self,parent)
		self.setObjectName(name)
		self.File = os.path.join(mw.config.configPath, "plugins","JxPlugin","User","JxTable.cpickle")
                if os.path.exists(self.File):
                        File = open(self.File, 'rb')
                        self.Table = cPickle.load(File)
                        File.close()
                        self.ResetJxLink()
                else:
                        self.ResetTables()
		if len(self.Table)>0:
			self.Entry = 0
		else:
			self._Entry = 0
			self._Name = "New Entry"
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

	#@QtCore.pyqtSlot(result=str) doesn't work with OS X 
        @pyqtSignature("",result="QString")		
	def GetForm(self):
		Form = u"""<select id="Entry" name="Entry" onchange="
		JxTemplateOverride.Entry = document.forms.Translator.Entry.options.selectedIndex;
		document.forms.Translator.Target.value = JxTemplateOverride.Target;
		document.forms.Translator.Source.value = JxTemplateOverride.Source;
		$('.Entry').html(JxTemplateOverride.GetForm());
		$('select#Entry').selectmenu({width:200});">"""
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
			return u"""<button class="ui-button" id="Entry" name="Entry" onclick="
			JxTemplateOverride.Entry = 0;
			document.forms.Translator.Target.value = JxTemplateOverride.Target;
			document.forms.Translator.Source.value = JxTemplateOverride.Source;
			$('.Entry').html(JxTemplateOverride.GetForm());
                           $('select#Entry').selectmenu({width:200});
                        ">New Entry</button>"""
		
	#@QtCore.pyqtSlot(str,int,result=str) doesn't work with OS X 
        @pyqtSignature("QString, int",result="QString")
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
	#@QtCore.pyqtSlot(result=str) doesn't work with OS X 
        @pyqtSignature("",result="QString")	
	def ReduceForm(self):
		if len(self.Table)>0:
			del JxLink[self._Source]
			self.Table.pop(self._Entry)
			self.SaveTable()

		if len(self.Table)>0:
			self.Entry = 0
		else:
			self._Entry = 0
			self._Name = "New Entry"
			self._Source = u""
			self._Target = u""
		return self.GetForm()
        @pyqtSignature("")
        def ResetTables(self):
                from default import Jx__Entry_Source_Target__Default
		self.Table = Jx__Entry_Source_Target__Default[:]
		self.SaveTable()
                self.ResetJxLink()
		
	def SaveTable(self):
		File = open(self.File, "wb")  
                cPickle.dump(self.Table, File, cPickle.HIGHEST_PROTOCOL)
		File.close()

        def ResetJxLink(self):
                Jxlink={}
                for (Name, Source,Target) in self.Table:
                        JxLink[Source] = Target                                  
        

JxTemplateOverride = Jx__Entry_Source_Target("JxTemplateOverride")


class Jx__Model_CardModel_String(QObject):
	"""Data class for the HtmlJavascript Model/Card/String Widget"""
	def __init__(self,name,parent=JxBase):
		QObject.__init__(self,parent)
		self.setObjectName(name)
                self.Sample={}
		self.UpdateModels()

	def Jx__Model_fset(self,value):
		self._Model = str(value)
		self.UpdateCardModels()
	@Jx__Prop
	def Model():return {'fset': lambda self,value:self.Jx__Model_fset(value)}

	def Jx__CardModel_fset(self,value):
		self._CardModel = str(value)
		self.UpdatePrefix()
	@Jx__Prop
	def CardModel():return {'fset': lambda self,value:self.Jx__CardModel_fset(value)}

	def Jx__Prefix_fset(self,value):
		self._Prefix = u"%s" % value
		self.UpdateDisplayString()
	@Jx__Prop
	def Prefix():return {'fset': lambda self,value:self.Jx__Prefix_fset(value)}

	# to do : implement writing display string in the database if it's different
	@Jx__Prop
	def DisplayString():pass
	

        @pyqtSignature("",result="QString")
	def GetModels(self):
		return u"{" + string.join([u"'" + Stuff + u"':'" + Stuff  + u"'" for Stuff in self.Models],u",") + u",'selected':'"  + self.Model + u"'}"
		

        @pyqtSignature("",result="QString")
	def GetFormModels(self):		
		Form = u"""<form id ="FormModel"><select id="Model" name="Model" onChange="
		var index = document.forms.FormModel.Model.options.selectedIndex;
		JxAnswerSettings.Model = document.forms.FormModel.Model.options[index].text;
		$('.CardModel').html(JxAnswerSettings.GetFormCardModels());
                  $('select#CardModel').selectmenu();
                  $('.Prefix').html(JxAnswerSettings.GetFormPrefix());
                  $('select#Prefix').selectmenu();                  
	       	$('.Answer').html(JxAnswerSettings.DisplayString);
		">"""
		for Stuff in self.Models:
			Select = u""	
			if Stuff == self._Model: 
				Select = u"selected"
			Form += u"""<option value="%(Entry)s" %(Selected)s>%(Text)s</option>""" % {u'Entry':Stuff, u'Text':Stuff , u'Selected':Select} 
		return Form + u"""</select></form>"""

        @pyqtSignature("",result="QString")
	def GetFormCardModels(self):		
		Form = u"""<form id="FormCardModel"><select  id="CardModel" name="CardModel" onChange="
		var index = document.forms.FormCardModel.CardModel.options.selectedIndex;
		JxAnswerSettings.CardModel = document.forms.FormCardModel.CardModel.options[index].text;
                  //$('select#CardModel').selectmenu();
                  $('.Prefix').html(JxAnswerSettings.GetFormPrefix());
                  $('select#Prefix').selectmenu();   
		$('.Answer').html(JxAnswerSettings.DisplayString);	
		">"""
		for Stuff in self.CardModels:
			Select = u""	
			if Stuff == self._CardModel: 
				Select = u" selected"
			Form += u"""<option value="%(Entry)s"%(Selected)s>%(Text)s</option>""" % {u'Entry':Stuff, u'Text':Stuff , u'Selected':Select} 
		return Form + u"""</select></form>"""
                
        @pyqtSignature("",result="QString")
	def GetFormPrefix(self):
		Query = u"""select cardModels.aformat from cardModels,models where 
		models.id = cardModels.modelId and models.name="%(Model)s" and cardModels.name="%(CardModel)s"
		""" % {'Model':self._Model,'CardModel':self._CardModel}
		Template = mw.deck.s.scalar(Query)		
		Form = u""
                L = len(Template)
                for Key in JxLink.keys():
                        K = len(Key)
                        if K > L:
                                if Key[K-L:] == Template and Key[K-L-1] == u"-" and Key[0:K-L-1].strip(u'-KWSGD') == u"":
                                        Select = u""
                                        if Key[0:K-L] == self._Prefix:
                                                Select = u"selected"
                                        Form += u"""<option value="%(Entry)s"%(Selected)s>%(Text)s</option>""" % {u'Entry':Key[0:K-L], u'Text':Key[0:K-L], u'Selected':Select}
                Select = u""
                if self._Prefix == u"Bypass":
                        Select = u"selected"
                Form += u"""<option value="%(Entry)s"%(Selected)s>%(Text)s</option>""" % {u'Entry':'Bypass', u'Text':'Bypass', u'Selected':Select}
		return u"""<form id="FormPrefix"><select id="Prefix" name="Prefix" onChange="
                var index = document.forms.FormPrefix.Prefix.options.selectedIndex;
                JxAnswerSettings.Prefix = document.forms.FormPrefix.Prefix.options[index].text;
                $('.Answer').html(JxAnswerSettings.DisplayString);
                ">"""+ Form + u"""</select></form>""" 

        @pyqtSignature("")
	def Toggle(self):
                if len(self.Sample)>1:
                        self.Sample = {}
                else:
                        from default import Jx__Sample__Default
                        self.Sample = Jx__Sample__Default
                self.Sample[u'Css']=u"""<style>%s</style>""" % JxSettings.Get(u'Css')

		self.UpdateDisplayString()
                
#        @pyqtSignature("",result="QString")
#	def GetCardModels(self):
#		return u"{" + string.join([u"'" + Stuff + u"':'" + Stuff  + u"'" for Stuff in self.CardModels],u",") + u",'selected':'"  + self.CardModel + u"'}"
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
	def UpdatePrefix(self):
		Query = u"""select cardModels.aformat from cardModels,models where 
                models.id = cardModels.modelId and models.name="%(Model)s" and cardModels.name="%(CardModel)s" 
                """ % {'Model':self._Model,'CardModel':self._CardModel}
		Template = mw.deck.s.scalar(Query)	
		L = len(Template)
		Select = True
		for Key in JxLink.keys():
                        K = len(Key)
                        if K > L:
                                if Key[K-L:] == Template and Key[K-L-1] == u"-" and Key[0:K-L-1].strip(u'-KWSTD') == u"":
                                        self.Prefix = Key[0:K-L]
                                        Select = False
                                        break
		if Select:
                        self.Prefix = u"Bypass"
	def UpdateDisplayString(self):
		Query = u"""select cardModels.aformat from cardModels,models where 
                models.id = cardModels.modelId and models.name="%(Model)s" and cardModels.name="%(CardModel)s"
                """ % {'Model':self._Model,'CardModel':self._CardModel}
		String = mw.deck.s.scalar(Query)
                if self._Prefix != u"Bypass" and self._Prefix + String in JxLink: 
                        Template = JxLink[self._Prefix + String]
                else:
                        Template = String
                self.DisplayString = re.sub("\$\{(.*?)\}",lambda x:JxReplace(x,self.Sample),Template)
	



	
	
	
JxMap={"Kanji2JLPT":MapJLPTKanji,"Tango2JLPT":MapJLPTTango,"Kanji2Jouyou":MapJouyouKanji,
"Kanji2Zone":MapZoneKanji,"Tango2Zone":MapZoneTango,"Kanji2Kanken":MapKankenKanji}

JxStatsMenu={
'JLPT':[('Kanji',HtmlReport,('Kanji',0)),('Words',HtmlReport,('Word',0))],
'Frequency':[('Kanji',HtmlReport,('Kanji',2)),('Kanji',JxWidgetAccumulatedReport,('Kanji',1)),('Word',HtmlReport,('Word',2)),
('Words',JxWidgetAccumulatedReport,('Word',1))],
'Kanken':[('Kanji',HtmlReport,('Kanji',3))],
'Jouyou':[('Kanji',HtmlReport,('Kanji',4))]}


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


def JxMissing(Type,Set):
	JxHtml = Template("""<br /><center><b style="font-size:1.4em;">MISSING ${CAPSET}</b></center><center><a href=py:JxSeen("${Type}","${Set}")>Seen</a>&nbsp;<a href=py:JxStats("${Type}")>Stats</a></center>""").substitute(Type=Type,Set=Set,CAPSET=upper(Set)) 
	JxHtml += MissingHtml(JxMap[Set+"2"+Type],JxQuery[Set])
	
	Dict = {"JLPT":'',"Jouyou":'',"Zone":'',"Tools":'',"Content":JxHtml}
	Dict[Type] = 'id="active"'
	JxPage = JxMenu #Template(JxMenu).safe_substitute(Dict)
	
	JxWindow.setHtml(JxPage)

def JxShowIn(Type,k,Label):
        JxPreview.setHtml(JxShowPartition(Type,k,Label),JxResourcesUrl)
        JxPreview.activateWindow()
        JxPreview.show()
        
	
def JxShowOut(Type,k):
        JxPreview.setHtml(JxShowMissingPartition(Type,k),JxResourcesUrl)
        JxPreview.activateWindow()
        JxPreview.show()  
        
def onClick(url):
	String = unicode(url.toString())
	if String.startswith("py:"):
		String = String[3:]
		eval(String)
	else:
		QDesktopServices.openUrl(QUrl(link))


		
from controls import Jx__MultiSelect                
Jx_Control_Tags = Jx__MultiSelect('JxTags',JxBase)        

class Jx__Menu(QWebView):
	"""A QWebkit Window with mw as parent for Menu related stuff"""
	def __init__(self,name,parent=None):
		QWebView.__init__(self,parent)
		sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
		self.setSizePolicy(sizePolicy)
		self.setMinimumSize(QtCore.QSize(410, 400))
		self.setMaximumSize(QtCore.QSize(410, 16777215))
                                
		self.page().setLinkDelegationPolicy(QWebPage.DelegateAllLinks) # delegates link (to be able to call python function with arguments from HTML)
		self.connect(self, QtCore.SIGNAL('linkClicked (const QUrl&)'), onClick) # delegates link (to be able to call python function with arguments from HTML)
		self.name = name #name that javascript will know
		self.BridgeToJavascript() # add inside javascript namespace
		mw.connect(self.page().mainFrame(),QtCore.SIGNAL('javaScriptWindowObjectCleared()'), self.BridgeToJavascript) #in case of rload, maintains in javascript
		self.hide()
	def BridgeToJavascript(self):
		self.page().mainFrame().addToJavaScriptWindowObject(self.name,self)
                self.page().mainFrame().addToJavaScriptWindowObject("JxTemplateOverride",JxTemplateOverride)	
                self.page().mainFrame().addToJavaScriptWindowObject("JxSettings",JxSettings)     
                self.page().mainFrame().addToJavaScriptWindowObject("JxTags",Jx_Control_Tags)   
	@pyqtSignature("")                
	def Hide(self):
		self.hide()
                
# The main JxPlugin Window
JxWindow = Jx__Menu('JxWindow',mw)






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








class Jx__Browser(QWebView):
	"""A modless QWebkit Window for Stuff that requires lot of space/focus."""
	def __init__(self,parent=None):
		QWebView.__init__(self,parent)
		sizePolicyd = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)	
		sizePolicyd.setHorizontalStretch(QSizePolicy.GrowFlag+QSizePolicy.ShrinkFlag)
		sizePolicyd.setVerticalStretch(QSizePolicy.GrowFlag+QSizePolicy.ShrinkFlag)
		#sizePolicyd.setHeightForWidth(self.sizePolicy().sizeHint())#hasHeightForWidth())
		self.setSizePolicy(sizePolicyd)
		self.setMinimumSize(QtCore.QSize(1200, 600))
		#self.setMaximumSize(QtCore.QSize(210, 16777215))
		self.page().setLinkDelegationPolicy(QWebPage.DelegateAllLinks)
		mw.connect(self, QtCore.SIGNAL('linkClicked (const QUrl&)'), onClick)	
		self.hide()

			
	def sizeHint(self):
		return(QSize(1400,1100))
	
	
	
# I now have 2windows =^.^=
JxPreview = Jx__Browser()




def JxBrowse():
		
	JxAnswerSettings = Jx__Model_CardModel_String("JxAnswerSettings")
	JxPreview.page().mainFrame().addToJavaScriptWindowObject("JxAnswerSettings",JxAnswerSettings)	
	mw.connect( JxPreview.page().mainFrame(),QtCore.SIGNAL('javaScriptWindowObjectCleared()'), Rah);
	JxPreview.setWindowTitle(u"Css and Template Browser")
        from html import Jx_Html_Preview
	JxPreview.setHtml(Jx_Html_Preview,JxResourcesUrl)
	JxPreview.activateWindow()
	JxPreview.show()



from PyQt4.QtWebKit import *

	


def onJxGraphs():
        from graphs import JxParseFacts4Stats, JxNewAlgorythm
        if not CardId2Types:
                JxParseFacts4Stats() 
        JxGraphsJSon =JxNewAlgorythm()
        from html import Jx_Html_Graphs
        JxHtml = Jx_Html_Graphs % (dict([('JSon:'+Type+'|'+str(k),"[" + ",".join(['{ label: "'+ String +'",data :'+ JxGraphsJSon[(Type,k,Key)] +'}' for (Key,String) in (reversed(Map.Order+[('Other','Other')]))]) +"]") for (Type,List) in JxStatsMap.iteritems() for (k,Map) in enumerate(List)]))
        JxProfile("JxGraphs().Substitute done")
        JxPreview.setHtml(JxHtml ,JxResourcesUrl)
        JxProfile("JxGraphs().Preview.SetHtml")
        JxPreview.show() 




# needed to run javascript inside JxWindow
QWebSettings.globalSettings().setAttribute(QWebSettings.JavascriptEnabled, True)
QWebSettings.globalSettings().setAttribute(QWebSettings.JavascriptCanOpenWindows, True)


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
	mw.mainWin.actionJxMenu.setStatusTip('Stats, Tools ans Settings for Japanese')
        mw.mainWin.actionJxMenu.setEnabled(not not mw.deck)
	mw.connect(mw.mainWin.actionJxMenu, QtCore.SIGNAL('triggered()'), onJxMenu)

	# creates graph entry
	mw.mainWin.actionJxGraphs = QtGui.QAction('JxGraphs', mw)
	mw.mainWin.actionJxGraphs.setStatusTip('Graphs for Japanese')
	mw.mainWin.actionJxGraphs.setEnabled(not not mw.deck)
	mw.connect(mw.mainWin.actionJxGraphs, QtCore.SIGNAL('triggered()'), onJxGraphs)

	# creates menu in the plugin sub menu
	#mw.mainWin.pluginMenu = mw.mainWin.menubar.addMenu('&JPlugin')
	#mw.mainWin.pluginMenu.addAction(mw.mainWin.actionJStats)

	#mw.mainWin.actionJStats.setShortcut(_("Ctrl+J"))


	# adds the plugin icons in the Anki Toolbar
	
	mw.mainWin.toolBar.addAction(mw.mainWin.actionJxMenu)
	mw.mainWin.toolBar.addAction(mw.mainWin.actionJxGraphs)
	
	# to enable or disable Jstats whenever a deck is opened/closed
	mw.deckRelatedMenuItems = mw.deckRelatedMenuItems + ("JxMenu","JxGraphs",)
	
	# Ading features through hooks !
	mw.addHook('drawAnswer', append_JxPlugin) # additional info in answer cards
	mw.addHook('deckClosed', exit_JxPlugin) # additional info in answer cards	

mw.addHook('init', init_JxPlugin)
mw.registerPlugin("Japanese Extended Support", 666)
print 'Japanese Extended Plugin loaded'





JxAnswerSettings={}

def Rah():
	JxAnswerSettings = JxBase.findChild(Jx__Model_CardModel_String,'JxAnswerSettings')	
	JxPreview.page().mainFrame().addToJavaScriptWindowObject("JxAnswerSettings",JxAnswerSettings)	
	JxPreview.page().mainFrame().addToJavaScriptWindowObject("JxSettings",JxSettings)  
        
        
        
        
        
        

	
