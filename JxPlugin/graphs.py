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

