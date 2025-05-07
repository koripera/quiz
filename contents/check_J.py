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

import re
from textwrap import dedent

from flask import (
	render_template,
	session,
	request,
	url_for,
)
import markdown

from core.QUESTION import QUESTION
from core.SCORE import SCORE
from core.NOTE import NOTE

from libs.DATABASE import DB
from setting import DB_PATH

DB.dbname=DB_PATH

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


	#ﾀｸﾞをﾘﾝｸにして、変更を簡易にする
	tags_html=""
	for tagname in Qdata["tag"]:
		link = url_for('tagchange',word = tagname,link="infiniteQ_Judge")
		tags_html += f"""<a class="tag" href="{link}"> {tagname} </a>"""	

	ret = {
		"result1" : A,
		"result2" : result,
		"Comment" : f"{Qdata['C']}\n\ntag:{tags_html}"
	}

	ret["Comment"] = replace_comment(ret["Comment"])

	#回答を記録
	if "username" in session:
		res = SCORE.insert(session['username'],QID,None,1 if ans==answer else 0)
		ret["logg"] = "".join(["〇" if e else "×" for e in res])

	else:
		ret["logg"] = ""



	return ret


def replace_comment(txt):
	#ﾉｰﾄからtxt
	md = markdown.Markdown(extensions=["fenced_code","tables"])

	#ﾉｰﾄを検索
	for name in re.findall(r"{(.*?)}", txt):
		q=dedent(
		f"""
		SELECT id 
		FROM note
		WHERE name = "{name}"
		""")

		#ﾉｰﾄIDを取得
		with DB().connect as d:
			conn,cur = d
			res = cur.execute(q)
			ID = res.fetchone()

		#ﾌﾟﾚｰｽﾎﾙﾀﾞの置き換え
		if ID!=None:
			ID=ID[0]
			data = NOTE.get(ID)
			content = md.convert(data["content"])

			txt = txt.replace("}\n","}")
			txt = re.sub("\n*?{", lambda _: "{", txt)

			content =dedent(
			f"""
			<div class='quote'>
			<details open>
			<summary>{name}</summary>
			<div class='quote_content'>{content}</div>	
			</details>
			</div>
			""")

			content = txt.replace(
				"{"+name+"}",
				content,
			).strip()
			txt = content

	return txt

			
