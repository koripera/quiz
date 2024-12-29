#ﾙｰﾃｨﾝｸﾞに必要な要素をargs,funcに記述する
#関数名"func"は変えないこと
#基本はﾌｧｲﾙ名,rule,endpointは同一にすること
#不要要素はｺﾒﾝﾄｱｳﾄすること

#------------------------------#
__all__ = ["args","func"]

args={
"rule"                      : "/add_P",
"methods"                   : ["POST"],
"endpoint"                  : "add_P",
#"strict_slashes"            : ,
#"provide_automatic_options" : ,
#"defaults"                  : ,
}
#------------------------------#

import pickle
import random

from flask import render_template,session,request,redirect,url_for
from core.QUESTION import QUESTION
from core.SCORE import SCORE
from util.tools import get_east_asian_width_count

import contents.__parts as parts

def func():
	#画面下部、問題の一覧を作って表示する

	#出題可能なIDの取得[(ID,chara),(ID,chara)...]
	all_ID = QUESTION.PHRASE.valid_id(tag=session["tag"],inQ=session["inQ"],inC=session["inC"])

	if not all_ID:return "noQuestion"

	QSET10=""

	for i in range(10):
		#ﾛｸﾞｲﾝ時は問題の出題重みを定める
		if "username" in session:
			#10問ﾗﾝﾀﾞﾑで取る[(ID,chara)(ID,chara)...]
			datas = random.choices(all_ID,k=10)

			#2**(10-直近10の正解数)[1024, 512, 256, 128, 64, 32, 16, 8, 4, 2,1] 
			w = [2**(10 - SCORE.result(session["username"],data[0],data[1])[-10:].count(1)) for data in datas]
			data  = random.choices(datas,weights=w)[0]

		else:
			#IDをﾗﾝﾀﾞﾑに選択ID=(ID,chara)
			data = random.choice(all_ID)

		#出題するIDと文字
		ID,chara=data

		Question = QUESTION.PHRASE.get(ID)

		#問題文の置き換え作業
		for c,v in Question["A"].items():
			#問題ﾃﾞｰﾀの問題部以外の置き換え
			if chara!=c:
				Question["Q"] = Question["Q"].replace("{"+c+"}",v)
			#問題部分を整える
			else:
				answer = v		
				width = get_east_asian_width_count(answer)-2
				if width < 2:width=2
				long = "__"*(width//2)
				Question["Q"] = Question["Q"].replace("{"+chara+"}",f"[{long}]")


		QSET10 += render_template(
						'parts/QSET_Phrase.html',
						to_edit   = url_for("edit.phrase",ID=ID),
						about     = f"< {' '.join( Question['about']) } >",
						Q         = Question["Q"],
						A         = "答："+answer,
						C         = Question["C"],
						Q_id      = ID,
						abc       = f"'{chara}'"
						)		

	return QSET10
