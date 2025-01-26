#ﾙｰﾃｨﾝｸﾞに必要な要素をargs,funcに記述する
#関数名"func"は変えないこと
#基本はﾌｧｲﾙ名,rule,endpointは同一にすること
#不要要素はｺﾒﾝﾄｱｳﾄすること

#------------------------------#
__all__ = ["args","func"]

args={
"rule"                      : "/add_J",
"methods"                   : ["POST"],
"endpoint"                  : "add_J",
#"strict_slashes"            : ,
#"provide_automatic_options" : ,
#"defaults"                  : ,
}
#------------------------------#

from flask import render_template,session,request,redirect,url_for

import pickle
import random
from core.QUESTION import QUESTION
from core.SCORE import SCORE

def func():
	#問題の追加を行う
	#session inQ,inCは出題ﾍﾟｰｼﾞ遷移時にﾃﾞﾌｫﾙﾄ設定	

	#出題可能なIDの取得[ID,ID...]
	all_ID = QUESTION.JUDGE.valid_id(tag=session["tag"],inQ=session["inQ"],inC=session["inC"])

	#出題可能な問題がなければ、処理しない
	if not all_ID:return "noQuestion"

	#画面下部、問題の一覧を作って表示する
	QSET10=""

	for i in range(10):		
		if "username" in session:
			#10問ﾗﾝﾀﾞﾑで取る[ID,ID...]
			IDs = random.choices(all_ID,k=10)

			#2**(10-直近10の正解数)[1024, 512, 256, 128, 64, 32, 16, 8, 4, 2, 1]
			#3[59049,19683,6561,2187,729,243,81,27,9,3,1]
			w = [3**(10 - SCORE.result(session["username"],ID[0],None)[-10:].count(1)) for ID in IDs]

			#choicesはﾘｽﾄで返る
			ID  = random.choices(IDs,weights=w)[0]

		else:
			ID = random.choice(all_ID)
	
		#問題ﾃﾞｰﾀの取得
		Question = QUESTION.JUDGE.get(ID[0])

		#問題ﾃﾞｰﾀの一部の置き換え
		num = random.randrange(len(Question["A"]))
		Q_txt = Question["Q"].replace("{x}",Question["A"][num][0])

		#ID,部分変換のindex,問題文等をHTMLに記入
		QSET10 += render_template(
			'parts/QSET_Judge.html',
			to_edit       = url_for("edit.judge",ID=ID[0]),
			Q_id          = ID[0],
			Q_num         = num,
			about         = f"< {' '.join(Question['about'])} >",
			Q_txt         = Q_txt,								  
		)

	return QSET10
