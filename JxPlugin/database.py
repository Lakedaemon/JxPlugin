# -*- coding: utf-8 -*-
# Copyright: Olivier Binda <olivier.binda@wanadoo.fr>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
# ---------------------------------------------------------------------------
# This file is a plugin for the "anki" flashcard application http://ichi2.net/anki/
# ---------------------------------------------------------------------------
from ankiqt import mw

from cache import save_cache
from answer import Tango2Dic,JxType,JxTypeJapanese, GuessType

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
                metadata[type] = (name,content) 
                
                
                
    save_cache(JxFacts)
    mw.help.showText(str(JxFacts))       
    

