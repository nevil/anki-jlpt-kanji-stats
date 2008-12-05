#-*- coding: utf-8 -*-

"""
DESCRIPTION:
Displays your % complete for each JLPT level.  If the kanji fact exists in your deck but it is unseen, it will still be counted.  Feel free to modify the SQL to chane it to only seen cards.  If you do, please post your changes back to the anki wiki.  Thanks.

INSTALLATION:
Put this in your .anki/plugins directory, and add "jlpt_prog_kanji" to the features field of the kanji field of your kanji model.  For example, I have a model named "Kanji" that has a field called "character" which contains a single kanji character.  Therefore, I add "jlpt_prog_kanji" to the features of field "character" for the "Kanji" model.

NOTES:
It is expected that there is only 1 character (ie. the kanji) in the kanji field that you added "jlpt_prog_kanji" to, with no duplicates.

AUTHOR:
flight16
"""

import os
import traceback
import sys
import unicodedata

from PyQt4 import QtGui, QtCore
from ankiqt import mw, ui

# This must be in the kanji field for this plugin to work.
FEATURE_FIELD = "jlpt_prog_kanji"

def init_hook():
  """
  Initialises the Anki GUI to present an option to invoke the plugin.
  """
  mw.mainWin.action_jlpt_stats = QtGui.QAction('Toggle JLPT Kanji Stats', mw)
  mw.mainWin.action_jlpt_stats.setStatusTip('Toggle JLPT Kanji Stats')
  mw.mainWin.action_jlpt_stats.setEnabled(True)
  mw.connect(mw.mainWin.action_jlpt_stats, QtCore.SIGNAL('triggered()'), slot_sync)

  mw.mainWin.menuPlugins.addAction(mw.mainWin.action_jlpt_stats)

def get_deck_kanji():
  kanji_field_model_id = mw.deck.s.scalar("select id from fieldModels where features like :feature", feature='%' + FEATURE_FIELD + '%')
  kanjis = mw.deck.s.column0("select value from fields where fieldModelId = :fmi", fmi=kanji_field_model_id)
  return kanjis

def is_kanji(unichar):
  try:
    return unicodedata.name(unichar).find('CJK UNIFIED IDEOGRAPH') >= 0
  except ValueError:
    # a control character
    return False

def make_stats():
  kanjis = get_deck_kanji()
 
  jlptMap = [
    {
      'kanji':      get_jlpt1_kanjis(),
      'all_count':  -1,
      'seen_count': 0,
      'missing':    get_jlpt1_kanjis()
    },
    {
      'kanji':      get_jlpt2_kanjis(),
      'all_count':  -1,
      'seen_count': 0,
      'missing':    get_jlpt2_kanjis()
    },
    {
      'kanji':      get_jlpt3_kanjis(),
      'all_count':  -1,
      'seen_count': 0,
      'missing':    get_jlpt3_kanjis()
    },
    {
      'kanji':      get_jlpt4_kanjis(),
      'all_count':  -1,
      'seen_count': 0,
      'missing':    get_jlpt4_kanjis()
    }
  ]

  # Count totals.
  for i in range(4): jlptMap[i]['all_count'] = len(jlptMap[i]['kanji']) 

  # Count the kanji in our deck.
  for el in kanjis:
    for k in el:
      if is_kanji(k):
        for i in range(4):
          if (k in jlptMap[i]['kanji']) and (k in jlptMap[i]['missing']):
            idx = jlptMap[i]['missing'].index(k)
            jlptMap[i]['missing'] = jlptMap[i]['missing'][0 : idx] + jlptMap[i]['missing'][idx + 1:]
            jlptMap[i]['seen_count'] += 1

  # Build a substitution map for the stats HTML
  sub_map = {}
  for i in range(4):
    sub_map['lvl' + str(i+1) + '_t'] = jlptMap[i]['all_count']  # Total kanji in this level
    sub_map['lvl' + str(i+1) + '_s'] = jlptMap[i]['seen_count'] # Total kanji in this level in our deck.
    sub_map['lvl' + str(i+1) + '_p'] = round(jlptMap[i]['seen_count'] * 100.0 / jlptMap[i]['all_count'],2)
    sub_map['lvl' + str(i+1) + '_m'] = jlptMap[i]['missing'] # Missing kanji in this level

  stats ="""
<center> <h2>JLPT Progress</h2> </center>

<hr/>

<table width="100%%">
<tr><td></td><td><b>Kanji</b></td><td><b>Percent</b></td></tr>
<tr><td><b>Level 4</b></td><td>%(lvl4_s)s / %(lvl4_t)s</td><td>%(lvl4_p)s%%</td></tr>
<tr><td><b>Level 3</b></td><td>%(lvl3_s)s / %(lvl3_t)s</td><td>%(lvl3_p)s%%</td></tr>
<tr><td><b>Level 2</b></td><td>%(lvl2_s)s / %(lvl2_t)s</td><td>%(lvl2_p)s%%</td></tr>
<tr><td><b>Level 1</b></td><td>%(lvl1_s)s / %(lvl1_t)s</td><td>%(lvl1_p)s%%</td></tr>
</table>
""" % sub_map

  stats += """
<hr/>
<table width="100%%">
<tr><td></td><td><b>Missing Kanji</b></td></tr>
<tr><td><b>Level 4</b></td><td>%(lvl4_m)s</td></tr>
<tr><td><b>Level 3</b></td><td>%(lvl3_m)s</td></tr>
<tr><td><b>Level 2</b></td><td>%(lvl2_m)s</td></tr>
<tr><td><b>Level 1</b></td><td>%(lvl1_m)s</td></tr>
</table>
""" % sub_map

  return stats

def slot_sync():
  text = make_stats();
  mw.help.showText(text)

def get_jlpt4_kanjis():
  return '一七万三上下中九二五人今休会何先入八六円出分前北十千午半南友口古右名四国土外多大天女子学安小少山川左年店後手新日時書月木本来東校母毎気水火父生男白百目社空立耳聞花行西見言話語読買足車週道金長間雨電食飲駅高魚'.decode("utf-8")

def get_jlpt3_kanjis():
  return '不世主乗事京仕代以低住体作使便借働元兄光写冬切別力勉動区医去台合同味品員問回図地堂場声売夏夕夜太好妹姉始字室家寒屋工市帰広度建引弟弱強待心思急悪意所持教文料方旅族早明映春昼暑暗曜有服朝村林森業楽歌止正歩死民池注洋洗海漢牛物特犬理産用田町画界病発県真着知短研私秋究答紙終習考者肉自色英茶菜薬親計試説貸質赤走起転軽近送通進運遠都重野銀門開院集青音頭題顔風飯館首験鳥黒'.decode("utf-8")

def get_jlpt2_kanjis():
  return '腕湾和論録老労路連練恋列歴齢零礼冷例令類涙輪緑領量良療涼両了粒留流略率律陸裏利卵乱落絡頼翌浴欲陽踊要葉溶様容幼預与余予郵遊由勇優輸油約役戻毛面綿鳴迷命娘無夢務眠未満末枚埋磨防貿棒望暴忙忘帽坊亡豊訪法放抱宝報包暮募補捕保返辺編片変壁米閉並平兵粉仏沸払複腹福幅復副封部舞武負膚符浮普怖府布富婦夫付貧秒評表氷標筆必匹鼻美備飛非費被皮疲比批悲彼否番晩販般犯版板反判抜髪畑肌箱麦爆薄泊倍配背杯敗拝馬破波農脳能濃悩燃念熱猫認任乳難軟内鈍曇届突独毒得銅童導逃到筒等当灯湯盗投島塔凍党倒怒努途登渡徒塗殿伝点展鉄適的滴泥程庭底定停痛追賃珍沈直頂超調張庁兆貯著駐虫柱宙仲竹畜築遅置恥値談段暖断団炭探担単谷達濯宅第退袋替帯対打他損尊孫存卒続速測束息則側造贈蔵臓憎増像装草総窓相争燥操掃捜想層双組祖全然善選船線浅泉戦専占絶雪節設折接責績積石昔席税静製精清晴星整政成性姓勢制数吹震針辛身臣神申深寝信伸触職植蒸畳状条情常城賞象紹笑章省照焼消昇招承床将商召勝除助諸署緒初処順純準述術祝宿柔舟拾修州周収授受酒種守取若捨実湿失識式辞示治次寺児似歯資誌詞脂糸枝支指志師史司刺伺残賛算散参皿雑殺札察刷冊昨咲坂財罪材在際細祭済歳採才妻最再座砂査差混根婚困込骨腰告刻号香降鉱郊講荒航肯耕紅硬港構更康幸向厚効公候交誤御互雇湖枯故戸庫固呼個限現減原険軒賢肩権検券健件血結決欠劇迎芸警経景敬恵形型傾係軍群訓君靴掘隅偶具苦禁均勤玉極曲局胸狭況橋挟恐境叫協共競供漁許巨居旧給級球泣求救吸久逆客詰喫議疑技記規季祈機期机希寄基器喜危願岩岸含丸関観簡管看甘環汗換慣感干官完巻刊乾活割額革較角覚確格拡各害貝階絵皆灰械改快解介過貨課菓荷河果科可加価仮化温億黄王欧横押応奥央汚塩煙演延園越液鋭泳永栄営雲羽宇因印育域違衣胃移異易委囲偉依位案圧愛'.decode("utf-8")

def get_jlpt1_kanjis():
  return '乙丁刀又勺士及己丈乏寸凡刃弓斤匁氏井仁丹幻凶刈冗弔斗尺屯孔升厄丙且弁功甲仙句巡矢穴丘玄巧矛汁尼迅奴囚凸凹斥弐吏企邦江吉刑充至芝扱旬旨尽缶仰后伏劣朴壮吐如匠妃朱伐舌羊朽帆妄芋沢佐攻系抗迫我抑択秀尾伴邸沖却災孝戒杉里妥肝妙序即寿励芳克没妊豆狂岐廷妨亜把呈尿忍呉伯扶忌肖迭吟汽坑抄壱但松郎房拠拒枠併析宗典祉免忠沿舎抵茂斉炎阻岳拘卓炉牧奇拍往屈径抽披沼肥拐拓尚征邪殴奉怪佳昆芽苗垂宜盲弦炊枢坪泡肪奔享拙侍叔岬侮抹茎劾泌肢附派施姿宣昭皇紀削為染契郡挑促俊侵括透津是奏威柄柳孤牲帝耐恒冒胞浄肺貞胆悔盾軌荘冠卸垣架砕俗洞亭赴盆疫訂怠哀臭洪狩糾峡厘胎窃恨峠叙逓甚姻幽卑帥逝拷某勅衷逐侯弧朕耗挙宮株核討従振浜素益逮陣秘致射貢浦称納紛託敏郷既華哲症倉索俳剤陥兼脅竜梅桜砲祥秩唆泰剣倫殊朗烈悟恩陛衰准浸虐徐脈俵栽浪紋逸隻鬼姫剛疾班宰娠桑飢郭宴珠唐恭悦粋辱桃扇娯俸峰紡胴挿剖唇匿畔翁殉租桟蚊栓宵酌蚕畝倣倹視票渉推崎盛崩脱患執密措描掲控渋掛排訳訟釈隆唱麻斎貫偽脚彩堀菊唯猛陳偏遇陰啓粘遂培淡剰虚帳惨据勘添斜涯眼瓶彫釣粛庶菌巣廊寂酔惜悼累陶粗蛇眺陵舶窒紳旋紺遍猟偵喝豚赦殻陪悠淑笛渇崇曹尉蛍庸渓堕婆脹痘統策提裁証援訴衆隊就塁遣雄廃創筋葬惑博弾塚項喪街属揮貴焦握診裂裕堅賀揺喚距圏軸絞棋揚雰殖随尋棟搭詐紫欺粧滋煮疎琴棚晶堤傍傘循幾掌渦猶慌款敢扉硫媒暁堪酢愉塀閑詠痢婿硝棺詔惰蛮塑虞幹義督催盟献債源継載幕傷鈴棄跡慎携誉勧滞微誠聖詳雅飾詩嫌滅滑頑蓄誇賄墓寛隔暇飼艇奨滝雷酬愚遭稚践嫁嘆碁漠該痴搬虜鉛跳僧溝睡猿摂飽鼓裸塊腸慈遮慨鉢禅絹傑禍酪賊搾廉煩愁楼褐頒嗣銑箇遵態閣摘維遺模僚障徴需端奪誘銭銃駆稲綱閥隠徳豪旗網酸罰腐僕塾漏彰概慢銘漫墜漂駄獄誓酷墨磁寧穀魂暦碑膜漬酵遷雌漆寡慕漸嫡謁賦監審影撃請緊踏儀避締撤盤養還慮緩徹衝撮誕歓縄範暫趣慰潟敵魅敷潮賠摩輝稼噴撲縁慶潜黙輩稿舗熟霊諾勲潔履憂潤穂賓寮澄弊餓窮幣槽墳閲憤戯嘱鋳窯褒罷賜錘墾衛融憲激壊興獲樹薦隣繁擁鋼縦膨憶諮謀壌緯諭糖懐壇奮穏謡憾凝獣縫憩錯縛衡薫濁錠篤隷嬢儒薪錬爵鮮厳聴償縮購謝懇犠翼繊擦覧謙頻轄鍛礁擬謹醜矯嚇霜謄濫離織臨闘騒礎鎖瞬懲糧覆翻顕鎮穫癒騎藩癖襟繕繭璽繰瀬覇簿鯨鏡髄霧麗羅鶏譜藻韻護響懸籍譲騰欄鐘醸躍露顧艦魔襲驚鑑'.decode("utf-8")



if __name__ == "__main__":
  print "Don't run me.  I'm a plugin"

else:  
  mw.addHook('init', init_hook)
  print 'jlpt AHAS progress plugin loaded'

