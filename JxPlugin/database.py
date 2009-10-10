# -*- coding: utf-8 -*-
# Copyright: Olivier Binda <olivier.binda@wanadoo.fr>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
# ---------------------------------------------------------------------------
# This file is a plugin for the "anki" flashcard application http://ichi2.net/anki/
# ---------------------------------------------------------------------------
from ankiqt import mw

from cache import save_cache
from answer import Tango2Dic,JxType,JxTypeJapanese, GuessType
def build_JxFacts():
    """builds JxFacts, the Jxplugin counterparts (with metadata) of the sqllite Facts, Cards, Fields and review history tables"""
    JxFacts = {}
    def assign(row):
        """basically does factsDB[factId].update(ordinal=value)"""
        try:
            fields = JxFacts[row[0]]
        except KeyError:
            JxFacts[row[0]] = {}
            fields = JxFacts[row[0]]
        fields[row[1]] = row[2]
    rows = mw.deck.s.all("""select factId,ordinal,value from fields""")
    map(assign,rows)
    save_cache(JxFacts)
    build_JxModels()
    
def build_JxModels():
    """builds JxModels, the Jxplugin counterparts (with metadata) of the sqllite model & fieldmodel tables"""
    JxModels = {} 
    query = """select models.id,models.name,models.tags,fieldModels.ordinal,fieldModels.name from models,fieldModels where models.id = fieldModels.modelId"""
    rows = mw.deck.s.all(query)
    def assign(row):
        (id, name, tags, ordinal, fieldName) = row
        try:
            fields = JxModels[id][2]
        except:
            JxModels[id] = (name, tags, {}, [])
            fields = JxModels[id][2]
        fields[ordinal] = fieldName
    map(assign,rows)    

    # got to parse the model tags and maybee the model name
    for (id, modelInfo) in JxModels.iteritems():
        (modelName, tags, fields, hints) = modelInfo
        #(modelId,modelTags,modelName,fieldName,fieldOrdinal) = row
        types = set()
        test = set(tags.split(" ")) # parses the model tags first
        for (Key,List) in JxType:
            if test.intersection(List):
                types.update([Key]) 
        if not(types): # checks the model name now
            for (Key,List) in JxType:
                if modelName in List:
                    types.update([Key])
                    break # no need to parse further
        if not(types): # checks the Field's name now
            for (ordinal,name) in fields.iteritems():
                for (Type,TypeList) in JxType:
                                        if name in TypeList:
                                                types.update([Type])
                                                hints.append((Type, name, ordinal, True))
                                                break # no need to parse this Field further
        if not(types): # Japanese Model ?
            test = set(tags.split(" ") + [modelName] + fields.values())   
            if test.intersection(JxTypeJapanese):
                types.update(['Kanji','Word','Sentence','Grammar'])  
        # now, we got to set the action and build a Hint
        if types and not(hints):
            # first, we try to affect relevant fields for each type (first try fields with the name similar to the type)
            for (Type,TypeList) in JxType:
                if Type in types:
                        for (ordinal,name) in fields.iteritems():
                                if name in TypeList:
                                        hints.append((Type,name,ordinal,True)) 
                                        break
            if len(hints) < len(types):
                # for the still missing fields, we try to find an "Expression" field next and update the List
                if hints:
                    (Done,Arga,Argb,Argc) = zip(*hints)
                else : 
                    Done = []
                TempList = []
                for (Type,TypeList) in JxType:
                    if Type in types and Type in Done:
                        TempList.append(hints.pop(0))
                    elif Type in types:
                        

                        for (ordinal, name) in fields.iteritems():
                            if name == 'Expression':
                                if len(types) == 1:
                                    TempList.append((Type,name,ordinal,True))
                                else:
                                    TempList.append((Type,name,ordinal,False))                                                                        
                                break 
                hints = TempList
                JxModels[id]=(modelName, tags, fields, hints[:])
                
