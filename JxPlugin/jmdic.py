# -*- coding: utf-8 -*-
# Copyright: Olivier Binda <olivier.binda@wanadoo.fr>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
# ---------------------------------------------------------------------------
# This file is a plugin for the "anki" flashcard application http://ichi2.net/anki/
# ---------------------------------------------------------------------------
#from xml.dom.minidom import parse
from os.path import join
from ankiqt import mw
import codecs
import re

# ok, let's say that we want to create a list for the entries of Kanjidic2.xml : 
JxJMdic = [] 


JxLanguage="fre"

# we don't care about lots of stuff : codepoint[cp], ...


def start_element(Name,Attributes):
        global JxElement, JxAttributes,JxBuffer
        JxElement = Name
        JxAttributes = Attributes
                
        if Name == 'entry':
                # multiple container node -> list
                JxBuffer = dict([('k_ele',[]),('r_ele',[]),('sense',[])])              
                
def char_data(Data):
        #global JxElement,JxAttributes,JxBuffer
        if Data != '\n':
                #got to save the data in a buffer respecting the structure
                if JxElement == 'ent_seq': 
                        ent_seq = Data
                elif JxElement in ['keb','reb','re_nokanji','s_inf']:
                        # unique node -> value
                        JxBuffer[JxElement] = Data
                elif JxElement in ['ke_inf','ke_pri','re_inf','re_pri','r_restr','stagk','stagr','xref','ant','pos','field','misc','dial']:
                        # multiple leaf node
                        try:
                                JxBuffer[JxElement].append(Data)
                        except KeyError:
                                JxBuffer[JxElement] = [Data]
                elif JxElement == 'gloss' and JxAttributes['xml:lang'] == JxLanguage:                    
                        try:
                                JxBuffer['gloss'].append(Data)
                        except KeyError:
                                JxBuffer['gloss'] = [Data]                                
                elif JxElement == 'lsource':
                        try:
                                Language = JxAttributes['xml:lang']
                        except KeyError:
                                Language = 'eng'
                        if 'ls_type' in JxAttributes:
                                Type = False #part
                        else:
                                Type = True #full
                        if 'ls_wasei' in JxAttributes:
                                Wasei = True 
                        else:
                                Wasei = False 
                        try:
                                JxBuffer['lsource'].append([(Data,Language,Type,Wasei)])                        
                        except KeyError:
                                JxBuffer['lsource'] = [(Data,Language,Type,Wasei)]               
        
def end_element(Name):
        if Name == 'entry':
                # saving the info and flushing
                if JxBuffer['sense']: #no need to save if there aren't any glosses in the target language
                        JxJMdic.append([JxBuffer])
        elif Name == 'sense':
                List = [Key for Key in ['gloss','stagk','stagr','xref','ant','pos','field','misc','dial','lsource','s_inf'] if Key in JxBuffer]
                
                if 'gloss' in JxBuffer:
                        JxBuffer['sense'].append([dict([(Key,JxBuffer[Key]) for Key in List])])
                for Key in List:
                        del JxBuffer[Key]
        elif Name == 'r_ele':
                List = [Key for Key in ['reb','re_inf','re_pri','re_nokanji','re_restr'] if Key in JxBuffer]
                JxBuffer['r_ele'].append([dict([(Key,JxBuffer[Key]) for Key in List])])
                for Key in List:
                        del JxBuffer[Key]                        
        if Name == 'k_ele':
                List = [Key for Key in ['keb','ke_inf','ke_pri'] if Key in JxBuffer]
                JxBuffer['k_ele'].append([dict([(Key,JxBuffer[Key]) for Key in List])])
                for Key in List:
                        del JxBuffer[Key]








File = join(os.path.dirname(__file__ ),"Data", "JMdict.gz")



import cPickle, os
import itertools                      
file_pickle = os.path.join(os.path.dirname(__file__ ),"Data", "JMdict.pickle")                      
if False:#(os.path.exists(file_pickle) and os.stat(file_pickle).st_mtime > os.stat(File).st_mtime):
	f = open(file_pickle, 'rb')
	JxJMdic = cPickle.load(f)
	f.close()
else:
        import gzip
        File = gzip.open(File, 'rb')
        JMdic = File.read()
        File.close()
        # I don't ncessarily want Entities to be replaced with the default JMdict strings... I may provide my own strings
        from re import sub
        from globalobjects import JxInitProfile,JxProfile,JxShowProfile
        JxInitProfile('JMdict.py')
        JMdic = sub(r'<info>.*?</info>','',JMdic)
        JMdicWithoutEntities = sub(r'<!ENTITY (.*?) ".*?">',lambda x:'<!ENTITY ' + x.group(1) + ' "${' + x.group(1) + '}">',JMdic)
        
        JxProfile('re-place')
        import xml.parsers.expat
        Jx_Parser_JMdic = xml.parsers.expat.ParserCreate() 
        JxStart = start_element
        JxEnd = end_element
        JxData = char_data
        Jx_Parser_JMdic.StartElementHandler = JxStart
        Jx_Parser_JMdic.EndElementHandler = JxEnd
        Jx_Parser_JMdic.CharacterDataHandler = JxData
        JxProfile('Parser created')
        Jx_Parser_JMdic.Parse(JMdicWithoutEntities)
        JxProfile('JMdit parsed')
        mw.help.showText(JxShowProfile()+str(JxJMdic[6666]))
	f = open(file_pickle, 'wb')
	cPickle.dump(JxJMdic, f, cPickle.HIGHEST_PROTOCOL)
	f.close()
#mw.help.showText(str(len(JxJMdic))+" " +str(JxJMdic[6666])+Debug)#str(JxKanjidic))
"""
<!DOCTYPE JMdict [
<!ELEMENT JMdict (entry*)>
<!--                                                                   -->
<!ELEMENT entry (ent_seq, k_ele*, r_ele+, info?, sense+)>
	<!-- Entries consist of kanji elements, reading elements, 
	general information and sense elements. Each entry must have at 
	least one reading element and one sense element. Others are optional.
	-->
<!ELEMENT ent_seq (#PCDATA)>
	<!-- A unique numeric sequence number for each entry
	-->
<!ELEMENT k_ele (keb, ke_inf*, ke_pri*)>
	<!-- The kanji element, or in its absence, the reading element, is 
	the defining component of each entry.
	The overwhelming majority of entries will have a single kanji
	element associated with a word in Japanese. Where there are 
	multiple kanji elements within an entry, they will be orthographical
	variants of the same word, either using variations in okurigana, or
	alternative and equivalent kanji. Common "mis-spellings" may be 
	included, provided they are associated with appropriate information
	fields. Synonyms are not included; they may be indicated in the
	cross-reference field associated with the sense element.
	-->
<!ELEMENT keb (#PCDATA)>
	<!-- This element will contain a word or short phrase in Japanese 
	which is written using at least one non-kana character (usually kanji,
	but can be other characters). The valid characters are
	kanji, kana, related characters such as chouon and kurikaeshi, and
	in exceptional cases, letters from other alphabets.
	-->
<!ELEMENT ke_inf (#PCDATA)>
	<!-- This is a coded information field related specifically to the 
	orthography of the keb, and will typically indicate some unusual
	aspect, such as okurigana irregularity.
	-->
<!ELEMENT ke_pri (#PCDATA)>
	<!-- This and the equivalent re_pri field are provided to record
	information about the relative priority of the entry,  and consist
	of codes indicating the word appears in various references which
	can be taken as an indication of the frequency with which the word
	is used. This field is intended for use either by applications which 
	want to concentrate on entries of  a particular priority, or to 
	generate subset files. 
	The current values in this field are:
	- news1/2: appears in the "wordfreq" file compiled by Alexandre Girardi
	from the Mainichi Shimbun. (See the Monash ftp archive for a copy.)
	Words in the first 12,000 in that file are marked "news1" and words 
	in the second 12,000 are marked "news2".
	- ichi1/2: appears in the "Ichimango goi bunruishuu", Senmon Kyouiku 
	Publishing, Tokyo, 1998.  (The entries marked "ichi2" were
	demoted from ichi1 because they were observed to have low
	frequencies in the WWW and newspapers.)
	- spec1 and spec2: a small number of words use this marker when they 
	are detected as being common, but are not included in other lists.
	- gai1/2: common loanwords, based on the wordfreq file.
	- nfxx: this is an indicator of frequency-of-use ranking in the
	wordfreq file. "xx" is the number of the set of 500 words in which
	the entry can be found, with "01" assigned to the first 500, "02"
	to the second, and so on. (The entries with news1, ichi1, spec1 and 
	gai1 values are marked with a "(P)" in the EDICT and EDICT2
	files.)

	The reason both the kanji and reading elements are tagged is because 
	on occasions a priority is only associated with a particular
	kanji/reading pair.
	-->
<!--                                                                   -->
<!ELEMENT r_ele (reb, re_nokanji?, re_restr*, re_inf*, re_pri*)>
	<!-- The reading element typically contains the valid readings
	of the word(s) in the kanji element using modern kanadzukai. 
	Where there are multiple reading elements, they will typically be
	alternative readings of the kanji element. In the absence of a 
	kanji element, i.e. in the case of a word or phrase written
	entirely in kana, these elements will define the entry.
	-->
<!ELEMENT reb (#PCDATA)>
	<!-- this element content is restricted to kana and related
	characters such as chouon and kurikaeshi. Kana usage will be
	consistent between the keb and reb elements; e.g. if the keb
	contains katakana, so too will the reb.
	-->
<!ELEMENT re_nokanji (#PCDATA)>
	<!-- This element, which will usually have a null value, indicates
	that the reb, while associated with the keb, cannot be regarded
	as a true reading of the kanji. It is typically used for words
	such as foreign place names, gairaigo which can be in kanji or
	katakana, etc.
	-->
<!ELEMENT re_restr (#PCDATA)>
	<!-- This element is used to indicate when the reading only applies
	to a subset of the keb elements in the entry. In its absence, all
	readings apply to all kanji elements. The contents of this element 
	must exactly match those of one of the keb elements.
	-->
<!ELEMENT re_inf (#PCDATA)>
	<!-- General coded information pertaining to the specific reading.
	Typically it will be used to indicate some unusual aspect of 
	the reading. -->
<!ELEMENT re_pri (#PCDATA)>
	<!-- See the comment on ke_pri above. -->
<!--                                                                   -->
<!ELEMENT info (links*, bibl*, etym*, audit*)>
	<!-- general coded information relating to the entry as a whole.-->
<!ELEMENT bibl (bib_tag?, bib_txt?)>
<!ELEMENT bib_tag (#PCDATA)>
<!ELEMENT bib_txt (#PCDATA)>
	<!-- Bibliographic information about the entry. The bib_tag will a 
	coded reference to an entry in an external bibliographic database.
	The bib_txt field may be used for brief (local) descriptions.-->
<!ELEMENT etym (#PCDATA)>
	<!-- This field is used to hold information about the etymology
	of the kanji or kana parts of the entry. For gairaigo,
	etymological information may also be in the <lsource> element.
	-->
<!ELEMENT links (link_tag, link_desc, link_uri)>
<!ELEMENT link_tag (#PCDATA)>
<!ELEMENT link_desc (#PCDATA)>
<!ELEMENT link_uri (#PCDATA)>
	<!-- This element holds details of linking information to 
	entries in other electronic repositories. The link_tag will be
	coded to indicate the type of link (text, image, sound), the 
	link_desc will provided a textual label for the link, and the 
	link_uri contains the actual URI.  -->
<!ELEMENT audit (upd_date, upd_detl)>
<!ELEMENT upd_date (#PCDATA)>
<!ELEMENT upd_detl (#PCDATA)>
	<!-- The audit element will contain the date and other information
	about updates to the entry. Can be used to record the source of 
	the material. -->
<!--                                                                   -->
<!ELEMENT sense (stagk*, stagr*, pos*, xref*, ant*, field*, misc*, s_inf*, lsource*, dial*, gloss*, example*)>
	<!-- The sense element will record the translational equivalent
	of the Japanese word, plus other related information. Where there
	are several distinctly different meanings of the word, multiple
	sense elements will be employed.
	-->
<!ELEMENT stagk (#PCDATA)>
<!ELEMENT stagr (#PCDATA)>
	<!-- These elements, if present, indicate that the sense is restricted
	to the lexeme represented by the keb and/or reb. -->
<!ELEMENT xref (#PCDATA)*>
	<!-- This element is used to indicate a cross-reference to another
	entry with a similar or related meaning or sense. The content of
	this element is typically a keb or reb element in another entry. In some
	cases a keb will be followed by a reb and/or a sense number to provide
	a precise target for the cross-reference. Where this happens, a JIS
	"centre-dot" (0x2126) is placed between the components of the 
	cross-reference.
	-->
<!ELEMENT ant (#PCDATA)*>
	<!-- This element is used to indicate another entry which is an
	antonym of the current entry/sense. The content of this element
	must exactly match that of a keb or reb element in another entry.
	-->
<!ELEMENT pos (#PCDATA)>
	<!-- Part-of-speech information about the entry/sense. Should use 
	appropriate entity codes. In general where there are multiple senses
	in an entry, the part-of-speech of an earlier sense will apply to
	later senses unless there is a new part-of-speech indicated.
	-->
<!ELEMENT field (#PCDATA)>
	<!-- Information about the field of application of the entry/sense. 
	When absent, general application is implied. Entity coding for 
	specific fields of application. -->
<!ELEMENT misc (#PCDATA)>
	<!-- This element is used for other relevant information about 
	the entry/sense. As with part-of-speech, information will usually
	apply to several senses.
	-->
<!ELEMENT lsource (#PCDATA)>
	<!-- This element records the information about the source
	language(s) of a loan-word/gairaigo. If the source language is other 
	than English, the language is indicated by the xml:lang attribute.
	The element value (if any) is the source word or phrase.
	-->
<!ATTLIST lsource xml:lang CDATA "eng">
	<!-- The xml:lang attribute defines the language(s) from which
	a loanword is drawn.  It will be coded using the three-letter language 
	code from the ISO 639-2 standard. When absent, the value "eng" (i.e. 
	English) is the default value. The bibliographic (B) codes are used. -->
<!ATTLIST lsource ls_type CDATA #IMPLIED>
	<!-- The ls_type attribute indicates whether the lsource element
	fully or partially describes the source word or phrase of the
	loanword. If absent, it will have the implied value of "full".
	Otherwise it will contain "part".  -->
<!ATTLIST lsource ls_wasei CDATA #IMPLIED>
	<!-- The ls_wasei attribute indicates that the Japanese word
	has been constructed from words in the source language, and
	not from an actual phrase in that language. Most commonly used to
	indicate "waseieigo". -->
<!ELEMENT dial (#PCDATA)>
	<!-- For words specifically associated with regional dialects in
	Japanese, the entity code for that dialect, e.g. ksb for Kansaiben.
	-->
<!ELEMENT gloss (#PCDATA | pri)*>
	<!-- Within each sense will be one or more "glosses", i.e. 
	target-language words or phrases which are equivalents to the 
	Japanese word. This element would normally be present, however it 
	may be omitted in entries which are purely for a cross-reference.
	-->
<!ATTLIST gloss xml:lang CDATA "eng">
	<!-- The xml:lang attribute defines the target language of the
	gloss. It will be coded using the three-letter language code from
	the ISO 639 standard. When absent, the value "eng" (i.e. English)
	is the default value. -->
<!ATTLIST gloss g_gend CDATA #IMPLIED>
	<!-- The g_gend attribute defines the gender of the gloss (typically
	a noun in the target language. When absent, the gender is either
	not relevant or has yet to be provided.
	-->
<!ELEMENT pri (#PCDATA)>
	<!-- These elements highlight particular target-language words which 
	are strongly associated with the Japanese word. The purpose is to 
	establish a set of target-language words which can effectively be 
	used as head-words in a reverse target-language/Japanese relationship.
	-->
<!ELEMENT example (#PCDATA)>
	<!-- The example elements provide for pairs of short Japanese and
	target-language phrases or sentences which exemplify the usage of the 
	Japanese head-word and the target-language gloss. Words in example 
	fields would typically not be indexed by a dictionary application.
	-->
<!ELEMENT s_inf (#PCDATA)>
	<!-- The sense-information elements provided for additional
	information to be recorded about a sense. Typical usage would
	be to indicate such things as level of currency of a sense, the
	regional variations, etc.
	-->
<!-- The following entity codes are used for common elements within the
various information fields.
-->
<!ENTITY MA "martial arts term">
<!ENTITY X "rude or X-rated term (not displayed in educational software)">
<!ENTITY abbr "abbreviation">
<!ENTITY adj-i "adjective (keiyoushi)">
<!ENTITY adj-na "adjectival nouns or quasi-adjectives (keiyodoshi)">
<!ENTITY adj-no "nouns which may take the genitive case particle `no'">
<!ENTITY adj-pn "pre-noun adjectival (rentaishi)">
<!ENTITY adj-t "`taru' adjective">
<!ENTITY adj-f "noun or verb acting prenominally">
<!ENTITY adj "former adjective classification (being removed)">
<!ENTITY adv "adverb (fukushi)">
<!ENTITY adv-to "adverb taking the `to' particle">
<!ENTITY arch "archaism">
<!ENTITY ateji "ateji (phonetic) reading">
<!ENTITY aux "auxiliary">
<!ENTITY aux-v "auxiliary verb">
<!ENTITY aux-adj "auxiliary adjective">
<!ENTITY Buddh "Buddhist term">
<!ENTITY chem "chemistry term">
<!ENTITY chn "children's language">
<!ENTITY col "colloquialism">
<!ENTITY comp "computer terminology">
<!ENTITY conj "conjunction">
<!ENTITY ctr "counter">
<!ENTITY derog "derogatory">
<!ENTITY eK "exclusively kanji">
<!ENTITY ek "exclusively kana">
<!ENTITY exp "Expressions (phrases, clauses, etc.)">
<!ENTITY fam "familiar language">
<!ENTITY fem "female term or language">
<!ENTITY food "food term">
<!ENTITY geom "geometry term">
<!ENTITY gikun "gikun (meaning) reading">
<!ENTITY hon "honorific or respectful (sonkeigo) language">
<!ENTITY hum "humble (kenjougo) language">
<!ENTITY iK "word containing irregular kanji usage">
<!ENTITY id "idiomatic expression">
<!ENTITY ik "word containing irregular kana usage">
<!ENTITY int "interjection (kandoushi)">
<!ENTITY io "irregular okurigana usage">
<!ENTITY iv "irregular verb">
<!ENTITY ling "linguistics terminology">
<!ENTITY m-sl "manga slang">
<!ENTITY male "male term or language">
<!ENTITY male-sl "male slang">
<!ENTITY math "mathematics">
<!ENTITY mil "military">
<!ENTITY n "noun (common) (futsuumeishi)">
<!ENTITY n-adv "adverbial noun (fukushitekimeishi)">
<!ENTITY n-suf "noun, used as a suffix">
<!ENTITY n-pref "noun, used as a prefix">
<!ENTITY n-t "noun (temporal) (jisoumeishi)">
<!ENTITY num "numeric">
<!ENTITY oK "word containing out-dated kanji">
<!ENTITY obs "obsolete term">
<!ENTITY obsc "obscure term">
<!ENTITY ok "out-dated or obsolete kana usage">
<!ENTITY on-mim "onomatopoeic or mimetic word">
<!ENTITY pn "pronoun">
<!ENTITY poet "poetical term">
<!ENTITY pol "polite (teineigo) language">
<!ENTITY pref "prefix">
<!ENTITY prt "particle">
<!ENTITY physics "physics terminology">
<!ENTITY rare "rare">
<!ENTITY sens "sensitive">
<!ENTITY sl "slang">
<!ENTITY suf "suffix">
<!ENTITY uK "word usually written using kanji alone">
<!ENTITY uk "word usually written using kana alone">
<!ENTITY v1 "Ichidan verb">
<!ENTITY v2a-s "Nidan verb with 'u' ending (archaic)">
<!ENTITY v4h "Yondan verb with `hu/fu' ending (archaic)">
<!ENTITY v4r "Yondan verb with `ru' ending (archaic)">
<!ENTITY v5 "Godan verb (not completely classified)">
<!ENTITY v5aru "Godan verb - -aru special class">
<!ENTITY v5b "Godan verb with `bu' ending">
<!ENTITY v5g "Godan verb with `gu' ending">
<!ENTITY v5k "Godan verb with `ku' ending">
<!ENTITY v5k-s "Godan verb - Iku/Yuku special class">
<!ENTITY v5m "Godan verb with `mu' ending">
<!ENTITY v5n "Godan verb with `nu' ending">
<!ENTITY v5r "Godan verb with `ru' ending">
<!ENTITY v5r-i "Godan verb with `ru' ending (irregular verb)">
<!ENTITY v5s "Godan verb with `su' ending">
<!ENTITY v5t "Godan verb with `tsu' ending">
<!ENTITY v5u "Godan verb with `u' ending">
<!ENTITY v5u-s "Godan verb with `u' ending (special class)">
<!ENTITY v5uru "Godan verb - Uru old class verb (old form of Eru)">
<!ENTITY v5z "Godan verb with `zu' ending">
<!ENTITY vz "Ichidan verb - zuru verb (alternative form of -jiru verbs)">
<!ENTITY vi "intransitive verb">
<!ENTITY vk "Kuru verb - special class">
<!ENTITY vn "irregular nu verb">
<!ENTITY vr "irregular ru verb, plain form ends with -ri">
<!ENTITY vs "noun or participle which takes the aux. verb suru">
<!ENTITY vs-s "suru verb - special class">
<!ENTITY vs-i "suru verb - irregular">
<!ENTITY kyb "Kyoto-ben">
<!ENTITY osb "Osaka-ben">
<!ENTITY ksb "Kansai-ben">
<!ENTITY ktb "Kantou-ben">
<!ENTITY tsb "Tosa-ben">
<!ENTITY thb "Touhoku-ben">
<!ENTITY tsug "Tsugaru-ben">
<!ENTITY kyu "Kyuushuu-ben">
<!ENTITY rkb "Ryuukyuu-ben">
<!ENTITY nab "Nagano-ben">
<!ENTITY vt "transitive verb">
<!ENTITY vulg "vulgar expression or word">
]>"""
