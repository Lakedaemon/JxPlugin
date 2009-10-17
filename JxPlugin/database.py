# -*- coding: utf-8 -*-
# Copyright: Olivier Binda <olivier.binda@wanadoo.fr>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
# ---------------------------------------------------------------------------
# This file is a plugin for the "anki" flashcard application http://ichi2.net/anki/
# ---------------------------------------------------------------------------
from ankiqt import mw

from cache import load_cache,save_cache
from answer import Tango2Dic,JxType,JxTypeJapanese, GuessType
from loaddata import *

JxKnownThreshold = 21 
JxKnownCoefficient = 0.70

  
JxDeck = {}
def build_JxDeck():
    global JxDeck, JxStats, JxGraphs
    JxDeck = load_cache() 
    try:
        JxStats = JxDeck['Stats']
    except KeyError:
        JxStats = {} 
    try:
        JxGraphs = JxDeck['Graphs']
    except KeyError:    
        JxGraphs = {} 
        
        
    modelsCached = set_models()
    factsCached = set_fields()
    # I'll have to downdate stats/graphs there 
    set_types()
    # I'll have to update stats/graphs there
    historyCached = set_history()
    cardsCached = set_states()



    JxDeck['Facts'] = JxFacts
    
    build_JxStats()
    #build_JxGraphs()
    JxDeck['ModelsCached'] = modelsCached
    JxDeck['FactsCached'] = factsCached
    JxDeck['CardsCached'] = cardsCached
    JxDeck['HistoryCached'] = historyCached
    save_cache(JxDeck) 
 

JxModels = {} 
def set_models():
    """initializes JxModels and sets the models and hints"""
    global JxModels
    # first get the workload
    try:
        JxModels = JxDeck['Models']
        modelsCached = JxDeck['ModelsCached'] 
        query = """select models.id,models.name,models.tags,fieldModels.ordinal,fieldModels.name, max(created,modified) from models,fieldModels where models.id = fieldModels.modelId and max( created,modified)>%s""" % modelsCached 
    except KeyError: 
        JxModels = {}
        modelsCached  = 0
        query = """select models.id,models.name,models.tags,fieldModels.ordinal,fieldModels.name,max(created,modified) from models,fieldModels where models.id = fieldModels.modelId"""

    # then set the JxModels name, tags, fieldsnames and ordinals     
    dic = {}
    def assign((id, name, tags, ordinal, fieldName, cached)):
        try: 
            model = dic[id]
        except KeyError:
            dic[id] = (name,tags,{},{})
            model = dic[id]
        model[2][ordinal]= fieldName
        return cached
    modelsCached = max(map(assign,mw.deck.s.all(query))+[modelsCached])
    
    # then compute types and hints
    def compute((modelName, tags, fields, hints)):
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
    map(compute, dic.values())
    
    # overwrite the models
    def copy((id, model)): 
        JxModels[id] = model
    map(copy, dic.iteritems()) 
    
    # save JxModels in the cache
    JxDeck['Models'] = JxModels
    return modelsCached
    
from anki.utils import stripHTML           
JxFacts = {}
def set_fields():
    """initializes Jxfacts and sets the fields"""
    global JxFacts
    try:
        JxFacts = JxDeck['Facts']
        factsCached = JxDeck['FactsCached']
        query = """select factId,value, max(created,modified) from fields, facts where fields.factId = facts.id and max(created,modified)>%s order by ordinal""" %  factsCached
    except KeyError:
        JxFacts = {}
        factsCached = 0
        query = """select factId,value, max(created,modified) from fields, facts where fields.factId = facts.id order by ordinal"""
    
    dic = {}
    def assign((id,value,cached)):
        """basically does factsDB[factId].update(ordinal=value)"""
        try:
            fields = dic[id]
        except KeyError:
            dic[id] = {}
            fields = dic[id]
        fields[len(fields)] = value# this is coded this way because in the anki database ordinal fields in fieldModels and fields aren't necessarily equals...
        return cached
    factsCached = max(map(assign,mw.deck.s.all(query))+[factsCached])
    
    # overwrite the fields
    def copy((id,fields)):
        JxFacts[id] = (fields,{},{},0,[])
    map(copy, dic.iteritems()) # I shouldn't overwrite the other fields...for JxStats/JxGraphs update purpose
    return factsCached
  
def set_types():
    try:
        query = """select facts.id,facts.tags, facts.modelId from facts,models where models.id=facts.modelId and (max(facts.created,facts.modified)>%s or max(models.created,models.modified)>%s)""" %  (JxDeck['FactsCached'],JxDeck['ModelsCached'])  
    except KeyError:
        query = """select id, tags, modelId from facts"""
        
    def compute((id,tags,modelId)):
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
        metadata = {}
        for (type,(name,ordinal,boolean)) in hints.iteritems():
            content = stripHTML(fields[ordinal])
            if boolean or type in GuessType(content):
                metadata[type] = content 
        JxFacts[id] = (fields,metadata,{},0,[]) #overwrite the types ... bad for stats/graphs....
    map(compute,mw.deck.s.all(query))
    
def set_states():    
    try:
        cardsCached = JxDeck['CardsCached']
        query = """select cards.factId, cards.id, cards.interval, cards.reps, max(cards.created, cards.modified) from cards where max(cards.created,cards.modified)>%s""" % cardsCached
    except KeyError:
        cardsCached = 0
        query = """select factId, id, interval, reps, max(created, modified) from cards"""      
     
    def assign((factId,id,interval,reps,cached)):
        """sets the cards states in the Jx database JxDeck"""
        if interval > JxKnownThreshold and reps:
            status = 1# known
        elif reps:
            status = 0# seen
        else:
            status = -1# in deck
        try:
            (state, changes) = JxFacts[factId][2][id]
            JxFacts[factId][2][id]= (status, changes)	 
        except KeyError:
            JxFacts[factId][2][id]= (status, [])	             
        return cached
    cardscached = max(map(assign, mw.deck.s.all(query) ) + [cardsCached])

    # compute the fact statuses
    def compute((id,(fields,types,cards,state,history))):
        list = [status for (status,changes) in cards.values() if status>=0]
        threshold = len(cards) * JxKnownCoefficient
        if list and sum(list)>= threshold:
            status = 1# known
        elif list:
            status = 0# seen
        else:
            status = -1# in deck
        JxFacts[id] = (fields,types,cards,status,history)
    map(compute, JxFacts.iteritems())
    return cardsCached
    
    #midnightOffset = time.timezone - self.deck.utcOffset
    #self.endOfDay = time.mktime(now) - midnightOffset
    #todaydt = datetime.datetime(*list(time.localtime(time.time())[:3]))

def set_history():    
    try:
        historyCached = JxDeck['HistoryCached']
        query = """select cards.factId, reviewHistory.cardId, reviewHistory.lastInterval, reviewHistory.nextInterval, reviewHistory.ease, reviewHistory.time from cards, reviewHistory where cards.id = reviewHistory.cardId and reviewHistory.time>%s  order by reviewHistory.cardId, reviewHistory.time""" %  historyCached
    except KeyError:
        historyCached = 0
        query = """select cards.factId, reviewHistory.cardId, reviewHistory.lastInterval, reviewHistory.nextInterval, reviewHistory.ease, reviewHistory.time from cards, reviewHistory where cards.id = reviewHistory.cardId order by reviewHistory.cardId, reviewHistory.time"""
        
    history = {}    
    def assign((factId,id,interval,nextInterval,ease,time)):
        """sets the cards status changes in the Jx database JxDeck"""
        if (interval <= JxKnownThreshold  and nextInterval > JxKnownThreshold ) or (interval > JxKnownThreshold  and ease == 1): 
            #Card Status Change
            day = int(time / 86400.0)
            #JxFacts[factId][2][id][1].append(day)
            try: 
                cardsHistory = history[factId]
            except KeyError:
                history[factId] = {}
                cardsHistory = history[factId]
            try:
                cardsHistory[id].append(day)
            except KeyError:
                cardsHistory[id] = [day]
        return time
    historyCached= max(map(assign,mw.deck.s.all(query)) + [historyCached])

    deltaHistory = {}
    def compute((factId,cardsHistory)):
        global debug
        stateArray = {}
        fact = JxFacts[factId]
        cards = fact[2]
        #factHistory = fact[4]
        threshold = len(history[factId]) * JxKnownCoefficient
        deltaHistory[factId] = []
        for (id,changes) in cardsHistory.iteritems():
            #try: 
                #boolean = (cards[id][0]  != 1)
            #except KeyError:
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
        #boolean = (fact[3] != 1)
        boolean=True
        #cumul = len([1 for (state, changes) in cards.values() if state ==1])
        cumul = 0
        for day in days:
            cumul += stateArray[day]
            if (boolean and cumul >=threshold ) or (not(boolean) and cumul < threshold): #xor
                #factHistory.append(day)
                deltaHistory[factId].append(day)
                boolean = not(boolean)   
                
    map(compute, history.iteritems())
    update_graphs(deltaHistory)
        
    return historyCached

JxGraphs = {}
def update_graphs(dic, add=True):
    for type in ['Word','Kanji']:
        def select((id,changelist)):
            try:
                return (JxFacts[id][1][type], changelist)
            except KeyError:
                return None
        list = filter(lambda x: x != None, map(select,dic.iteritems()))

        tasks = {'Word':{'W-JLPT':MapJLPTTango,'W-AFreq':MapZoneTango}, 'Kanji':{'K-JLPT':MapJLPTKanji,'K-AFreq':MapZoneKanji,'Jouyou':MapJouyouKanji,'Kanken':MapKankenKanji}} 
        
        for (name,mapping) in tasks[type].iteritems():  
            if  name == 'W-AFreq':
                def assign_WAF((content,days)):
                    try:
                        value = mapping.Value(content)
                        increment = Jx_Word_Occurences[content]
                        try:
                            stateArray = JxGraphs[(name,value)]
                        except KeyError:
                            JxGraphs[(name,value)] = {}
                            stateArray = JxGraphs[(name,value)]
                        boolean = True
                        for day in days:
                            try:
                                if boolean:
                                    stateArray[day] += increment
                                else:
                                    stateArray[day] -= increment 
                            except KeyError:
                                if boolean:
                                    stateArray[day] = increment
                                else:
                                    stateArray[day] = -increment 
                            boolean = not(boolean)  
                    except KeyError:
                        pass                     
                map(assign_WAF,list)                    
            elif name == 'K-AFreq':                
                def assign_KAF((content,days)):
                    try:
                        value = mapping.Value(content)
                        increment = Jx_Kanji_Occurences[content]
                        try:
                            stateArray = JxGraphs[(name,value)]
                        except KeyError:
                            JxGraphs[(name,value)] = {}
                            stateArray = JxGraphs[(name,value)]
                        boolean = True
                        for day in days:
                            try:
                                if boolean:
                                    stateArray[day] += increment
                                else:
                                    stateArray[day] -= increment 
                            except KeyError:
                                if boolean:
                                    stateArray[day] = increment
                                else:
                                    stateArray[day] = -increment 
                            boolean = not(boolean)  
                    except KeyError:
                        pass   
                map(assign_KAF,list)                            
            else:               
                def assign((content,days)):
                    boolean = True
                    try:
                        value = mapping.Value(content)
                    except KeyError:
                        value = 'Other'
                    try:
                        stateArray = JxGraphs[(name,value)]
                    except KeyError:
                        JxGraphs[(name,value)] = {}
                        stateArray = JxGraphs[(name,value)]
                    for day in days:
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
                map(assign,list) 
    JxDeck['Graphs'] = JxGraphs

JxGraphs = {}
def build_JxGraphs():
    global JxFacts, JxGraphs
    for type in ['Word', 'Kanji']:
        def select((fields,metadata,cards,state,changelist)):
            if state <0:
                return None
            try:
                return (metadata[type], changelist)
            except KeyError:
                return None
        list = filter(lambda x: x != None, map(select,JxFacts.values()))
        tasks = {'Word':{'W-JLPT':MapJLPTTango,'W-AFreq':MapZoneTango}, 'Kanji':{'K-JLPT':MapJLPTKanji,'K-AFreq':MapZoneKanji,'Jouyou':MapJouyouKanji,'Kanken':MapKankenKanji}} 
        
        for (name,mapping) in tasks[type].iteritems():  
            if  name == 'W-AFreq':
                def assign_WAF((content,days)):
                    try:
                        value = mapping.Value(content)
                        increment = Jx_Word_Occurences[content]
                        try:
                            stateArray = JxGraphs[(name,value)]
                        except KeyError:
                            JxGraphs[(name,value)] = {}
                            stateArray = JxGraphs[(name,value)]
                        boolean = True
                        for day in days:
                            try:
                                if boolean:
                                    stateArray[day] += increment
                                else:
                                    stateArray[day] -= increment 
                            except KeyError:
                                if boolean:
                                    stateArray[day] = increment
                                else:
                                    stateArray[day] = -increment 
                            boolean = not(boolean)  
                    except KeyError:
                        pass                     
                map(assign_WAF,list)                    
            elif name == 'K-AFreq':                
                def assign_KAF((content,days)):
                    try:
                        value = mapping.Value(content)
                        increment = Jx_Kanji_Occurences[content]
                        try:
                            stateArray = JxGraphs[(name,value)]
                        except KeyError:
                            JxGraphs[(name,value)] = {}
                            stateArray = JxGraphs[(name,value)]
                        boolean = True
                        for day in days:
                            try:
                                if boolean:
                                    stateArray[day] += increment
                                else:
                                    stateArray[day] -= increment 
                            except KeyError:
                                if boolean:
                                    stateArray[day] = increment
                                else:
                                    stateArray[day] = -increment 
                            boolean = not(boolean)  
                    except KeyError:
                        pass   
                map(assign_KAF,list)                            
            else:               
                def assign((content,days)):
                    boolean = True
                    try:
                        value = mapping.Value(content)
                    except KeyError:
                        value = 'Other'
                    try:
                        stateArray = JxGraphs[(name,value)]
                    except KeyError:
                        JxGraphs[(name,value)] = {}
                        stateArray = JxGraphs[(name,value)]
                    for day in days:
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
                map(assign,list) 
    JxDeck['Graphs'] = JxGraphs
                
import time
def JxGraphs_into_json():
    global JxGraphs
    today = int(time.time() / 86400.0)
    dict_json = {}
    tasks = {'W-JLPT':MapJLPTTango, 'W-AFreq':MapZoneTango, 'K-JLPT':MapJLPTKanji, 'K-AFreq':MapZoneKanji, 'Jouyou':MapJouyouKanji, 'Kanken':MapKankenKanji} 
    for (graph,mapping) in tasks.iteritems():
        for (key,string) in mapping.Order +[('Other','Other')]:
            try:
                dict = JxGraphs[(graph,key)]
            except KeyError:
                dict = {}
            if today not in dict:
                dict[today] = 0
            keys = dict.keys()
            if graph == 'W-AFreq':
                dict_json[(graph,key)] =  JxJSon([(limit-today,sum([dict[day] for day in keys if day <=limit])*100.0/Jx_Word_SumOccurences) for limit in range(min(keys), max(keys) + 1)]) 
            elif graph == 'K-AFreq':
                dict_json[(graph,key)] =  JxJSon([(limit-today,sum([dict[day] for day in keys if day <=limit])*100.0/Jx_Kanji_SumOccurences) for limit in range(min(keys), max(keys) + 1)]) 
            else:
                dict_json[(graph,key)] =  JxJSon([(limit-today,sum([dict[day] for day in keys if day <=limit])) for limit in range(min(keys), max(keys) + 1)])                 
    return dict_json
    
def JxJSon(CouplesList):
        return "[" + ",".join(map(lambda (x,y): "[%s,%s]"%(x,y),CouplesList)) + "]" 
        
JxStats = {}      
def build_JxStats():
    global JxFacts, JxStats
    for type in ['Word','Kanji']:
        def select((fields,types,cards,state,changelist)):
            try:
                return (types[type], state)
            except KeyError:
                return None
        list = filter(lambda x: x != None, map(select,JxFacts.values()))
        
        JxStatTasks = {'Word':{'W-JLPT':MapJLPTTango,'W-Freq':MapZoneTango,'W-AFreq':MapZoneTango}, 'Kanji':{'K-JLPT':MapJLPTKanji,'K-Freq':MapZoneKanji,'K-AFreq':MapZoneKanji,'Jouyou':MapJouyouKanji,'Kanken':MapKankenKanji}} 
        
        for (name,mapping) in JxStatTasks[type].iteritems():           
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
    JxDeck['Stats'] = JxStats
    
def get_stat(key):
    try:
        return JxStats[key]
    except KeyError:
        return 0
               
def display_stats(stats):
    mappings = {'W-JLPT':MapJLPTTango, 'W-Freq':MapZoneTango, 'W-AFreq':MapZoneTango, 'K-JLPT':MapJLPTKanji, 'K-Freq':MapZoneKanji, 'K-AFreq':MapZoneKanji, 'Jouyou':MapJouyouKanji, 'Kanken':MapKankenKanji}
    mapping = mappings[stats]
    html = """
    <style>
	    .BackgroundHeader {background-color: #eee8d4;}
	    .Background {background-color: #fff9e5;}
	    .JxStats td{align:center;text-align:center;}
	    .JxStats tr > td:first-child,.JxStats tr > th:first-child{
            border-right:1px solid black;
            border-left:1px solid black;
        }
        .BorderRight{border-right:1px solid black;}
        .Border td,.Border th{border-top:1px solid black;border-bottom:1px solid black;}
    </style>
	<table class="JxStats" width="100%%" align="center" style="margin:0 20 0 20;border:0px solid black;" cellspacing="0px"; cellpadding="4px">
	    <tr class="Border BackgroundHeader">
	    <th><b>%s</b></th>
	    <th><b>%%</b></th>
	    <th><b>Known</b></th>
	    <th><b>Seen</b></th>
	    <th><b>Deck</b></th>
	    <th class="BorderRight"><b>Total</b></th>
	    </tr>
	""" % mapping.To
    (sumKnown, sumSeen, sumInDeck, sumTotal)=(0,0,0,0)
    for (key,value) in mapping.Order:
        known = get_stat((stats,1,key))
        seen = known + get_stat((stats,0,key))
        inDeck = seen + get_stat((stats,-1,key))
        total = get_stat((stats,'Total',key))
        sumKnown += known
        sumSeen += seen
        sumInDeck += inDeck
        sumTotal += total
        html += """
        <tr class="Background">
		    <td><b>%s</b></td>
		    <td><b style="font-size:small">%.0f%%</b></td>
		    <td>%.0f</td>
		    <td>%.0f</td>
		    <td>%.0f</td>
		    <td class="BorderRight">%.0f</td>
		</tr>""" % (value, known*100.0/max(1,total), known, seen, inDeck, total)
    html += """
    <tr class="Border BackgroundHeader">
        <td><b>%s</b></td>
        <td><b style="font-size:small">%.0f%%</b></td>
        <td>%.0f</td>
        <td>%.0f</td>
        <td>%.0f</td>
        <td class="BorderRight">%.0f</td>
    </tr>""" % ('Total',sumKnown*100.0/max(1,sumTotal),sumKnown,sumSeen,sumInDeck,sumTotal)     
    known = get_stat((stats,1,'Other'))
    seen = known + get_stat((stats,0,'Other'))
    inDeck = seen + get_stat((stats,-1,'Other'))
    if (known,seen,inDeck) != (0,0,0):
        html += """
        <tr>
            <td style="border:0px solid black;"><b>%s</b></td>
            <td></td><td>%.0f</td>
            <td>%.0f</td>
            <td>%.0f</td>
            <td></td>
        </tr>""" % ('Other', known, seen, inDeck)                
    html += '</table>'
    return html
    
def display_astats(stats):
    mappings = {'W-AFreq':MapZoneTango, 'K-AFreq':MapZoneKanji}
    mapping = mappings[stats]
    html = """
    <style>
        .BackgroundHeader {background-color: #817865;}
        .Background {background-color: #fece2f;}
        .JxStats td{align:center;text-align:center;}
        .JxStats tr > td:first-child,.JxStats tr > th:first-child{
            border-right:1px solid black;
            border-left:1px solid black;
        }
        .BorderRight{border-right:1px solid black;}
        .Border td,.Border th{border-top:1px solid black;border-bottom:1px solid black;}
    </style>
    <br/>
	<table class="JxStats" width="100%%" align="center" style="margin:0 20 0 20;border:0px solid black;" cellspacing="0px"; cellpadding="4px">
	    <tr class="Border BackgroundHeader">
	        <th><b>Accumulated</b></th>
	        <th><b>Known</b></th>
	        <th><b>Seen</b></th>
	        <th><b>Deck</b></th>
	        <th class="BorderRight"><b>Total</b></th>
	    </tr>"""
    grandTotal = sum([get_stat((stats,'Total',key)) for (key, value) in mapping.Order])
    (sumKnown, sumSeen, sumInDeck, sumTotal)=(0,0,0,0)
    for (key,value) in mapping.Order:
        known = get_stat((stats,1,key))
        seen = known + get_stat((stats,0,key))
        inDeck = seen + get_stat((stats,-1,key))
        total = get_stat((stats,'Total',key))
        sumKnown += known
        sumSeen += seen
        sumInDeck += inDeck
        sumTotal += total
        html +="""
        <tr class="Background">
            <td><b>%s</b></td>
            <td>%s%%</td>
            <td>%s%%</td>
            <td>%s%%</td>
            <td class="BorderRight">%.0f%%</td>
        </tr>""" % (value, JxFormat(known*100.0/max(1,grandTotal)), JxFormat(seen*100.0/max(1,grandTotal)), JxFormat(inDeck*100.0/max(1,grandTotal)), total*100.0/max(1,grandTotal))
    html += """
    <tr class="Border BackgroundHeader">
        <td><b>%s</b></td>
        <td>%s%%</td>
        <td>%s%%</td>
        <td>%s%%</td>
        <td class="BorderRight">%s%%</td>
    </tr>""" % ('Total', JxFormat(sumKnown*100.0/max(1,grandTotal)),JxFormat(sumSeen*100.0/max(1,grandTotal)),JxFormat(sumInDeck*100.0/max(1,grandTotal)),100)        
    html += "</table>"
    return html        
    
def JxFormat(Float):
    if Float < 0.01:                            # 0.001 -> 0
        return "0"
    if Float < 0.1:                             # 0.016 -> 0.02
        return "%.1g" % Float       
    if Float <1:                                # 0.168 -> 0.17
        return "%.2g" % Float                            
    else:                                       # 4.00 -> 4          4.10 -> 4           4.1678 -> 4.17           15.28 -> 15.3
        return "%.3g" % Float    
        

    
def JxVal(Dict,x):
    try:
        return  Dict[x]
    except KeyError:
        return -1
                
def display_partition(stat,label):
    """Returns an Html report of the label=known|seen|in deck stuff inside the list stat"""
    from database import JxFacts
    mappings = {'W-JLPT':MapJLPTTango, 'W-Freq':MapZoneTango, 'K-JLPT':MapJLPTKanji, 'K-Freq':MapZoneKanji,  'Jouyou':MapJouyouKanji, 'Kanken':MapKankenKanji}
    mapping = mappings[stat]
    partition = {}
    for (key,string) in mapping.Order+ [('Other','Other')]:
        partition[key] = []
    if stat == 'W-JLPT' or stat =='W-Freq':
        dic = Jx_Word_Occurences
        type = 'Word'
    else:
        dic = Jx_Kanji_Occurences
        type = 'Kanji'
    def assign((id,(fields,metadata,cards,state,history))):
        if state==label:
            try:
                content = metadata[type]
                try:
                    key = mapping.Dict[content]
                except KeyError:
                    key = 'Other'
                partition[key].append((content,id))
            except KeyError:
                pass
    map(assign, JxFacts.iteritems())


    for (key,string) in mapping.Order+ [('Other','Other')]:
        partition[key].sort(lambda x,y:JxVal(dic,y)-JxVal(dic,x))

    color = dict([(key,True) for (key,string) in mapping.Order + [('Other','Other')]])
    buffer = dict([(key,"") for (key,string) in mapping.Order + [('Other','Other')]])
    for (key,string) in mapping.Order + [('Other','Other')]:
        for (stuff,id) in partition[key]:
            color[key] = not(color[key])			
            if color[key]:
                buffer[key] += u"""<a style="text-decoration:none;color:black;" href="py:JxAddo(u'%(Stuff)s','%(Id)s')">%(Stuff)s</a>""" % {"Stuff":stuff,"Id":id}
            else:
                buffer[key] += u"""<a style="text-decoration:none;color:blue;" href="py:JxAddo(u'%(Stuff)s','%(Id)s')">%(Stuff)s</a>""" % {"Stuff":stuff,"Id":id}
    html = ''
    for (key,string) in mapping.Order:
        if buffer[key]:
            html += u"""<h2  align="center">%s</h2><p><font size=+2>%s</font></p>""" % (string,buffer[key])
    if buffer['Other']:
        html += u"""<h2  align="center">Other</h2><p><font size=+2>%s</font></p>""" % buffer['Other']
    return html

def display_complement(stat):
    """Returns an Html report of the missing seen stuff in the stat list"""
    from database import JxFacts
    mappings = {'W-JLPT':MapJLPTTango, 'W-Freq':MapZoneTango, 'K-JLPT':MapJLPTKanji, 'K-Freq':MapZoneKanji,  'Jouyou':MapJouyouKanji, 'Kanken':MapKankenKanji}
    mapping = mappings[stat]
    partition = {}
    def assign((key,value)):
        try:
            partition[value].add(key)
        except KeyError:
            partition[value] = set(key)
    map(assign, mapping.Dict.iteritems())
    if stat == 'W-JLPT' or stat =='W-Freq':
        dic = Jx_Word_Occurences
        type = 'Word'
    else:
        dic = Jx_Kanji_Occurences
        type = 'Kanji'
    def assign((id,(fields,metadata,cards,state,history))):
            try:
                content = metadata[type]
                key = mapping.Dict[content]
                partition[key].discard(content)
            except KeyError:
                pass
    map(assign, JxFacts.iteritems())
    for (key,string)in mapping.Order:
        partition[key] = sorted(partition[key],lambda x,y:JxVal(dic,y)-JxVal(dic,x))
    color = dict([(key,True) for (key,string) in mapping.Order])
    buffer = dict([(key,"") for (key,string) in mapping.Order])
    for (key,string) in mapping.Order:
        for stuff in partition[key]:
            color[key] = not(color[key])			
            if color[key]:
                buffer[key] += u"""<a style="text-decoration:none;color:black;" href="py:JxDoNothing(u'%(Stuff)s')">%(Stuff)s</a>""" % {"Stuff":stuff}
            else:
                buffer[key] += u"""<a style="text-decoration:none;color:blue;" href="py:JxDoNothing(u'%(Stuff)s')">%(Stuff)s</a>""" % {"Stuff":stuff}
    html = ''
    for (key,string) in mapping.Order:
        if buffer[key]:
            html += u"""<h2  align="center">%s</h2><p><font size=+2>%s</font></p>""" % (string,buffer[key])
    return html

