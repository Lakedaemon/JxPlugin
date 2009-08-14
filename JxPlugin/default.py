# -*- coding: utf-8 -*-
# Copyright: Olivier Binda <olivier.binda@wanadoo.fr>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
# ---------------------------------------------------------------------------
# This file is a plugin for the "anki" flashcard application http://ichi2.net/anki/
# ---------------------------------------------------------------------------
Jx__Entry_Source_Target__Default = [
(u"Word recall",u"""D-%(Reading)s""",u"""${Css}${W-JLPT}${W-Freq}${W-Stroke}${Expression}<br/>${Reading}<br/>${W-Sentences}"""),
(u"Word recognition",u"""D-%(Reading)s<br>%(Meaning)s""",u"""${Css}${W-JLPT}${W-Freq}${W-Stroke}${Reading}<br/>${Meaning}<br/>${W-Sentences}"""),
(u"Kanji recall",u"""K-%(Reading)s""",u"""${Css}${K-Stroke}${K-JLPT}${K-Jouyou}${K-Freq}${Reading}<br />${Meaning}<br /><br />${K-Words}"""),
(u"Kanji recognition",u"""K-%(Reading)s<br>%(Meaning)s""",u"""${Css}${K-Stroke}${K-JLPT}${K-Jouyou}${K-Freq}${K-Words}"""),
(u"Kanji/Word recall",u"""KW-%(Reading)s""",u"""${Css}${W-JLPT}${W-Freq}${K-Stroke}${K-JLPT}${K-Jouyou}${K-Freq}${Expression}${Reading}<br />${Meaning}<br />${K-Words}"""),
(u"Kanji/Word recognition",u"""KW-%(Reading)s<br>%(Meaning)s""",u"""${Css}${W-JLPT}${W-Freq}${K-Stroke}${K-JLPT}${K-Jouyou}${K-Freq}${Expression}${Reading}<br />${Meaning}<br />${K-Words}"""),
(u"Sentence recall",u"""S-%(Reading)s""",u"""${Css}${S-Stroke}${Expression}<br />${Reading}"""),
(u"Sentence recognition",u"""S-%(Reading)s<br>%(Meaning)s""",u"""${Css}${S-Stroke}${Reading}<br />${Meaning}"""),
(u"Grammar recall",u"""G-%(Reading)s""",u"""${Css}${G-Stroke}${Expression}<br />${Reading}"""),
(u"Grammar recognition",u"""G-%(Reading)s<br>%(Meaning)s""",u"""${Css}${G-Stroke}${Reading}<br />${Meaning}"""),
(u"Kanji character",u"""K-%(Kanji)s""",u"""${Css}${K-Stroke}${K-JLPT}${K-Jouyou}${K-Freq}${K-Words}"""),
(u"Kanji meanings",u"""K-%(Meaning)s""",u"""${Css}${K-Stroke}${K-JLPT}${K-Jouyou}${K-Freq}${Meaning}<br /><br />${K-Words}"""),
(u"Kanji readings",u"""K-%(OnYomi)s<br>%(KunYomi)s""",u"""${Css}${K-Stroke}${K-JLPT}${K-Jouyou}${K-Freq}${OnYomi}<br />${KunYomi}<br /><br />${K-Words}""")]
Jx__Css__Default = u"""
/* Romaji */

.Meaning, .Romaji {
        font-family: Osaka,Arial,Helvetica,sans-serif; 
        font-weight: normal; 
        text-decoration: none; 
        font-size:30px;
        text-align:center;
        display:block;
        margin:0 auto;
}

/* Japanese */

.Expression,.Reading,.Kanji,.OnYomi,.KunYomi,.Readings,.Kana,.W,.K,.S,.G,.F {
        font-family: "Hiragino Mincho Pro",'ヒラギノ明朝 Pro W3',Meiryo,'Hiragino Kaku Gothic Pro','MS Mincho',Arial,sans-serif; 
        font-weight: normal; 
        text-decoration: none; 
        font-size:35px;
        text-align:center;
        display:block;
        margin:0 auto;
}

/* W:JLPT, W:Freq info about the Word */

.W-JLPT { 
        font-family: Osaka,Arial,Helvetica,sans-serif; 
        font-weight: normal; 
        font-size:18px;
        text-align:center;
        border :1px solid black;
        width:55px;
        display:block;
        float:left;
        clear:left;
        margin-bottom:-1px;
}
.W-Freq { 
        font-family: Osaka,Arial,Helvetica,sans-serif; 
        font-weight: normal; 
        font-size:18px;
        text-align:center;
        border :1px solid black;
        width:55px;
        display:block;
        margin-left:54px;
        float:left;
        margin-bottom:-1px;
clear:right;
}

/* W-Stroke Order for Words */

.W-Stroke, .G-Stroke,.S-Stroke,.F-Stroke {
        float:left; 
        font-family: KanjiStrokeOrders; 
        font-size: 150px;
        line-height:150px;
        clear:both;
        display:block;
        width: 166px;
        border: 1px solid black;
}

/* K:JLPT, K:Jouyou,K:Freq Info about the Kanji */

.K-JLPT{
        clear:left;
}
.K-JLPT,.K-Jouyou,.K-Freq,.K-Kanken {
        font-family: Osaka,Arial,Helvetica,sans-serif; 
        font-weight: normal; 
        font-size:18px;
        border :1px solid black;
        width:55px;
        float:left;
        text-align:center;
        margin-top:-1px;
        margin-right:-1px;
        display:block;
}
.K-Jouyou {
        width:54px;
}

/* K:Stroke Order for the Kanji */

.K-Stroke {
        float:left; 
        font-family: KanjiStrokeOrders; 
        font-size: 150px;
        line-height:150px;
        clear:both;
        display:block;
        width: 166px;
        border: 1px solid black;
}

/* K-Words related to the Kanji Table */

.Tr-Even {
        background-color:none;
}
.Tr-Odd {
        background-color:#ddedfc;
}
table.K-Words, table.W-Sentences{
        font-size:20px;
        line-height:20px;
        text-align:center;
        margin:0 auto;
        font-family: "Hiragino Mincho Pro",'ヒラギノ明朝 Pro W3',Meiryo,'Hiragino Kaku Gothic Pro','MS Mincho',Arial,sans-serif; 
        font-weight: normal; 
        text-decoration: none;
}
table.K-Words td, table.W-Sentences td{
        padding:6px 10px 6px 10px;
}
table.K-Words .Td-One, table.W-Sentences .Td-One {
        font-family: Osaka,Arial,Helvetica,sans-serif; 
        font-weight: normal; 
        text-decoration: none; 
        font-size:16px
}
"""
from answer import JxTableDisplay
Jx__Sample__Default = {
u'K':u'次',
u'W':u'説明する',
u'S':u'長文んがあるといいな。',
u'G':u'文法ではないね。',
u'F':u'事実です。',
u'S-Stroke':u'長文',
u'G-Stroke':u'文法',
u'F-Stroke':u'事実',
u'Expression':u'説明する',
u'W-Stroke':u'説明',
u'Tags':u'japanese kb01 word',
u'F-Tags':u'kb01',
u'M-Tags':u'japanese',
u'Reading':u'せつめいする',
u'Meaning':u'to explain',
u'W-JLPT':u'3級',
u'W-Freq':u"47",
u'OnYomi':u'ジ',
u'KunYomi':u'つーぐ, つぎ',
u'K-JLPT':u'2級',
u'K-Jouyou':u'G3',
u'K-Freq':u'62',
u'K-Stroke':u'次',
u'K-Words':JxTableDisplay([(u"次第に",u"gradually",u"しだいに"),(u"次回",u"next time",u"じかい"),(u"次ぐ",u"to be next",u"つぐ"),(u"次",u"next",u"つぎ"),(u"第二次",u"the second",u"だいにじ"),(u"目次",u"a table of contents",u"もくじ")],u"K-Words"),
u'W-Sentences':JxTableDisplay([(u'日本語が好きだと言てた。','he said that he loved Japanese.', u'にほんごがすきだといてた。'), (u'交渉は決裂した。',u'The negociations broke off.',u'こうしょうはけつれつした。'),(u'日本へ行くといいな。',u'I would like to go to Japan.',u'にほんへいくといいな。')],u"W-Sentences")}
