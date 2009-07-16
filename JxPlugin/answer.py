# -*- coding: utf-8 -*-
# Copyright: Olivier Binda <olivier.binda@wanadoo.fr>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
# ---------------------------------------------------------------------------
# This file is a plugin for the "anki" flashcard application http://repose.cx/anki/
# ---------------------------------------------------------------------------
import re
from string import Template
from loaddata import *

###############################################################################################################
#
#    displays aditionnal info  in the answer (Words : JLPT, Kanji : JLPT/Grade/stroke order/related words.
#
###############################################################################################################
Map = {1:"JLPT 1",2:"JLPT 2",3:"JLPT 3",4:"JLPT 4",5:"Other"}

def Tango2Dic(string):
	String = string.strip(u" ")
	if String.endswith(u"する") and len(String)>2:
		return String[0:-2]
	elif (String.endswith(u"な") or String.endswith(u"の") or String.endswith(u"に")) and len(String)>1: #python24 fix for OS X                  
#	elif String.endswith((u"な",u"の",u"に")) and len(String)>1:    #python25
		return String[0:-1]
	else:
		return String

def JxDefaultAnswer(Buffer,String,Dict):
	if re.search(u"\${.*?}",Buffer):
		return String
	else: 
		return Buffer + String
		
def append_JxPlugin(Answer,Card):
    """Append additional information about kanji and words in answer."""
    
    Append = re.search(u"\${.*?}",Answer) == None

    for key in [u"Expression",u"単語",u"言葉"]:
	    try:
		Tango = Tango2Dic(Card.fact[key])
		break
	    except KeyError:
                Tango = None		    
		
    for key in [u"Kanji",u"漢字"]:
	    try:
		Kanji = Card.fact[key].strip()
		break
	    except KeyError:
		Kanji = None	


    JxAnswerDict = {}
    for key in [u"T2JLPT",u"T2Freq",u"Stroke",u"K2JLPT",u"K2Jouyou",u"K2Freq",u"K2Words"]:
	    JxAnswerDict[key] = u""

    JxAnswerDict[u"Stroke"] =  """<span class="LDKanjiStroke">%s</span>""" % Kanji
    JxAnswerDict[u"Css"] = """
    <style> 
    .Kanji { font-family: Meiryo,'Hiragino Kaku Gothic Pro','MS Mincho',Arial,sans-serif; font-weight: normal; text-decoration: none; font-size:2.5em;}
    .Kana { font-family: Meiryo,'Hiragino Kaku Gothic Pro','MS Mincho',Arial,sans-serif; font-weight: normal; text-decoration: none; font-size:1.8em; }
    .Romaji { font-family: Arial,sans-serif; font-weight: normal; text-decoration: none; font-size:1.5em;}
    .JLPT,.Jouyou,.Frequency { font-family: Arial,sans-serif; font-weight: normal; font-size:1.2em;}
    .LDKanjiStroke  { font-family: KanjiStrokeOrders; font-size: 10em;}
    td { padding: 2px 15px 2px 15px;}
    </style>"""


    if Append:
	    AnswerBuffer = u"""${Css}"""		
    
    # Word2JLPT
    try:
        JxAnswerDict[u"T2JLPT"] =  u"""<span class="JLPT">%s</span>""" % Map[Word2Data[Tango]]
	if Append:
		AnswerBuffer += u""" <div class="JLPT">${T2JLPT}</div>"""
    except KeyError:
	    pass

    # Word2Frequency
    try:
		JxAnswerDict[u"T2Freq"] = u"""<span class="Frequency">LFreq %s</span>"""  % int((math.log(Word2Frequency[Tango]+1,2)-math.log(MinWordFrequency+1,2))/(math.log(MaxWordFrequency+1,2)-math.log(MinWordFrequency+1,2))*100) 
		if Append:
			AnswerBuffer += """ <div class="Frequency">${T2Freq}</div>"""
    except KeyError:
		pass

    if Kanji != None:
		
		# Stroke Order
		if Append:
			AnswerBuffer += u"""<div style="float:left;">${Stroke}</div>"""
			
		# Kanji2JLPT
		try:
			JxAnswerDict[u"K2JLPT"] =  """<span class="JLPT">%s</span>""" % Map[Kanji2JLPT[Kanji]]
			if Append:
				AnswerBuffer += u""" <div class="JLPT">${K2JLPT}</div>"""
		except KeyError:
			pass
	
		# Kanji2Jouyou	
		try:
			JxAnswerDict[u"K2Jouyou"] =  """<span class="Jouyou">%s</span>""" % MapJouyouKanji["Legend"][Kanji2JLPT[Kanji]]
			if Append:
				AnswerBuffer += u""" <div class="Jouyou">${K2Jouyou}</div>"""
		except KeyError:
			pass

		# Word2Frequency
		try:    
			JxAnswerDict[u"K2Freq"] = u"""<span class="Frequency">LFreq %s</span>"""  % int((math.log(Kanji2Frequency[Kanji]+1,2)-math.log(MaxFrequency+1,2))*10+100)
			if Append:
				AnswerBuffer += """ <div class="Frequency">${K2Freq}</div>"""
		except KeyError:
			pass		
				
		# Finds all word facts whose expression uses the Kanji and returns a table with expression, reading, meaning
		query = """select expression.value, reading.value, meaning.value from 
		fields as expression, fields as reading, fields as meaning, 
		fieldModels as fmexpression, fieldModels as fmreading, fieldModels as fmmeaning where 
		expression.fieldModelId= fmexpression.id and fmexpression.name="Expression" and 
		reading.fieldModelId= fmreading.id and fmreading.name="Reading" and reading.factId=expression.factId and 
		meaning.fieldModelId= fmmeaning.id and fmmeaning.name="Meaning" and meaning.factId=expression.factId and 
		expression.value like "%%%s%%" """ % Kanji

		# HTML Buffer 
		info = "" 
		# Adds the words to the HTML Buffer 
		for (u,v,w) in mw.deck.s.all(query):
			info += """ <tr><td><span class="%s">%s </span></td><td><span class="%s">%s</span></td><td><span class="%s"> %s</td></tr>
			""" % ("Kanji",u.strip(),"Romaji" ,w.strip(),"Kana",v.strip())

		# if there Html Buffer isn't empty, adds it to the card info
		if len(info):
			JxAnswerDict[u"K2Words"] = """<table style="text-align:center;" align="center">%s</table>""" % info
			if Append:
				AnswerBuffer += """${K2Words}"""
		else:
			pass			

    if Append:
	    return Template(Answer+AnswerBuffer).safe_substitute(JxAnswerDict)
    else:
	    return Template(Answer).safe_substitute(JxAnswerDict)





