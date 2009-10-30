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
            dir = os.path.dirname(os.path.abspath(__file__))
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
                
                
                
                
if sys.platform == "win32":
    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
else:
    si = None                
mecabCmd = ["mecab",'--node-format=(%m,%f[0],%f[1],%f[8]) ',  '--eos-format=\n','--unk-format=%m[Unknown] '] #1/#0
me = MecabControl()

def escapeTextOL(text):
    # strip characters that trip up kakasi/mecab
    text = text.replace("\n", " ")
    text = text.replace(u'\uff5e', "~")
    text = re.sub("<br( /)?>", "---newline---", text)
    text = stripHTML(text)
    text = text.replace("---newline---", "<br>")
    return text

debug=""

def call_mecab(string):

    stringe = escapeTextOL(string)
    stringe = stringe.encode("euc-jp", "replace") + '\n'


    me.ensureOpen()
    me.mecab.stdin.write(stringe)
    me.mecab.stdin.flush()
    return unicode(me.mecab.stdout.readline().rstrip('\r\n'), "euc-jp")
    



