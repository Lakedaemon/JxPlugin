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
#dom = parse(join(mw.config.configPath, "plugins","JxPlugin","Data", "Kanjidic2.xml"))
#dom = xml.dom.minidom.parseString(document)
import xml.parsers.expat
import itertools



# ok, let's say that we want to create a list (or a dictionary) for the entries of Kanjidic2.xml : 
JxKanjidic = [] 




# need this to see what happens
#Debug=""

# we don't care about lots of stuff : codepoint[cp], 

def start_element(Name,Attributes):
        global JxElement,JxAttributes,JxBuffer
        JxElement = Name
        JxAttributes = Attributes
        if Name == 'character':
                # multiple container node -> list
                JxBuffer = dict([('rad_value',[]),('stroke_count',[]),('rmgroup',[]),('nanori',[])])
        if Name == 'rmgroup':
                JxBuffer['ja_on'] = []
                JxBuffer['ja_kun'] = []
                JxBuffer['meaning'] = []                

                
        #global Debug
        #if len(Debug)<100000:
        #        String = u''
        #        if Attributes:
        #                for (Key,Value) in Attributes.iteritems():
        #                        String += " " + str(Key) + '="' + str(Value) + '"'
        #        Debug += '&lt;' +str(Name)+ String +'&gt;<br/>'
                
def char_data(Data):
        if Data != '\n':
                #got to save the data in a buffer respecting the structure
                if JxElement in ['literal','grade','jlpt','rad_name','freq']:
                        # unique node -> value
                        JxBuffer[JxElement] = Data                              
                if JxElement in ['rad_value']:
                        # multiple leaf node with attribute -> List
                        JxBuffer[JxElement].append((JxAttributes['rad_type'],Data))
                if JxElement in ['stroke_count','nanori']:
                        # multiple leaf node with attribute -> List
                        JxBuffer[JxElement].append(Data)
                if JxElement in ['meaning'] and not(JxAttributes):
                        # multiple leaf node with attribute -> List
                        JxBuffer[JxElement].append(Data)  
                if JxElement in ['reading'] and JxAttributes['r_type'] in ['ja_on','ja_kun']:
                        # multiple leaf node with attribute -> List
                        JxBuffer[JxAttributes['r_type']].append(Data)                          
        #global Debug
        #if len(Debug)<100000 and Data !=u'\n':
        #        Debug+= 'Data:' +str(repr(Data)) +"<br/>"                
                
                
def end_element(Name):
        if Name == 'rmgroup':
                JxBuffer['rmgroup'].append((JxBuffer['ja_on'],JxBuffer['ja_kun'],JxBuffer['meaning']))
                del JxBuffer['ja_on']
                del JxBuffer['ja_kun']
                del JxBuffer['meaning']
        if Name == 'character':
                # saving the info and flushing
                JxKanjidic.append([JxBuffer])      
        
        #global Debug
        #if len(Debug)<100000:
        #        Debug+= '&lt;/' +str( Name)+"&gt;<br/>"





File = join(mw.config.configPath, "plugins","JxPlugin","Data", "Kanjidic2.xml.gz")



import cPickle, os
import itertools                      
file_pickle = os.path.join(mw.config.configPath, "plugins","JxPlugin","Data", "Kanjidic.pickle")                      
if (os.path.exists(file_pickle) and os.stat(file_pickle).st_mtime > os.stat(File).st_mtime):
	f = open(file_pickle, 'rb')
	JxKanjidic = cPickle.load(f)
	f.close()
else:
        import gzip
        File = gzip.open(File, 'rb')
        Kanjidic2 = File.read()
        File.close()
        Jx_Parser_Kanjidic = xml.parsers.expat.ParserCreate()                
        Jx_Parser_Kanjidic.StartElementHandler = start_element
        Jx_Parser_Kanjidic.EndElementHandler = end_element
        Jx_Parser_Kanjidic.CharacterDataHandler = char_data
        Jx_Parser_Kanjidic.Parse(Kanjidic2)
	f = open(file_pickle, 'wb')
	cPickle.dump(JxKanjidic, f, cPickle.HIGHEST_PROTOCOL)
	f.close()
#mw.help.showText(str(JxKanjidic))

"""
<!DOCTYPE kanjidic2 [
	<!-- Version 1.6 - April 2008
	This is the DTD of the XML-format kanji file combining information from
	the KANJIDIC and KANJD212 files. It is intended to be largely self-
	documenting, with each field being accompanied by an explanatory
	comment.

	The file covers the following kanji:
	(a) the 6,355 kanji from JIS X 0208;
	(b) the 5,801 kanji from JIS X 0212;
	(c) the 3,693 kanji from JIS X 0213 as follows:
		(i) the 2,741 kanji which are also in JIS X 0212 have
		JIS X 0213 code-points (kuten) added to the existing entry;
		(ii) the 952 "new" kanji have new entries.

	At the end of the explanation for a number of fields there is a tag
	with the format [N]. This indicates the leading letter(s) of the
	equivalent field in the KANJIDIC and KANJD212 files.

	The KANJIDIC documentation should also be read for additional 
	information about the information in the file.
	-->
<!ELEMENT kanjidic2 (header,character*)>
<!ELEMENT header (file_version,database_version,date_of_creation)>
<!--
	The single header element will contain identification information
	about the version of the file 
	-->
<!ELEMENT file_version (#PCDATA)>
<!--
	This field denotes the version of kanjidic2 structure, as more
	than one version may exist.
	-->
<!ELEMENT database_version (#PCDATA)>
<!--
	The version of the file, in the format YYYY-NN, where NN will be
	a number starting with 01 for the first version released in a
	calendar year, then increasing for each version in that year.
	-->
<!ELEMENT date_of_creation (#PCDATA)>
<!--
	The date the file was created in international format (YYYY-MM-DD).
	-->
<!ELEMENT character (literal,codepoint, radical, misc, dic_number?, query_code?, reading_meaning?)*>
<!ELEMENT literal (#PCDATA)>
<!--
	The character itself in UTF8 coding.
	-->
<!ELEMENT codepoint (cp_value+)>
	<!-- 
	The codepoint element states the code of the character in the various
	character set standards.
	-->
<!ELEMENT cp_value (#PCDATA)>
	<!-- 
	The cp_value contains the codepoint of the character in a particular
	standard. The standard will be identified in the cp_type attribute.
	-->
<!ATTLIST cp_value cp_type CDATA #REQUIRED>
	<!-- 
	The cp_type attribute states the coding standard applying to the
	element. The values assigned so far are:
		jis208 - JIS X 0208-1997 - kuten coding (nn-nn)
		jis212 - JIS X 0212-1990 - kuten coding (nn-nn)
		jis213 - JIS X 0213-2000 - kuten coding (p-nn-nn)
		ucs - Unicode 4.0 - hex coding (4 or 5 hexadecimal digits)
	-->
<!ELEMENT radical (rad_value+)>
<!ELEMENT rad_value (#PCDATA)>
	<!-- 
	The radical number, in the range 1 to 214. The particular
	classification type is stated in the rad_type attribute.
	-->
<!ATTLIST rad_value rad_type CDATA #REQUIRED>
	<!-- 
	The rad_type attribute states the type of radical classification.
		classical - as recorded in the KangXi Zidian.
		nelson_c - as used in the Nelson "Modern Japanese-English 
		Character Dictionary" (i.e. the Classic, not the New Nelson).
		This will only be used where Nelson reclassified the kanji.
	-->
<!ELEMENT misc (grade?, stroke_count+, variant*, freq?, rad_name*,jlpt?)>
<!ELEMENT grade (#PCDATA)>
	<!-- 
	The kanji grade level. 1 through 6 indicates a Kyouiku kanji
	and the grade in which the kanji is taught in Japanese schools. 
	8 indicates it is one of the remaining Jouyou Kanji to be learned 
	in junior high school, and 9 or 10 indicates it is a Jinmeiyou (for use 
	in names) kanji. [G]
	-->
<!ELEMENT stroke_count (#PCDATA)>
	<!-- 
	The stroke count of the kanji, including the radical. If more than 
	one, the first is considered the accepted count, while subsequent ones 
	are common miscounts. (See Appendix E. of the KANJIDIC documentation
	for some of the rules applied when counting strokes in some of the 
	radicals.) [S]
	-->
<!ELEMENT variant (#PCDATA)>
	<!-- 
	Either a cross-reference code to another kanji, usually regarded as a 
	variant, or an alternative indexing code for the current kanji.
	The type of variant is given in the var_type attribute.
	-->
<!ATTLIST variant var_type CDATA #REQUIRED>
	<!-- 
	The var_type attribute indicates the type of variant code. The current
	values are: 
		jis208 - in JIS X 0208 - kuten coding
		jis212 - in JIS X 0212 - kuten coding
		jis213 - in JIS X 0213 - kuten coding
		  (most of the above relate to "shinjitai/kyuujitai" 
		  alternative character glyphs)
		deroo - De Roo number - numeric
		njecd - Halpern NJECD index number - numeric
		s_h - The Kanji Dictionary (Spahn & Hadamitzky) - descriptor
		nelson_c - "Classic" Nelson - numeric
		oneill - Japanese Names (O'Neill) - numeric
		ucs - Unicode codepoint- hex
	-->
<!ELEMENT freq (#PCDATA)>
	<!-- 
	A frequency-of-use ranking. The 2,500 most-used characters have a 
	ranking; those characters that lack this field are not ranked. The 
	frequency is a number from 1 to 2,500 that expresses the relative 
	frequency of occurrence of a character in modern Japanese. This is
	based on a survey in newspapers, so it is biassed towards kanji
	used in newspaper articles. The discrimination between the less
	frequently used kanji is not strong.
	-->
<!ELEMENT rad_name (#PCDATA)>
	<!-- 
	When the kanji is itself a radical and has a name, this element
	contains the name (in hiragana.) [T2]
	-->
<!ELEMENT jlpt (#PCDATA)>
	<!--
	Japanese Language Proficiency test level for this kanji. Values
	range from 1 (most advanced) to 4 (most elementary). This field 
	does not appear for kanji that are not required for any JLPT level.
	-->
<!ELEMENT dic_number (dic_ref+)>
	<!-- 
	This element contains the index numbers and similar unstructured
	information such as page numbers in a number of published dictionaries,
	and instructional books on kanji.
	-->
<!ELEMENT dic_ref (#PCDATA)>
	<!-- 
	Each dic_ref contains an index number. The particular dictionary,
	etc. is defined by the dr_type attribute.
	-->
<!ATTLIST dic_ref dr_type CDATA #REQUIRED>
	<!-- 
	The dr_type defines the dictionary or reference book, etc. to which
	dic_ref element applies. The initial allocation is:
	  nelson_c - "Modern Reader's Japanese-English Character Dictionary",  
	  	edited by Andrew Nelson (now published as the "Classic" 
	  	Nelson).
	  nelson_n - "The New Nelson Japanese-English Character Dictionary", 
	  	edited by John Haig.
	  halpern_njecd - "New Japanese-English Character Dictionary", 
	  	edited by Jack Halpern.
	  halpern_kkld - "Kanji Learners Dictionary" (Kodansha) edited by 
	  	Jack Halpern.
	  heisig - "Remembering The  Kanji"  by  James Heisig.
	  gakken - "A  New Dictionary of Kanji Usage" (Gakken)
	  oneill_names - "Japanese Names", by P.G. O'Neill. 
	  oneill_kk - "Essential Kanji" by P.G. O'Neill.
	  moro - "Daikanwajiten" compiled by Morohashi. For some kanji two
	  	additional attributes are used: m_vol:  the volume of the
	  	dictionary in which the kanji is found, and m_page: the page
	  	number in the volume.
	  henshall - "A Guide To Remembering Japanese Characters" by
	  	Kenneth G.  Henshall.
	  sh_kk - "Kanji and Kana" by Spahn and Hadamitzky.
	  sakade - "A Guide To Reading and Writing Japanese" edited by
	  	Florence Sakade.
	  jf_cards - Japanese Kanji Flashcards, by Max Hodges and
		Tomoko Okazaki.
	  henshall3 - "A Guide To Reading and Writing Japanese" 3rd
		edition, edited by Henshall, Seeley and De Groot.
	  tutt_cards - Tuttle Kanji Cards, compiled by Alexander Kask.
	  crowley - "The Kanji Way to Japanese Language Power" by
	  	Dale Crowley.
	  kanji_in_context - "Kanji in Context" by Nishiguchi and Kono.
	  busy_people - "Japanese For Busy People" vols I-III, published
		by the AJLT. The codes are the volume.chapter.
	  kodansha_compact - the "Kodansha Compact Kanji Guide".
	  maniette - codes from Yves Maniette's "Les Kanjis dans la tete" French adaptation of Heisig.
	-->
<!ATTLIST dic_ref m_vol CDATA #IMPLIED>
	<!-- 
	See above under "moro".
	-->
<!ATTLIST dic_ref m_page CDATA #IMPLIED>
	<!-- 
	See above under "moro".
	-->
<!ELEMENT query_code (q_code+)>
	<!-- 
	These codes contain information relating to the glyph, and can be used
	for finding a required kanji. The type of code is defined by the
	qc_type attribute.
	-->
<!ELEMENT q_code (#PCDATA)>
	<!--
	The q_code contains the actual query-code value, according to the
	qc_type attribute.
	-->
<!ATTLIST q_code qc_type CDATA #REQUIRED>
	<!-- 
	The qc_type attribute defines the type of query code. The current values
	are:
	  skip -  Halpern's SKIP (System  of  Kanji  Indexing  by  Patterns) 
	  	code. The  format is n-nn-nn.  See the KANJIDIC  documentation 
	  	for  a description of the code and restrictions on  the 
	  	commercial  use  of this data. [P]  There are also
		a number of misclassification codes, indicated by the
		"skip_misclass" attribute.
	  sh_desc - the descriptor codes for The Kanji Dictionary (Tuttle 
	  	1996) by Spahn and Hadamitzky. They are in the form nxnn.n,  
	  	e.g.  3k11.2, where the  kanji has 3 strokes in the 
	  	identifying radical, it is radical "k" in the SH 
	  	classification system, there are 11 other strokes, and it is 
	  	the 2nd kanji in the 3k11 sequence. (I am very grateful to 
	  	Mark Spahn for providing the list of these descriptor codes 
	  	for the kanji in this file.) [I]
	  four_corner - the "Four Corner" code for the kanji. This is a code 
	  	invented by Wang Chen in 1928. See the KANJIDIC documentation 
	  	for  an overview of  the Four Corner System. [Q]

	  deroo - the codes developed by the late Father Joseph De Roo, and 
	  	published in  his book "2001 Kanji" (Bonjinsha). Fr De Roo 
	  	gave his permission for these codes to be included. [DR]
	  misclass - a possible misclassification of the kanji according
		to one of the code types. (See the "Z" codes in the KANJIDIC
		documentation for more details.)
	  
	-->
<!ATTLIST q_code skip_misclass CDATA #IMPLIED>
	<!--
	The values of this attribute indicate the type if
	misclassification:
	- posn - a mistake in the division of the kanji
	- stroke_count - a mistake in the number of strokes
	- stroke_and_posn - mistakes in both division and strokes
	- stroke_diff - ambiguous stroke counts depending on glyph
	-->

<!ELEMENT reading_meaning (rmgroup*, nanori*)>
	<!-- 
	The readings for the kanji in several languages, and the meanings, also
	in several languages. The readings and meanings are grouped to enable
	the handling of the situation where the meaning is differentiated by 
	reading. [T1]
	-->
<!ELEMENT rmgroup (reading*, meaning*)>
<!ELEMENT reading (#PCDATA)>
	<!-- 
	The reading element contains the reading or pronunciation
	of the kanji.
	-->
<!ATTLIST reading r_type CDATA #REQUIRED>
	<!-- 
	The r_type attribute defines the type of reading in the reading
	element. The current values are:
	  pinyin - the modern PinYin romanization of the Chinese reading 
	  	of the kanji. The tones are represented by a concluding 
	  	digit. [Y]
	  korean_r - the romanized form of the Korean reading(s) of the 
	  	kanji.  The readings are in the (Republic of Korea) Ministry 
	  	of Education style of romanization. [W]
	  korean_h - the Korean reading(s) of the kanji in hangul.
	  ja_on - the "on" Japanese reading of the kanji, in katakana. 
	  	Another attribute r_status, if present, will indicate with
	  	a value of "jy" whether the reading is approved for a
	  	"Jouyou kanji".
		A further attribute on_type, if present,  will indicate with 
		a value of kan, go, tou or kan'you the type of on-reading.
	  ja_kun - the "kun" Japanese reading of the kanji, usually in 
		hiragana. 
	  	Where relevant the okurigana is also included separated by a 
	  	".". Readings associated with prefixes and suffixes are 
	  	marked with a "-". A second attribute r_status, if present, 
	  	will indicate with a value of "jy" whether the reading is 
	  	approved for a "Jouyou kanji".
	-->
<!ATTLIST reading on_type CDATA #IMPLIED>
	<!-- 
	See under ja_on above.
	-->
<!ATTLIST reading r_status CDATA #IMPLIED>
	<!-- 
	See under ja_on and ja_kun above.
	-->
<!ELEMENT meaning (#PCDATA)>
	<!-- 
	The meaning associated with the kanji.
	-->
<!ATTLIST meaning m_lang CDATA #IMPLIED>
	<!-- 
	The m_lang attribute defines the target language of the meaning. It 
	will be coded using the two-letter language code from the ISO 639-1 
	standard. When absent, the value "en" (i.e. English) is implied. [{}]
	-->
<!ELEMENT nanori (#PCDATA)>
	<!-- 
	Japanese readings that are now only associated with names.
	-->
]>"""
