#ﾙｰﾃｨﾝｸﾞに必要な要素をargs,funcに記述する
#関数名"func"は変えないこと
#基本はﾌｧｲﾙ名,rule,endpointは同一にすること
#不要要素はｺﾒﾝﾄｱｳﾄすること

#------------------------------#
__all__ = ["args","func"]

args={
"rule"                      : "/check_J",
"methods"                   : ["POST"],
"endpoint"                  : "check_J",
#"strict_slashes"            : ,
#"provide_automatic_options" : ,
#"defaults"                  : ,
}
#------------------------------#

from flask import render_template, session, request

from core.QUESTION import QUESTION
from core.SCORE import SCORE

def func():
	#答え合わせを行う#jsonを受け取り、jsonを返す
	#Qid,num,answerを受け取る#inputDataはdict
	QID    = int(request.json["Qid"])#pathに使用するID
	num    = int(request.json["num"])#1問題中のﾗﾝﾀﾞﾑ
	answer = 1 if request.json["answer"]=="〇" else 0 #押したﾎﾞﾀﾝ

	#問題ﾃﾞｰﾀの取得
	Qdata = QUESTION.JUDGE.get(QID)
	ans   = 1 if Qdata["A"][num][1]=="o" else 0
	A      = "〇を押しました" if answer else "×を押しました"
	result = "<font color='red'>正解</font>" if ans==answer else "<font color='blue'>不正解</font>"

	ret = {
		"result1" : A,
		"result2" : result,
		"Comment" : f"{Qdata['C']}\n\ntag:{','.join(Qdata['tag'])}"
	}

	#回答を記録
	if "username" in session:
		SCORE.insert(session['username'],QID,None,1 if ans==answer else 0)
		ret["logg"] = "".join(["〇" if e else "×" for e in SCORE.result(session['username'],QID,None)])

	else:
		ret["logg"] = ""

	return ret
