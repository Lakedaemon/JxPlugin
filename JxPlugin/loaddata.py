# -*- coding: utf-8 -*-
# Copyright: Olivier Binda <olivier.binda@wanadoo.fr>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
# ---------------------------------------------------------------------------
# This file is a plugin for the "anki" flashcard application http://ichi2.net/anki/
# ---------------------------------------------------------------------------
from ankiqt import mw
from math import log
######################################################################
#
#                      JLPT for Kanji
#
######################################################################

KanjiList_JLPT = {
4: '一七万三上下中九二五人今休会何先入八六円出分前北十千午半南友口古右名四国土外多大天女子学安小少山川左年店後手新日時書月木本来東校母毎気水火父生男白百目社空立耳聞花行西見言話語読買足車週道金長間雨電食飲駅高魚'.decode("utf-8"), 
3:
'不世主乗事京仕代以低住体作使便借働元兄光写冬切別力勉動区医去台合同味品員問回図地堂場声売夏夕夜太好妹姉始字室家寒屋工市帰広度建引弟弱強待心思急悪意所持教文料方旅族早明映春昼暑暗曜有服朝村林森業楽歌止正歩死民池注洋洗海漢牛物特犬理産用田町画界病発県真着知短研私秋究答紙終習考者肉自色英茶菜薬親計試説貸質赤走起転軽近送通進運遠都重野銀門開院集青音頭題顔風飯館首験鳥黒'.decode("utf-8"),
2: '腕湾和論録老労路連練恋列歴齢零礼冷例令類涙輪緑領量良療涼両了粒留流略率律陸裏利卵乱落絡頼翌浴欲陽踊要葉溶様容幼預与余予郵遊由勇優輸油約役戻毛面綿鳴迷命娘無夢務眠未満末枚埋磨防貿棒望暴忙忘帽坊亡豊訪法放抱宝報包暮募補捕保返辺編片変壁米閉並平兵粉仏沸払複腹福幅復副封部舞武負膚符浮普怖府布富婦夫付貧秒評表氷標筆必匹鼻美備飛非費被皮疲比批悲彼否番晩販般犯版板反判抜髪畑肌箱麦爆薄泊倍配背杯敗拝馬破波農脳能濃悩燃念熱猫認任乳難軟内鈍曇届突独毒得銅童導逃到筒等当灯湯盗投島塔凍党倒怒努途登渡徒塗殿伝点展鉄適的滴泥程庭底定停痛追賃珍沈直頂超調張庁兆貯著駐虫柱宙仲竹畜築遅置恥値談段暖断団炭探担単谷達濯宅第退袋替帯対打他損尊孫存卒続速測束息則側造贈蔵臓憎増像装草総窓相争燥操掃捜想層双組祖全然善選船線浅泉戦専占絶雪節設折接責績積石昔席税静製精清晴星整政成性姓勢制数吹震針辛身臣神申深寝信伸触職植蒸畳状条情常城賞象紹笑章省照焼消昇招承床将商召勝除助諸署緒初処順純準述術祝宿柔舟拾修州周収授受酒種守取若捨実湿失識式辞示治次寺児似歯資誌詞脂糸枝支指志師史司刺伺残賛算散参皿雑殺札察刷冊昨咲坂財罪材在際細祭済歳採才妻最再座砂査差混根婚困込骨腰告刻号香降鉱郊講荒航肯耕紅硬港構更康幸向厚効公候交誤御互雇湖枯故戸庫固呼個限現減原険軒賢肩権検券健件血結決欠劇迎芸警経景敬恵形型傾係軍群訓君靴掘隅偶具苦禁均勤玉極曲局胸狭況橋挟恐境叫協共競供漁許巨居旧給級球泣求救吸久逆客詰喫議疑技記規季祈機期机希寄基器喜危願岩岸含丸関観簡管看甘環汗換慣感干官完巻刊乾活割額革較角覚確格拡各害貝階絵皆灰械改快解介過貨課菓荷河果科可加価仮化温億黄王欧横押応奥央汚塩煙演延園越液鋭泳永栄営雲羽宇因印育域違衣胃移異易委囲偉依位案圧愛'.decode("utf-8"),
1:
'乙丁刀又勺士及己丈乏寸凡刃弓斤匁氏井仁丹幻凶刈冗弔斗尺屯孔升厄丙且弁功甲仙句巡矢穴丘玄巧矛汁尼迅奴囚凸凹斥弐吏企邦江吉刑充至芝扱旬旨尽缶仰后伏劣朴壮吐如匠妃朱伐舌羊朽帆妄芋沢佐攻系抗迫我抑択秀尾伴邸沖却災孝戒杉里妥肝妙序即寿励芳克没妊豆狂岐廷妨亜把呈尿忍呉伯扶忌肖迭吟汽坑抄壱但松郎房拠拒枠併析宗典祉免忠沿舎抵茂斉炎阻岳拘卓炉牧奇拍往屈径抽披沼肥拐拓尚征邪殴奉怪佳昆芽苗垂宜盲弦炊枢坪泡肪奔享拙侍叔岬侮抹茎劾泌肢附派施姿宣昭皇紀削為染契郡挑促俊侵括透津是奏威柄柳孤牲帝耐恒冒胞浄肺貞胆悔盾軌荘冠卸垣架砕俗洞亭赴盆疫訂怠哀臭洪狩糾峡厘胎窃恨峠叙逓甚姻幽卑帥逝拷某勅衷逐侯弧朕耗挙宮株核討従振浜素益逮陣秘致射貢浦称納紛託敏郷既華哲症倉索俳剤陥兼脅竜梅桜砲祥秩唆泰剣倫殊朗烈悟恩陛衰准浸虐徐脈俵栽浪紋逸隻鬼姫剛疾班宰娠桑飢郭宴珠唐恭悦粋辱桃扇娯俸峰紡胴挿剖唇匿畔翁殉租桟蚊栓宵酌蚕畝倣倹視票渉推崎盛崩脱患執密措描掲控渋掛排訳訟釈隆唱麻斎貫偽脚彩堀菊唯猛陳偏遇陰啓粘遂培淡剰虚帳惨据勘添斜涯眼瓶彫釣粛庶菌巣廊寂酔惜悼累陶粗蛇眺陵舶窒紳旋紺遍猟偵喝豚赦殻陪悠淑笛渇崇曹尉蛍庸渓堕婆脹痘統策提裁証援訴衆隊就塁遣雄廃創筋葬惑博弾塚項喪街属揮貴焦握診裂裕堅賀揺喚距圏軸絞棋揚雰殖随尋棟搭詐紫欺粧滋煮疎琴棚晶堤傍傘循幾掌渦猶慌款敢扉硫媒暁堪酢愉塀閑詠痢婿硝棺詔惰蛮塑虞幹義督催盟献債源継載幕傷鈴棄跡慎携誉勧滞微誠聖詳雅飾詩嫌滅滑頑蓄誇賄墓寛隔暇飼艇奨滝雷酬愚遭稚践嫁嘆碁漠該痴搬虜鉛跳僧溝睡猿摂飽鼓裸塊腸慈遮慨鉢禅絹傑禍酪賊搾廉煩愁楼褐頒嗣銑箇遵態閣摘維遺模僚障徴需端奪誘銭銃駆稲綱閥隠徳豪旗網酸罰腐僕塾漏彰概慢銘漫墜漂駄獄誓酷墨磁寧穀魂暦碑膜漬酵遷雌漆寡慕漸嫡謁賦監審影撃請緊踏儀避締撤盤養還慮緩徹衝撮誕歓縄範暫趣慰潟敵魅敷潮賠摩輝稼噴撲縁慶潜黙輩稿舗熟霊諾勲潔履憂潤穂賓寮澄弊餓窮幣槽墳閲憤戯嘱鋳窯褒罷賜錘墾衛融憲激壊興獲樹薦隣繁擁鋼縦膨憶諮謀壌緯諭糖懐壇奮穏謡憾凝獣縫憩錯縛衡薫濁錠篤隷嬢儒薪錬爵鮮厳聴償縮購謝懇犠翼繊擦覧謙頻轄鍛礁擬謹醜矯嚇霜謄濫離織臨闘騒礎鎖瞬懲糧覆翻顕鎮穫癒騎藩癖襟繕繭璽繰瀬覇簿鯨鏡髄霧麗羅鶏譜藻韻護響懸籍譲騰欄鐘醸躍露顧艦魔襲驚鑑'.decode("utf-8")
}


Kanji2JLPT = {}
for a in range(1,5):
    for b in KanjiList_JLPT[a]:
        Kanji2JLPT[b]=a


######################################################################
#
#                      Grade for Kanji
#
######################################################################
		    
KanjiList_Jouyou={
1:
u'一九七二人入八力十下三千上口土夕大女子小山川五天中六円手文日月木水火犬王正出本右四左玉生田白目石立百年休先名字早気竹糸耳虫村男町花見貝赤足車学林空金雨青草音校森',
2:
u'刀万丸才工弓内午少元今公分切友太引心戸方止毛父牛半市北古台兄冬外広母用矢交会合同回寺地多光当毎池米羽考肉自色行西来何作体弟図声売形汽社角言谷走近里麦画東京夜直国姉妹岩店明歩知長門昼前南点室後春星海活思科秋茶計風食首夏弱原家帰時紙書記通馬高強教理細組船週野雪魚鳥黄黒場晴答絵買朝道番間雲園数新楽話遠電鳴歌算語読聞線親頭曜顔',
3:
u'丁予化区反央平申世由氷主仕他代写号去打皮皿礼両曲向州全次安守式死列羊有血住助医君坂局役投対決究豆身返表事育使命味幸始実定岸所放昔板泳注波油受物具委和者取服苦重乗係品客県屋炭度待急指持拾昭相柱洋畑界発研神秒級美負送追面島勉倍真員宮庫庭旅根酒消流病息荷起速配院悪商動宿帳族深球祭第笛終習転進都部問章寒暑植温湖港湯登短童等筆着期勝葉落軽運遊開階陽集悲飲歯業感想暗漢福詩路農鉄意様緑練銀駅鼻横箱談調橋整薬館題',
4:
u'士不夫欠氏民史必失包末未以付令加司功札辺印争仲伝共兆各好成灯老衣求束兵位低児冷別努労告囲完改希折材利臣良芸初果刷卒念例典周協参固官底府径松毒泣治法牧的季英芽単省変信便軍勇型建昨栄浅胃祝紀約要飛候借倉孫案害帯席徒挙梅残殺浴特笑粉料差脈航訓連郡巣健側停副唱堂康得救械清望産菜票貨敗陸博喜順街散景最量満焼然無給結覚象貯費達隊飯働塩戦極照愛節続置腸辞試歴察旗漁種管説関静億器賞標熱養課輪選機積録観類験願鏡競議',
5:
u'久仏支比可旧永句圧弁布刊犯示再仮件任因団在舌似余判均志条災応序快技状防武承価舎券制効妻居往性招易枝河版肥述非保厚故政査独祖則逆退迷限師個修俵益能容恩格桜留破素耕財造率貧基婦寄常張術情採授接断液混現略眼務移経規許設責険備営報富属復提検減測税程絶統証評賀貸貿過勢幹準損禁罪義群墓夢解豊資鉱預飼像境増徳慣態構演精総綿製複適酸銭銅際雑領導敵暴潔確編賛質興衛燃築輸績講謝織職額識護',
6:
u'亡寸己干仁尺片冊収処幼庁穴危后灰吸存宇宅机至否我系卵忘孝困批私乱垂乳供並刻呼宗宙宝届延忠拡担拝枚沿若看城奏姿宣専巻律映染段洗派皇泉砂紅背肺革蚕値俳党展座従株将班秘純納胸朗討射針降除陛骨域密捨推探済異盛視窓翌脳著訪訳欲郷郵閉頂就善尊割創勤裁揮敬晩棒痛筋策衆装補詞貴裏傷暖源聖盟絹署腹蒸幕誠賃疑層模穀磁暮誤誌認閣障劇権潮熟蔵諸誕論遺奮憲操樹激糖縦鋼厳優縮覧簡臨難臓警',
'HS':
u'乙了又与及丈刃凡勺互弔井升丹乏匁屯介冗凶刈匹厄双孔幻斗斤且丙甲凸丘斥仙凹召巨占囚奴尼巧払汁玄甘矛込弐朱吏劣充妄企仰伐伏刑旬旨匠叫吐吉如妃尽帆忙扱朽朴汚汗江壮缶肌舟芋芝巡迅亜更寿励含佐伺伸但伯伴呉克却吟吹呈壱坑坊妊妨妙肖尿尾岐攻忌床廷忍戒戻抗抄択把抜扶抑杉沖沢沈没妥狂秀肝即芳辛迎邦岳奉享盲依佳侍侮併免刺劾卓叔坪奇奔姓宜尚屈岬弦征彼怪怖肩房押拐拒拠拘拙拓抽抵拍披抱抹昆昇枢析杯枠欧肯殴況沼泥泊泌沸泡炎炊炉邪祈祉突肢肪到茎苗茂迭迫邸阻附斉甚帥衷幽為盾卑哀亭帝侯俊侵促俗盆冠削勅貞卸厘怠叙咲垣契姻孤封峡峠弧悔恒恨怒威括挟拷挑施是冒架枯柄柳皆洪浄津洞牲狭狩珍某疫柔砕窃糾耐胎胆胞臭荒荘虐訂赴軌逃郊郎香剛衰畝恋倹倒倣俸倫翁兼准凍剣剖脅匿栽索桑唆哲埋娯娠姫娘宴宰宵峰貢唐徐悦恐恭恵悟悩扇振捜挿捕敏核桟栓桃殊殉浦浸泰浜浮涙浪烈畜珠畔疾症疲眠砲祥称租秩粋紛紡紋耗恥脂朕胴致般既華蚊被託軒辱唇逝逐逓途透酌陥陣隻飢鬼剤竜粛尉彫偽偶偵偏剰勘乾喝啓唯執培堀婚婆寂崎崇崩庶庸彩患惨惜悼悠掛掘掲控据措掃排描斜旋曹殻貫涯渇渓渋淑渉淡添涼猫猛猟瓶累盗眺窒符粗粘粒紺紹紳脚脱豚舶菓菊菌虚蛍蛇袋訟販赦軟逸逮郭酔釈釣陰陳陶陪隆陵麻斎喪奥蛮偉傘傍普喚喫圏堪堅堕塚堤塔塀媒婿掌項幅帽幾廃廊弾尋御循慌惰愉惑雇扉握援換搭揚揺敢暁晶替棺棋棚棟款欺殖渦滋湿渡湾煮猶琴畳塁疎痘痢硬硝硫筒粧絞紫絡脹腕葬募裕裂詠詐詔診訴越超距軸遇遂遅遍酢鈍閑隅随焦雄雰殿棄傾傑債催僧慈勧載嗣嘆塊塑塗奨嫁嫌寛寝廉微慨愚愁慎携搾摂搬暇楼歳滑溝滞滝漠滅溶煙煩雅猿献痴睡督碁禍禅稚継腰艇蓄虞虜褐裸触該詰誇詳誉賊賄跡践跳較違遣酬酪鉛鉢鈴隔雷零靴頑頒飾飽鼓豪僕僚暦塾奪嫡寡寧腐彰徴憎慢摘概雌漆漸漬滴漂漫漏獄碑稲端箇維綱緒網罰膜慕誓誘踊遮遭酵酷銃銑銘閥隠需駆駄髪魂錬緯韻影鋭謁閲縁憶穏稼餓壊懐嚇獲穫潟轄憾歓環監緩艦還鑑輝騎儀戯擬犠窮矯響驚凝緊襟謹繰勲薫慶憩鶏鯨撃懸謙賢顕顧稿衡購墾懇鎖錯撮擦暫諮賜璽爵趣儒襲醜獣瞬潤遵償礁衝鐘壌嬢譲醸錠嘱審薪震錘髄澄瀬請籍潜繊薦遷鮮繕礎槽燥藻霜騒贈濯濁諾鍛壇鋳駐懲聴鎮墜締徹撤謄踏騰闘篤曇縄濃覇輩賠薄爆縛繁藩範盤罷避賓頻敷膚譜賦舞覆噴墳憤幣弊壁癖舗穂簿縫褒膨謀墨撲翻摩磨魔繭魅霧黙躍癒諭憂融慰窯謡翼羅頼欄濫履離慮寮療糧隣隷霊麗齢擁露'
}

Kanji2Grade = {}
for a in (1,2,3,4,5,6,'HS'):
    for b in KanjiList_Jouyou[a]:
        Kanji2Grade[b]=a

		



######################################################################
#
#                      JLPT for words
#
######################################################################

import os
import codecs
import cPickle
import itertools

Word2Data = {}
JLPTWordLists={1:0,2:0,3:0,4:0} #utility ?

file = os.path.join(mw.config.configPath, "plugins","JxPlugin","Data", "JLPT.Word.List.csv")
file_pickle = os.path.join(mw.config.configPath, "plugins","JxPlugin","Data", "Word2Data.pickle")

def read_JLPT(file):
	"""Reads JLPT wordlists from file."""
	f = codecs.open(file, "r", "utf8")
	
	def keyfunc(line):
		if line=="\n":
			return False
		else:
			return True
	Html=""
	for key, group in itertools.groupby(f.readlines(), keyfunc):
		if key:
			group=list(group)
			data=[l.rstrip().split("	".decode("utf-8")) for l in group]
			for linol in data:
		            
			    if linol[1] == "":
				Html+= linol[0]+u" "    
			        Word2Data[linol[0].strip(u" ")] = int(linol[4])
		            else:
				Html+= linol[1]+u" "  
			        Word2Data[linol[1].strip(u" ")] = int(linol[4])
			    JLPTWordLists[int(linol[4])] = JLPTWordLists[int(linol[4])] + 1
	f.close()

if (os.path.exists(file_pickle) and 
	os.stat(file_pickle).st_mtime > os.stat(file).st_mtime):
	f = open(file_pickle, 'rb')
	Word2Data = cPickle.load(f)
	f.close()
else:
	read_JLPT(file)
	f = open(file_pickle, 'wb')
	cPickle.dump(Word2Data, f, cPickle.HIGHEST_PROTOCOL)
	f.close()
	
######################################################################
#
#                      Kanken for Kanji
#
######################################################################
Kanji2Kanken = {}

file = os.path.join(mw.config.configPath, "plugins","JxPlugin","Data", "Kanken.csv")

def read_Kanken(file):
	"""Reads Kanken levels from file."""
	f = codecs.open(file, "r", "utf8")
	
	def keyfunc(line):
		if line=="\n":
			return False
		else:
			return True
	for key, group in itertools.groupby(f.readlines(), keyfunc):
		if key:
			group=list(group)
			data=[l.rstrip().split("	".decode("utf-8")) for l in group]
			for linol in data:
			    Kanji2Kanken[linol[0].strip(u" ")] = str(linol[1])
	f.close()

read_Kanken(file)


######################################################################
#
#                      Frequency for Kanji
#
######################################################################
Kanji2Frequency = {}

file = os.path.join(mw.config.configPath, "plugins","JxPlugin","Data", "KanjiFrequencyWikipedia.csv")

def read_Frequency(file):
	"""Reads Kanji frequency from file."""
	f = codecs.open(file, "r", "utf8")
	
	def keyfunc(line):
		if line=="\n":
			return False
		else:
			return True
	for key, group in itertools.groupby(f.readlines(), keyfunc):
		if key:
			group=list(group)
			data=[l.rstrip().split("	".decode("utf-8")) for l in group]
			for linol in data:
			    Kanji2Frequency[linol[0].strip(u" ")] = int(linol[1])
	f.close()

read_Frequency(file)
MaxKanjiOccurences = max(Kanji2Frequency.values())
SumKanjiOccurences = sum(Kanji2Frequency.values())
Kanji2Zone ={}
for (key,value) in Kanji2Frequency.iteritems():
	a= (log(value+1,2)-log(MaxKanjiOccurences+1,2))*10+100
	if a > 62.26: #1/2
		Kanji2Zone[key] = 1
	elif a > 45: #1/5
		Kanji2Zone[key] = 2
	elif a > 30.32: #1/13
		Kanji2Zone[key] = 3
	elif a > 0.6: #1/100
		Kanji2Zone[key] = 4
	else:
		Kanji2Zone[key] = 5
		
######################################################################
#
#                      Frequency for Words
#
######################################################################
{}

file = os.path.join(mw.config.configPath, "plugins","JxPlugin","Data", "CorpusInternet.csv")

def read_Frequency(file,Dict):
	"""Reads Kanji frequency from file."""
	f = codecs.open(file, "r", "utf8")
	
	def keyfunc(line):
		if line=="\n":
			return False
		else:
			return True
	for key, group in itertools.groupby(f.readlines(), keyfunc):
		if key:
			group=list(group)
			data=[l.rstrip().split("	".decode("utf-8")) for l in group]
			for linol in data:
			    Dict[linol[0].strip(u" ")] = int(linol[1])
	f.close()
	return Dict
	
Word2Frequency = read_Frequency(file,{})
SumWordOccurences = sum(Word2Frequency.values())
MaxWordFrequency = max(Word2Frequency.values())
MinWordFrequency = min(Word2Frequency.values())
Word2Zone ={}
for (key,value) in Word2Frequency.iteritems():
	a= (log(value+1,2)-log(MinWordFrequency+1,2))/(log(MaxWordFrequency+1,2)-log(MinWordFrequency+1,2))*100
	if a > 38: #1/2
		Word2Zone[key] = 1
	elif a > 30: #1/5
		Word2Zone[key] = 2
	elif a > 12: #1/13
		Word2Zone[key] = 3
	elif a > 4: #1/100
		Word2Zone[key] = 4
	else:
		Word2Zone[key] = 5

class FileList(dict):
        def __init__(self,From,To,Dict,Order,Tidy = lambda x:x):
                self.From = From
                self.To = To
                self.Dict = Dict
                self.Order = Order
                self.LegendDict = dict(Order)
                self.Tidy = Tidy
                self.Rank = [Value for Key,Value in Order]
        def Legend(self,Key):
                return self.LegendDict[Key]
        def String(self,Stuff):
                return self.LegendDict[self.Dict[self.Tidy(Stuff)]]
        def Value(self,Stuff,Process = lambda x:x):        
                return Process(self.Dict[self.Tidy(Stuff)])
  
def Tango2Dic(string):
	String = string.strip(u" ")
	if String.endswith(u"する") and len(String)>2:
		return String[0:-2]
	elif (String.endswith(u"な") or String.endswith(u"の") or String.endswith(u"に")) and len(String)>1: #python24 fix for OS X                  
#	elif String.endswith((u"な",u"の",u"に")) and len(String)>1:    #python25
		return String[0:-1]
	else:
		return String
               
MapJLPTTango = FileList("Tango","JLPT",Word2Data,[(4,u"4級"),(3,u"3級"),(2,u"2級"),(1,u"1級")],Tidy=Tango2Dic)
MapFreqTango = FileList("Tango","Occurences",Word2Frequency,[],Tidy=Tango2Dic)
MapZoneTango = FileList("Tango","Frequency",Word2Zone,[(1,"Highest"),(2,"High"),(3,"Fair"),(4,"Low"),(5,"Lowest")],Tidy=Tango2Dic)
MapJLPTKanji = FileList("Kanji","JLPT",Kanji2JLPT,[(4,u"4級"),(3,u"3級"),(2,u"2級"),(1,u"1級")])
MapFreqKanji = FileList("Tango","Occurences",Kanji2Frequency,[])
MapZoneKanji = FileList("Kanji","Frequency",Kanji2Zone,[(1,"Highest"),(2,"High"),(3,"Fair"),(4,"Low"),(5,"Lowest")])
MapJouyouKanji = FileList("Kanji","Jouyou",Kanji2Grade,[(1,"G1"),(2,"G2"),(3,"G3"),(4,"G4"),(5,"G5"),(6,"G6"),("HS","HS")])
MapKankenKanji = FileList("Kanji","Kanken",Kanji2Kanken,[('10','10'),('9','9'),('8','8'),('7','7'),('6','6'),('5','5'),('4',"4"),('3',"3"),('2,5',"half 2"),('2',"2"),('1,5',"half 1"),('1',"1")])

