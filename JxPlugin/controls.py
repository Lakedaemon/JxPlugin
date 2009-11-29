# -*- coding: utf-8 -*-
# Copyright: Olivier Binda <olivier.binda@wanadoo.fr>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
# ---------------------------------------------------------------------------
# This file is a plugin for the "anki" flashcard application http://ichi2.net/anki/
# ---------------------------------------------------------------------------
import os
import cPickle
import re 

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtWebKit import *
from PyQt4 import QtGui, QtCore
from PyQt4.QtWebKit import QWebPage, QWebView

from ankiqt import mw

from metacode import Jx__Prop
from globalobjects import JxLink
from tools import ensureDirExists
from ui_menu import *
from answer import JxReplace

JxBase = QObject()



class Jx__Settings(QObject):
	"""Data class for the settings of the JxPlugin"""
	def __init__(self,name="JxSettings",parent=JxBase):
		QObject.__init__(self,parent)
		self.setObjectName(name)
                self.File = os.path.join(os.path.dirname(__file__ ), "Settings.pickle")
                self.Load()
         
        @pyqtSignature("QString", result="QString")	
	def Get(self,Key):
                return self.Dict[u"%s" % Key]
                
        @pyqtSignature("QString, QString")	
	def Set(self,Key,Value):
                self.Dict[u"%s" % Key] = str(Value)
                self.Update()
                  
        def Load(self):
                from default import  Jx__Css__Default
                self.Dict = {"Mode":"Override","Css":Jx__Css__Default,'reportReset':'1','cacheRebuild':'14'}
                if os.path.exists(self.File):
                          File = open(self.File, 'rb')
                          self.Dict.update(cPickle.load(File))
                          File.close()

        def Update(self):
                File = open(self.File, 'wb')
                cPickle.dump(self.Dict, File, cPickle.HIGHEST_PROTOCOL)
                File.close()
        

class PythonJavascript(QObject):
    """implements methods to move int between python and javascript"""
    def __init__(self,name,parent=JxBase):
	QObject.__init__(self,parent)
	self.setObjectName(name)
	
    @pyqtSignature("QString",result="QString")		
    def get(self,var):
        from database import eDeck
        if var =="cardsKnownThreshold":            
            return "%s" % eDeck.cardsKnownThreshold
        elif var =="factsKnownThreshold":            
            return "%s" % eDeck.factsKnownThreshold
        elif var =="atomsKnownThreshold":            
            return "%s" % eDeck.atomsKnownThreshold
        elif var in ['JLPT','Frequency', 'Kanken','Jouyou']:
            from ui_menu import JxStats
            return JxStats(str(var))
        elif var =="kanjiMode":            
            return "%s" % eDeck.kanjiMode
            
    @pyqtSignature("QString,QString")		
    def set(self,var,value)	:
        from database import eDeck
        if var =="cardsKnownThreshold":    
            eDeck.set_cardsKnownThreshold(int(value))
        elif var =="factsKnownThreshold":            
            eDeck.set_factsKnownThreshold(float(value))
        elif var =="atomsKnownThreshold":            
            eDeck.set_atomsKnownThreshold(float(value))            
        elif var =="kanjiMode":            
            eDeck.set_kanjiMode(int(value))             
                    
class Jx__Entry_Source_Target(QObject):
	"""Data class for the HtmlJavascript Entry/Name/Source/Target Widget"""
	def __init__(self,name,parent=JxBase):
		QObject.__init__(self,parent)
		self.setObjectName(name)
		self.File = os.path.join(os.path.dirname(__file__ ),"User","JxTable.cpickle")
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
	        ensureDirExists("User")
		File = open(self.File, "wb")  
                cPickle.dump(self.Table, File, cPickle.HIGHEST_PROTOCOL)
		File.close()

        def ResetJxLink(self):
                Jxlink={}
                for (Name, Source,Target) in self.Table:
                        JxLink[Source] = Target                                  
   
   
   
   
   
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
	







class Jx__MultiSelect(QObject):
	"""Data class for the HtmlJavascript Multiselect Widget"""
	def __init__(self,name,parent=JxBase):
		QObject.__init__(self,parent)
		self.setObjectName(name)
                self.name = name
		self.Javascript=u"""
                        function ReturnField(){return (document.getElementById("%(Id)s").selected)?document.getElementById("%(Id)s").innerHTML:"";}
                        ReturnField();
                        """
        def Update(self):
		self.Models = mw.deck.s.column0(u"""select name from models group by name order by name""")
		self.FieldModels = mw.deck.s.column0(u"""select name from fieldModels group by name order by name""")                        
	@pyqtSignature("",result="QString")
	def GetOptions(self):     
		Buffer =  u"""<option id="Model" selected="selected">All</option>"""
		Buffer +=  u"""<optgroup label="Models">"""
		JxPopulateModels = []
		for Name in self.Models:
                        Buffer +=  u"""<option id="%(Id)s" selected="selected">%(Name)s</option> """ % {"Name":Name,"Id":u"Model."+ Name}
                        JxPopulateModels.append(Name)
		Buffer +=  u"""</optgroup>"""
		Buffer +=  u"""<optgroup label="Fields">"""
		for Name in self.FieldModels:
                        Buffer +=  u"""<option id="%(Id)s" selected="selected">%(Name)s</option> """ % {"Name":Name,"Id":u"Field."+ Name}
		Buffer +=  u"""</optgroup>"""
		return Buffer
	@pyqtSignature("")
	def TagThemAll(self):
		Models = []
		for Name in self.Models:
                        Value = str(JxWindow.page().mainFrame().evaluateJavaScript(self.Javascript % {"Id":u"Model." + Name}).toString())
                        if Value != u"":
                                Models.append(Value)                        
		Fields = []
		for Name in self.FieldModels:
                        Value = str(JxWindow.page().mainFrame().evaluateJavaScript(self.Javascript % {"Id":u"Field." + Name}).toString())
                        if Value != u"":
                                Fields.append(Value)
		from tools import JxTagDuplicates
		JxTagDuplicates(u"""select fields.value, facts.id, facts.created, facts.tags from fields,facts,fieldModels,models where 
		facts.id = fields.factId and fields.fieldModelId = fieldModels.id and facts.modelId = models.id and  
		fieldModels.name in ('""" + "','".join(Fields) + """') and models.name in  ('""" + "','".join(Models) + """') group by facts.id order by fields.value """)

from PyQt4.QtWebKit import QWebPage, QWebView
from PyQt4 import QtGui, QtCore

def onClick(url):
        String = unicode(url.toString())
	if String.startswith("py:"):
	        String = String[3:]
	        from ui_menu import JxShowIn,JxShowOut, JxBrowse
	        from export import JxAddo, JxDoNothing
	        eval(String)
	else:
	        from PyQt4.QtGui import QDesktopServices
	        QDesktopServices.openUrl(QUrl(url))

JxSettings = Jx__Settings()
JxTemplateOverride = Jx__Entry_Source_Target("JxTemplateOverride")             
Jx_Control_Tags = Jx__MultiSelect('JxTags',JxBase) 
Jx_Control_Bridge = PythonJavascript('py',JxBase)

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
	def BridgeToJavascript(self): # I should automate this todo
		self.page().mainFrame().addToJavaScriptWindowObject(self.name,self)
                self.page().mainFrame().addToJavaScriptWindowObject("JxTemplateOverride",JxTemplateOverride)	
                self.page().mainFrame().addToJavaScriptWindowObject("JxSettings",JxSettings)     
                self.page().mainFrame().addToJavaScriptWindowObject("JxTags",Jx_Control_Tags)   
                self.page().mainFrame().addToJavaScriptWindowObject("py",Jx_Control_Bridge)  
	@pyqtSignature("")                
	def Hide(self):
		self.hide()
JxWindow = Jx__Menu('JxWindow',mw)

# I now have 2windows =^.^=

class Jx__Browser(QWebView):
	"""A modless QWebkit Window for Stuff that requires lot of space/focus."""
	def __init__(self,parent=None):
		QWebView.__init__(self,parent)
		sizePolicyd = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)	
		sizePolicyd.setHorizontalStretch(QSizePolicy.GrowFlag+QSizePolicy.ShrinkFlag)
		sizePolicyd.setVerticalStretch(QSizePolicy.GrowFlag+QSizePolicy.ShrinkFlag)
		#sizePolicyd.setHeightForWidth(self.sizePolicy().sizeHint())#hasHeightForWidth())
		self.setSizePolicy(sizePolicyd)
      		rect=QtGui.QApplication.desktop().availableGeometry()
		self.setMinimumSize(QtCore.QSize(min(1200,rect.width()), min(600,rect.height()-10)))
		#self.setMaximumSize(QtCore.QSize(210, 16777215))
		self.page().setLinkDelegationPolicy(QWebPage.DelegateAllLinks)
		mw.connect(self, QtCore.SIGNAL('linkClicked (const QUrl&)'), onClick)	
		self.BridgeToJavascript() # add inside javascript namespace
		mw.connect(self.page().mainFrame(),QtCore.SIGNAL('javaScriptWindowObjectCleared()'), self.BridgeToJavascript) #in case of rload, maintains in javascript
		self.hide()
	def BridgeToJavascript(self): # I should automate this todo
	        	JxAnswerSettings = JxBase.findChild(Jx__Model_CardModel_String,'JxAnswerSettings')	
	        	self.page().mainFrame().addToJavaScriptWindowObject("JxAnswerSettings",JxAnswerSettings)	
	        	self.page().mainFrame().addToJavaScriptWindowObject("JxSettings",JxSettings)  
	def sizeHint(self):
      		rect=QtGui.QApplication.desktop().availableGeometry()
		return(QSize(min(1400,rect.width()), min(1100,rect.height()-10)))

		
JxPreview = Jx__Browser()

# needed to run javascript inside JxWindow
QWebSettings.globalSettings().setAttribute(QWebSettings.JavascriptEnabled, True)
QWebSettings.globalSettings().setAttribute(QWebSettings.JavascriptCanOpenWindows, True)
