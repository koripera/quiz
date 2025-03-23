#ﾙｰﾃｨﾝｸﾞに必要な要素をargs,funcに記述する
#関数名"func"は変えないこと
#基本はﾌｧｲﾙ名,rule,endpointは同一にすること
#不要要素はｺﾒﾝﾄｱｳﾄすること

#------------------------------#
__all__ = ["args","func"]

args={
"rule"                      : "/judge_search",
"methods"                   : ["POST"],
"endpoint"                  : "judge_search",
#"strict_slashes"            : ,
#"provide_automatic_options" : ,
#"defaults"                  : ,
}
#------------------------------#

from itertools import chain
from flask import (
	render_template,
	session,
	request,
	redirect,
	url_for,
	jsonify,
)
import contents.__parts as parts
from core.QUESTION import QUESTION

def func():
	data = request.get_json()
	query1 = data.get('query1', '').split()
	query2 = data.get('query2', '')
	query3 = data.get('query3', '')

	session["inQ"]=query2
	session["inC"]=query3
	session["tag"]=query1

	match = {e[0] for e in QUESTION.JUDGE.valid_id(tag=query1,inQ=query2,inC=query3)}
	
	data = {
		"match":list(match),
	}

	return jsonify(data)


