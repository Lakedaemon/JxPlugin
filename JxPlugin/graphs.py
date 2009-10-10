# -*- coding: utf-8 -*-
# Copyright: Olivier Binda <olivier.binda@wanadoo.fr>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
# ---------------------------------------------------------------------------
# This file is a plugin for the "anki" flashcard application http://ichi2.net/anki/
# ---------------------------------------------------------------------------
import time
#import datetime


#from anki.utils import ids2str
from loaddata import *
from answer import Tango2Dic,JxType,JxTypeJapanese, GuessType
from globalobjects import JxStatsMap,JxProfile,Jx_Profile,JxShowProfile,JxInitProfile

from cache import load_cache, save_cache

#colours for graphs
colorGrade={1:"#CC9933",2:"#FF9933",3:"#FFCC33",4:"#FFFF33",5:"#CCCC99",6:"#CCFF99",7:"#CCFF33",8:"#CCCC33"}
colorFreq={1:"#3333CC",2:"#3366CC",3:"#3399CC",4:"#33CCCC",5:"#33FFCC"}
colorJLPT={4:"#996633",3:"#999933",2:"#99CC33",1:"#99FF33",0:"#FFFF33"}


######################################################################
#
#          Routines for building the Card2Type Dictionnary
#
######################################################################
from globalobjects import CardId2Types, FactId2Types


def JxParseFacts4Stats():
        global ModelInfo,Fields,Tuple,Tau
        JxProfile("Before Query")
        # We are going to use 1 select and do most of the work in python (there might be other ways, but I have no time to delve into sqllite and sql language...haven't found any good tutorial about functions out there). 
        Query = """select cards.id, facts.tags, models.id, models.tags, models.name, fieldModels.name, fields.value, facts.id, fieldModels.ordinal
        from cards,facts,fields,fieldModels, models where 
        cards.factId = facts.id and facts.id = fields.factId and fields.fieldModelId = fieldModels.id and facts.modelId = models.id 
        order by models.id,facts.id,cards.id,fieldModels.ordinal"""
        Rows = mw.deck.s.all(Query)
        JxProfile("Parse Cards start")
        Length = len(Rows)
        ModelInfo = None
        Index = 0
        while Index < Length:
                #(0:CardId, 1:FactTags, 2:ModelId, 3:ModelTags, 4:ModelName, 5:FieldName, 6:FieldContent, 7: FactId, 8: FieldOrdinal)
                Tuple = Rows[Index]                
                Tau = 1
                while Index + Tau < Length:# For OS X users. We need python 2.5 for "short and" and "short or".  
                        if Rows[Index + Tau][0] == Tuple[0]:
                                Tau += 1
                        else:
                                break
                Delta = Tau
                while Index + Delta < Length:
                        if Rows[Index + Delta][7] == Tuple[7]: 
                                Delta += Tau                
                        else:
                                break
                Fields = [(Rows[a][5],Rows[a][6],Rows[a][8]) for a in range(Index,Index + Tau)]# beware of unpacking 2 out of 3 values
                List = JxParseFactTags4Stats(Rows,Index)
                CardsIds = [Rows[a][0] for a in range(Index,Index + Delta,Tau)]
                CardId2Types.update([(Id,(List,CardsIds)) for Id in CardsIds])
                FactId2Types.update([(Rows[Index][7],(List,CardsIds))])
                Index += Delta
                if Index < Length:
                        if Rows[Index][2] != Tuple[2]:
                                # resets the model types
                                ModelInfo = None
        del ModelInfo,Fields,Tuple,Tau
        JxProfile("Card Parsing Ended")
      
       
                
                
                
                
def JxParseFactTags4Stats(Rows,Index):               
                # first check the tags of the fact
                Types = set()
                JxFactTags = set(Tuple[1].split(" "))
                for (Key,List) in JxType:
                        if JxFactTags.intersection(List):
                                Types.update([Key])
                if Types: 
                        return JxAffectFields4Stats(Fields,Types)
                # no relevant Fact tags, parse the model
                return JxParseModel4Stats(Rows,Index)
                 
def JxParseModel4Stats(Rows,Index):
        global ModelInfo
        # first check the model types
        if ModelInfo == None:# got to parse the model tags and maybee the model name
                ModelInfo = (set(),[])
                JxModelTags = set(Tuple[3].split(" "))
                for (Key,List) in JxType:
                        if JxModelTags.intersection(List):
                                ModelInfo[0].update([Key]) 
                if not(ModelInfo[0]):# model name now
                        for (Key,List) in JxType:
                                if Tuple[4] in List:
                                        ModelInfo[0].update([Key])
                                        break # no need to parse further
                if not(ModelInfo[0]):# Fields name now
                        for (Name,Content,Ordinal) in Fields:
                                for (Type,TypeList) in JxType:
                                        if Name in TypeList:
                                                ModelInfo[0].update([Type])
                                                ModelInfo[1].append((Type,Name,Ordinal,True))
                                                break # no need to parse this Field further
                if not(ModelInfo[0]): # Japanese Model ?
                        Set = set(Tuple[1].split(" ") + Tuple[3].split(" ") + [Tuple[4]] + [Rows[a][5] for a in range(Index,Index + Tau)])   
                        if Set.intersection(JxTypeJapanese):
                                ModelInfo[0].update(['Kanji','Word','Sentence','Grammar'])   
                if not(ModelInfo[0]):
                        pass 
                        # this set might still be related to japanese if it's content includes Kana (as I expect the japanese user of Anki NOT to use the JxPlugin, 
                        # I test for Kana in case there are koreans or chinese users learning japanese, it'll be hard finding the relevant field for those though
                        # I expect that anybody wantng to learn japanese will want to display kana readings)
                        # Anyway, I need Jmdict.xml to do anything about this
                        
                # now, we got to set the action and build a Hint
                elif not(ModelInfo[1]):
                        # first, we try to affect relevant fields for each type (first try fields with the name similar to the type)
                        for (Type,TypeList) in JxType:
                                if Type in ModelInfo[0]:
                                        for (Name,Content,Ordinal) in Fields:
                                                if Name in TypeList:
                                                        ModelInfo[1].append((Type,Name,Ordinal,True)) 
                                                        break
                        if len(ModelInfo[1]) < len(ModelInfo[0]):
                                # for the still missing fields, we try to find an "Expression" field next and update the List
                                if ModelInfo[1]:
                                        (Done,Arga,Argb,Argc) = zip(*ModelInfo[1])
                                else : 
                                        Done = []
                                TempList = []
                                for (Type,TypeList) in JxType:
                                        if Type in ModelInfo[0] and Type in Done:
                                                TempList.append(ModelInfo[1].pop(0))
                                        elif Type in ModelInfo[0]:
                                                for (Name,Content,Ordinal) in Fields:
                                                        if Name == "Expression":
                                                                if len(ModelInfo[0])==1:
                                                                        TempList.append((Type,"Expression",Ordinal,True))
                                                                else:
                                                                        TempList.append((Type,"Expression",Ordinal,False))                                                                        
                                                                break 
                                ModelInfo = (ModelInfo[0],TempList)
                
                        #if len(ModelInfo[1]) < len(ModelInfo[0]):
                        #        # there is nothing we can do about that at the model level
                        #        pass
        
                
        # now that we have ModelInfo, we can set/guess (True/False) the value of the fields and return a list of (type/name/content)
        
        if not(ModelInfo[0]) :
                return []
        # use the Hint if there is one
        List = []
        for (Type,Name,Ordinal,Boolean) in ModelInfo[1]:
                Content = Rows[Index + Ordinal][6]
                if Boolean:
                        List.append((Type,Name,Content))
                elif Type in GuessType(Content):
                        List.append((Type,Name,Content))
                                
        if len(List) < len(ModelInfo[0]):
                # we need Jmdict.xml to do something sensible about that
                # field names and "Expression" have failed, we could still try to guess with the fields content
                # but for the time being, we will pass because I don't know how to choose between two fields that might only have kanas (maybee query other cards to decide between the fields, might be doable for sentences (ponctuation helps) and Kanji (only 1 Kanji character))
                pass
                
        return List           

def JxAffectFields4Stats(FieldNameContentList,Types):# could be optimized for Rows and stats, maybee...but that way, it can be usd by both routines
        # we now try to affect relevant fields for each type (first try fields with the name similar to the type)
        List=[]
        for (Type,TypeList) in JxType:
                if Type in Types:
                        for (Name,Content,Ordinal) in FieldNameContentList:
                                if Name in TypeList:
                                        List.append((Type,Name,Content)) 
                                        break
                                             
        if len(List)<len(Types):
                # there are still missing fields for the types, we could try the "Expression" field next and update the List
                if len(List)>0:
                        (Done,Field) = zip(*List)
                else : 
                        Done=[]
                TempList=[]
                for (Type,TypeList) in JxType:
                        if Type in Types and Type in Done:
                                TempList.append(List.pop(0))
                        elif Type in Types:
                                for (Name,Content,Ordinal) in FieldNameContentList:
                                        if Name == u"Expression":
                                                TempList.append((Type,Name,Content)) 
                                                break 
                List = TempList
                                                
        if len(List)<len(Types):
                # field names and "Expression" have failed, we could still try to guess with the fields content
                # but for the time being, we will pass because I don't know how to choose between two fields that might only have kanas (maybee query other cards to decide between the fields, might be doable for sentences (ponctuation helps) and Kanji (only 1 Kanji character))
                pass
   
        return List
######################################################################
#
#                               Graphs
#
######################################################################

def JxJSon(CouplesList):
        return "[" + ",".join(map(lambda (x,y): "[%s,%s]"%(x,y),CouplesList)) + "]" 
                    
#midnightOffset = time.timezone - self.deck.utcOffset
#self.endOfDay = time.mktime(now) - midnightOffset
#todaydt = datetime.datetime(*list(time.localtime(time.time())[:3]))
Facts = {}
def update_stats_cache():
    global JxStateArray,JxStatsMap
    JxProfile('Load Cache')
    JxCache = load_cache()
    JxProfile('Load Cache ended')
    try:
        query = """
	select cards.factId,reviewHistory.cardId, reviewHistory.time, reviewHistory.lastInterval, reviewHistory.nextInterval, reviewHistory.ease 
	from reviewHistory,cards where cards.id = reviewHistory.cardId and cards.modified>%s 
	order by cards.factId,reviewHistory.cardId,reviewHistory.time""" % JxCache['TimeCached']
        JxStateArray = JxCache['StateArray']
    except:
        query = """
	select cards.factId ,reviewHistory.cardId, reviewHistory.time, reviewHistory.lastInterval, reviewHistory.nextInterval, reviewHistory.ease 
	from reviewHistory,cards where cards.id = reviewHistory.cardId order by cards.factId ,reviewHistory.cardId,reviewHistory.time"""
        JxStateArray = {}
    rows = mw.deck.s.all(query)	
    JxProfile("Query ended")

    length = len(rows)
    index = 0
    JxCardState = []
    JxCardStateArray = []
    StatusStart = 0
    # We will initialize other stuff on the fly !
    while index < length:
        # 0:FactId 1:CardId, 2:Time, 3: lastInterval, 4: next interval, 5:ease
        (FactId,CardId,Time,Interval,NextInterval,Ease) = rows[index]                  
        # first, we have to build a list of the days where status changes happened for this card (+ - + - + - ...)
        if (Interval <= 21 and NextInterval > 21): 
            #Card Status Change
            Day = int(Time / 86400.0)
            JxCardState.append(Day)
            if StatusStart == 0:
                StatusStart = 1
        elif (Interval > 21 and Ease == 1):
            #Card Status Change
            Day = int(Time / 86400.0)
            JxCardState.append(Day)
            if StatusStart == 0:
                StatusStart = -1		
        index += 1
        if index == length: 
            # we have finished parsing the Entries.Flush the last Fact and break
            JxCardStateArray.append((StatusStart,JxCardState[:]))
            flush_facts(JxCardStateArray,CardId)
            break
            # we have finished parsing the Entries, flush the Status change
        elif CardId == rows[index][1]:
            # Same Card : Though it does nothing, we put this here for speed purposes because it happens a lot.
            pass
        elif FactId != rows[index][0]:                        
            # Fact change : Though it happens a bit less often than cardId change, we have to put it there or it won't be caught, flush the status change.
            JxCardStateArray.append((StatusStart,JxCardState[:]))
            flush_facts(JxCardStateArray,CardId)
            JxCardState = []
            JxCardStateArray = []
            StatusStart = 0
        else:
            # CardId change happens just a little bit more often than fact changes (if deck has more than 3 card models;..). Store and intit the card status change
            JxCardStateArray.append((StatusStart,JxCardState[:]))
            JxCardState = []
	    StatusStart = 0
	    
    JxProfile("NewAlgorythm Ends")
    
    
    # let's partition the deck now
    #try:
        #query = """select id, factId, interval, reps from cards where modified>%s order by factId""" % dJxCache['TimeCached']
    #except:
    query = """select id, factId, interval, reps from cards order by factId"""

    rows = mw.deck.s.all(query)
    # let's create a list of Facts with all associated cards and their state : Known/Seen and produce the equivalent list for facts
    
    TempFacts={}
    def munge_row(x):
            if x[2] > 21:
                y = (x[0], 1) # Known
            elif x[3] > 0:
                y = (x[0], -1) # Seen
            else:
                y = (x[0], 0) # In Deck
            try:
                TempFacts[x[1]].append(y)
            except KeyError:
                TempFacts[x[1]] = [y]
    map(munge_row,rows)
    
    # now update the fact list to include the fact state 
    def partition(x):
            L = zip(*x[1])[1]
            if not any(L):
                Facts[x[0]]= (2, x[1])# InDeck                    
            elif sum(L)>=0 :
                Facts[x[0]]= (0, x[1])# Known
            else:
                Facts[x[0]]= (1, x[1])# Seen
    map(partition,TempFacts.iteritems())
    JxProfile(str(len(filter(lambda x:(x[0]==0),Facts.values())))+" "+str(len(filter(lambda x:(x[0]==1),Facts.values())))+" "+str(len(filter(lambda x:(x[0]==2),Facts.values()))))    


    
    
    # now cache the updated graphs
    JxCache['StateArray'] = JxStateArray
    JxCache['TimeCached'] = time.time() # among the few things that could corrupt the cache : 
    # new entries in the database before the cache was saved...sigh...
    save_cache(JxCache)
    JxProfile("Saving Cache")
    
    #mw.help.showText(JxShowProfile())
    


def extract_stats():
    global JxStatsMap
    array = {}
    for (Type,List) in JxStatsMap.iteritems():
        for (k, Map) in enumerate(List):
            for (Key,String) in Map.Order+[('Other','Other')]:  
                #try:
                #    Dict = JxStateArray[(Type,k,Key)]
                #except KeyError:
                #    Dict = {0:0}
                #Known = sum(Dict.values())
                
                def filtering(x):
                        for (type, name,content) in FactId2Types[x[0]][0]:
                                if Type == type:
                                        try: 
                                            if Map.Dict[content] == Key: 
                                                return True
                                        except KeyError:
                                            if Key == 'Other':
                                                return True            
                        return False
                def evaluating_word(x):
                        for (type, name,content) in FactId2Types[x[0]][0]:
                                if Type == type:
                                        try: 
                                            return Jx_Word_Occurences[content]
                                        except KeyError:
                                            return 0           
                        return 0   
                def evaluating_kanji(x):
                        for (type, name,content) in FactId2Types[x[0]][0]:
                                if Type == type:
                                        try: 
                                            return Jx_Kanji_Occurences[content]
                                        except KeyError:
                                            return 0           
                        return 0                        
                if k != 1:
                        array[(Type,k,Key)] = (len(filter(lambda x:(x[1][0]<1) and filtering(x),Facts.iteritems())), 
                                len(filter(lambda x:(x[1][0]<2) and filtering(x),Facts.iteritems())), len(filter(filtering,Facts.iteritems())), 
                                len([Item for (Item,Value) in Map.Dict.iteritems() if Value == Key])) 
                elif Type =='Word':
                        array[(Type,k,Key)] = (sum(map(evaluating_word,filter(lambda x:(x[1][0]<1) and filtering(x),Facts.iteritems()))), 
                                sum(map(evaluating_word,filter(lambda x:(x[1][0]<2) and filtering(x),Facts.iteritems()))), 
                                sum(map(evaluating_word,filter(filtering,Facts.iteritems()))), sum([Jx_Word_Occurences[Item] 
                    for (Item,Value) in Map.Dict.iteritems() if Value == Key]))
                else:
                    array[(Type,k,Key)] = (sum(map(evaluating_kanji,filter(lambda x:(x[1][0]<1) and filtering(x),Facts.iteritems()))),  
                            sum(map(evaluating_kanji,filter(lambda x:(x[1][0]<2) and filtering(x),Facts.iteritems()))), 
                            sum(map(evaluating_kanji,filter(filtering,Facts.iteritems()))), sum([Jx_Kanji_Occurences[Item] 
                    for (Item,Value) in Map.Dict.iteritems() if Value == Key])) 
    return array

def stats_cache_into_json():
    global JxStateArray,JxStatsMap
    Today = int(time.time() / 86400.0)
    JxGraphsJSon = {}
    for (Type,List) in JxStatsMap.iteritems():
        for (k, Map) in enumerate(List):
            for (Key,String) in Map.Order +[('Other','Other')]:
                try:
                    Dict = JxStateArray[(Type,k,Key)]
                except KeyError:
                    Dict = {Today:0}
                if Today not in Dict:
                    Dict[Today] = 0
                keys = Dict.keys()		
                JxGraphsJSon[(Type,k,Key)] =  JxJSon([(Day-Today,sum([Dict[day] for day in keys if day <=Day])) for Day in range(min(keys), max(keys) + 1)]) 
    return JxGraphsJSon


def flush_facts(JxCardStateArray,CardId):
    global JxStateArray,JxStatsMap
    """Flush the fact stats into the state array"""
    try:# get the card type and the number of shared cardsids by the fact
        (CardInfo,CardsNumber) = CardId2Types[CardId]
        CardWeight = 1.0/max(1,len(CardsNumber))
        for (Type,Name,Content) in CardInfo:
            for (k, Map) in enumerate(JxStatsMap[Type]):
                try:
                    Key = Map.Value(Content)
                except KeyError:
                    Key = 'Other' 
                if k != 1:
                #if Map.To != 'Occurences':    #something is wrong there, why do I have to comment that ? 
                    Change = CardWeight
                elif Type == "Word":
                #elif Map.From == 'Tango':
                    try:
                        Change = Jx_Word_Occurences[Content] * CardWeight
                    except KeyError:
                        Change = 0
                else:
                    try:
                        Change = Jx_Kanji_Occurences[Content] * CardWeight
                    except KeyError:
                        Change = 0 
                        # we have to update the graph of each type
                try:
                    Dict = JxStateArray[(Type,k,Key)]
                except KeyError:
                    # got to initialize it
                    JxStateArray[(Type,k,Key)] = {}
                    Dict = JxStateArray[(Type,k,Key)]
############################################################################################################# upgrade this part to support "over-optimist", "optimist", "realist", "pessimist" modes                                        
                #now, we got to flush the fact. Let's go for the realist model first
                for (StatusStart,JxDaysList) in JxCardStateArray:
                    Status = (StatusStart>0)
                    for JxDay in JxDaysList:
                        try: 
                            if Status:
                                Dict[JxDay] += Change
                            else:
                                Dict[JxDay] -= Change
                        except KeyError:
                            if Status:
                                Dict[JxDay] = Change
                            else:
                                Dict[JxDay] = -Change 
                        Status = not(Status) 
##############################################################################################################
    except KeyError:# we do nothing, this Fact has no type.
        pass
        
 
