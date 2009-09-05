#!/usr/bin/python
#-*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# This is a plugin for Anki: http://ichi2.net/anki/
#
# To install, place this file in your ~/.anki/plugins/ directory.
# To remove, delete this file from your ~/.anki/plugins/ directory.
# Restart Anki after installation or removal for the changes to 
# take effect.
# ---------------------------------------------------------------------------
# File:        ankidssync.py
# Description: used to sync anki to the ds
# Author:      Olivier Binda (I used lots of code from Jake Probst)
# License:     GNU GPL
# ---------------------------------------------------------------------------

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from ankiqt import mw
import anki.cards

import time
import re
import socket
import select
import struct

DAY = 60*60*24
DAYSAHEAD = DAY * 2

debug = ""
    
def striphtml(s):
    s = s.replace("<br>", "|")
    s = s.replace("<br/>", "|")
    s = s.replace("<br />", "|")
    s = s.replace("\t", "    ")
    r = re.compile("<[\s\S]*?>")
    g = r.findall(s)
    for i in g:
        s = s.replace(i, "")
    return s     

class DSSyncThread(QThread):
        
    def __init__(self,parent = None):
        QThread.__init__(self,parent)
        self.connect(self, SIGNAL("Sync"), Sync)
        self.connect(self, SIGNAL("Start"), self.start)
        
    def stop(self):
        self.Loop = False
        
    def run(self):
        fd = socket.socket()#socket.AF_INET, socket.SOCK_STREAM)
        fd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        fd.bind(("", 24550))
        fd.listen(5)
        self.Loop = True
        while self.Loop:
            while self.Loop:
                rd,wr,er = select.select([fd],[],[], 30)         
                if len(rd) != 0:
                    c = fd.accept()[0]
                    break
            if self.Loop:        
                self.emit(SIGNAL("Sync"),c)# Sync will be run outside the thread, in some event loop of the QTGui (you can't use widget in Qthreads...).
            

        
def Sync(c):        
        l = struct.pack("I", len(mw.deck.name()))
        c.sendall(l)
        c.sendall(mw.deck.name())                  
        d = c.recv(4)# maybee we should loop there too because we could get less than 4 bytes... it's quite unlikely though (besides, the ds buffers it's sends in a 8k stack)
        l = struct.unpack("i", d)[0]    
        if l >0:
            r = 0
            data = ''
            while r < l:
                d = c.recv(l-r)
                r += len(d)
                data += d                  
            data = data.split('\n')# we could remove the trailing \n before splitting too....
            for i in data:
                    if i.count(':')==2:
                        id, ease, reps = i.split(':')
                        ScoreCard(int(id),int(ease),int(reps))
        
        s = mw.deck.s.all("select id from cards where due < " + str(time.time() + DAYSAHEAD) + " order by due limit 20")

        cards = []
        for id in s:
            cq = mw.deck.s.query(anki.cards.Card).get(id[0])
            q = striphtml(cq.question).encode("utf-8")
            a = striphtml(cq.answer).encode("utf-8")
            cards.append((id[0], cq.due, cq.reps, q, a))

        for (id,due,rep,question,answer) in cards:
            f.append("%d\t%d\t%d\t%s\t%s" % (id, due, rep, question, answer))
            
        srs = '\n'.join(f)
        l = struct.pack("I", len(srs))
        c.sendall(l) 
        c.sendall(srs) 
        
        c.close()
        mw.loadDeck(mw.deck.path, sync=False)  
            
        
def ScoreCard(id, ease, reps):
        card = mw.deck.cardFromId(id)
        
        # not equal means it was reviewed on anki at some point so ditch the change
        if card.reps != reps:
            return
        
        mw.deck.answerCard(card, ease)
	
	
mw.registerPlugin("Sincyng with AnkiDs", 667)
print 'DsSync Plugin loaded'

mythread=DSSyncThread(mw)
# should ovrload opening of deck/closing of deck and make it run/stop there
mythread.start()# for the time being, it runs and never stops...









