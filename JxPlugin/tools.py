# -*- coding: utf-8 -*-
# Copyright: Olivier Binda <olivier.binda@wanadoo.fr>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
# ---------------------------------------------------------------------------
# This file is a plugin for the "anki" flashcard application http://repose.cx/anki/
# ---------------------------------------------------------------------------
from ankiqt import mw
from anki.utils import canonifyTags, addTags
import time

def JxTagDuplicates():

	Query = """select fields.value, facts.id, facts.created, facts.tags from fields,facts,fieldModels,models where 
		facts.id = fields.factId and fields.fieldModelId = fieldModels.id and facts.modelId = models.id and  
		fieldModels.name = "Expression" and models.tags like "%Japanese%" group by facts.id order by fields.value """

	Rows = mw.deck.s.all(Query)
	Seen={}
	Duplicates = {}
	for (Field,Id,Time,Tags) in Rows:
		Entry = Field.strip(u' ')
		if Entry in Seen:
			(lastId,lastTime,lastTags) = Seen[Entry]
			if  lastTime > Time:		
				# first duplicate younger
				Duplicates[lastId] = Entry
				Seen[Entry] = (Id,Time,canonifyTags(addTags(lastTags,Tags)))
			else:
				# second duplicate younger
				Duplicates[Id] = Entry
				Seen[Entry] = (lastId,lastTime,canonifyTags(addTags(lastTags,Tags)))		
		else:
			Seen[Entry] = (Id,Time,Tags)
	MasterDuplicates = []
	Html = u"""<style> li {font-size: x-large;}</style><h2>Duplicated Entries</h2><ul>"""
	for Entry in Duplicates.values():
		(Id,Time,Tags) = Seen[Entry]
		MasterDuplicates.append(Id)
		Html += u"""<li>%s</li>""" % Entry
		mw.deck.s.statement("update facts set tags = :tags, modified = :t where id =:id",id=Id, t=time.time(),tags=canonifyTags(Tags))
	Html += u"""</ul>"""	
	mw.deck.addTags(MasterDuplicates,u"JxMasterDuplicate")
	mw.deck.addTags(Duplicates.keys(),u"JxDuplicate")
	mw.deck.deleteTags(MasterDuplicates,u"JxDuplicate")
	mw.help.showText(Html)	
