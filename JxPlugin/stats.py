# -*- coding: utf-8 -*-
# Copyright: Olivier Binda <olivier.binda@wanadoo.fr>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
# ---------------------------------------------------------------------------
# This file is a plugin for the "anki" flashcard application http://repose.cx/anki/
# ---------------------------------------------------------------------------
from ankiqt import mw

######################################################################
#
#                      JxStats : Stats
#
######################################################################

def ComputeCount(Dict,Query):  #### try to clean up, now that you are better at python
	"""compute and Display an HTML report of the result of a Query against a Map"""
	# First compute the cardinal of every equivalence class in Stuff2Val
	Count = {"InQuery":0, "Inside":0, "L0":0}
	Values = set(Dict.values())
	for value in Values:
		Count["T" + str(value)] = 0
		Count["L" + str(value)] = 0		
	for key, value in Dict.iteritems():
		Count["T" + str(value)] += 1
	Count["InMap"] = sum(Count["T" + str(value)] for value in Values)
	Counted = {}
	for Stuff in mw.deck.s.column0(Query):
		Stuffed=Stuff.strip(u" ")
		if Stuffed.endswith((u"する",u"の",u"な",u"に")):
			if Stuffed.endswith(u"する"):
				Stuffed=Stuffed[0:-2]
			else:
				Stuffed=Stuffed[0:-1]
		if Stuffed not in Counted:
			Counted[Stuffed] = 0
			if Stuffed in Dict:
				a = "L" + str(Dict[Stuffed])
			else:
				a = "L0"
			Count[a] += 1
	Count["Inside"] = sum(Count["L" + str(value)] for value in Values)
	Count["InQuery"] = Count["Inside"] + Count["L0"]
	for value in Values:
		Count["P" + str(value)] = round(Count["L" + str(value)] * 100.0 / max(Count["T" + str(value)],1),2)
	Count["PInsideInMap"] = round(Count["Inside"] *100.0 / max(Count["InMap"],1),2)
	Count["PInsideInQuery"] = round(Count["Inside"] *100.0 / max(Count["InQuery"],1),2)
	return Count

def HtmlReport(Map,Query):
	Map.update(ComputeCount(Map["Dict"],Query))
	JStatsHTML = """
	<table width="100%%" align="center" style="margin:0 20 0 20;">
	<tr><td align="left"><b>%(To)s</b></td><th colspan=2 align="center"><b>%(From)s</b></th><td align="right"><b>Percent</b></td></tr>
	""" 
	for key,value in Map["Legend"].iteritems():
		JStatsHTML += """
		<tr><td align="left"><b>%s</b></td><td align="right">%%(L%s)s</td><td align="left"> / %%(T%s)s</td><td align="right">%%(P%s).1f %%%%</td></tr>
		""" % (value,key,key,key) 

	JStatsHTML += """
	<tr><td align="left"><b>Total</b></td><td align="right">%(Inside)s</td><td align="left"> / %(InMap)s</td><td align="right">%(PInsideInMap).1f %%</td></tr>
	<tr><td colspan=4><hr/></td/></tr>
	<tr><td align="left"><b> %(To)s/All</b></td><td align="right">%(Inside)s</td><td align="left"> / %(InQuery)s</td><td align="right">%(PInsideInQuery).1f %%</td></tr>
	</table>
	""" 
        return JStatsHTML % Map

def SeenHtml(Map,Query):
	Dict=Map["Dict"]
	Seen = {}
	Color = {0:True}
	Buffer = {0:""}
	for value in Dict.values():
		Buffer[value] = ""
		Color[value] = True	
	for Stuff in mw.deck.s.column0(Query):
		if Stuff not in Seen:
			try: 
				value = Dict[Stuff]	  
			except KeyError:
				value = 0
			Seen[Stuff] = 0
			Color[value] = not(Color[value])			
			if Color[value]:
				Buffer[value] += Stuff
			else:
				Buffer[value] += """<span style="color:blue">"""+ Stuff +"""</span>"""
	HtmlBuffer = ""
	for key, string in Buffer.iteritems():
		if key == 0:
			HtmlBuffer += """<h2  align="center">Other</h2><p><font size=+2>%s</font></p>""" % string
		else:
			HtmlBuffer += """<h2  align="center">%s</h2><p><font size=+2>%s</font></p>""" % (Map["Legend"][key],string)
	return HtmlBuffer

def MissingHtml(Map,Query):
	Dict=Map["Dict"]
	Seen = {}
	for Stuff in mw.deck.s.column0(Query):
		Seen[Stuff] = 0
		
	Color = {0:True}
	Buffer = {0:""}
	for value in Dict.values():
		Buffer[value] = ""
		Color[value] = True	
	for Stuff,Note in Dict.iteritems():
		if Stuff not in Seen:
			Color[Note] = not(Color[Note])			
			if Color[Note]:
				Buffer[Note] += Stuff
			else:
				Buffer[Note] += """<span style="color:blue">"""+ Stuff +"""</span>"""
	HtmlBuffer = ""
	for key, string in Buffer.iteritems():
		if key != 0:
			HtmlBuffer += """<h2  align="center">%s</h2><p><font size=+2>%s</font></p>""" % (Map["Legend"][key],string)
	return HtmlBuffer	





