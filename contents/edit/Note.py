#ﾙｰﾃｨﾝｸﾞに必要な要素をargs,funcに記述する
#関数名"func"は変えないこと
#基本はﾌｧｲﾙ名,rule,endpointは同一にすること
#不要要素はｺﾒﾝﾄｱｳﾄすること

#------------------------------#
__all__ = ["args","func"]

args={
"rule"                      : "/note/<ID>",
"methods"                   : ["GET","POST"],
"endpoint"                  : "note",
#"strict_slashes"            : ,
#"provide_automatic_options" : ,
#"defaults"                  : ,
}
#------------------------------#

from flask import render_template,session,request,redirect,url_for
import markdown

from core.QUESTION import QUESTION
from core.NOTE import NOTE

import contents.__parts as parts

def func(ID):
	if request.method == 'GET':
		return Edit_note_get(ID)
	if request.method == 'POST':
		return Edit_note_post(ID)

def Edit_note_get(ID):

	md = markdown.Markdown(extensions=["fenced_code","tables"])

	if ID == "new":#新規ﾃﾞｰﾀ
		page = render_template(
			'Edit_Note.html',
		)

		return page

	elif ID == "list":
		pass
	
	else:#既存ﾃﾞｰﾀの表示
		#noteの辞書ﾃﾞｰﾀ取得
		data = NOTE.get(ID)

		#該当IDがなければ、404ｴﾗｰ
		if data==None:return "nopage",404

		#noteの内容をhtmlに変換
		content = md.convert(data["content"])

		if False:#javascript側で呼び出す
			#ﾀｲﾄﾙが含まれる問題を取得する
			all_ID_J = QUESTION.JUDGE.valid_id(inC="{"+data["name"]+"}")
			all_ID_P = QUESTION.PHRASE.valid_id(inC="{"+data["name"]+"}")

			#出題可能な問題がなければ、処理しない
			if not all_ID_J + all_ID_P:
				question = "noQuestion"
			else:
				question=""
				for e in all_ID_J:
					question+=QUESTION.JUDGE.to_html(e[0])
				for e in all_ID_P:
					question+=QUESTION.PHRASE.to_html(e[0],e[1])

		#表示用のデータを作成する
		data["converted_content"]=NOTE.replace_comment(md.convert(data["content"]),set([data["name"]]))

		#内容の表示
		result_html = render_template(
			'Edit_Note.html',
			title     = data["name"],
			tag       = ",".join(data["tag"]),
			content   = data["content"],
			body      = data["converted_content"],
			#question  = question,
		)

		return result_html

def Edit_note_post(ID):
	if request.form.get("addnew") != None:
		#新ﾃﾞｰﾀ追加後、その編集ﾍﾟｰｼﾞへ移動
		ID = NOTE.make(request)
		return redirect(url_for("edit.note",ID=ID))

	elif request.form.get("update") != None:
		#ﾃﾞｰﾀの更新後、その編集ﾍﾟｰｼﾞに移動
		NOTE.update(ID,request)
		return redirect(url_for("edit.note",ID=ID))

	elif request.form.get("delete") != None:
		#ﾃﾞｰﾀ削除後、新規作成ﾍﾟｰｼﾞに移動			
		NOTE.delete(ID)
		return redirect(url_for("edit.note",ID="new"))

def datalist():
	pass
