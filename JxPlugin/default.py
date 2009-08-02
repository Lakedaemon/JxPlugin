# -*- coding: utf-8 -*-
# Copyright: Olivier Binda <olivier.binda@wanadoo.fr>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
# ---------------------------------------------------------------------------
# This file is a plugin for the "anki" flashcard application http://repose.cx/anki/
# ---------------------------------------------------------------------------
Jx__Entry_Source_Target__Default = [
(u"Word recall","""%(Reading)s""","""${Css}<div style="float:left"><div>${T2JLPT}</div><div>${T2Freq}</div></div><div><center>${Expression}<br />${Reading}</center></div>"""),
(u"Word recognition","""%(Reading)s<br>%(Meaning)s""","""${Css}<div style="float:left;"><div>${T2JLPT}</div><div>${T2Freq}</div></div><div><center>${Reading}<br \>${Meaning}</center></div>"""),
(u"Kanji recall","""K:%(Reading)s""","""${Css}<div style="float:left">${Stroke}<div>${K2JLPT}</div><div>${K2Jouyou}</div><div>${K2Freq}</div></div><center>${OnYomi}<br />${KunYomi}</center><center>${K2Words}</center>"""),
(u"Kanji recognition","""K:%(Reading)s<br>%(Meaning)s""","""${Css}<div style="float:left">${Stroke}<div>${K2JLPT}</div><div>${K2Jouyou}</div><div>${K2Freq}</div></div><center>${K2Words}</center>"""),
(u"Sentence recall","""S:%(Reading)s""","""<center>${Expression}<br />${Reading}<br />${WStroke}gah</center>"""),
(u"Sentence recognition","""S:%(Reading)s<br>%(Meaning)s""","""<center>${Reading}<br \>${Meaning}</center>"""),
(u"Grammar recall","""G:%(Reading)s""","""${Expression}<br />${Reading}</center>"""),
(u"Grammar recognition","""G:%(Reading)s<br>%(Meaning)s""","""<center>${Reading}<br \>${Meaning}</center>"""),
(u"Kanji character","""K:%(Kanji)s""","""${Css}<div style="float:left">${Stroke}<div>${K2JLPT}</div><div>${K2Jouyou}</div><div>${K2Freq}</div></div><center>${K2Words}</center>"""),
(u"Kanji meanings","""K:%(Meaning)s""","""${Css}<div style="float:left">${Stroke}<div>${K2JLPT}</div><div>${K2Jouyou}</div><div>${K2Freq}</div></div><center>${Meaning}</center><center>${K2Words}</center>"""),
(u"Kanji readings","""K:%(OnYomi)s<br>%(KunYomi)s""","""${Css}<div style="float:left">${Stroke}<div>${K2JLPT}</div><div>${K2Jouyou}</div><div>${K2Freq}</div></div><center>${OnYomi}<br />${KunYomi}</center><center>${K2Words}</center>""")]
