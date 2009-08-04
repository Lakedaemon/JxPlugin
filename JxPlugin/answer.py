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
from globalobjects import JxLink
from anki.hooks import *
from anki.utils import hexifyID










def JxReplace(String,Dict):
        try: 
                Tail = String.group(1).split(u",")
                Head = Tail.pop(0)
                if len(Tail)>0 and Tail[0].find(u"=")==False:
                        Container = Tail.pop(0)
                else:
                        Container=u"span"
                Head = u'<'+ Container + u' class="' + re.sub(u":",u"-",Head).rstrip(u"-") + u'">' + Dict[Head] + u"</" + Container + u'span>'                     
                for Item in Tail:
                        if u"=" in Item:
                                (Container,Class)=tuple(Item.split(u"="))
                                Head = u"<" + Container + u' class=">' + Class + u'">' + Head + u"</" + Container + u">" 
                        else:
                                Head = u"<" + Item + u">" + Head + u"</" + Item + u">" 
                return Head
        except KeyError:
                return String.group(0)


###############################################################################################################
#
#    displays aditionnal info  in the answer (Words : JLPT, Kanji : JLPT/Grade/stroke order/related words.
#
###############################################################################################################
Map = {1:"JLPT 1",2:"JLPT 2",3:"JLPT 3",4:"JLPT 4",5:"Other"}
KanjiRange=[c for c in range(ord(u'一'),ord(u'龥'))] + [c for c in range(ord(u'豈'),ord(u'鶴'))]


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
                



###################################################################################################################################################################################
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
    
JxTypeJapanese = [u"japanese",u"Japanese",u"JAPANESE",u"日本語",u"にほんご"]
JxType=[(u'Kanji',[u"kanji",u"Kanji",u"KANJI",u"漢字",u"かんじ"]),(u'Word',[u"word",u"Word",u"WORD",u"単語",u"たんご",u"言葉",u"ことば"]),
(u'Sentence',[u"sentence",u"Sentence",u"SENTENCE",u"文",u"ぶん"]),(u'Grammar',[u"grammar",u"Grammar",u"GRAMMAR",u"文法",u"ぶんぽう"])]    
JxKanjiRange=[unichr(c) for c in range(ord(u'一'),ord(u'龥'))] + [unichr(c) for c in range(ord(u'豈'),ord(u'鶴'))]
JxPonctuation = [unichr(c) for c in range(ord(u'　'),ord(u'〿')+1)]+[u' ',u'      ',u',',u';',u'.',u'?',u'"',u"'",u':',u'/',u'!']
JxPonctuation.remove(u'々')    
    
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
                                        List.append((Type,Field.name,Card.fact[Field.name])) 
                                        break
                                             
        if len(List)<len(Types):
                # there are still missing fields for the types, we could try the "Expression" field next and update the List
                if len(List)>0:
                        (Done,Field) = zip(*List)
                else : 
                        Done=[]
                TempList=[]
                for (Type,TypeList) in JxType:
                        if Type in Types and Type in Done:
                                TempList.append(List.pop(0))
                        elif Type in Types:
                                for Field in Card.fact.model.fieldModels:
                                        if Field.name == u"Expression":
                                                TempList.append((Type,Field.name,Card.fact[Field.name])) 
                                                break 
                List = TempList
                                                
        if len(List)<len(Types):
                # field names and "Expression" have failed, we could still try to guess with the fields content
                # but for the time being, we will pass because I don't know how to choose between two fields that might only have kanas (maybee query other cards to decide between the fields, might be doable for sentences (ponctuation helps) and Kanji (only 1 Kanji character))
                pass
   
        return List
        
# The following function is nearly the same appart from the  and Type in GuessType(Card.fact[u"Expression"]) condition !!!!!
def JxFindTypeAndField(Card,Types):
        # we now try to affect relevant fields for each type (first try fields with the name similar to the type)      
        
        List=[]
        for (Type,TypeList) in JxType:
                if Type in Types:
                        for Field in Card.fact.model.fieldModels:
                                if Field.name in TypeList:
                                        List.append((Type,Field.name,Card.fact[Field.name]))
                                        break
                                             
        if len(List)<len(Types):
                # for the still missing fields, we try to find an "Expression" field next and update the List
                if len(List) > 0:
                        (Done,Field) = zip(*List)
                else : 
                        Done = []
                TempList=[]
                for (Type,TypeList) in JxType:
                        if Type in Types and Type in Done:
                                TempList.append(List.pop(0))
                        elif Type in Types:
                                for Field in Card.fact.model.fieldModels:
                                        if Field.name == u"Expression" and Type in GuessType(Card.fact[u"Expression"]):
                                                TempList.append((Type,Field.name,Card.fact[Field.name])) 
                                                break 
                List=TempList
                
        if len(List)<len(Types):
                # field names and "Expression" have failed, we could still try to guess with the fields content
                # but for the time being, we will pass because I don't know how to choose between two fields that might only have kanas (maybee query other cards to decide between the fields)
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

  


        
def GuessType(String):

        if len(set(unicode(c) for c in String.strip(u'  \t　	')).intersection(JxPonctuation))>0:
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
                
                
############################## not implemented yet                
                
def JxParseForJapaneseCharacters(Card):
        # try to find Kana inside Fields
        
        Set=set()
        for Field in Card.fact.model.fieldModels:   
                Set.update([Field.value])
        if len(Set.intersection(JxPonctuation))>0:
                #it holds Kana, this is related to Japanese, now go and try to find Fields
                return []

        # There is no way this card could be related to Japanese
        return []
                        
################################################################################################################################################               
JxAbbrev = {u'Kanji':u'K',u'Word':u'W',u'Sentence':u'S',u'Grammar':u'G'}

JxFieldsDoc = [
(u'F:Types',u'displays a list of triplets (Type,Field,Content) of possible Types for the Fact of this card, associated to the relevant Field, that holds Content'),
(u'K:',u'displays the Kanji of the Card, if it has a Kanji fact'), 
(u'W:',u'displays the (guessed) Word of the Card, if it has a Word fact'),
(u'S:',u'displays the (guessed) Sentence of the Card, if it has a Sentence fact'),
(u'G:',u'displays the Grammar point of the Card, if it has a Gramar fact'),
(u'F:',u'displays the content of the relevant field of the Fact, if it has one guessed type'),
(u'<Field>',u'displays the content of the <Field> of the Fact')]
def JxDoc(Field,Code,DocString):
        """adds DocString as documentation for ${Field}"""
        pass

def append_JxPlugin(Answer,Card):
    """Append additional information about kanji and words in answer."""


    # Guess the type(s) and the relevant content(s) of the Fact
    JxGuessedList = JxMagicalGuess(Card) # that's it. Chose the right name for the right job. This should always work now, lol...
    
    # Get and translate the new CardModel Template
    JxPrefix = u''
    for (Type,Field,Content) in JxGuessedList:
           JxPrefix += JxAbbrev[Type]
    try:
	    JxAnswer = JxLink[JxPrefix + u':' + Card.cardModel.aformat]
            JxAnswerOk= True
    except KeyError:
            try:
                    JxAnswer = JxLink["D:"+Card.cardModel.aformat]     # in case the right template hasn't been set, we try with the default template "D:"
                    JxAnswerOk = True
            except KeyError: 
	            JxAnswer = Card.cardModel.aformat
                    JxAnswerOk = False



    
    # Then create a dictionnary for all data replacement strings...
    
    JxAnswerDict = {}    
    
    # ${F:Types}
    JxAnswerDict[u"F:Types"] = str(JxGuessedList)    
 
    # ${K:}, ${W:}, ${S:}, ${G:}
    for (Type,TypeList) in JxType:
            JxAnswerDict[JxAbbrev[Type] + u':'] = u""            
    for (Type,Field,Content) in JxGuessedList:
            JxAnswerDict[JxAbbrev[Type] + u':'] = Content
    

    # ${F:}, ${F:Stroke}
    if len(JxGuessedList)>0: 
            Temp = JxGuessedList[0][0]
            Tempa = u"""<span class="KanjiStrokeOrder">%s</span>""" % ''.join([c for c in Temp.strip() if ord(c) in KanjiRange])
    else:
            Temp = u''
            Tempa = u""
    JxAnswerDict[u'F:'] = Temp
    JxAnswerDict[u'F:Stroke'] = Tempa
    
    # ${K:Stroke}, ${W:Stroke}, ${S:Stroke}, ${G:Stroke}
    for (Type,TypeList) in JxType:
            if JxAnswerDict[JxAbbrev[Type]+ u':'] != u"":
                    Temp =  u"""<span class="KanjiStrokeOrder">%s</span>""" % ''.join([c for c in JxAnswerDict[JxAbbrev[Type] + u':'].strip() if ord(c) in KanjiRange])
            else:
                    Temp =  u""
            JxAnswerDict[JxAbbrev[Type] + u":Stroke"] = Temp
            
    # ${W:JLPT}
    try:
            JxAnswerDict[u"W:JLPT"] =  u"""<span class="JLPT">%s</span>""" % MapJLPTTango.String(JxAnswerDict[u'W:'])
    except KeyError:
	    JxAnswerDict[u"W:JLPT"] =  u""
            
    # ${W:Freq}
    try:
            JxAnswerDict[u"W:Freq"] =  u"""<span class="Frequency">LFreq %s</span>"""  % MapFreqTango.Value(JxAnswerDict[u'W:'], lambda x:int(100*(log(x+1,2)-log(MinWordFrequency+1,2))/(log(MaxWordFrequency+1,2)-log(MinWordFrequency+1,2)))) 
    except KeyError:
	    JxAnswerDict[u"W:Freq"] =  u""
            
 
    # ${K:JLPT}
    try:
            JxAnswerDict[u"K:JLPT"] =  u"""<span class="JLPT">%s</span>""" % MapJLPTKanji.String(JxAnswerDict[u'K:'])
    except KeyError:
            JxAnswerDict[u"K:JLPT"] =  u""
            
	
    # ${K:Jouyou}	
    try:
            JxAnswerDict[u"K:Jouyou"] =  """<span class="Jouyou">%s</span>""" % MapJouyouKanji.String(JxAnswerDict[u'K:'])
    except KeyError:
            JxAnswerDict[u"K:Jouyou"] =  u""

    # ${K:Freq}
    try:    
            JxAnswerDict[u"K:Freq"] = u"""<span class="Frequency">LFreq %s</span>"""  % MapFreqKanji.Value(JxAnswerDict[u'K:'], lambda x:int((log(x+1,2)-log(MaxFrequency+1,2))*10+100))
    except KeyError:
            JxAnswerDict[u"K:Freq"] = u""	
            
    try : # Finds all word facts whose expression uses the Kanji and returns a table with expression, reading, meaning            
            query = """select expression.value, reading.value, meaning.value from 
            fields as expression, fields as reading, fields as meaning, fieldModels as fmexpression, fieldModels as fmreading, fieldModels as fmmeaning where 
            expression.fieldModelId= fmexpression.id and fmexpression.name="Expression" and 
            reading.fieldModelId= fmreading.id and fmreading.name="Reading" and reading.factId=expression.factId and 
            meaning.fieldModelId= fmmeaning.id and fmmeaning.name="Meaning" and meaning.factId=expression.factId and 
            expression.value like "%%%s%%" """ % JxAnswerDict[u'K:']
                
            # implement a control to limit the number of words displayed 

            # HTML Buffer 
            JxHtmlBuffer = u"" 
            Boolean = True
            # Adds the words to the HTML Buffer 
            for (u,v,w) in mw.deck.s.all(query):
                    if Boolean:
                            JxHtmlBuffer += u""" <tr class="odd Words"><td ><span class="%s">%s </span></td><td><span class="%s">%s</span></td><td><span class="%s"> %s</td></tr>
			        """ % (u"Kanji",u.strip(),u"Romaji" ,w.strip(),u"Kana",v.strip())
                    else:
                            JxHtmlBuffer += u""" <tr class="even Words"><td><span class="%s">%s </span></td><td><span class="%s">%s</span></td><td><span class="%s"> %s</td></tr>
			        """ % (u"Kanji",u.strip(),u"Romaji" ,w.strip(),u"Kana",v.strip())     
                    Boolean = not(Boolean)
            # if there Html Buffer isn't empty, adds it to the card info
            if len(JxHtmlBuffer):
                    JxAnswerDict[u"K:Words"] = u"""<table style="text-align:center;" cellspacing="0px" cellpadding="0px" border="0px" align="center">%s</table>""" % JxHtmlBuffer
    except KeyError:
                    JxAnswerDict[u"K:Words"] = u""	
    from ui_menu import JxSettings
    JxAnswerDict[u"Css"] = """<style>%s</style>""" % JxSettings.Get(u'Css')
    
    # ${<Field>}
    for FieldModel in Card.fact.model.fieldModels:
	    JxAnswerDict[FieldModel.name] = '<span class="fm%s">%s</span>' % (
                hexifyID(FieldModel.id), Card.fact[FieldModel.name])
    
    mw.help.showText(JxAnswerDict[u"F:Types"])   
                
    JxAnswer = re.sub("\$\{(.*?)\}",lambda x:JxReplace(x,JxAnswerDict),JxAnswer)
    
                      
    from ui_menu import JxSettings
    Mode=JxSettings.Get(u'Mode')
    if Mode == "Append" and JxAnswerOk: JxAnswer = Answer + Template(JxAnswer).safe_substitute(JxAnswerDict)
    elif Mode == "Prepend" and JxAnswerOk: JxAnswer =  Template(JxAnswer).safe_substitute(JxAnswerDict) + Answer
    elif Mode == "Override" and JxAnswerOk: JxAnswer = Template(JxAnswer).safe_substitute(JxAnswerDict)
    else : JxAnswer =  Answer

    removeHook("drawAnswer",append_JxPlugin)
    JxAnswer = runFilter("drawAnswer",JxAnswer, Card)
    addHook("drawAnswer",append_JxPlugin)
    return JxAnswer






