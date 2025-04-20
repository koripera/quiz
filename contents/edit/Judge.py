#ﾙｰﾃｨﾝｸﾞに必要な要素をargs,funcに記述する
#関数名"func"は変えないこと
#基本はﾌｧｲﾙ名,rule,endpointは同一にすること
#不要要素はｺﾒﾝﾄｱｳﾄすること

#------------------------------#
__all__ = ["args","func"]

args={
"rule"                      : "/judge/<ID>",
"methods"                   : ["GET","POST"],
"endpoint"                  : "judge",
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
		return Edit_J_get(ID)
	if request.method == 'POST':
		return Edit_J_post(ID)

def Edit_J_get(ID):
	if ID == "new":#新規ﾃﾞｰﾀ
		page = render_template(
			'Edit_Judge.html',
			headlinks = parts.headlink()
		)

		return page

	elif ID == "list":
		pass
	
	else:#既存ﾃﾞｰﾀの表示
		#問題の辞書ﾃﾞｰﾀ取得
		Question = QUESTION.JUDGE.get(ID)

		#該当IDがなければ、404ｴﾗｰ
		if Question==None:return "nopage",404		
		
		result_html = render_template(
			'Edit_Judge.html',
			headlinks = parts.headlink(),
			about     = ",".join(Question["about"]),
			title     = Question["name"],
			tag       = ",".join(Question["tag"]),
			Q         = Question["Q"],
			ans       = Question["A"],
			comment   = Question["C"],
		)

		return result_html

def Edit_J_post(ID):
	if request.form.get("addnew") != None:
		#新ﾃﾞｰﾀ追加後、その編集ﾍﾟｰｼﾞへ移動
		ID = QUESTION.JUDGE.make(request)
		return redirect(url_for("edit.judge",ID=ID))

	elif request.form.get("update") != None:
		#ﾃﾞｰﾀの更新後、その編集ﾍﾟｰｼﾞに移動
		QUESTION.JUDGE.update(ID,request)
		return redirect(url_for("edit.judge",ID=ID))

	elif request.form.get("delete") != None:
		#ﾃﾞｰﾀ削除後、新規作成ﾍﾟｰｼﾞに移動			
		QUESTION.JUDGE.delete(ID)
		return redirect(url_for("edit.judge",ID="new"))

def datalist():
	pass
