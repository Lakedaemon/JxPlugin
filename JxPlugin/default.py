# -*- coding: utf-8 -*-
# Copyright: Olivier Binda <olivier.binda@wanadoo.fr>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
# ---------------------------------------------------------------------------
# This file is a plugin for the "anki" flashcard application http://repose.cx/anki/
# ---------------------------------------------------------------------------
Jx__Entry_Source_Target__Default = [
(u"Word recall",u"""D:%(Reading)s""",u"""${Css}<div style="float:left"><div>${W:JLPT}</div><div>${W:Freq}</div></div><div><center>${Expression}<br />${Reading}</center></div>"""),
(u"Word recognition",u"""D:%(Reading)s<br>%(Meaning)s""",u"""${Css}<div style="float:left;"><div>${W:JLPT}</div><div>${W:Freq}</div></div><div><center>${Reading}<br \>${Meaning}</center></div>"""),
(u"Kanji recall",u"""K:%(Reading)s""",u"""${Css}<div class="K">${K:Stroke}<div>${K:JLPT}</div><div>${K:Jouyou}</div><div>${K:Freq}</div></div><center>${OnYomi}<br />${KunYomi}</center><center>${K:Words}</center>"""),
(u"Kanji recognition",u"""K:%(Reading)s<br>%(Meaning)s""",u"""${Css}<div class="K">${K:Stroke}<div>${K:JLPT}</div><div>${K:Jouyou}</div><div>${K:Freq}</div></div><center>${K:Words}</center>"""),
(u"Kanji/Word recall",u"""KW:%(Reading)s""",u"""${Css}<div class="K">${K:Stroke}<div>${K:JLPT}</div><div>${K:Jouyou}</div><div>${K:Freq}</div></div><center>${OnYomi}<br />${KunYomi}</center><center>${K:Words}</center>"""),
(u"Kanji/Word recognition",u"""KW:%(Reading)s<br>%(Meaning)s""",u"""${Css}<div class="K">${K:Stroke}<div>${K:JLPT}</div><div>${K:Jouyou}</div><div>${K:Freq}</div></div><center>${K:Words}</center>"""),
(u"Sentence recall",u"""S:%(Reading)s""",u"""<center>${Expression}<br />${Reading}<br />${W:Stroke}</center>"""),
(u"Sentence recognition",u"""S:%(Reading)s<br>%(Meaning)s""",u"""<center>${Reading}<br \>${Meaning}</center>"""),
(u"Grammar recall",u"""G:%(Reading)s""",u"""${Expression}<br />${Reading}</center>"""),
(u"Grammar recognition",u"""G:%(Reading)s<br>%(Meaning)s""",u"""<center>${Reading}<br \>${Meaning}</center>"""),
(u"Kanji character",u"""K:%(Kanji)s""",u"""${Css}${K:JLPT}${K:Jouyou}${K:Freq}${K:Stroke}<center>${K:Words}</center>"""),
(u"Kanji meanings",u"""K:%(Meaning)s""",u"""${Css}${K:JLPT,div}${K:Jouyou,div}${K:Freq,div}${K:Stroke,div}<center>${Meaning,div}<br /><br />${K:Words,div}</center>"""),
(u"Kanji readings",u"""K:%(OnYomi)s<br>%(KunYomi)s""",u"""${Css}${K:JLPT,div}${K:Jouyou,div}${K:Freq,div}${K:Stroke,div}<center>${OnYomi}<br />${KunYomi}<br /><br />${K:Words,div}</center>""")]
Jx__Css__Default = u"""
.Kanji {font-family: 'Hiragino Mincho Pro','ヒラギノ明朝 Pro W3',Meiryo,'Hiragino Kaku Gothic Pro','MS Mincho',Arial,sans-serif; font-weight: normal; text-decoration: none; }
.Kana { font-family: "Hiragino Mincho Pro",'ヒラギノ明朝 Pro W3',Meiryo,'Hiragino Kaku Gothic Pro','MS Mincho',Arial,sans-serif; font-weight: normal; text-decoration: none; }
.Romaji { font-family: Osaka,Arial,Helvetica,sans-serif; font-weight: normal; text-decoration: none; font-size:16px}



.K {font-family: 'Hiragino Mincho Pro','ヒラギノ明朝 Pro W3',Meiryo,'Hiragino Kaku Gothic Pro','MS Mincho',Arial,sans-serif; font-weight: normal; text-decoration: none; }
.Kana { font-family: "Hiragino Mincho Pro",'ヒラギノ明朝 Pro W3',Meiryo,'Hiragino Kaku Gothic Pro','MS Mincho',Arial,sans-serif; font-weight: normal; text-decoration: none; }
.Romaji { font-family: Osaka,Arial,Helvetica,sans-serif; font-weight: normal; text-decoration: none; font-size:16px}

.K-JLPT,.W-JLPT,.K-Jouyou,.K-Freq,W-Freq,.K-Kanken { font-family: Osaka,Arial,Helvetica,sans-serif; font-weight: normal; font-size:18px;border :1px solid black;border-bottom:0px solid black;border-right:0px solid black;width:55px;float:left;text-align:center;clear:all;}
.K-Jouyou{width:54px;}
.K-Freq {border-right:1px solid black;}
.K-Stroke  {float:left; font-family: KanjiStrokeOrders; font-size: 150px;line-height:150px;clear:both;border: 1px solid black;}

.even {background-color:none;}
.odd {background-color:#ddedfc;}
.K-Words {font-size:20px;line-height:28px;text-align:center;cellspacing:0px;cellpadding:0px;border:0px;align:center;}
.td-one{padding:5px;}
"""
from answer import JxTableDisplay
Jx__Sample__Default = {
u'K:':u'次',
u'W:':u'悪魔',
u'S':u'',
u'G':u'',
u'Meaning':u'Next',
u'OnYomi':u'ジ',
u'KunYomi':u'つーぐ, つぎ',
u'K:JLPT':u'2級',
u'K:Jouyou':u'G3',
u'K:Freq':u'62',
u'K:Stroke':u'次',
u'K:Words':JxTableDisplay([(u"次第に",u"gradually",u"しだいに"),(u"次回",u"next time",u"じかい"),(u"次ぐ",u"to be next",u"つぐ"),(u"次",u"next",u"つぎ"),(u"第二次",u"the second",u"だいにじ"),(u"目次",u"a table of contents",u"もくじ")],u"K-Words")}
