# -*- coding: utf-8 -*-
# Copyright: Olivier Binda <olivier.binda@wanadoo.fr>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
# ---------------------------------------------------------------------------
# This file is a plugin for the "anki" flashcard application http://ichi2.net/anki/
# ---------------------------------------------------------------------------
"""Ideally, all japanese specific constants, variables, functions should go in there (in case we want to support other languages in the future)"""

# beware... if this file is named "japanese", it creates import problems with the japanese support plugin

JxTypeJapanese = ["japanese","Japanese","JAPANESE",u"日本語",u"にほんご"]

JxType=[('Kanji',["kanji","Kanji","KANJI",u"漢字",u"かんじ"]),
('Word',["word","Word","WORD",u"単語",u"たんご",u"言葉",u"ことば"]),
('Sentence',["sentence","Sentence","SENTENCE",u"文",u"ぶん"]),
('Grammar',["grammar","Grammar","GRAMMAR",u"文法",u"ぶんぽう"])]

JxPonctuation = [unichr(c) for c in range(ord(u'　'),ord(u'〿')+1)]+[u' ',u'      ',u',',u';',u'.',u'?',u'"',u"'",u':',u'/',u'!']
JxPonctuation.remove(u'々')  

def JxIsKanji(Char):
        N = ord(Char)
        if N >= ord(u'一')  and N < ord(u'龥'):
                return True
        if N >= ord(u'豈')  and N < ord(u'鶴'):
                return True             
        return False

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
