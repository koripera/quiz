#ﾙｰﾃｨﾝｸﾞに必要な要素をargs,funcに記述する
#関数名"func"は変えないこと
#基本はﾌｧｲﾙ名,rule,endpointは同一にすること
#不要要素はｺﾒﾝﾄｱｳﾄすること

#------------------------------#
__all__ = ["args","func"]

args={
"rule"                      : "/load_P",
"methods"                   : ["POST"],
"endpoint"                  : "load_P",
#"strict_slashes"            : ,
#"provide_automatic_options" : ,
#"defaults"                  : ,
}
#------------------------------#

#phrase問題の折りたたみ部の生成をして、htmlを返す

import re
from textwrap import dedent

from flask import render_template,session,request,redirect,url_for
import markdown

from libs.DATABASE import DB
from setting import DB_PATH
from core.NOTE import NOTE
import contents.__parts as parts
from core.QUESTION import QUESTION


def func():
	data = request.get_json()
	ID = int(data.get('id', ''))
	chara = data.get('chara', '')

	Question = QUESTION.PHRASE.get(ID)

	#ﾀｸﾞをﾘﾝｸにして、変更を簡易にする
	tags_html="\n\ntag:"
	for tagname in Question["tag"]:
		link = url_for('tagchange',word = tagname,link="infiniteQ_Phrase")
		tags_html += f"""<a class="tag" href="{link}"> {tagname} </a>"""

	answer=Question["A"][chara]

	#ﾉｰﾄからの引用をできるように・・・
	md = markdown.Markdown(extensions=["fenced_code","tables"])
	for name in re.findall(r"{(.*?)}", Question["C"]):
		q=dedent(
		f"""
		SELECT id 
		FROM note
		WHERE name = "{name}"
		""")

		with DB().connect as d:
			conn,cur = d
			res = cur.execute(q)
			NID = res.fetchone()

		if NID!=None:
			NID=NID[0]
			data = NOTE.get(NID)
			content = data["converted_content"]

			Question["C"] = Question["C"].replace("{"+name+"}\n","{"+name+"}")
			Question["C"] = re.sub("\n*?{", lambda _: "{", Question["C"])

			content =dedent(
			f"""
			<div class='quote'>
			<details>
			<summary>{name}</summary>
			<div class='quote_content'>{content}</div>	
			</details>
			</div>
			""")

			Question["C"] = Question["C"].replace(
				"{"+name+"}",
				content,
			).strip()
	

	html=render_template(
		"parts/QSET_Phrase_details.html",
		to_edit   = url_for("edit.phrase",ID=ID),
		A         = "答："+answer,
		C         = Question["C"]+tags_html,
		Q_id      = ID,
		abc       = f"{chara}"
	)

	return html


