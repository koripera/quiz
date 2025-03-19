#ﾙｰﾃｨﾝｸﾞに必要な要素をargs,funcに記述する
#関数名"func"は変えないこと
#基本はﾌｧｲﾙ名,rule,endpointは同一にすること
#不要要素はｺﾒﾝﾄｱｳﾄすること

#------------------------------#
__all__ = ["args","func"]

args={
"rule"                      : "/note_search",
"methods"                   : ["POST"],
"endpoint"                  : "note_search",
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
from core.NOTE import NOTE

def func():
	data = request.get_json()
	query1 = data.get('query1', '').split()
	query2 = data.get('query2', '')

	match = {e[0] for e in NOTE.valid_id(tag=query1,search=query2)}
	nomatch = {e[0] for e in NOTE.valid_id() if e[0] not in match}
	
	data = {
		"__match":list(match),
		"__nomatch":list(nomatch),
	}

	for ID in chain(match,nomatch):
		data[ID]={
			"url":url_for("edit.note",ID=ID),
			"name":NOTE.get(ID)["name"]
		}

	return jsonify(data)


