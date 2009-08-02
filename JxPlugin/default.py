# -*- coding: utf-8 -*-
# Copyright: Olivier Binda <olivier.binda@wanadoo.fr>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
# ---------------------------------------------------------------------------
# This file is a plugin for the "anki" flashcard application http://repose.cx/anki/
# ---------------------------------------------------------------------------
Jx__Entry_Source_Target__Default = [
(u"Word recall","""%(Reading)s""","""${Css}<div style="float:left"><div>${T2JLPT}</div><div>${T2Freq}</div></div><div><center>${Expression}<br />${Reading}</center></div>"""),
(u"Word recognition","""%(Reading)s<br>%(Meaning)s""","""${Css}<div style="float:left;"><div>${T2JLPT}</div><div>${T2Freq}</div></div><div><center>${Reading}<br \>${Meaning}</center></div>"""),
(u"Kanji character","""%(Kanji)s""","""${Css}<div style="float:left">${Stroke}<div>${K2JLPT}</div><div>${K2Jouyou}</div><div>${K2Freq}</div></div><center>${K2Words}</center>"""),
(u"Kanji meaning","""%(Meaning)s""","""${Css}<div style="float:left">${Stroke}<div>${K2JLPT}</div><div>${K2Jouyou}</div><div>${K2Freq}</div></div><center>${Meaning}</center><center>${K2Words}</center>"""),
(u"Kanji readings","""%(OnYomi)s<br>%(KunYomi)s""","""${Css}<div style="float:left">${Stroke}<div>${K2JLPT}</div><div>${K2Jouyou}</div><div>${K2Freq}</div></div><center>${OnYomi}<br />${KunYomi}</center><center>${K2Words}</center>""")]

JxLink={
"""%(Reading)s""":
	"""${Css}<div style="float:left"><div>${T2JLPT}</div><div>${T2Freq}</div></div><div><center><font style="font-size:500%">${Expression}</font><br /><font style="font-size:300%">${Reading}</font></center></div>""",
"""%(Reading)s<br>%(Meaning)s""":
	"""${Css}<div style="float:left;"><div>${T2JLPT}</div><div>${T2Freq}</div></div><div><center><font style="font-size:300%">${Reading}<br \>${Meaning}</font></center></div>""",
"""%(Kanji)s""":
	"""${Css}<div style="float:left">${Stroke}<div>${K2JLPT}</div><div>${K2Jouyou}</div><div>${K2Freq}</div></div><center>${K2Words}</center>""",
"""%(Meaning)s""":
	"""${Css}<div style="float:left">${Stroke}<div>${K2JLPT}</div><div>${K2Jouyou}</div><div>${K2Freq}</div></div><center><font style="font-size:300%">${Meaning}</font></center><center>${K2Words}</center>""",
"""%(OnYomi)s<br>%(KunYomi)s""":
	"""${Css}<div style="float:left">${Stroke}<div>${K2JLPT}</div><div>${K2Jouyou}</div><div>${K2Freq}</div></div><center><font style="font-size:500%">${OnYomi}<br />${KunYomi}</font></center><center>${K2Words}</center>"""
}
