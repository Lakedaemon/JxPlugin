# -*- coding: utf-8 -*-
# Copyright: Olivier Binda <olivier.binda@wanadoo.fr>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
# ---------------------------------------------------------------------------
# This file is a plugin for the "anki" flashcard application http://ichi2.net/anki/
# ---------------------------------------------------------------------------

JxLink = {}
from loaddata import *
JxStatsMap = {
'Word':[MapJLPTTango,MapZoneTango,MapZoneTango],
'Kanji':[MapJLPTKanji,MapZoneKanji,MapZoneKanji,MapJouyouKanji,MapKankenKanji],
'Grammar':[],
'Sentence':[]}
CardId2Types = {}
FactId2Types = {}
################### my profiling (simple) tools ####################
from time import time
Jx_Profile = [("Init",time())]

def JxInitProfile(String):
        global Jx_Profile
        Jx_Profile = [(String,time())]
def JxProfile(String):
        global Jx_Profile
        Jx_Profile.append((String,time()))
def JxShowProfile():
        global Jx_Profile
        JxHtml = ""
        for a in range(len(Jx_Profile)):
                (String,Time) = Jx_Profile[a]
                if a==0:
                        JxHtml+="<tr><td>"+ String +"</td><td>"+ str(Time) +"</td></tr>"
                else:
                        JxHtml+="<tr><td>"+ String +"</td><td>"+ str(Time-Jx_Profile[a-1][1]) +"</td></tr>"                
        return "<table>" + JxHtml + "</table>"
