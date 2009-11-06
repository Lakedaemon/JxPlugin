# -*- coding: utf-8 -*-
# Copyright: Olivier Binda <olivier.binda@wanadoo.fr>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
# ---------------------------------------------------------------------------
# This file is a plugin for the "anki" flashcard application http://ichi2.net/anki/
# ---------------------------------------------------------------------------
import cPickle
from copy import deepcopy

from ankiqt import mw
from PyQt4.QtCore import QObject
from anki.utils import stripHTML

from loaddata import *
from controls import JxBase

from JxPlugin.japan import JxType,JxTypeJapanese,GuessType, parse_content

def sliding_day(seconds):
    """let's decide that a day stats at 4h in the morning, to minimize border problems (you should be sleeping at that time)""" 
    return int((seconds - time.timezone + 14400) / 86400.0)

class Database(QObject):
    """Data structure for the JxPlugin tables"""
    
    def __init__(self,name="Deck",parent=JxBase):
        QObject.__init__(self,parent)
        self.setObjectName(name)
        try:
            self.load()
            from controls import JxSettings
            if sliding_day(time.time()) - sliding_day(self.cache['cacheBuilt']) <= JxSettings.Get('cacheRebuild'):
                self.update() 
            else:
                self.reset()       
        except KeyError:
            self.reset()
            
    #############################      
    #                           #
    # Maintain the database     #
    #                           #
    #############################
    
    def reset(self):
        self.cache = {'models':{}, 'fields':{}, 'types':{}, 'states':{}, 'history':{}, 'stats':{}, 'oldStats':{},'graphs':{}, 
        'modelsModified':0, 'factsDeleted':0, 'factsModified':0, 'cardsModified':0, 'historyModified':0, 'statsModified':0, 
        'cacheBuilt':0, 'cardsKnownThreshold':21,'factsKnownThreshold':1}
        self.build()
        
    def update(self):
        self.reference_data()
        self.set_models(True)
        self.set_fields(True)
        self.save_stats(True)
        self.drop_deleted_facts(True)
        self.set_types(True)
        self.set_new_states(True)
        self.set_history(True)
        self.apply_new_states(True)
        self.save() 
        
    def build(self):
        self.reference_data()
        self.set_models(False)
        self.set_fields(False)
        self.drop_deleted_facts(False)
        self.set_types(False)
        self.set_efacts(False)
        self.set_new_states(False)
        self.set_history(False)
        self.apply_new_states(False)        
        self.save_stats(False)
        self.save() 

    def set_efacts(self):
        pass

    def set_cardsKnownThreshold(self,value):
        val = int(value)
        if val != self.cardsKnownThreshold:
            self.cache.update({'states':{}, 'history':{}, 'stats':{}, 'oldStats':{},'graphs':{},
                'cardsModified':0, 'historyModified':0, 'statsModified':0, 'cacheBuilt':0, 
                'cardsKnownThreshold':val})
            self.reference_data()
            self.set_new_states(False)
            self.set_history(False)
            self.apply_new_states(False)   
            self.save_stats(False)
            self.save()        
      
    def set_factsKnownThreshold(self,value): 
        val = float(value)
        if val != self.factsKnownThreshold:
            self.cache.update({'states':{},'history':{}, 'stats':{}, 'oldStats':{},'graphs':{},
                'cardsModified':0, 'historyModified':0, 'statsModified':0, 'cacheBuilt':0, 
                'factsKnownThreshold':val})
            self.reference_data()
            self.set_new_states(False)
            self.set_history(False)
            self.apply_new_states(False)    
            self.save_stats(False)
            self.save()   

    def reference_data(self):
        cache = self.cache
        self.models = cache['models']
        self.fields = cache['fields']
        self.types = cache['types']
        self.states = cache['states']
        self.history = cache['history']
        self.stats = cache['stats']
        self.oldStats = cache['oldStats']
        self.graphs = cache['graphs']
            
        self.modelsModified = cache['modelsModified']
        self.factsDeleted = cache['factsDeleted']
        self.factsModified = cache['factsModified']
        self.cardsModified = cache['cardsModified']
        self.historyModified = cache['historyModified']
            
        self.statsModified = cache['statsModified']
        self.cacheBuilt = cache['cacheBuilt']
        self.cardsKnownThreshold = cache['cardsKnownThreshold']
        self.factsKnownThreshold = cache['factsKnownThreshold']
            
    def load(self):
        """returns the cache if it exists on disk and {} if it doesn't"""
        path = os.path.join(mw.config.configPath, "plugins", "JxPlugin", "Cache", mw.deck.name() + ".cache")                      
        if not os.path.exists(path): 
            self.cache = {}
        else:
            file = open(path, 'rb')
            self.cache = cPickle.load(file)
            file.close()
        
    def save(self):
        from ui_menu import JxStats
        """saves the cache on disk"""  
        #mw.help.showText(self.debug)
        path = os.path.join(mw.config.configPath, "plugins", "JxPlugin", "Cache", mw.deck.name() + ".cache")   
        file = open(path, 'wb')
        cPickle.dump(self.cache, file, cPickle.HIGHEST_PROTOCOL)
        file.close()        

    def set_models(self,update):
        """builds the models and hints if update is false or updates them otherwise"""
        
        # sets things up for the build/update process
        if update:
            dic = {}
            query = """select models.id,models.name,models.tags,fieldModels.ordinal,fieldModels.name, models.modified from models,fieldModels where models.id = fieldModels.modelId and models.modified>%.8f""" % self.modelsModified
        else:
            dic = self.models
            query = """select models.id,models.name,models.tags,fieldModels.ordinal,fieldModels.name,models.modified from models,fieldModels where models.id = fieldModels.modelId"""

        # then sets the JxModels name, tags, fieldsnames and ordinals     
        def assign((id, name, tags, ordinal, fieldName, cached)):
            try: 
                model = dic[id]
            except KeyError:
                dic[id] = (name,tags,{},{})
                model = dic[id]
            model[2][ordinal]= fieldName
            return cached
        self.cache['modelsModified'] = max(map(assign,mw.deck.s.all(query))+[self.modelsModified])
    
        # then computes types and hints
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
        if update:
            models= self.models
            def copy((id, model)): 
                models[id] = model
            map(copy, dic.iteritems()) 
        self.debug = "Models (" + str(len(dic)) +")<br/>" 
    
    def set_fields(self,update):
        from anki.utils import stripHTML
        """fills the fields if update is false or overwrites them otherwise"""
        if update:  
            dic = {}
            query = """select factId,value, modified from fields, facts where fields.factId = facts.id and modified>%.8f order by ordinal""" %  self.factsModified
        else:
            dic = self.fields
            query = """select factId,value, modified from fields, facts where fields.factId = facts.id order by ordinal"""
    
        def assign((id,value,cached)):
            """basically does factsDB[factId].update(ordinal=value)"""
            try:
                fields = dic[id]
            except KeyError:
                dic[id] = {}
                fields = dic[id]
            fields[len(fields)] = value# this is coded this way because in the anki database ordinal fields in fieldModels and fields aren't necessarily equals...
            return cached
        self.cache['factsModified'] = max(map(assign,mw.deck.s.all(query)) + [self.factsModified])
    
        if update:
            # overwrite the fields
            fields = self.fields
            def copy((id,dict)):
                fields[id] = dict
            map(copy, dic.iteritems())
        self.debug += "Facts (" + str(len(dic)) +")<br/>" 
        
    def save_stats(self, update):
        from copy import deepcopy
        from controls import JxSettings
        now = time.time()
        if not(update) or sliding_day(now) - sliding_day(self.statsModified) >= int(JxSettings.Get('reportReset')):
            self.cache['oldStats'] = deepcopy(self.stats)
            self.cache['statsModified'] = now
            self.oldStats = self.cache['oldStats']
        
    def drop_deleted_facts(self,update):
        if update:
            query = """select factId,deletedTime from factsDeleted where deletedTime>%.8f""" % self.factsDeleted  
        else:
            # no need to drop facts
            query = """select deletedTime from factsDeleted""" 
            self.factsDeleted = max(map(lambda x:x[0],mw.deck.s.all(query))+[0]) # I want python to compute the max, this is why I code this like this
            return
            
        drop = mw.deck.s.all(query)
        self.debug += "Facts (-" + str(len(drop)) +") : " 
        list = []
        dic = {}
        history = self.history
        states = self.states
        def build((factId, time)):
            try:
                dic[factId] = (False, history[factId][:])
                list.append((factId, states[factId][0]))
            except KeyError:
                pass
            return time
        self.cache['factsDeleted'] = max(map(build,drop) + [self.factsDeleted]) 
        self.update_graphs(dic)
        self.set_stats(list,-1)
        fields = self.fields
        types = self.types
        states = self.states
        history = self.history
        def delete((id,time)):
            try: 
                del fields[id]
                del types[id] 
                del states[id]
                del history[id]
            except:
                pass        
        map(delete,drop) 

         
    def set_types(self,update):
        if update:
            query = """select facts.id,facts.tags, facts.modelId from facts,models where models.id=facts.modelId and (facts.modified>%.8f or models.modified>%.8f)""" %  (self.factsModified,self.modelsModified)  
        else:
            query = """select id, tags, modelId from facts"""
    
        table = mw.deck.s.all(query)
    
        #downdate stats/graphs
        history = self.history
        states = self.states
        if update:
            dic = {}
            lis = []
            def build((factId, tags,modelId)):
                try:
                    dic[factId] = (False, history[factId][:])
                    lis.append((factId,states[factId][0]))
                except KeyError:
                    pass
            map(build,table)
            self.debug += "---- " 
            self.update_graphs(dic)
            self.set_stats(lis,-1)          

        models = self.models
        def compute((id,tags,modelId)):
            types = set()
            test = set(tags.split(" "))
            for (key,list) in JxType:
                if test.intersection(list):
                    types.update([key])
            if not(types): 
                hints = models[modelId][3]
            else:
                hints={}
                modelFields = models[modelId][2].iteritems()
                # first, we try to affect relevant fields for each type (first try fields with the name similar to the type)
                for (type,typeList) in JxType:
                    if type in types:
                        for (ordinal,name) in modelFields:
                            if name in typeList:
                                    hints[type] = (name,ordinal,True) 
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
            fields = self.fields[id]
            metadata = {}
            for (type,(name,ordinal,boolean)) in hints.iteritems():
                ######################################################################## I will have to change it there thanks to mecab
                #content = stripHTML(fields[ordinal])
                #if boolean or type in GuessType(content):
                #    metadata[type] = content 
                metadata.update(parse_content(stripHTML(fields[ordinal]),type))
                ######################################################################## (type, boolean, content) ->  metadata[type] = guessed content if non empty
            self.types[id] = metadata
        map(compute,table)
        
        self.debug += "Types (" + str(len(table)) + ")<br/>" 
        
        #update stats/graphs
        if update:
            def invert((factId,(boolean,dict))):
                dic[factId] = (True, dict)        
            map(invert,dic.iteritems())
            self.debug += "++++ " 
            self.update_graphs(dic)
            self.set_stats(lis,1)
            
    def set_new_states(self,update):
        if update:
            self.newStates = {}
            States = self.newStates
            query = """select cards.factId, cards.id, cards.interval, cards.reps, cards.modified from cards where cards.modified>%.8f""" % self.cardsModified
        else:
            States = self.states
            query = """select factId, id, interval, reps, modified from cards"""      
     
        cardsStates = {}
        cardsKnownThreshold = self.cardsKnownThreshold
        factsKnownThreshold = self.factsKnownThreshold
        def assign((factId,id,interval,reps,cached)):
            """sets the cards states in the Jx database JxDeck"""
            if interval > cardsKnownThreshold and reps:
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
        self.cache['cardsModified'] = max(map(assign, mw.deck.s.all(query)) + [self.cardsModified])
        #self.cardsModified= self.cache['cardsModified'] 
        
        def compute((factId,dic)):
            list = [status for status in dic.values() if status>=0]
            threshold = len(dic) * factsKnownThreshold 
            if list and sum(list)>= threshold:
                status = 1# known
            elif list:
                status = 0# seen
            else:
                status = -1# in deck
            States[factId] = (status, dic)
        map(compute, cardsStates.iteritems())
        self.debug += "States (" + str(len(cardsStates)) + ")<br/>" 
            
    def set_history(self,update): 
        if update:
            query = """select cards.factId, reviewHistory.cardId, reviewHistory.lastInterval, reviewHistory.nextInterval, reviewHistory.ease, reviewHistory.time from cards, reviewHistory where cards.id = reviewHistory.cardId and reviewHistory.time>%.8f  order by reviewHistory.cardId, reviewHistory.time""" %  self.historyModified
        else:
            query = """select cards.factId, reviewHistory.cardId, reviewHistory.lastInterval, reviewHistory.nextInterval, reviewHistory.ease, reviewHistory.time from cards, reviewHistory where cards.id = reviewHistory.cardId order by reviewHistory.cardId, reviewHistory.time"""
        
        history = {}         
        self.cardId = None
        states = self.states
        cardsKnownThreshold = self.cardsKnownThreshold
        factsKnownThreshold = self.factsKnownThreshold        
        def assign((factId,id,interval,nextInterval,ease,time)):
            """sets the cards status changes in the Jx database JxDeck"""
            if self.cardId != id:
                if update:
                    try:
                        self.switch = (states[factId][1][id] != 1)
                    except KeyError:
                        # in case a new fact has been created
                        self.switch = True                             
                else:
                    self.switch = True            
                self.cardId = id
            if (nextInterval > cardsKnownThreshold  and self.switch) or (nextInterval <= cardsKnownThreshold  and not(self.switch)):
                self.switch = not(self.switch)
                #Card Status Change
                day = sliding_day(time)
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
        self.cache['historyModified'] = max(map(assign,mw.deck.s.all(query)) + [self.historyModified])
        
        self.debug += "History ("+str(len(history)) + ") : "         
        
        deltaHistory = {}
        def compute((factId,cardsHistory)):         
            (status, cardsStates) = states[factId]
            stateArray = {}    
            for (id,changes) in cardsHistory.iteritems():
                if update: 
                    boolean = (cardsStates[id] != 1)                    
                else:
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

            list = []
            threshold = len(cardsStates) * factsKnownThreshold
            if update:
                boolean = (status != 1)
                cumul = len([1 for state in cardsStates.values() if state ==1])
            else:
                boolean = True
                cumul = 0

            for day in days:
                cumul += stateArray[day]
                if (boolean and cumul >=threshold ) or (not(boolean) and cumul < threshold): #xor
                    list.append(day)
                    boolean = not(boolean)  
            if update:
                try:
                    self.history[factId].extend(list[:]) ##### no risk taken 
                except KeyError:
                    self.history[factId]=list[:]
                deltaHistory[factId] = ((status != 1), list[:])  
            else:
                self.history[factId] = list[:]
                deltaHistory[factId] = (True, list[:])
        
        map(compute, history.iteritems())

        self.update_graphs(deltaHistory)

    def update_graphs(self,dic):
        self.debug += "graphs(" + str(len(dic)) +")&nbsp;&nbsp;&nbsp;" 
        types = self.types
        graphs = self.graphs
        for type in ['Word','Kanji']:
            def select((id,(add,changelist))):
                try:
                    return (types[id][type], add, changelist)
                except KeyError:
                    return None
            list = filter(lambda x: x != None, map(select,dic.iteritems()))

            tasks = {'Word':{'W-JLPT':MapJLPTTango,'W-AFreq':MapZoneTango}, 'Kanji':{'K-JLPT':MapJLPTKanji,'K-AFreq':MapZoneKanji,'Jouyou':MapJouyouKanji,'Kanken':MapKankenKanji}} 
        
            for (name,mapping) in tasks[type].iteritems():  
                if  name == 'W-AFreq' or name == 'K-AFreq':
                    if name == 'K-AFreq':
                        dict = MapFreqKanji                     
                    else:
                        dict = MapFreqTango      
                    def assign((content, add, days)):
                        try:
                            value = mapping.Value(content)
                            increment = dict.Value(content)
                            try:
                                stateArray = graphs[(name,value)]
                            except KeyError:
                                graphs[(name,value)] = {}
                                stateArray = graphs[(name,value)]
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
                else:               
                    def assign((content,add,days)):
                        boolean = add
                        try:
                            value = mapping.Value(content)
                        except KeyError:
                            value = 'Other'
                        try:
                            stateArray = graphs[(name,value)]
                        except KeyError:
                            graphs[(name,value)] = {}
                            stateArray = graphs[(name,value)]
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

    def apply_new_states(self,update):
        """downdates stats, apply new states and updates stats""" 
        states = self.states
        def build(factId):
                return (factId,states[factId][0])
        self.debug += "<br/>ApplyStates :"
        if update:
            self.set_stats(map(build,[id for id in self.newStates.keys() if id in states]),-1)
            states.update(self.newStates)
            self.debug += " --> "
            self.set_stats(map(build,self.newStates.keys()),1)
            del self.newStates
        else:
            self.set_stats(map(build,self.states.keys()),0)


    def set_stats(self, List, add):
        """updates stats positively if add>0, negatively if add<0 or build stats if add=0"""
        self.debug += "stats(" + str(len(List))  + ")<br/>" 
        types = self.types
        for type in ['Word','Kanji']:
            def select((factId, status)):
                try:
                    return (types[factId][type], status)
                except KeyError:
                    return None
            list = filter(lambda x: x != None, map(select,List))
        
            JxStatTasks = {'Word':{'W-JLPT':MapJLPTTango,'W-Freq':MapZoneTango,'W-AFreq':MapZoneTango}, 'Kanji':{'K-JLPT':MapJLPTKanji,'K-Freq':MapZoneKanji,'K-AFreq':MapZoneKanji,'Jouyou':MapJouyouKanji,'Kanken':MapKankenKanji}} 
        
            stats = self.stats
            for (name,mapping) in JxStatTasks[type].iteritems():           
                if  name == 'W-AFreq' or name == 'K-AFreq':
                    if name == 'K-AFreq':
                        dic = MapFreqKanji
                    else:
                        dic = MapFreqTango
                    def assign_A((content,state)):
                        try:
                            value = mapping.Value(content)
                            if add >= 0:
                                increment = dic.Value(content)
                            else:
                                increment = - dic.Value(content)
                            try:
                                stats[(name,state,value)] += increment
                            except KeyError:
                                stats[(name,state,value)] = increment
                        except KeyError:
                            pass                         
                    map(assign_A,list)
                    if add == 0:
                        zoneDict = mapping.Dict
                        def count_A((content,value)):
                            zone = zoneDict[content]
                            try:
                                stats[(name,'Total',zone)] += value
                            except KeyError:
                                stats[(name,'Total',zone)] = value                
                        map(count_A,dic.Dict.iteritems())
                else:  
                    if add >= 0:
                        increment = 1
                    else:
                        increment = -1
                    def assign((content,state)):
                        try:
                            value = mapping.Value(content)
                        except KeyError:
                            value = 'Other'                           
                        try:
                            stats[(name,state,value)] += increment
                        except KeyError:
                            stats[(name,state,value)] = increment
                    map(assign,list)
                    if add == 0:
                        def count(value):
                            try:
                                stats[(name,'Total',value)] += 1
                            except KeyError:
                                stats[(name,'Total',value)] = 1                
                        map(count,mapping.Dict.values())

    #############################      
    #                           #
    #   Access the database     #
    #                           #
    #############################

    def get_stat(self,key):
        try:
            return self.stats[key]
        except KeyError:
            return 0

    def get_old_stat(self,key):
        try:
            return self.oldStats[key]
        except KeyError:
            return 0

############################### 
 
 
 
 
 
    
def build_JxDeck():
    """loads JxDeck and inits stuff"""
    global eDeck
    eDeck = Database()




   
                
import time
def JxGraphs_into_json():
    global JxGraphs
    graphs = eDeck.graphs
    today = sliding_day(time.time())
    dict_json = {}
    tasks = {'W-JLPT':MapJLPTTango, 'W-AFreq':MapZoneTango, 'K-JLPT':MapJLPTKanji, 'K-AFreq':MapZoneKanji, 'Jouyou':MapJouyouKanji, 'Kanken':MapKankenKanji} 
    for (graph,mapping) in tasks.iteritems():
        for (key,string) in mapping.Order +[('Other','Other')]:
            if graph == 'W-AFreq':
                    a = 100.0/Jx_Word_SumOccurences
            elif graph == 'K-AFreq':
                    a = 100.0/Jx_Kanji_SumOccurences
            else:
                    a = 1
            try:
                dict = graphs[(graph,key)]
            except KeyError:
                dict = {}
            if today not in dict:
                dict[today] = 0
            sortedList = list(dict.iteritems())
            sortedList.sort(lambda x,y:x[0]-y[0])
            s = 0
            List = []
            for (day,value) in sortedList:
                s = s + value
                List.append("[%s,%s]"% (day - today,s * a))
            dict_json[(graph,key)] =  "[" + ",".join(List) + "]"              
    return dict_json

def get_report(new,ancient) :
    if  new == ancient:
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
    get_stat = eDeck.get_stat
    get_old_stat = eDeck.get_old_stat
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
        Aknown = get_old_stat((stats,1,key))
        Aseen = Aknown + get_old_stat((stats,0,key))
        AinDeck = Aseen + get_old_stat((stats,-1,key))           
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
    Aknown = get_old_stat((stats,1,'Other'))
    Aseen = Aknown + get_old_stat((stats,0,'Other'))
    AinDeck = Aseen + get_old_stat((stats,-1,'Other'))     
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
    if  new == ancient:
        return "%s%%" % JxFormat(new)
    elif ancient < new:
        return """%s%%<br/><font face="Comic Sans MS" color="green" size=2>+%s%%</font>""" % (JxFormat(new),JxFormat(new-ancient))
    else:
        return """%s%%<br/><font face="Comic Sans MS" color="red" size=2>-%s%%</font>""" % (JxFormat(new),JxFormat(ancient-new))    

def display_astats(stats):
    mappings = {'W-AFreq':MapZoneTango, 'K-AFreq':MapZoneKanji}
    mapping = mappings[stats]
    get_stat = eDeck.get_stat
    get_old_stat = eDeck.get_old_stat
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
    AgrandTotal = sum([get_old_stat((stats,'Total',key)) for (key, value) in mapping.Order])     
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
        Aknown = get_old_stat((stats,1,key))
        Aseen = Aknown + get_old_stat((stats,0,key))
        AinDeck = Aseen + get_old_stat((stats,-1,key))        
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
        

def JxValue(mapping,x):
    try:
        return  mapping.Value(x)
    except KeyError:
        return -1     

                
def display_partition(stat,label):
    """Returns an Html report of the label=known|seen|in deck stuff inside the list stat"""
    mappings = {'W-JLPT':MapJLPTTango, 'W-Freq':MapZoneTango, 'K-JLPT':MapJLPTKanji, 'K-Freq':MapZoneKanji,  'Jouyou':MapJouyouKanji, 'Kanken':MapKankenKanji}
    mapping = mappings[stat]
    partition = {}
    for (key,string) in mapping.Order + [('Other','Other')]:
        partition[key] = []
    if stat == 'W-JLPT' or stat =='W-Freq':
        dic = MapFreqTango
        type = 'Word'
    else:
        dic = MapFreqKanji
        type = 'Kanji'
    types = eDeck.types
    def assign((id,(state, cardsStates))):
        if state==label:
            try:
                content = types[id][type]
                try:
                    key = mapping.Value(content)
                except KeyError:
                    key = 'Other'
                partition[key].append((content,id))
            except KeyError:
                pass
    map(assign, eDeck.states.iteritems())


    for (key,string) in mapping.Order+ [('Other','Other')]:
        partition[key].sort(lambda x,y:JxValue(dic,y[0])-JxValue(dic,x[0]))

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
        dic = MapFreqTango
        type = 'Word'
    else:
        dic = MapFreqKanji
        type = 'Kanji'
    def assign((id,metadata)):
            try:
                content = metadata[type]
                key = mapping.Value(content)
                partition[key].discard(content)
            except KeyError:
                pass
    map(assign, eDeck.types.iteritems())
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

