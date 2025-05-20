#ﾙｰﾃｨﾝｸﾞに必要な要素をargs,funcに記述する
#関数名"func"は変えないこと
#基本はﾌｧｲﾙ名,rule,endpointは同一にすること
#不要要素はｺﾒﾝﾄｱｳﾄすること

#------------------------------#
__all__ = ["args","func"]

args={
"rule"                      : "/infiniteQ_Judge",
"methods"                   : ["GET"],
"endpoint"                  : "infiniteQ_Judge",
#"strict_slashes"            : ,
#"provide_automatic_options" : ,
#"defaults"                  : ,
}
#------------------------------#

from flask import render_template, session
import contents.__parts as parts

def func():
	#ﾍﾟｰｼﾞ内で使うので、ｾｯﾃｨﾝｸﾞ
	if "inQ" not in session:session["inQ"]=""
	if "inC" not in session:session["inC"]=""
	if "tag" not in session:session["tag"]=[]

	page = render_template(
		'infiniteQ_Judge.html',
		mode="J",
		headlinks = parts.headlink(),
		tag=" ".join(session["tag"]),
		inQ=session["inQ"],
		inC=session["inC"],
	)

	return page
