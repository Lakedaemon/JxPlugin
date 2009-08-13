# -*- coding: utf-8 -*-
# Copyright: Olivier Binda <olivier.binda@wanadoo.fr>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
# ---------------------------------------------------------------------------
# This file is a plugin for the "anki" flashcard application http://ichi2.net/anki/
# ---------------------------------------------------------------------------
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from ankiqt import mw
from ui_menu import JxBase

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
 
