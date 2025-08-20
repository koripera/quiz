#ﾙｰﾃｨﾝｸﾞに必要な要素をargs,funcに記述する
#関数名"func"は変えないこと
#基本はﾌｧｲﾙ名,rule,endpointは同一にすること
#不要要素はｺﾒﾝﾄｱｳﾄすること

#------------------------------#
__all__ = ["args","func"]

args={
"rule"                      : "/check_P",
"methods"                   : ["GET","POST"],
"endpoint"                  : "check_P",
#"strict_slashes"            : ,
#"provide_automatic_options" : ,
#"defaults"                  : ,
}
#------------------------------#

from flask import render_template,session,request,redirect,url_for

from core.QUESTION import QUESTION
from core.TAG import TAG
from core.SCORE import SCORE
from core.PROGRESS import PROGRESS

def func():
	inputData = request.json

	#Qid,abc,answerを受け取る
	QID    = int(inputData["Qid"])#pathに使用するID
	abc    = inputData["abc"]     #問題中の出題箇所
	answer = inputData["answer"]  #自己申告の○×

	#ﾛｸﾞｲﾝ状態
	if "username" in session:
		SCORE.insert(session['username'],QID,abc,1 if answer=="〇" else 0)
		tagnamelist = QUESTION.PHRASE.get(QID)["tag"]

		log = "".join(["〇" if e else "×" for e in SCORE.result(session['username'],QID,abc)])

		#進捗への反映
		for name in tagnamelist:
			ID=TAG.name_to_id(name)
			#print(session['username'],"tag",ID,log[-10:].count("〇"))
			PROGRESS.update(session['username'],"tag",ID,log[-10:].count("〇"))

		return {"log":log}

	#ﾛｸﾞｱｳﾄ状態
	else:
		return {"log":""}




