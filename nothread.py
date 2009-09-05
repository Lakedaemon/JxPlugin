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
            #self.exec_()
            if self.Loop:        
                self.emit(SIGNAL("Sync"),c)
            

        
def Sync(c):        
        global debug 
        debug = ""
        l = struct.pack("I", len(mw.deck.name()))
        c.sendall(l)
        c.sendall(mw.deck.name())                  
        Debug('<br>Receiving rep length :')
        d = c.recv(4)
        l = struct.unpack("i", d)[0]
        Debug(str(l) +"<br>")       
        if l >0:
            r = 0
            data = ''
            while r < l:
                Debug("While : "+str(l-r)+"<br>" )
                d = c.recv(l-r)
                r += len(d)
                data += d                  
            Debug(data.decode("utf-8"))
            data = data.split('\n')
            for i in data:
                    Debug("(-"+ i+ "-)")
                    if i.count(':')==2:
                        id, ease, reps = i.split(':')
                        ScoreCard(int(id),int(ease),int(reps))
        else:
            Debug("no change to apply")
        
        
        f = []
        s = mw.deck.s.all("select id from cards where due < " + str(time.time() + DAYSAHEAD) + " order by due limit 20")
        def csort(a, b):
            a, b = a[1], b[1]
            if a > b:
                return 1
            if a < b:
                return -1
            return 0
        Debug(" query <br>")
        cards = []
        status=0
        for id in s:
            cq = mw.deck.s.query(anki.cards.Card).get(id[0])  #this is slow, speedup possible there
            q = striphtml(cq.question).encode("utf-8")
            a = striphtml(cq.answer).encode("utf-8")
            cards.append((id[0], cq.due, cq.reps, q, a))
            status+=1
        Debug("filter html " + str(status) +"<br>")
        cards.sort(csort)
        Debug("sort<br>")
        a =0
        for (id,due,rep,question,answer) in cards:
            f.append("%d\t%d\t%d\t%s\t%s" % (id, due, rep, question, answer))
            a+=1
        Debug("output" +str(a)+"<br>")
        srs = '\n'.join(f)
           
        Debug("<br> Srs length : " + str(len(srs))  + "<br> srs : " + srs.decode("utf-8"))
        l = struct.pack("I", len(srs))
        c.sendall(l) 
        c.sendall(srs) 
        Debug("done<br>")
        c.shutdown(1)
        c.close()
        Debug('')
        mw.loadDeck(mw.deck.path, sync=False)  
            
def Debug(text,*args):
        global debug
        debug += text
        mw.help.showText(debug)
        

        
def ScoreCard(id, ease, reps):
        card = mw.deck.cardFromId(id)
        
        # not equal means it was reviewed on anki at some point so ditch the change
        if card.reps != reps:
            return
        
        mw.deck.answerCard(card, ease)


 
def init_DsSync():
        """Initialises the Anki GUI to present an option to invoke the plugin."""
        from PyQt4 import QtGui, QtCore
	
	# creates menu entry
	mw.mainWin.actionDsSync = QtGui.QAction('DsSync', mw)
	mw.mainWin.actionDsSync.setStatusTip('Syncing through TCP/IP with AnkiDs')
        mw.mainWin.actionDsSync.setEnabled(not not mw.deck)
	mw.connect(mw.mainWin.actionDsSync, QtCore.SIGNAL('triggered()'), Sync)


	# adds the plugin icons in the Anki Toolbar
	
	mw.mainWin.toolBar.addAction(mw.mainWin.actionDsSync)
	
	# to enable or disable Jstats whenever a deck is opened/closed
	mw.deckRelatedMenuItems = mw.deckRelatedMenuItems + ("DsSync",)
	
	
# adds JxPlugin to the list of plugin to process in Anki 
mw.addHook('init', init_DsSync)
mw.registerPlugin("Sincyng with AnkiDs", 667)
print 'DsSync Plugin loaded'

mythread=DSSyncThread(mw)

mythread.start()









