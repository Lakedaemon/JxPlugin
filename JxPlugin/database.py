# -*- coding: utf-8 -*-
# Copyright: Olivier Binda <olivier.binda@wanadoo.fr>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
# ---------------------------------------------------------------------------
# This file is a plugin for the "anki" flashcard application http://ichi2.net/anki/
# ---------------------------------------------------------------------------
from ankiqt import mw

from cache import save_cache
from answer import Tango2Dic,JxType,JxTypeJapanese, GuessType
from loaddata import *
JxModels = {} 
def build_JxModels():
    """builds the JxModels dictionnary, the Jxplugin counterparts (with metadata) of the sqllite model & fieldmodel tables"""
    query = """select models.id,models.name,models.tags,fieldModels.ordinal,fieldModels.name from models,fieldModels where models.id = fieldModels.modelId"""
    rows = mw.deck.s.all(query)
    def assign((id, name, tags, ordinal, fieldName)):
        try:
            fields = JxModels[id][2]
        except:
            JxModels[id] = (name, tags, {}, {})
            fields = JxModels[id][2]
        fields[ordinal] = fieldName
    map(assign,rows)    

    # got to parse the model tags and maybee the model name
    for (modelName, tags, fields, hints) in JxModels.values():
        types = set()
        test = set(tags.split(" ")) # parses the model tags first
        for (key,list) in JxType:
            if test.intersection(list):
                types.update([key]) 
        if not(types): # checks the model name now
            for (key,list) in JxType:
                if modelName in list:
                    types.update([key])
                    break # no need to parse further
        if not(types): # checks the Field's name now
            for (ordinal,name) in fields.iteritems():
                for (type,typeList) in JxType:
                                        if name in typeList:
                                                types.update([type])
                                                hints[type] = (name, ordinal, True)
                                                break # no need to parse this Field further
        if not(types): # Japanese Model ?
            test = set(tags.split(" ") + [modelName] + fields.values())   
            if test.intersection(JxTypeJapanese):
                types.update(['Kanji','Word','Sentence','Grammar'])  
        # now, we got to set the action and build a Hint
        if types and not(hints):
            # first, we try to affect relevant fields for each type (first try fields with the name similar to the type)
            for (type,typeList) in JxType:
                if type in types:
                        for (ordinal,name) in fields.iteritems():
                                if name in typeList:
                                        hints[type] = (name,ordinal,True) 
                                        break
            if len(hints) < len(types):
                # for the still missing fields, we try to find an "Expression" field next and update the List
                for (type,typeList) in JxType:
                    if type in types and type not in hints:
                        for (ordinal, name) in fields.iteritems():
                            if name == 'Expression':
                                if len(types) == 1:
                                    hints[type] = (name,ordinal,True)
                                else:
                                    hints[type] = (name,ordinal,False)                                                                        
                                break
            
JxFacts = {}
def build_JxFacts():
    """builds JxFacts, the Jxplugin counterparts (with metadata) of the sqllite Facts, Cards, Fields and review history tables"""
    build_JxModels()
    def assign((id,value)):
        """basically does factsDB[factId].update(ordinal=value)"""
        try:
            fields = JxFacts[id][0]
        except KeyError:
            JxFacts[id] = ({},{},{},0,[])
            fields = JxFacts[id][0]
        fields[len(fields)] = value# this is coded this way because in the anki database ordinal fields in fieldModels and fields aren't necessarily equals...
    rows = mw.deck.s.all("""select factId,value from fields order by ordinal""")
    map(assign,rows)

    rows = mw.deck.s.all("""select id,tags,modelId from facts""") 
    for (id,tags,modelId) in rows:
        types = set()
        test = set(tags.split(" "))
        for (key,list) in JxType:
            if test.intersection(list):
                types.update([key])
        if not(types): 
            hints = JxModels[modelId][3]
        else:
            hints={}
            modelFields = JxModels[modelId][2].iteritems()
            # first, we try to affect relevant fields for each type (first try fields with the name similar to the type)
            for (type,typeList) in JxType:
                if type in types:
                        for (ordinal,name) in modelFields:
                                if name in typeList:
                                        hint[type] = (name,ordinal,True) 
                                        break
            if len(hints) < len(types):
                # for the still missing fields, we try to find an "Expression" field next and update the List
                for (type,typeList) in JxType:
                    if type in types and type not in hints:
                        for (ordinal, name) in modelFields:
                            if name == 'Expression':
                                if len(types) == 1:
                                    hints[type] = (name,ordinal,True)
                                else:
                                    hints[type] = (name,ordinal,False)                                                                        
                                break          
        fields = JxFacts[id][0]
        metadata = JxFacts[id][1]
        for (type,(name,ordinal,boolean)) in hints.iteritems():
            content = fields[ordinal]
            if boolean or type in GuessType(content):
                metadata[type] = content
                
                
    JxKnownThreshold = 21 
    JxKnownCoefficient = 0.5
    
    rows = mw.deck.s.all("""select factId, id, interval, reps from cards""")      
    def assign((factId,id,interval,reps)):
        """sets the cards states in the Jx database JxDeck"""
        if interval > JxKnownThreshold and reps:
            status = 1# known
        elif reps:
            status = 0# seen
        else:
            status = -1# in deck
        JxFacts[factId][2][id]= (status, [])	 
    map(assign, rows)
     
    #midnightOffset = time.timezone - self.deck.utcOffset
    #self.endOfDay = time.mktime(now) - midnightOffset
    #todaydt = datetime.datetime(*list(time.localtime(time.time())[:3]))
    
    def assign((factId,id,interval,nextInterval,ease,time)):
        """sets the cards status changes in the Jx database JxDeck"""
        if (interval <= JxKnownThreshold  and nextInterval > JxKnownThreshold ) or (interval > JxKnownThreshold  and ease == 1): 
            #Card Status Change
            day = int(time / 86400.0)
            JxFacts[factId][2][id][1].append(day)	

    query = """select cards.factId, reviewHistory.cardId, reviewHistory.lastInterval, reviewHistory.nextInterval, reviewHistory.ease, reviewHistory.time 
	from cards, reviewHistory where cards.id = reviewHistory.cardId order by reviewHistory.cardId, reviewHistory.time"""
    rows = mw.deck.s.all(query)
    map(assign,rows)


    def assign((id,(fields,metadata,cards,state,history))):
        """sets the fact states and the fact history in the Jx database JxDeck"""
        list = [status for (status,changes) in cards.values() if status>=0]
        threshold = len(cards) * JxKnownCoefficient
        if list and sum(list)>= threshold:
            status = 1# in deck
        elif list:
            status = 0# seen
        else:
            status = -1# in deck
            
        if status >=0:    
            stateArray = {}
            for (status,changes) in cards.values():
                boolean = True
                for day in changes:
                    try:
                        if boolean:
                            stateArray[day] += 1
                        else:
                            stateArray[day] -= 1 
                    except KeyError:
                        if boolean:
                            stateArray[day] = 1
                        else:
                            stateArray[day] = -1  
                    boolean = not(boolean)
                
            days = stateArray.keys()
            days.sort()
            boolean = True
            for day in days:
                if (boolean and stateArray[day] >=threshold ) or (not(boolean) and stateArray[day] < threshold): #xor
                    history.append(day)
                    boolean = not(boolean)
            
        JxFacts[id] = (fields, metadata, cards, status, history)	 
        
    map(assign, JxFacts.iteritems())        
       
    build_JxStats()   
    save_cache(JxFacts)
    mw.help.showText(str(JxStats))   

JxStatsTask = {
'Word':{'W-JLPT':MapJLPTTango,'W-Freq':MapZoneTango,'W-AFreq':MapZoneTango},
'Kanji':{'K-JLPT':MapJLPTKanji,'W-Freq':MapZoneKanji,'W-AFreq':MapZoneKanji,'W-Jouyou':MapJouyouKanji,'W-Kanken':MapKankenKanji}} 

JxStats = {}      
def build_JxStats():
    
    for type in ['Word','Kanji']:
        def select((fields,types,cards,state,changelist)):
            try:
                return (types[type], state)
            except KeyError:
                return None
        list = filter(lambda x: x != None, map(select,JxFacts.values()))
        for (name,mapping) in JxStatsTask[type].iteritems():
            
            if  name == 'W-AFreq':
                def assign_WAF((content,state)):
                    try:
                        value = mapping.Value(content)
                        increment = Jx_Word_Occurences[content]
                        try:
                            JxStats[(name,state,value)] += increment
                        except KeyError:
                            JxStats[(name,state,value)] = increment
                    except KeyError:
                        pass    
                        
                map(assign_WAF,list)
                def count_WAF((content,value)):
                    zone = Word2Zone[content]
                    try:
                        JxStats[(name,'Total',zone)] += value
                    except KeyError:
                        JxStats[(name,'Total',zone)] = value                
                map(count_WAF,Jx_Word_Occurences.iteritems())                    
            elif name == 'K-AFreq':
                
                def assign_KAF((content,state)):
                    try:
                        value = mapping.Value(content)
                        increment = Jx_Kanji_Occurences[content]
                        try:
                            JxStats[(name,state,value)] += increment
                        except KeyError:
                            JxStats[(name,state,value)] = increment
                    except KeyError:
                        pass        
                map(assign_KAF,list)                    
                def count_KAF((content,value)):
                    zone = Kanji2Zone[content]
                    try:
                        JxStats[(name,'Total',zone)] += value
                    except KeyError:
                        JxStats[(name,'Total',zone)] = value                
                map(count_KAF,Jx_Kanji_Occurences.iteritems())                
            else:
                
                def assign((content,state)):
                    try:
                        value = mapping.Value(content)
                    except KeyError:
                        value = 'Other'
                    try:
                        JxStats[(name,state,value)] += 1
                    except KeyError:
                        JxStats[(name,state,value)] = 1
                map(assign,list)                  
                def count(value):
                    try:
                        JxStats[(name,'Total',value)] += 1
                    except KeyError:
                        JxStats[(name,'Total',value)] = 1                
                map(count,mapping.Dict.values())
    
    
   
