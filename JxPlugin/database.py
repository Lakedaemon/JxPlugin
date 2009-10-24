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
JxKnownCoefficient = 1

from copy import deepcopy
JxDeck = {}
JxSavedStats = {}
JxHistory = {}
def build_JxDeck():
    global JxDeck, JxFields, JxTypes, JxStates, JxHistory, JxGraphs, JxStats, JxSavedStats
    JxDeck = load_cache() 
    JxFields = {}
    JxTypes = {}
    JxStates = {}
    JxHistory = {}
    JxStats ={}
    JxGraphs = {}    
    modelsCached = set_models()
    factsCached = set_fields()
    try : 
        JxSavedStats = deepcopy(JxDeck['Stats'])
    except KeyError:
        JxSavedStats = {}
    factsDeleted = drop_facts()
    set_types()
    (States, cardsCached) = get_deltaStates()
    historyCached = set_history(States)
    set_states(States)
    JxDeck['Fields'] = JxFields
    JxDeck['Types'] = JxTypes
    JxDeck['States'] = JxStates
    JxDeck['History'] = JxHistory
    JxDeck['Stats'] = JxStats
    JxDeck['Graphs'] = JxGraphs
    JxDeck['ModelsCached'] = modelsCached
    JxDeck['FactsCached'] = factsCached
    JxDeck['FactsDeleted'] = factsDeleted   
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
        query = """select models.id,models.name,models.tags,fieldModels.ordinal,fieldModels.name, max(models.created,models.modified) from models,fieldModels where models.id = fieldModels.modelId and max( models.created,models.modified)>%.3f""" % modelsCached 
    except KeyError: 
        JxModels = {}
        modelsCached  = 0
        query = """select models.id,models.name,models.tags,fieldModels.ordinal,fieldModels.name,max(models.created,models.modified) from models,fieldModels where models.id = fieldModels.modelId"""

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

JxFields = {}
from anki.utils import stripHTML
def set_fields():
    global JxFields
    """initializes Jxfacts and sets the fields"""
    try:
        JxFields = JxDeck['Fields']    
        factsCached = JxDeck['FactsCached']
        query = """select factId,value, max(created,modified) from fields, facts where fields.factId = facts.id and max(created,modified)>%.3f order by ordinal""" %  factsCached
    except KeyError:
        JxFields = {}
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
        JxFields[id] = fields
    map(copy, dic.iteritems()) # I shouldn't overwrite the other fields...for JxStats/JxGraphs update purpose
    return factsCached

def drop_facts():
    global JxHistory, JxStates, JxFields, JxTypes, JxStates, JxHistory
    try:
        JxFields = JxDeck['Fields']
        JxTypes = JxDeck['Types']       
        JxStates = JxDeck['States']
        JxHistory = JxDeck['History']
        factsDeleted = JxDeck['FactsDeleted']
        query = """select factId,deletedTime from factsDeleted where deletedTime>%.3f""" % factsDeleted  
        update = True
    except KeyError:
        query = """select deletedTime from factsDeleted""" 
        return max(map(lambda x:x[0],mw.deck.s.all(query))+[0])

    changelist = mw.deck.s.all(query)
    workload = {}
    def build_workload((factId, time)):
        try:
            workload[factId] = (False, JxHistory[factId][:])
        except KeyError:
            pass
    map(build_workload,changelist)
    update_graphs(workload)
    worklist = []
    def build((factId,time)):
        try:
            worklist.append((factId,JxStates[factId][0]))
        except KeyError:
            pass
    map(build,changelist)
    set_stats(worklist,False)
    
    def drop((id,time)):
        try: 
            del JxFields[id]
        except:
            pass
        try:
            del JxType[id] 
        except:
            pass
        try: 
            del JxStates[id]
        except:
            pass
        try: 
            del JxHistory[id]
        except:
            pass        
        return time
    return max(map(drop,changelist) + [factsDeleted])

JxTypes = {}
def set_types():
    global JxTypes, JxHistory, JxStates, JxGraphs, debug
    try:
        JxTypes = JxDeck['Types']
        JxStates = JxDeck['States']
        JxHistory = JxDeck['History']
        query = """select facts.id,facts.tags, facts.modelId from facts,models where models.id=facts.modelId and (facts.modified>%.3f or models.modified>%.3f)""" %  (JxDeck['FactsCached'],JxDeck['ModelsCached'])  
        update = True
    except KeyError:
        update = False
        JxTypes = {}
        JxHistory={}
        JxStates={}
        query = """select id, tags, modelId from facts"""
    
    changelist = mw.deck.s.all(query)
    
    #downdate stats/graphs
    if update:
        workload = {}
        def build_workload((factId, tags,modelId)):
            try:
                workload[factId] = (False, JxHistory[factId][:])
            except KeyError:
                pass
        map(build_workload,changelist)

        update_graphs(workload)
        worklist = []
        def build((factId,tags,modelId)):
            try:
                worklist.append((factId,JxStates[factId][0]))
            except KeyError:
                pass
        map(build,changelist)
        set_stats(worklist,False)

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
        fields = JxFields[id]
        metadata = {}
        for (type,(name,ordinal,boolean)) in hints.iteritems():
            content = stripHTML(fields[ordinal])
            if boolean or type in GuessType(content):
                metadata[type] = content 
        JxTypes[id] = metadata
    map(compute,changelist)

    #update stats/graphs
    if update:
        def change_workload((factId,(boolean,dic))):
            workload[factId] = (True, dic)        
        map(change_workload,workload.iteritems())
        update_graphs(workload)
        set_stats(worklist,True)

    
def get_deltaStates():
    global JxStates
    try:
        JxStates = JxDeck['States']
        cardsCached = JxDeck['CardsCached']
        query = """select cards.factId, cards.id, cards.interval, cards.reps, max(cards.created, cards.modified) from cards where max(cards.created,cards.modified)>%.3f""" % cardsCached
    except KeyError:
        JxStates = {}
        cardsCached = 0
        query = """select factId, id, interval, reps, max(created, modified) from cards"""      
     
    cardsStates = {}
    def assign((factId,id,interval,reps,cached)):
        """sets the cards states in the Jx database JxDeck"""
        if interval > JxKnownThreshold and reps:
            status = 1 # known
        elif reps:
            status = 0 # seen
        else:
            status = -1 # in deck
        try:
            cardsStates[factId][id] = status
        except KeyError:
            cardsStates[factId] = {id : status} 
        return cached
    cardsCached = max(map(assign, mw.deck.s.all(query)) + [cardsCached])

    States = {}
    def compute((factId,dic)):
        list = [status for status in dic.values() if status>=0]
        threshold = len(dic) * JxKnownCoefficient
        if list and sum(list)>= threshold:
            status = 1# known
        elif list:
            status = 0# seen
        else:
            status = -1# in deck
        States[factId] = (status, dic)
    map(compute, cardsStates.iteritems())

    return (States, cardsCached)
    
def set_states(States):
    # compute the fact statuses and sets card & fact states
    
    def build(factId):
        return (factId,JxStates[factId][0])    
    
    if JxStats:
        set_stats(map(build,States.keys()),False)
    
    def copy((factId, (status, cardsStates))):
        JxStates[factId] = (status, cardsStates)
    map(copy, States.iteritems())
    
    set_stats(map(build,States.keys()),True)
    #midnightOffset = time.timezone - self.deck.utcOffset
    #self.endOfDay = time.mktime(now) - midnightOffset
    #todaydt = datetime.datetime(*list(time.localtime(time.time())[:3]))
   
def set_stats(List, add=True):
    global JxStats
    try:
        JxStats = JxDeck['Stats']
        build= False
    except KeyError:
        JxStats = {} 
        build = True
        add = True
    for type in ['Word','Kanji']:
        def select((factId, status)):
            try:
                return (JxTypes[factId][type], status)
            except KeyError:
                return None
        list = filter(lambda x: x != None, map(select,List))
        
        JxStatTasks = {'Word':{'W-JLPT':MapJLPTTango,'W-Freq':MapZoneTango,'W-AFreq':MapZoneTango}, 'Kanji':{'K-JLPT':MapJLPTKanji,'K-Freq':MapZoneKanji,'K-AFreq':MapZoneKanji,'Jouyou':MapJouyouKanji,'Kanken':MapKankenKanji}} 
        
        for (name,mapping) in JxStatTasks[type].iteritems():           
            if  name == 'W-AFreq':
                def assign_WAF((content,state)):
                    try:
                        value = mapping.Value(content)
                        if add:
                            increment = Jx_Word_Occurences[content]
                        else:
                            increment = - Jx_Word_Occurences[content]
                        try:
                            JxStats[(name,state,value)] += increment
                        except KeyError:
                            JxStats[(name,state,value)] = increment
                    except KeyError:
                        pass                         
                map(assign_WAF,list)
                if build:
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
                        if add:
                            increment = Jx_Kanji_Occurences[content]
                        else:
                            increment = - Jx_Kanji_Occurences[content]                            
                        try:
                            JxStats[(name,state,value)] += increment
                        except KeyError:
                            JxStats[(name,state,value)] = increment
                    except KeyError:
                        pass        
                map(assign_KAF,list) 
                if build:
                    def count_KAF((content,value)):
                        zone = Kanji2Zone[content]
                        try:
                            JxStats[(name,'Total',zone)] += value
                        except KeyError:
                            JxStats[(name,'Total',zone)] = value                
                    map(count_KAF,Jx_Kanji_Occurences.iteritems()) 
            else:     
                if add:
                    increment = 1
                else:
                    increment = -1
                def assign((content,state)):
                    try:
                        value = mapping.Value(content)
                    except KeyError:
                        value = 'Other'                           
                    try:
                        JxStats[(name,state,value)] += increment
                    except KeyError:
                        JxStats[(name,state,value)] = increment
                map(assign,list)
                if build:
                    def count(value):
                        try:
                            JxStats[(name,'Total',value)] += 1
                        except KeyError:
                            JxStats[(name,'Total',value)] = 1                
                    map(count,mapping.Dict.values())

def set_history(States): 
    global JxGraphs, debug
    try:
        historyCached = JxDeck['HistoryCached']
        JxGraphs = JxDeck['Graphs']
        build = False
        query = """select cards.factId, reviewHistory.cardId, reviewHistory.lastInterval, reviewHistory.nextInterval, reviewHistory.ease, reviewHistory.time from cards, reviewHistory where cards.id = reviewHistory.cardId and reviewHistory.time>%.3f  order by reviewHistory.cardId, reviewHistory.time""" %  historyCached
    except KeyError:
        historyCached = 0
        JxGraphs = {}# I can use this to decide if I should build or not maybee
        build = True
        query = """select cards.factId, reviewHistory.cardId, reviewHistory.lastInterval, reviewHistory.nextInterval, reviewHistory.ease, reviewHistory.time from cards, reviewHistory where cards.id = reviewHistory.cardId order by reviewHistory.cardId, reviewHistory.time"""
        
    history = {}         
    global card    
    card = None
    def assign((factId,id,interval,nextInterval,ease,time)):
        """sets the cards status changes in the Jx database JxDeck"""
        global switch
        global card
        if card != id:
            if build:
                switch = True
            else:            
                switch = (JxStates[factId][1][id] != 1)
            card = id
        if (nextInterval > JxKnownThreshold  and switch) or (nextInterval <= JxKnownThreshold  and not(switch)):
            switch = not(switch)
            #Card Status Change
            day = int(time / 86400.0)
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
    try:
        del card
        del switch
    except :
        pass
    deltaHistory = {}
    def compute((factId,cardsHistory)):
        if build:
            (status, cardsStates) = States[factId]
        else:            
             (status, cardsStates) = JxStates[factId]
        stateArray = {}    
        for (id,changes) in cardsHistory.iteritems():
            if build:
                boolean = True
            else:
                boolean = (cardsStates[id] != 1)
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


        threshold = len(cardsStates) * JxKnownCoefficient
        if build:
            boolean = True
        else:
            boolean = (status != 1)

        list = []
        if build:
            cumul = 0
        else : 
            cumul = len([1 for state in cardsStates.values() if state ==1])
        for day in days:
            cumul += stateArray[day]
            if (boolean and cumul >=threshold ) or (not(boolean) and cumul < threshold): #xor
                list.append(day)
                boolean = not(boolean)  
        if build:
            JxHistory[factId] = list[:]
            deltaHistory[factId] = (True, list[:])
        else:
            JxHistory[factId].append(list[:])
            deltaHistory[factId] = ((status != 1), list[:])             
        
    map(compute, history.iteritems())
    update_graphs(deltaHistory)
        
    return historyCached


def update_graphs(dic):
    global JxGraphs
    try:
        JxGraphs = JxDeck['Graphs']
    except KeyError:
        JxGraphs = {}
    for type in ['Word','Kanji']:
        def select((id,(add,changelist))):
            try:
                return (JxTypes[id][type], add, changelist)
            except KeyError:
                return None
        list = filter(lambda x: x != None, map(select,dic.iteritems()))

        tasks = {'Word':{'W-JLPT':MapJLPTTango,'W-AFreq':MapZoneTango}, 'Kanji':{'K-JLPT':MapJLPTKanji,'K-AFreq':MapZoneKanji,'Jouyou':MapJouyouKanji,'Kanken':MapKankenKanji}} 
        
        for (name,mapping) in tasks[type].iteritems():  
            if  name == 'W-AFreq':
                def assign_WAF((content, add, days)):
                    try:
                        value = mapping.Value(content)
                        increment = Jx_Word_Occurences[content]
                        try:
                            stateArray = JxGraphs[(name,value)]
                        except KeyError:
                            JxGraphs[(name,value)] = {}
                            stateArray = JxGraphs[(name,value)]
                        boolean = add
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
                def assign_KAF((content,add,days)):
                    try:
                        value = mapping.Value(content)
                        increment = Jx_Kanji_Occurences[content]
                        try:
                            stateArray = JxGraphs[(name,value)]
                        except KeyError:
                            JxGraphs[(name,value)] = {}
                            stateArray = JxGraphs[(name,value)]
                        boolean = add
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
                def assign((content,add,days)):
                    boolean = add
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
          
def get_stat(key):
    try:
        return JxStats[key]
    except KeyError:
        return 0

def get_ancient_stat(key):
    try:
        return JxSavedStats[key]
    except KeyError:
        return 0

def get_report(new,ancient) :
    if not(JxSavedStats) or new == ancient:
        return "%.0f" % new
    elif ancient < new:
        return """%.0f<sup>&nbsp;<font face="Comic Sans MS" color="green" size=2>+%d</font></sup>""" % (new,new-ancient)
    else:
        return """%.0f<sup>&nbsp;<font face="Comic Sans MS" color="red" size=2>-%d</font></sup>""" % (new,ancient-new)    

def JxVal(Dict,x):
    try:
        return  Dict[x]
    except KeyError:
        return -1        
        
def display_stats(stats):
    mappings = {'W-JLPT':MapJLPTTango, 'W-Freq':MapZoneTango, 'K-JLPT':MapJLPTKanji, 'K-Freq':MapZoneKanji,  'Jouyou':MapJouyouKanji, 'Kanken':MapKankenKanji}
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
    (AsumKnown, AsumSeen, AsumInDeck)=(0,0,0)
    for (key,value) in mapping.Order:
        known = get_stat((stats,1,key))
        seen = known + get_stat((stats,0,key))
        inDeck = seen + get_stat((stats,-1,key))
        total = get_stat((stats,'Total',key))
        sumKnown += known
        sumSeen += seen
        sumInDeck += inDeck
        sumTotal += total
        if JxSavedStats:
            Aknown = get_ancient_stat((stats,1,key))
            Aseen = Aknown + get_ancient_stat((stats,0,key))
            AinDeck = Aseen + get_ancient_stat((stats,-1,key))
        else:
            Aknown = known
            Aseen = seen
            AinDeck = inDeck              
        AsumKnown += Aknown
        AsumSeen += Aseen        
        AsumInDeck += AinDeck       
        knownString = get_report(known, Aknown)
        seenString = get_report(seen, Aseen)
        inDeckString = get_report(inDeck, AinDeck)
        html += """
        <tr class="Background">
		    <td><b>%s</b></td>
		    <td><b style="font-size:small">%.0f%%</b></td>
		    <td>%s</td>
		    <td>%s</td>
		    <td>%s</td>
		    <td class="BorderRight">%.0f</td>
		</tr>""" % (value, known*100.0/max(1,total), knownString, seenString, inDeckString, total)
	sumKnownString = get_report(sumKnown, AsumKnown)
    sumSeenString = get_report(sumSeen, AsumSeen)
    sumInDeckString = get_report(sumInDeck, AsumInDeck)
    html += """
    <tr class="Border BackgroundHeader">
        <td><b>%s</b></td>
        <td><b style="font-size:small">%.0f%%</b></td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td class="BorderRight">%.0f</td>
    </tr>""" % ('Total',sumKnown*100.0/max(1,sumTotal),sumKnownString,sumSeenString,sumInDeckString,sumTotal)     
    known = get_stat((stats,1,'Other'))
    seen = known + get_stat((stats,0,'Other'))
    inDeck = seen + get_stat((stats,-1,'Other'))
    if JxSavedStats:
        Aknown = get_ancient_stat((stats,1,'Other'))
        Aseen = Aknown + get_ancient_stat((stats,0,'Other'))
        AinDeck = Aseen + get_ancient_stat((stats,-1,'Other'))
    else:
        Aknown = known
        Aseen = seen
        AinDeck = inDeck         
    if (known,seen,inDeck) != (0,0,0):
        knownString = get_report(known, Aknown)
        seenString = get_report(seen, Aseen)
        inDeckString = get_report(inDeck, AinDeck)  
        html += """
        <tr>
            <td style="border:0px solid black;"><b>%s</b></td>
            <td></td><td>%s</td>
            <td>%s</td>
            <td>%s</td>
            <td></td>
        </tr>""" % ('Other', knownString, seenString, inDeckString)                
    html += '</table>'
    return html

def get_Areport(new,ancient) :
    if not(JxSavedStats) or new == ancient:
        return "%s%%" % JxFormat(new)
    elif ancient < new:
        return """%s%%<br/><font face="Comic Sans MS" color="green" size=2>+%s%%</font>""" % (JxFormat(new),JxFormat(new-ancient))
    else:
        return """%s%%<br/><font face="Comic Sans MS" color="red" size=2>-%s%%</font>""" % (JxFormat(new),JxFormat(ancient-new))    

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
    if JxSavedStats:
        AgrandTotal = sum([get_ancient_stat((stats,'Total',key)) for (key, value) in mapping.Order])     
    else:
        AgrandTotal = grandTotal
    (sumKnown, sumSeen, sumInDeck, sumTotal)=(0,0,0,0)
    (AsumKnown, AsumSeen, AsumInDeck)=(0,0,0)
    for (key,value) in mapping.Order:
        known = get_stat((stats,1,key))
        seen = known + get_stat((stats,0,key))
        inDeck = seen + get_stat((stats,-1,key))
        total = get_stat((stats,'Total',key))
        sumKnown += known
        sumSeen += seen
        sumInDeck += inDeck
        sumTotal += total
        if JxSavedStats:
            Aknown = get_ancient_stat((stats,1,key))
            Aseen = Aknown + get_ancient_stat((stats,0,key))
            AinDeck = Aseen + get_ancient_stat((stats,-1,key))
        else:
            Aknown = known
            Aseen = seen
            AinDeck = inDeck              
        AsumKnown += Aknown
        AsumSeen += Aseen        
        AsumInDeck += AinDeck      
        html +="""
        <tr class="Background">
            <td><b>%s</b></td>
            <td>%s%%</td>
            <td>%s%%</td>
            <td>%s%%</td>
            <td class="BorderRight">%.0f%%</td>
        </tr>""" % (value, JxFormat(known*100.0/max(1,grandTotal)), JxFormat(seen*100.0/max(1,grandTotal)), JxFormat(inDeck*100.0/max(1,grandTotal)), total*100.0/max(1,grandTotal))
    sumKnownString = get_Areport(sumKnown*100.0/max(1,grandTotal), AsumKnown*100.0/max(1,AgrandTotal))
    sumSeenString = get_Areport(sumSeen*100.0/max(1,grandTotal), AsumSeen*100.0/max(1,AgrandTotal))
    sumInDeckString = get_Areport(sumInDeck*100.0/max(1,grandTotal), AsumInDeck*100.0/max(1,AgrandTotal))
    html += """
    <tr class="Border BackgroundHeader">
        <td><b>Total</b></td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td class="BorderRight">100%%</td>
    </tr>""" % (sumKnownString,sumSeenString,sumInDeckString)        
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
        

    

                
def display_partition(stat,label):
    """Returns an Html report of the label=known|seen|in deck stuff inside the list stat"""
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
    def assign((id,(state, cardsStates))):
        if state==label:
            try:
                content = JxTypes[id][type]
                try:
                    key = mapping.Dict[content]
                except KeyError:
                    key = 'Other'
                partition[key].append((content,id))
            except KeyError:
                pass
    map(assign, JxStates.iteritems())


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
    def assign((id,metadata)):
            try:
                content = metadata[type]
                key = mapping.Dict[content]
                partition[key].discard(content)
            except KeyError:
                pass
    map(assign, JxTypes.iteritems())
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

