#ﾙｰﾃｨﾝｸﾞに必要な要素をargs,funcに記述する
#関数名"func"は変えないこと
#基本はﾌｧｲﾙ名,rule,endpointは同一にすること
#不要要素はｺﾒﾝﾄｱｳﾄすること

#------------------------------#
__all__ = ["args","func"]

args={
"rule"                      : "/phrase/<ID>",
"methods"                   : ["GET","POST"],
"endpoint"                  : "phrase",
#"strict_slashes"            : ,
#"provide_automatic_options" : ,
#"defaults"                  : ,
}
#------------------------------#

from flask import render_template,session,request,redirect,url_for
from core.QUESTION import QUESTION

import contents.__parts as parts

def func(ID):
	if request.method == 'GET':
		return Edit_P_get(ID)
	if request.method == 'POST':
		return Edit_P_post(ID)


def Edit_P_get(ID):
	if ID == "new":#新規ﾃﾞｰﾀ
		page = render_template(
			'Edit_Phrase.html',
			headlinks = parts.headlink(),
		)

		return page
	
	else:#既存ﾃﾞｰﾀの表示
		#問題の辞書ﾃﾞｰﾀ取得
		Question = QUESTION.PHRASE.get(ID)			

		"""
		log = {}
		#ﾛｸﾞｲﾝ時回答履歴を編集可能にする
		if "username" in session:
			for chara,answer in Question["A"].items():	
				data = QUESTION.PHRASE.SCORE.get(session["username"],(ID,chara))
				log[f"log{chara}"] = "".join(["〇" if e else "×" for e in data])
		"""
		
		result_html = render_template(
			'/Edit_Phrase.html',
			headlinks = parts.headlink(),
			about   = ",".join(Question["about"]),
			title   = Question["name"],
			tag     = ",".join(Question["tag"]),
			Q       = Question["Q"],
			comment = Question["C"],
			**Question["A"],#{"A":ans1,"B":ans2,"C":ans3}									
		)
		return result_html
def Edit_P_post(ID):
	if request.form.get("addnew") != None:
		#新ﾃﾞｰﾀ追加後、その編集ﾍﾟｰｼﾞへ移動
		ID = QUESTION.PHRASE.make(request)
		return redirect(url_for("edit.phrase",ID=ID))

	elif request.form.get("update") != None:
		#ﾃﾞｰﾀの更新後、その編集ﾍﾟｰｼﾞに移動
		QUESTION.PHRASE.update(ID,request)
		return redirect(url_for("edit.phrase",ID=ID))

	elif request.form.get("delete") != None:
		#ﾃﾞｰﾀ削除後、新規作成ﾍﾟｰｼﾞに移動			
		QUESTION.PHRASE.delete(ID)
		return redirect(url_for("edit.phrase",ID="new"))


