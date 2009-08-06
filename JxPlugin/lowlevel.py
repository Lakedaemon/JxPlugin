# -*- coding: utf-8 -*-
# Copyright: Olivier Binda <olivier.binda@wanadoo.fr>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
# ---------------------------------------------------------------------------
# This file is a plugin for the "anki" flashcard application http://ichi2.net/anki/
# ---------------------------------------------------------------------------
import codecs
import os

def JxReadFile(File):
	"""Reads a tab separated text file and returns a list of tuples."""
	List = []
	File = codecs.open(File, "r", "utf8")
	for Line in File:
		List.append(tuple(Line.strip('\n').split('\t')))
	File.close()
	return List
