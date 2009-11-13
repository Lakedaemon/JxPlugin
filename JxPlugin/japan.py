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


                
                
 
from japanese.reading import *
import sys, os, platform, re, subprocess

                
class MecabControl(object):

    def __init__(self):
        self.mecab = None

    def setup(self):
        if sys.platform == "win32":
            dir = WIN32_READING_DIR
            os.environ['PATH'] += (";%s\\mecab\\bin" % dir)
            os.environ['MECABRC'] = ("%s\\mecab\\etc\\mecabrc" % dir)
        elif sys.platform.startswith("darwin"):
            dir = os.path.dirname(os.path.abspath(".py/../japanese"))
            os.environ['PATH'] += ":" + dir + "/osx/mecab/bin"
            os.environ['MECABRC'] = dir + "/osx/mecab/etc/mecabrc"
            os.environ['DYLD_LIBRARY_PATH'] = dir + "/osx/mecab/bin"
            os.chmod(dir + "/osx/mecab/bin/mecab", 0755)

    def ensureOpen(self):
        if not self.mecab:
            self.setup()
            try:
                self.mecab = subprocess.Popen(
                    mecabCmd, bufsize=-1, stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE, startupinfo=si)
            except OSError:
                raise Exception(_("Please install mecab"))
                
 
    

def escapeTextOL(text):
    # strip characters that trip up kakasi/mecab
    text = text.replace("\n", " ")
    text = text.replace(u'\uff5e', "~")
    text = text.replace('\t', "")   # we strip the tabs \t
    text = text.replace('\r', "")   # and the \r    
    text = re.sub("<br( /)?>", "---newline---", text)
    text = stripHTML(text)
    text = text.replace("---newline---", "<br>")
    return text

debug=""


    
def GuessType(String):
        if len(String)==1 and JxIsKanji(String):
                #if  String has one Kanji, it is a Kanji (or a Word)
                return set(["Kanji","Word"])    
        elif set(unicode(c) for c in String.strip(u'  \t　	')).intersection(JxPonctuation):
                #if  String has ponctuations marks, it is a sentence
                return set(["Sentence"])             
        else:              
                #in other cases, it is a word (still don't know what to do with grammar)    
                return set(["Word"])


                ######################################################################## I will have to change it there thanks to mecab
                #content = stripHTML(fields[ordinal])
                #if boolean or type in GuessType(content):
                #    metadata[type] = content 
                ######################################################################## (type, boolean, content) ->  metadata[type] = guessed content if non empty

#1 形容詞,接続詞,動詞,助詞,Unknown,記号,副詞,連体詞,助動詞,接頭詞,名詞


#2,数接続,空白,接尾,非自立,数,サ変接続,副詞化,一般,ナイ形容詞語幹,固有名詞,接続助詞,副助詞／並立助詞／終助詞,接続詞的,格助詞,係助詞,句点,形容動詞語幹,終助詞,連体化,代名詞,名詞接続,自立,副詞可能,助詞類接続

#### version 1

#setIgnore = set(u'形容詞',u'接続詞',u'動詞',u'助詞',u'Unknown',u'記号',u'副詞',u'連体詞',u'助動詞',u'接頭詞',u'名詞')
setGobble = set([u'形容詞',u'接続詞',u'動詞',u'副詞',u'接頭詞', u'名詞'])# we gobble adjectivs, conjunction, verbs, adverbs, prefixes, names

def parse_content(string,type,kanjiMode):
    if type == 'Kanji':
        kanjiList = []
        for char in string:
            if JxIsKanji(char):
                kanjiList.append(char)
        if kanjiList and not(kanjiMode):
            return {'kanji':kanjiList[:]}
        elif kanjiList and len(kanjiList)==1:
            return {'kanji':kanjiList.pop()} 
        return {}
    # first mecab the string
    list = call_mecab(string)
    # then we have got to extract relevant info from the mecab output
    number = 0
    lastType = None
    tail = u""
    List = []
    for (head, type, subtype, katakana) in list:
        if tail == u"":
            # we don't care about lastType, we gobble or ignore
            if type in setGobble:
                # we gobble
                tail += head
                number += 1
            lastType = type
        else:
            # we either gobble some more or flush and gobble/ignore
            flush = True
            if lastType == u"形容詞" and (head, type, subtype, katakana) == (u'さ',u'名詞',u'接尾',u'サ'):
                #gobble and flush
                tail += head
            elif lastType == u'接頭詞' and type == u'名詞':
                #gobble
                tail += head
                flush = False
            elif lastType == u'名詞'and type == u'名詞':
                #gobble
                tail += head
                flush = False
            elif lastType == u'名詞'and (head, type, subtype, katakana) == (u'する',u'動詞',u'自立',u'スル'):  
                #gobble and flush
                tail += head
            elif lastType == u'動詞' and (head, type, subtype, katakana) == (u'て',u'助詞',u'接続助詞',u'テ'):# maybee I shouldn't do that and just flush the verb
                #gobble
                tail += head
                flush = False
            elif lastType == u'助詞'and (head, type, subtype, katakana) == (u'いる',u'動詞',u'非自立',u'イル'): # should be the same with aru/kuru/iku/miru...
                #gobble
                tail += head
                flush = False
            if flush:
                # do something
                List.append(tail)
                tail = ""
            lastType = type
    if tail:
        # out of the loop, gotta flush...
        List.append(tail)
    if number >= 1:
        return {'words':List[:]}
    return {}

canLoad = True
if sys.platform.startswith("darwin"):
    while 1:
        try:
            proc = platform.processor()
        except IOError:
            proc = None
        if proc:
            canLoad = proc != "powerpc"
            break                
if canLoad:
    if sys.platform == "win32":
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    else:
        si = None                
    mecabCmd = ["mecab",'--node-format=%m\t%f[0]\t%f[1]\t%f[8]\r',  '--eos-format=\n','--unk-format=%m\tUnknown\t\t\r'] #1/#0
    me = MecabControl()
    def call_mecab(string):

        stringe = escapeTextOL(string)
        stringe = stringe.encode("euc-jp", "replace") + '\n'


        me.ensureOpen()
        me.mecab.stdin.write(stringe)
        me.mecab.stdin.flush()
        string = unicode(me.mecab.stdout.readline().rstrip('\r\n'), "euc-jp")
        # then split the output in a list
        output = string.split('\r')
        list = []
        for string in output:
            list.append(tuple(string.split('\t')))
        return list
else:
    def parse_content(content,type,kanjiMode):
        if type == 'Kanji':
            kanjiList = []
            for char in string:
                if JxIsKanji(char):
                    kanjiList.append(char)
            if kanjiList and not(kanjiMode):
                return {'kanji':kanjiList[:]}
            elif kanjiList and len(kanjiList)==1:
                return {'kanji':kanjiList.pop()} 
            return {}
        if type in GuessType(content):
            return {type:content}
        return {}  
