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
			w = [3**(10 - SCORE.result(session["username"],data[0],data[1])[-10:].count(1)) for data in datas]
			data  = random.choices(datas,weights=w)[0]

		else:
			#IDをﾗﾝﾀﾞﾑに選択ID=(ID,chara)
			data = random.choice(all_ID)

		#
		QSET10 += QUESTION.PHRASE.to_html(*data)

	return QSET10
