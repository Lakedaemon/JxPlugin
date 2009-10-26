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
from controls import JxBase
import cPickle
from copy import deepcopy
JxDeck = {}
JxSavedStats = {}
JxHistory = {}
from PyQt4.QtCore import *
from anki.utils import stripHTML

class Database(QObject):
    """Data structure for the JxPlugin tables"""
    
    def __init__(self,name="Deck",parent=JxBase):
        QObject.__init__(self,parent)
        self.setObjectName(name)
        try:
            self.load()
            self.reference_data()
            self.update()
            
        except KeyError:
            self.cache = {'models':{}, 'fields':{}, 'types':{}, 'states':{}, 'history':{}, 'stats':{}, 'oldStats':{},'graphs':{},
                'modelsModified':0, 'factsDeleted':0, 'factsModified':0, 'cardsModified':0, 'historyModified':0, 'statsModified':0, 
                'cacheBuilt':0, 'cardsKnownThreshold':21,'factsKnownThreshold':1}
            self.reference_data()
            self.build() 
        
    def update(self):
        self.set_models(True)
        self.set_fields(True)
        self.save_stats(True)
        self.drop_deleted_facts(True)
        self.set_types(True)
        self.set_new_states(True)
        self.set_history(True)
        self.apply_new_states(True)
        
    def build(self):
        self.set_models(False)
        self.set_fields(False)
        self.drop_deleted_facts(False)
        self.set_types(False)
        self.set_new_states(False)
        self.set_history(False)
        self.apply_new_states(False)        
        self.save_stats(False)
        self.save() 

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
            self.cache.update({'history':{}, 'stats':{}, 'oldStats':{},'graphs':{},
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
        """saves the cache on disk"""                   
        path = os.path.join(mw.config.configPath, "plugins", "JxPlugin", "Cache", mw.deck.name() + ".cache")   
        file = open(path, 'wb')
        cPickle.dump(self.cache, file, cPickle.HIGHEST_PROTOCOL)
        file.close()        

    def set_models(self,update):
        """builds the models and hints if update is false or updates them otherwise"""
        
        # sets things up for the build/update process
        if update:
            dic = {}
            query = """select models.id,models.name,models.tags,fieldModels.ordinal,fieldModels.name, models.modified from models,fieldModels where models.id = fieldModels.modelId and models.modified>%.3f""" % self.modelsModified
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
    
    def set_fields(self,update):
        from anki.utils import stripHTML
        """fills the fields if update is false or overwrites them otherwise"""
        if update:  
            dic = {}
            query = """select factId,value, modified from fields, facts where fields.factId = facts.id and modified>%.3f order by ordinal""" %  self.factsModified
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

    def save_stats(self, update):
        from copy import deepcopy
        from controls import JxSettings
        now = time.time()
        if not(update) or int(now/86400.0) - int(self.statsModified/86400.0) >= int(JxSettings.Get('reportReset')):
            self.cache['oldStats'] = deepcopy(self.stats)
            self.oldStats = self.cache['oldStats']
            self.cache['statsModified'] = now
            
    def drop_deleted_facts(self,update):
        if update:
            query = """select factId,deletedTime from factsDeleted where deletedTime>%.3f""" % self.factsDeleted  
        else:
            # no need to drop facts
            query = """select deletedTime from factsDeleted""" 
            self.factsDeleted = max(map(lambda x:x[0],mw.deck.s.all(query))+[0]) # I want python to compute the max, this is why I code this like this
            return
            
        drop = mw.deck.s.all(query)
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
            query = """select facts.id,facts.tags, facts.modelId from facts,models where models.id=facts.modelId and (facts.modified>%.3f or models.modified>%.3f)""" %  (self.factsModified,self.modelsModified)  
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
            fields = self.fields[id]
            metadata = {}
            for (type,(name,ordinal,boolean)) in hints.iteritems():
                content = stripHTML(fields[ordinal])
                if boolean or type in GuessType(content):
                    metadata[type] = content 
            self.types[id] = metadata
        map(compute,table)

        #update stats/graphs
        if update:
            def invert((factId,(boolean,dict))):
                dic[factId] = (True, dict)        
            map(invert,dic.iteritems())
            self.update_graphs(dic)
            self.set_stats(lis,1)

    def set_new_states(self,update):
        if update:
            self.newStates = {}
            States = self.newStates
            query = """select cards.factId, cards.id, cards.interval, cards.reps, cards.modified from cards where cards.modified>%.3f""" % self.cardsModified
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

    def set_history(self,update): 
        if update:
            query = """select cards.factId, reviewHistory.cardId, reviewHistory.lastInterval, reviewHistory.nextInterval, reviewHistory.ease, reviewHistory.time from cards, reviewHistory where cards.id = reviewHistory.cardId and reviewHistory.time>%.3f  order by reviewHistory.cardId, reviewHistory.time""" %  self.historyModified
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
                    self.switch = (states[factId][1][id] != 1)                
                else:
                    self.switch = True            
                self.cardId = id
            if (nextInterval > cardsKnownThreshold  and self.switch) or (nextInterval <= cardsKnownThreshold  and not(self.switch)):
                self.switch = not(self.switch)
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
        self.cache['historyModified'] = max(map(assign,mw.deck.s.all(query)) + [self.historyModified])
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
                    self.history[factId].append(list[:])
                except KeyError:
                    self.history[factId]=list[:]
                deltaHistory[factId] = ((status != 1), list[:])  
            else:
                self.history[factId] = list[:]
                deltaHistory[factId] = (True, list[:])
        
        map(compute, history.iteritems())
        self.update_graphs(deltaHistory)

    def update_graphs(self,dic):
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
                        dict = Jx_Kanji_Occurences                       
                    else:
                        dict = Jx_Word_Occurences        
                    def assign((content, add, days)):
                        try:
                            value = mapping.Value(content)
                            increment = dict[content]
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
        if update:
            list = self.newStates.keys()
            self.set_stats(map(build,list),-1)
            states.update(self.newStates)
            del self.newStates
            self.set_stats(map(build,list),1)
        else:
            list = self.states.keys()
            self.set_stats(map(build,list),0)


    def set_stats(self, List, add):
        """updates stats positively if add>0, negatively if add<0 or build stats if add=0"""
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
                        dic = Jx_Kanji_Occurences
                    else:
                        dic = Jx_Word_Occurences
                    def assign_A((content,state)):
                        try:
                            value = mapping.Value(content)
                            if add >= 0:
                                increment = dic[content]
                            else:
                                increment = - dic[content]
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
                        map(count_A,dic.iteritems())
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




########################### access database



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
    #from controls import Jx_Control_Cache 
    global jxdeck
    jxdeck = Database()

    #Jx_Control_Cache .load()


 
    #midnightOffset = time.timezone - self.deck.utcOffset
    #self.endOfDay = time.mktime(now) - midnightOffset
    #todaydt = datetime.datetime(*list(time.localtime(time.time())[:3]))
   
                
import time
def JxGraphs_into_json():
    global JxGraphs
    graphs = jxdeck.graphs
    today = int(time.time() / 86400.0)
    dict_json = {}
    tasks = {'W-JLPT':MapJLPTTango, 'W-AFreq':MapZoneTango, 'K-JLPT':MapJLPTKanji, 'K-AFreq':MapZoneKanji, 'Jouyou':MapJouyouKanji, 'Kanken':MapKankenKanji} 
    for (graph,mapping) in tasks.iteritems():
        for (key,string) in mapping.Order +[('Other','Other')]:
            try:
                dict = graphs[(graph,key)]
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
    get_stat = jxdeck.get_stat
    get_ancient_stat = jxdeck.get_old_stat
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
    if  new == ancient:
        return "%s%%" % JxFormat(new)
    elif ancient < new:
        return """%s%%<br/><font face="Comic Sans MS" color="green" size=2>+%s%%</font>""" % (JxFormat(new),JxFormat(new-ancient))
    else:
        return """%s%%<br/><font face="Comic Sans MS" color="red" size=2>-%s%%</font>""" % (JxFormat(new),JxFormat(ancient-new))    

def display_astats(stats):
    mappings = {'W-AFreq':MapZoneTango, 'K-AFreq':MapZoneKanji}
    mapping = mappings[stats]
    get_stat = jxdeck.get_stat
    get_old_stat = jxdeck.get_old_stat
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
    types = jxdeck.types
    def assign((id,(state, cardsStates))):
        if state==label:
            try:
                content = types[id][type]
                try:
                    key = mapping.Dict[content]
                except KeyError:
                    key = 'Other'
                partition[key].append((content,id))
            except KeyError:
                pass
    map(assign, jxdeck.states.iteritems())


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
    map(assign, jxdeck.types.iteritems())
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

