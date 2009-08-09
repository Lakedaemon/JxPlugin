# -*- coding: utf-8 -*-
# Copyright: Olivier Binda <olivier.binda@wanadoo.fr>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
# ---------------------------------------------------------------------------
# This file is a plugin for the "anki" flashcard application http://ichi2.net/anki/
# ---------------------------------------------------------------------------
import re
from math import log
from string import Template

from loaddata import *
from globalobjects import JxLink
from anki.hooks import *
from anki.utils import hexifyID
import time


def JxReplace(String,Dict):

        Head = String.group(1)
        try:      
                Content = Dict[Head].strip()
        except KeyError:
                Content = u'${'+ Head + u'}'             
        if Content:
                return u'<span class="' + Head + u'">' + Content + u'</span>'
        return u'<span style="border-color:transparent;" class="' + Head + u'">&nbsp;</span>'                


def JxIntReplace(Match):
        Char = Match.group(0)
        if Char=="0": return"Zero"
        elif Char=="1": return"One"
        elif Char=="2": return"Two"
        elif Char=="3": return"Three"
        elif Char=="4": return"Four"
        elif Char=="5": return"Five"
        elif Char=="6": return"Six"
        elif Char=="7": return"Seven"
        elif Char=="8": return"Height"
        elif Char=="9": return"Nine"
        
def JxInt2Name(Int):
        return re.sub(u".",JxIntReplace,str(Int))

def JxTableDisplay(TupleList,Class):
        JxHtmlBuffer = u"" 
        Boolean = True 
        for Tuple in TupleList:
                if Boolean:
                            JxHtmlBuffer += u"""<tr class="Tr-Odd">"""
                else:
                            JxHtmlBuffer += u"""<tr class="Tr-Even">"""
                Boolean = not(Boolean)
                for Index in range(len(Tuple)):
                        JxHtmlBuffer += u'<td class="Td-' + JxInt2Name(Index) + u'">' + Tuple[Index].strip() + u'</td>'
                JxHtmlBuffer += u"</tr>"

        if len(JxHtmlBuffer):
                return u'<table cellspacing="0px" cellpadding="0px" class="' + Class + u'">%s</table>' % JxHtmlBuffer
        else:
                return u""

def JxStrokeDisplay(KanjiList):
        result={}
        Kanjis='","'.join(KanjiList)
        try : # Finds all Kanji facts whose kanji is in the list
                Query = u"""select kanji.value, meaning.value from 
                fields as kanji, fields as meaning, fieldModels as fmkanji, fieldModels as fmmeaning where kanji.fieldModelId= fmkanji.id and fmkanji.name="Kanji" and 
                meaning.fieldModelId= fmmeaning.id and fmmeaning.name="Meaning" and meaning.factId=kanji.factId and
                kanji.value in ("%s")""" % Kanjis
                KanjiQuery=mw.deck.s.all(Query)
        except KeyError:pass
        for item in KanjiQuery:
                result[item[0]]=item[1]
        Kanjis2='","'.join([k for k in KanjiList if k not in result])
        if Kanjis2:
                try : # Now do the same for kanjis in models, that can also have one-kanji-words
                        Query = u"""select expression.value, meaning.value from 
                        fields as expression, fields as meaning, fieldModels as fmexpression, fieldModels as fmmeaning where expression.fieldModelId= fmexpression.id and fmexpression.name="Expression" and 
                        meaning.fieldModelId= fmmeaning.id and fmmeaning.name="Meaning" and meaning.factId=expression.factId and
                        expression.value in ("%s")""" % Kanjis2
                        ExpressionQuery=mw.deck.s.all(Query)
                except KeyError:pass
                for item in ExpressoinQuery:
                        result[item[0]]=item[1]
        ret=''
        for k in KanjiList:
                if k not in result:
                        result[k]=''
                ret+='<span title="' + result[k] + '">'+ k + '</span>'
        return ret
        
        
###############################################################################################################
#
#    displays aditionnal info  in the answer (Words : JLPT, Kanji : JLPT/Grade/stroke order/related words.
#
###############################################################################################################
Map = {1:"JLPT 1",2:"JLPT 2",3:"JLPT 3",4:"JLPT 4",5:"Other"}


JxN = [ord(u'一'),ord(u'龥'),ord(u'豈'),ord(u'鶴')]
def JxIsKanji(Char):
        N = ord(Char)
        if N >=JxN[0]  and N < JxN[1]:
                return True
        if N >=JxN[2]  and N < JxN[3]:
                return True             
        return False

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
    
JxTypeJapanese = ["japanese","Japanese","JAPANESE",u"日本語",u"にほんご"]
JxType=[(u'Kanji',[u"kanji",u"Kanji",u"KANJI",u"漢字",u"かんじ"]),('Word',["word","Word","WORD",u"単語",u"たんご",u"言葉",u"ことば"]),
('Sentence',["sentence","Sentence","SENTENCE",u"文",u"ぶん"]),('Grammar',["grammar","Grammar","GRAMMAR",u"文法",u"ぶんぽう"])]    
JxKanjiRange=[unichr(c) for c in range(ord(u'一'),ord(u'龥'))] + [unichr(c) for c in range(ord(u'豈'),ord(u'鶴'))]
JxPonctuation = [unichr(c) for c in range(ord(u'　'),ord(u'〿')+1)]+[u' ',u'      ',u',',u';',u'.',u'?',u'"',u"'",u':',u'/',u'!']
JxPonctuation.remove(u'々')    
    
def JxMagicalGuess(Card):  
        # for version 1, we are only going to investigate the tags of the Fact & Models, the names of the Model and the Fields.
        
        # first check the facts of the Fact, in case they have only one tag among "Kanji", "Word", "Sentence", "Grammar".

        

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

#### there

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
        if len(String)==1 and JxIsKanji(String):
                #if  String has one Kanji, it is a Kanji (or a Word)
                return set([u"Kanji",u"Word"])    
        elif set(unicode(c) for c in String.strip(u'  \t　	')).intersection(JxPonctuation):
                #if  String has ponctuations marks, it is a sentence
                return set([u"Sentence"])             
        else:              
                #in other cases, it is a word (still don't know what to do with grammar)    
                return set([u"Word"])
        

        
######################################### this can go in JxParsemodelTags -> there : ####
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
        for Field in Card.fact.fields:
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
(u'K',u'displays the Kanji of the Card, if it has a Kanji fact'), 
(u'W',u'displays the (guessed) Word of the Card, if it has a Word fact'),
(u'S',u'displays the (guessed) Sentence of the Card, if it has a Sentence fact'),
(u'G',u'displays the Grammar point of the Card, if it has a Gramar fact'),
(u'F',u'displays the content of the relevant field of the Fact, if it has one guessed type'),
(u'<Field>',u'displays the content of the <Field> of the Fact')]
def JxDoc(Field,Code,DocString):
        """adds DocString as documentation for ${Field}"""
        pass

Jx_Profile=[("Init",time.time())]
def JxInitProfile(String):
        global Jx_Profile
        Jx_Profile=[(String,time.time())]
def JxProfile(String):
        global Jx_Profile
        Jx_Profile.append((String,time.time()))
def JxShowProfile():
        global Jx_Profile
        JxHtml = ""
        for a in range(len(Jx_Profile)):
                (String,Time)=Jx_Profile[a]
                if a==0:
                        JxHtml+="<tr><td>"+ String +"</td><td>"+ str(Time) +"</td></tr>"
                else:
                        JxHtml+="<tr><td>"+ String +"</td><td>"+ str(Time-Jx_Profile[a-1][1]) +"</td></tr>"                
        return "<table>" + JxHtml + "</table>"

        
def append_JxPlugin(Answer,Card):
    """Append additional information about kanji and words in answer."""

    JxProfile("Start")
    
    # Guess the type(s) and the relevant content(s) of the Fact
    JxGuessedList = JxMagicalGuess(Card) # that's it. Chose the right name for the right job. This should always work now, lol...

    JxProfile("Guess")
    
    # Get and translate the new CardModel Template
    JxPrefix = u''
    for (Type,Field,Content) in JxGuessedList:
           JxPrefix += JxAbbrev[Type]
    try:
	    JxAnswer = JxLink[JxPrefix + u'-' + Card.cardModel.aformat]
    except KeyError:
            try:
                    JxAnswer = JxLink["D-"+Card.cardModel.aformat]     # in case the right template hasn't been set, we try with the default template "D:"
            except KeyError: 
                    return Answer
                    
    JxProfile("Get Template")

    
    # Then create a dictionnary for all data replacement strings...
    
    JxAnswerDict = {
        'F':'','F-Stroke':'',
        'K':'','W':'','S':'','G':'',
        'K-Stroke':'','W-Stroke':'','S-Stroke':'','G-Stroke':'',
        "W-JLPT":'','W-Freq':'',
        'K-JLPT':'','K-Jouyou':'','K-Freq':'',
        'K-Words':''
        }    
    
    # ${F-Types}
    JxAnswerDict[u"F-Types"] = str(JxGuessedList)    
 
    # ${K}, ${W}, ${S}, ${G}  and  ${K-Stroke}, ${W-Stroke}, ${S-Stroke}, ${G-Stroke}        
    for (Type,Field,Content) in JxGuessedList:
            ShortType = JxAbbrev[Type]
            Stripped = Content.strip()
            JxAnswerDict[ShortType] = Stripped
            KanjiList=[c for c in Stripped if JxIsKanji(c)]
            if ShortType != 'K':
                    JxAnswerDict[ShortType + "-Stroke"] = JxStrokeDisplay(KanjiList)
            else:
                    JxAnswerDict[ShortType + "-Stroke"] = ''.join(KanjiList)
    
    # need those for performance : every tenth second counts if you review 300+ Card a day
    # (the first brutal implementation had sometimes between 0.5s and 2s of lag to display the answer (i.e. make the user wait).
    
    JxK = JxAnswerDict['K']
    JxW = JxAnswerDict['W']
    JxS = JxAnswerDict['S']
    JxG = JxAnswerDict['G']    
    

    # ${F} and ${F-Stroke}
    if JxGuessedList: 
            JxAnswerDict['F'] = JxGuessedList[0][0].strip()
            JxAnswerDict['F-Stroke'] = u"""%s""" % ''.join([c for c in JxGuessedList[0][0].strip() if JxIsKanji(c)])
    
            

    if JxW:
            try:        # ${W-JLPT}
                    JxAnswerDict['W-JLPT'] =  '%s' % MapJLPTTango.String(JxW)
            except KeyError:pass
            
            try:        # ${W-Freq}
                    JxAnswerDict['W-Freq'] =  '%s'  % MapFreqTango.Value(JxW, lambda x:int(100*(log(x+1,2)-log(MinWordFrequency+1,2))/(log(MaxWordFrequency+1,2)-log(MinWordFrequency+1,2)))) 
            except KeyError:pass
            
    if JxK:
            try:        # ${K:JLPT}
                    JxAnswerDict['K-JLPT'] =  '%s' % MapJLPTKanji.String(JxK)
            except KeyError:pass
            
            try:        # ${K:Jouyou}
                    JxAnswerDict['K-Jouyou'] =  '%s' % MapJouyouKanji.String(JxK)
            except KeyError:pass

            try:        # ${K:Freq}    
                    JxAnswerDict['K-Freq'] = '%s'  % MapFreqKanji.Value(JxK, lambda x:int((log(x+1,2)-log(MaxKanjiOccurences+1,2))*10+100))
            except KeyError:pass
            	
            
            try : # Finds all word facts whose expression uses the Kanji and returns a table with expression, reading, meaning            
                    Query = """select expression.value, meaning.value, reading.value from 
                    fields as expression, fields as reading, fields as meaning, fieldModels as fmexpression, fieldModels as fmreading, fieldModels as fmmeaning where expression.fieldModelId= fmexpression.id and fmexpression.name="Expression" and 
                    reading.fieldModelId= fmreading.id and fmreading.name="Reading" and reading.factId=expression.factId and 
                    meaning.fieldModelId= fmmeaning.id and fmmeaning.name="Meaning" and meaning.factId=expression.factId and 
                    expression.value like "%%%s%%" """ % JxK
                    JxAnswerDict['K-Words'] = JxTableDisplay(mw.deck.s.all(Query),'K-Words')    
            except KeyError:pass
    
    from ui_menu import JxSettings
    JxAnswerDict[u"Css"] = """<style>%s</style>""" % JxSettings.Get(u'Css')
    
    # ${<Field>}
    for FieldModel in Card.fact.model.fieldModels:
	    JxAnswerDict[FieldModel.name] = '<span class="fm%s">%s</span>' % (
                hexifyID(FieldModel.id), Card.fact[FieldModel.name])
                
    JxProfile("Fill JxCodes")
    
    JxAnswer = re.sub("\$\{(.*?)\}",lambda x:JxReplace(x,JxAnswerDict),JxAnswer)
    
    JxProfile("Substitutions")
                      
    from ui_menu import JxSettings
    Mode=JxSettings.Get(u'Mode')
    if Mode == "Append": JxAnswer = Answer + JxAnswer
    elif Mode == "Prepend": JxAnswer += Answer


    JxProfile("Concatenation")    
    
    removeHook("drawAnswer",append_JxPlugin)
    JxAnswer = runFilter("drawAnswer",JxAnswer, Card)
    addHook("drawAnswer",append_JxPlugin)
    
    JxProfile("Filter")
    #JxShowProfile()
    return JxAnswer






