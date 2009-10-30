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
from japanese.furigana import rubify
from globalobjects import JxProfile,Jx_Profile,JxShowProfile,JxInitProfile

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
        elif Char=="8": return"Eight"
        elif Char=="9": return"Nine"
        
def JxInt2Name(Int):
        return re.sub(u".",JxIntReplace,str(Int))

def JxTableDisplay(TupleList,Class,Type=None):
        if Type != None:
                tupleStart=1
        else:
                tupleStart=0

        JxHtmlBuffer = u"" 
        Boolean = True 
        for Tuple in TupleList:
                if Type != None:
                        from JxPlugin.database import eDeck 
                        Types= [type for (type,list) in JxType if type in eDeck.types[Tuple[0]]] 
                if Type == None or Type in Types:
                        if Boolean:
                                    JxHtmlBuffer += u"""<tr class="Tr-Odd">"""
                        else:
                                    JxHtmlBuffer += u"""<tr class="Tr-Even">"""
                        Boolean = not(Boolean)
                        for Index in range(tupleStart,len(Tuple)):
                                JxHtmlBuffer += u'<td class="Td-' + JxInt2Name(Index) + u'">' + rubify(Tuple[Index].strip()) + u'</td>'
                        JxHtmlBuffer += u"</tr>"

        if len(JxHtmlBuffer):
                return u'<table cellspacing="0px" cellpadding="0px" class="' + Class + u'">%s</table>' % JxHtmlBuffer
        else:
                return u""

def JxStrokeDisplay(KanjiList,Class):
        # Maybee we should use the Card2Type fonction to filter out the wordswrong K/W but it's working as is and it'll have to wait for an upgrade of the guesstype function...
        # the "title" tag is a bit slow and tiny, maybee we should inject some javascript/use a nice jquery tooltip plugin... but this will have to wait till we allow javascript inside the main QWebView window (We''ll have to convince damien to set a nice resource directory for javascript..or override hisroutines).
       
        Kanjis='","'.join(KanjiList)
        # Finds all Kanji facts whose kanji is in the list
        Query = u"""select kanji.value, meaning.value from 
        fields as kanji, fields as meaning, fieldModels as fmkanji, fieldModels as fmmeaning where kanji.fieldModelId= fmkanji.id and fmkanji.name in ("%s") and 
        meaning.fieldModelId= fmmeaning.id and fmmeaning.name="Meaning" and meaning.factId=kanji.factId and kanji.value in ("%s")""" % ('","'.join(JxTypeHash[u'Kanji'])+'","'+JxExpression,Kanjis)
        Rows = mw.deck.s.all(Query)

        Meaning = {}
        for Item in Rows:
                if Item[0] not in Meaning:
                        Meaning[Item[0]]=[]
                if Item[1] not in Meaning[Item[0]]:
                        Meaning[Item[0]].append(Item[1])
        #mw.help.showText(str(Meaning))
        Buffer = ''
        for Kanji in KanjiList:
                if Kanji in Meaning:
                        Buffer += '<span class="' + Class + '-Kanji" title="' + ' | '.join(Meaning[Kanji]) + '">'+ Kanji + '</span><span style="font-size:1px;width:1px;height:1px"> </span>' # the ' ' allows a linbreak after every kanji, but if two of them fit in the box, it doent break
                else:
                        Buffer += '<span class="' + Class + '-Kanji">'+ Kanji + '</span><span style="font-size:1px;width:1px;height:1px"> </span>'
        return Buffer
        
        
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



    
JxTypeJapanese = ["japanese","Japanese","JAPANESE",u"日本語",u"にほんご"]
JxType=[('Kanji',["kanji","Kanji","KANJI",u"漢字",u"かんじ"]),('Word',["word","Word","WORD",u"単語",u"たんご",u"言葉",u"ことば"]),
('Sentence',["sentence","Sentence","SENTENCE",u"文",u"ぶん"]),('Grammar',["grammar","Grammar","GRAMMAR",u"文法",u"ぶんぽう"])]    
JxTypeHash={u'Kanji':[u"kanji",u"Kanji",u"KANJI",u"漢字",u"かんじ"],'Word':["word","Word","WORD",u"単語",u"たんご",u"言葉",u"ことば"],
'Sentence':["sentence","Sentence","SENTENCE",u"文",u"ぶん"],'Grammar':["grammar","Grammar","GRAMMAR",u"文法",u"ぶんぽう"]}
JxExpression='expression","Expression","EXPRESSION'
JxKanjiRange=[unichr(c) for c in range(ord(u'一'),ord(u'龥'))] + [unichr(c) for c in range(ord(u'豈'),ord(u'鶴'))]
JxPonctuation = [unichr(c) for c in range(ord(u'　'),ord(u'〿')+1)]+[u' ',u'      ',u',',u';',u'.',u'?',u'"',u"'",u':',u'/',u'!']
JxPonctuation.remove(u'々')    
    

from anki.utils import stripHTML


        
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
        
               

                        
################################################################################################################################################               
JxAbbrev = {u'Kanji':u'K',u'Word':u'W',u'Sentence':u'S',u'Grammar':u'G'}

JxFieldsDoc = [
('F:Types','displays a list of triplets (Type,Field,Content) of possible Types for the Fact of this card, associated to the relevant Field, that holds Content'),
('K','displays the Kanji of the Card, if it has a Kanji fact'), 
('W','displays the (guessed) Word of the Card, if it has a Word fact'),
('S','displays the (guessed) Sentence of the Card, if it has a Sentence fact'),
('G','displays the Grammar point of the Card, if it has a Grammar fact'),
('F','displays the content of the relevant field of the Fact, if it has one guessed type'),
('<Field>','displays the content of the <Field> of the Fact')]
def JxDoc(Field,Code,DocString):
        """adds DocString as documentation for ${Field}"""
        pass


# I'll have to change that when I'll star supporting streaming questions/answers to Anki.nds/Android
def append_JxPlugin(Answer,Card):
    """Append additional information about kanji and words in answer."""

    
    # Guess the type(s) and the relevant content(s) of the Fact
    from database import eDeck  
    types = eDeck.types[Card.factId]
    JxGuessedList = [(type,"", types[type]) for (type,list) in JxType if type in types]

    
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
                    


    
    # Then create a dictionnary for all data replacement strings...
    
    JxAnswerDict = {
        'F':'','F-Stroke':'',
        'K':'','W':'','S':'','G':'',
        'K-Stroke':'','W-Stroke':'','S-Stroke':'','G-Stroke':'',
        "W-JLPT":'','W-Freq':'',
        'K-JLPT':'','K-Jouyou':'','K-Freq':'',
        'K-Words':'',
        'W-Sentences':''
        }    
    
    # ${F-Types}
    JxAnswerDict['F-Types'] = str(JxGuessedList)    
 
    # ${K}, ${W}, ${S}, ${G}  and  ${K-Stroke}, ${W-Stroke}, ${S-Stroke}, ${G-Stroke}        
    for (Type,Field,Content) in JxGuessedList:
            ShortType = JxAbbrev[Type]
            Stripped = Content.strip()
            JxAnswerDict[ShortType] = Stripped
            KanjiList= [c for c in Stripped if JxIsKanji(c)]
            if ShortType != 'K':
                    JxAnswerDict[ShortType + '-Stroke'] = JxStrokeDisplay(KanjiList,ShortType + '-Stroke')
            else:
                    JxAnswerDict[ShortType + '-Stroke'] = ''.join(KanjiList)
    
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
                    JxAnswerDict['W-Freq'] =  '%s'  % MapFreqTango.Value(JxW, lambda x:int(100*(log(x+1,2)-log(Jx_Word_MinOccurences+1,2))/(log(Jx_Word_MaxOccurences+1,2)-log(Jx_Word_MinOccurences+1,2)))) 
            except KeyError:pass

            Query = """select expression.factId, expression.value, meaning.value, reading.value from 
            fields as expression, fields as reading, fields as meaning, fieldModels as fmexpression, fieldModels as fmreading, fieldModels as fmmeaning where expression.fieldModelId= fmexpression.id and fmexpression.name in ("%s") and reading.fieldModelId= fmreading.id and fmreading.name="Reading" and reading.factId=expression.factId and meaning.fieldModelId= fmmeaning.id and fmmeaning.name="Meaning" and meaning.factId=expression.factId and
            expression.factId != "%s" and
            expression.value like "%%%s%%" """ % ('","'.join(JxTypeHash[u'Sentence'])+'","'.join(JxTypeHash[u'Word'])+'","'+'","'+JxExpression,Card.factId,JxW)
            result=mw.deck.s.all(Query)
            JxAnswerDict['W-Sentences'] = JxTableDisplay(result,'W-Sentences',u'Sentence')    
            JxAnswerDict['W-Words'] = JxTableDisplay(result,'W-Words',u'Word') #for idioms and compound words    

    if JxK:
            try:        # ${K:JLPT}
                    JxAnswerDict['K-JLPT'] =  '%s' % MapJLPTKanji.String(JxK)
            except KeyError:pass
            
            try:        # ${K:Jouyou}
                    JxAnswerDict['K-Jouyou'] =  '%s' % MapJouyouKanji.String(JxK)
            except KeyError:pass

            try:        # ${K:Freq}    
                    JxAnswerDict['K-Freq'] = '%s'  % MapFreqKanji.Value(JxK, lambda x:int((log(x+1,2)-log(Jx_Kanji_MaxOccurences+1,2))*10+100))
            except KeyError:pass      	       
            
            Query = """select expression.factId, expression.value, meaning.value, reading.value from 
            fields as expression, fields as reading, fields as meaning, fieldModels as fmexpression, fieldModels as fmreading, fieldModels as fmmeaning where expression.fieldModelId= fmexpression.id and fmexpression.name in ("%s") and reading.fieldModelId= fmreading.id and fmreading.name="Reading" and reading.factId=expression.factId and meaning.fieldModelId= fmmeaning.id and fmmeaning.name="Meaning" and meaning.factId=expression.factId and
            expression.factId != "%s" and
            expression.value like "%%%s%%" """ % ('","'.join(JxTypeHash[u'Sentence'])+'","'+'","'.join(JxTypeHash[u'Word'])+'","'+JxExpression,Card.factId,JxK)
            result=mw.deck.s.all(Query)
            JxAnswerDict['K-Words'] = JxTableDisplay(result,'K-Words',u'Word')    
            JxAnswerDict['K-Sentences'] = JxTableDisplay(result,'K-Sentences',u'Sentence')    

    
    from controls import JxSettings
    JxAnswerDict['Css'] = '<style>%s</style>' % JxSettings.Get(u'Css')
    
    # ${<Field>}
    for FieldModel in Card.fact.model.fieldModels:
	    JxAnswerDict[FieldModel.name] = '<span class="fm%s">%s</span>' % (
                hexifyID(FieldModel.id), Card.fact[FieldModel.name])
            
    # ${F-Tags}, ${M-Tags}, ${Tags}
    JxAnswerDict['F-Tags'] = Card.fact.tags
    JxAnswerDict['M-Tags'] = Card.fact.model.tags
    JxAnswerDict['Tags'] = " ".join(set(Card.fact.model.tags.split(" ") + Card.fact.tags.split(" ") + [Card.cardModel.name]))
                
    JxProfile("Fill JxCodes")
    
    JxAnswer = re.sub("\$\{(.*?)\}",lambda x:JxReplace(x,JxAnswerDict),JxAnswer)
    
    JxProfile("Substitutions")
                      
    from controls import JxSettings
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






