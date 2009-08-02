# -*- coding: utf-8 -*-
# Copyright: Olivier Binda <olivier.binda@wanadoo.fr>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
# ---------------------------------------------------------------------------
# This file is a plugin for the "anki" flashcard application http://repose.cx/anki/
# ---------------------------------------------------------------------------
import re
from math import log
from string import Template

from loaddata import *

JxLink = {
"""%(Reading)s""":
	"""${Css}<div style="float:left"><div>${T2JLPT}</div><div>${T2Freq}</div></div><div><center><font style="font-size:500%">${Expression}</font><br /><font style="font-size:300%">${Reading}</font></center></div>""",
"""%(Reading)s<br>%(Meaning)s""":
	"""${Css}<div style="float:left;"><div>${T2JLPT}</div><div>${T2Freq}</div></div><div><center><font style="font-size:300%">${Reading}<br \>${Meaning}</font></center></div>""",
"""%(Kanji)s""":
	"""${Css}<div style="float:left">${Stroke}<div>${K2JLPT}</div><div>${K2Jouyou}</div><div>${K2Freq}</div></div><center>${K2Words}</center>""",
"""%(Meaning)s""":
	"""${Css}<div style="float:left">${Stroke}<div>${K2JLPT}</div><div>${K2Jouyou}</div><div>${K2Freq}</div></div><center><font style="font-size:300%">${Meaning}</font></center><center>${K2Words}</center>""",
"""%(OnYomi)s<br>%(KunYomi)s""":
	"""${Css}<div style="float:left">${Stroke}<div>${K2JLPT}</div><div>${K2Jouyou}</div><div>${K2Freq}</div></div><center><font style="font-size:500%">${OnYomi}<br />${KunYomi}</font></center><center>${K2Words}</center>"""
}
###############################################################################################################
#
#    displays aditionnal info  in the answer (Words : JLPT, Kanji : JLPT/Grade/stroke order/related words.
#
###############################################################################################################
Map = {1:"JLPT 1",2:"JLPT 2",3:"JLPT 3",4:"JLPT 4",5:"Other"}
KanjiRange=[c for c in range(ord(u'一'),ord(u'龥'))] + [c for c in range(ord(u'豈'),ord(u'鶴'))]
JxKanjiRange=[unichr(c) for c in range(ord(u'一'),ord(u'龥'))] + [unichr(c) for c in range(ord(u'豈'),ord(u'鶴'))]
JxPonctuation = [unichr(c) for c in range(ord(u'　'),ord(u'〿')+1)]+[u' ',u'      ',u',',u';',u'.',u'?',u'"',u"'",u':',u'/',u'!']
JxPonctuation.remove(u'々')

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
                
JxTypeJapanese = [u"japanese",u"Japanese",u"JAPANESE",u"日本語",u"にほんご"]
JxType=[(u'Kanji',[u"kanji",u"Kanji",u"KANJI",u"漢字",u"かんじ"]),(u'Word',[u"word",u"Word",u"WORD",u"単語",u"たんご",u"言葉",u"ことば"]),
(u'Sentence',[u"sentence",u"Sentence",u"SENTENCE",u"文",u"ぶん"]),(u'Grammar',[u"grammar",u"Grammar",u"GRAMMAR",u"文法",u"ぶんぽう"])]



def JxMagicalGuess(Card):  
        # for version 1, we are only going to investigate the tags of the Fact & Models, the names of the Model and the Fields.
        
        # first check the facts of the Fact, in case they have only one tag among "Kanji", "Word", "Sentence", "Grammar".
        # mw.help.showText(Card.fact.model.tags + "Fact" + Card.fact.tags)
        

        # First : parse the fact tags
        Types = set()
        JxFactTags = set(Card.fact.tags.split(" "))
        for (Key,List) in JxType:
                if len(JxFactTags.intersection(List))>0:
                        Types.update([Key])
        # Types countains the numerous possible type of the card
        # 0 -> usuall case (no restriction) we know nothing. Parse further ! Later, we might check for the Japanese Tag.
        # 1 -> we found the type, now affect the related field
        # 2 & 3 & 4 -> the user is (posibly wrongly) telling that he wants this card to be considered of those types (what to do now ? affecting the fields). 
        
        if len(Types)>=1:
                return JxAffectFields(Card,Types)
                # needed for stats and graphs. We need to know on what field we are working. 
                # -> Expression if japanese model
        else:
                return JxParseModelTags(Card)
                # Tex-Like programmation, to avoid nested ifs
                
def JxAffectFields(Card,Types):
        # we now try to affect relevant fields for each type (first try fields with the name similar to the type)
        List=[]
        for (Type,TypeList) in JxType:
                if Type in Types:
                        for Field in Card.fact.model.fieldModels:
                                if Field.name in TypeList:
                                        List.append((Type,Field.name)) #possibly put the content of the field in there too
                                        break
                                             
        if len(List)<len(Types):
                # there are still missing fields for the types, we could try the "Expression" field next and update the List
                if len(List)>0:
                        (Done,Field) = zip(*List)
                else : 
                        Done=[]
                Index = 0 
                for (Type,TypeList) in JxType:
                        if Type in Types and Type in Done:
                                Index += 1
                        elif Type in Types:
                                for Field in Card.fact.model.fieldModels:
                                        if Field.name == u"Expression":
                                                List[Index:]=[(Type,Field.name)] + List[Index:] #possibly put the content of the field in there too
                                                break 
                                                
        if len(List)<len(Types):
                # field names and "Expression" have failed, we could still try to guess with the fields content
                # but for the time being, we will pass because I don't know how to choose between two fields that might only have kanas (maybee query other cards to decide between the fields, might be doable for sentences (ponctuation helps) and Kanji (only 1 Kanji character))
                pass
   
        return List
                
def JxParseModelTags(Card):

        # Secondly : parse the model tags (most of the hope is there : it would catch my kanji model, 
        # but do "nothing" for the japanese model except saying that it is a japanese deck)
        Types = set()
        JxModelTags = set(Card.fact.model.tags.split(" "))
        for (Key,List) in JxType:
                if len(JxModelTags.intersection(List))>0:
                        Types.update([Key])  

        # Types countains the numerous possible type of the card as before, yet in a slightly different context
        # 0 -> unusuall case (no type) we still know nothing. Parse further ! Later, we might check for the Japanese Tag...our only hope left resisdes in the name of the model, 
        # of the fields and the contents of the fields (but who knows what the owner put there). Maybee I shouldn't look further than the names (for speed).
        # 1 -> we found the type, now find the related field
        # 2 & 3 & 4 & 5 -> the user is telling what kind of facts he has in this model. We still have to parse further to know exactly how this card is supposed to be displayed
        # (user might want cards in this model to participate to different kind of stats too ?). But we know that we are in the Japanese case. 


        if len(Types) == 1:
                # great, we found the type, now affect the field. 
                return JxAffectFields(Card,Types)

        elif len(Types) >1:
                # we must now find the relevant field to guess the type of the card (names of Model and Fields won't help to determine the type 
                #there because it opposes the model's tags purpose, yet it can help finding the relevant field)
                return JxFindTypeAndField(Card,Types)

        # we will now parse the name of the model, and the names of the fields..and later the content, to reduce the possibilities (for display)
        # we will do the same, except that we don't want to reduce the possibilities, we want to find at least one !
        return JxParseModelName(Card)

  

def JxFindTypeAndField(Card,Types):
        # we now try to affect relevant fields for each type (first try fields with the name similar to the type)      
        
        List=[]
        for (Type,TypeList) in JxType:
                if Type in Types:
                        for Field in Card.fact.model.fieldModels:
                                if Field.name in TypeList:
                                        List.append((Type,Field.name)) #possibly put the content of the field in there too
                                        break
                                             
        if len(List)<len(Types):
                # for the still missing fields, we try to find an "Expression" field next and update the List
                if len(List) > 0:
                        (Done,Field) = zip(*List)
                else : 
                        Done = []
                Index = 0 
                for (Type,TypeList) in JxType:
                        if Type in Types and Type in Done:
                                Index += 1
                        elif Type in Types:
                                for Field in Card.fact.model.fieldModels:
                                        if Field.name == u"Expression" and Type in GuessType(Card.fact["Expression"]):
                                                List[Index:]=[(Type,Field.name)] + List[Index:] #possibly put the content of the field in there too
                                                #break 
        if len(List)<len(Types):
                # field names and "Expression" have failed, we could still try to guess with the fields content
                # but for the time being, we will pass because I don't know how to choose between two fields that might only have kanas (maybee query other cards to decide between the fields)
                pass
        
        return List
        
def GuessType(String):

        if len(set(unicode(c) for c in String).intersection(JxPonctuation))>0:
                #if  String has ponctuations marks, it is a sentence
                return set([u"Sentence"])
        elif unicode(String) in JxKanjiRange:
                #if  String has one Kanji, it is a Kanji (or a Word)
                return set([u"Kanji",u"Word"])                        
        else:              
                #in other cases, it is a word (still don't know what to do with grammar)    
                return set([u"Word"])
        

        

def JxParseModelName(Card):
        # thirdly : parse the name of the model
        
        Types = set()
        for (Key,List) in JxType:
                if Card.fact.model.name in List:
                        Types.update([Key])
                        break # no need to parse further
        
        if len(Types) == 1:
                # great, we found the type, now find the field. 
                return JxAffectFields(Card,Types)

        #Next, we'll parse the names of the fields
        return JxParseFieldsName(Card)

def JxParseFieldsName(Card):
        # tries to find a field with a relevant name and checks for the japanese model last.
        
        Types = set()
        for Field in Card.fact.model.fieldModels:
                for (Key,List) in JxType:
                        if Field.name in List:
                                Types.update([Key])
                                break # no need to parse this Field further
        # same cases than for JxParseModelTags()
        
        if len(Types) ==1:
                # great, we found the type, now find the field. 
                return JxAffectFields(Card,Types)

        elif len(Types) >1:
                # we must now find the relevant field to guess the type of the card 
                 return JxAffectFields(Card,Types)               

        # this should be the usual case for the Japanese model, we'll now check if this is a deck related to Japanese
        return JxParseForJapanese(Card)
   
def JxParseForJapanese(Card):             
        # try to find a Japanese Tag/Name
        Set = set(Card.fact.tags.split(" "))
        Set.update(Card.fact.model.tags.split(" "))
        Set.update([Card.fact.model.name])
        for Field in Card.fact.model.fieldModels:   
                Set.update([Field.name])
        if len(Set.intersection(JxTypeJapanese))>0:
                #this is a model related to japanese (like the japanese model), so people might have put anything in it, try to guess the relevant field and then it's nature                
                return JxFindTypeAndField(Card,set([u'Kanji',u'Word',u'Sentence',u'Grammar']))

        # this set might still be related to japanese if it's content includes Kana (as I expect the japanese user of Anki NOT to use the JxPlugin, 
        # I test for Kana in case there are koreans or chinese users learning japanese, it'll be hard finding the relevant field for those though
        # I expect that anybody wantng to learn japanese will want to display kana readings)
        return JxParseForJapaneseCharacters(Card)
                
                
def JxParseForJapaneseCharacters(Card):
        # try to find Kana inside Fields
        
        Set=set()
        for Field in Card.fact.model.fieldModels:   
                Set.update([Field.value])
        if len(Set.intersection(JxPonctuation))>0:
                #it holds Kana, this is related to Japanese, now go and try to find Fields
                return "gah"

        # There is no way this card could be related to Japanese
        return "boh"
                        
                




#     class Fact(object):  
#        self.tags





#     class Model(object):  
#        self.name = name
#        self.id = genID()
#        self.modified = time.time()
#        self.fieldModels.append(field)
#        self.cardModels.append(card)
#        self.tags

           
def append_JxPlugin(Answer,Card):
    """Append additional information about kanji and words in answer."""
    #mw.help.showText("Card : " + str(Card.id) +"Fact :" + str(Card.fact) + "CardModel : " + str(Card.cardModel.aformat))
    

#    Append = re.search(u"\${.*?}",Answer) == None
################################################################################################################################################
    # try to guess if this is a Tango card or a Kanji card and fill the appropriate data Tango & Expression (for stroke order of tango) or Kanji 

    # Given a card (-> a model & a fact), I have to guess whether it is a Kanji/Word/Sentence/Grammar card so that I can use the correct card template
    # for the "foolish" people who like to put different stuff in the same container and who expect dumb machine code to make the difference
    #
    ## I could display the same card template whether it's a Word/kanji/... (that's probably what they do anyway) but then, they would complain, whine and pester me...
    #
    ## Besides, for stats and Graph, I will have to guess whether a card advances a Kanji/Word/Grammara/Sentence stats...(and guess on which field it applies...sigh...)...
    #
    #
    # Well, this difficult problem requires human intelligence and japanese knowledge to solve it correctly, so i'm going for a simple/generally working solution 
    # (because me and my code are lacking those) that might err sometimes (when it lacks guidance), but I don't care because I'll use tidy deck (and help my code guess with tags and names). I'll try to fully support tidy decks and at leat the japanese model at 99% (won't be able to make the difference between 1 kanji and 1 Kanji word). 

    mw.help.showText(str(JxMagicalGuess(Card))) # that's it. Chose the right name for the right job. This should always work now, lol...

    
    for key in [u"Expression",u"単語",u"言葉"]:
	    try:
		Tango = Tango2Dic(Card.fact[key])
		Expression = ''.join([c for c in Card.fact[key].strip() if ord(c) in KanjiRange])
		break
	    except KeyError:
                Tango = None	
                Expression = None	
		
    for key in [u"Kanji",u"漢字"]:
	    try:
		Kanji = Card.fact[key].strip()
		break
	    except KeyError:
		Kanji = None	
################################################################################################################################################

    # First, get and translate the CardModel Template
    try:
	    JxAnswer = JxLink[Card.cardModel.aformat]
    except KeyError:
	    JxAnswer = Card.cardModel.aformat

    # Then create a dictionnary for all data replacement strings...


    JxAnswerDict = {}
    
    # first fill in the fact information
    for FieldModel in Card.fact.model.fieldModels:
	    JxAnswerDict[FieldModel.name] = Card.fact[FieldModel.name]     #(FieldModel.id, FieldModel.fact[FieldModel.name])
    
    for key in [u"T2JLPT",u"T2Freq",u"Stroke",u"K2JLPT",u"K2Jouyou",u"K2Freq",u"K2Words"]:
	    JxAnswerDict[key] = u""

    JxAnswerDict[u"Stroke"] =  """<span class="LDKanjiStroke">%s</span>""" % Kanji
    if Kanji==None and Expression != None: 
	    JxAnswerDict[u"WStroke"] =  """<span class="LDKanjiStroke">%s</span>""" % Expression
    else:
           JxAnswerDict[u"WStroke"] = u"" 	    
    JxAnswerDict[u"Css"] = """<style> 
    .Kanji { font-family: Meiryo,'Hiragino Kaku Gothic Pro','MS Mincho',Arial,sans-serif; font-weight: normal; text-decoration: none; font-size:2.5em;}
    .Kana { font-family: Meiryo,'Hiragino Kaku Gothic Pro','MS Mincho',Arial,sans-serif; font-weight: normal; text-decoration: none; font-size:1.8em; }
    .Romaji { font-family: Arial,sans-serif; font-weight: normal; text-decoration: none; font-size:1.5em;}
    .JLPT,.Jouyou,.Frequency { font-family: Arial,sans-serif; font-weight: normal; font-size:1.2em;}
    .LDKanjiStroke  { font-family: KanjiStrokeOrders; font-size: 10em;}
    td { padding: 2px 15px 2px 15px;}
    </style>"""


#    if Append:
#	    AnswerBuffer = u"""${Css}"""		
    
    # Word2JLPT
    try:
        JxAnswerDict[u"T2JLPT"] =  u"""<span class="JLPT">%s</span>""" % Map[Word2Data[Tango]]
#	if Append:
#		AnswerBuffer += u""" <div class="JLPT">${T2JLPT}</div>"""
    except KeyError:
	    JxAnswerDict[u"T2JLPT"] =  u""

    # Word2Frequency
    try:
		JxAnswerDict[u"T2Freq"] = u"""<span class="Frequency">LFreq %s</span>"""  % int((log(Word2Frequency[Tango]+1,2)-log(MinWordFrequency+1,2))/(log(MaxWordFrequency+1,2)-log(MinWordFrequency+1,2))*100) 
#		if Append:
#			AnswerBuffer += """ <div class="Frequency">${T2Freq}</div>"""
    except KeyError:
		JxAnswerDict[u"T2Freq"] = u""

    if Kanji != None:
		
		# Stroke Order
#		if Append:
#			AnswerBuffer += u"""<div style="float:left;">${Stroke}</div>"""
			
		# Kanji2JLPT
		try:
			JxAnswerDict[u"K2JLPT"] =  u"""<span class="JLPT">%s</span>""" % Map[Kanji2JLPT[Kanji]]
#			if Append:
#				AnswerBuffer += u""" <div class="JLPT">${K2JLPT}</div>"""
		except KeyError:
			JxAnswerDict[u"K2JLPT"] =  u""
	
		# Kanji2Jouyou	
		try:
			JxAnswerDict[u"K2Jouyou"] =  """<span class="Jouyou">%s</span>""" % MapJouyouKanji["Legend"][Kanji2JLPT[Kanji]]
#			if Append:
#				AnswerBuffer += u""" <div class="Jouyou">${K2Jouyou}</div>"""
		except KeyError:
			JxAnswerDict[u"K2Jouyou"] =  u""

		# Word2Frequency
		try:    
			JxAnswerDict[u"K2Freq"] = u"""<span class="Frequency">LFreq %s</span>"""  % int((log(Kanji2Frequency[Kanji]+1,2)-log(MaxFrequency+1,2))*10+100)
#			if Append:
#				AnswerBuffer += """ <div class="Frequency">${K2Freq}</div>"""
		except KeyError:
			JxAnswerDict[u"K2Freq"] = u""	
				
		# Finds all word facts whose expression uses the Kanji and returns a table with expression, reading, meaning 
		# limit hardcoded to 6
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
#			if Append:
#				AnswerBuffer += """${K2Words}"""
		else:
			JxAnswerDict[u"K2Words"] = u""			
                        
    from ui_menu import JxSettings
    if JxSettings.Mode == "Append": return Answer + Template(JxAnswer).safe_substitute(JxAnswerDict)
    elif JxSettings.Mode == "Prepend": return Template(JxAnswer).safe_substitute(JxAnswerDict) + Answer
    elif JxSettings.Mode == "Bypass": return Answer
    else : return Template(JxAnswer).safe_substitute(JxAnswerDict)





