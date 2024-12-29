#ﾙｰﾃｨﾝｸﾞに必要な要素をargs,funcに記述する
#関数名"func"は変えないこと
#基本はﾌｧｲﾙ名,rule,endpointは同一にすること
#不要要素はｺﾒﾝﾄｱｳﾄすること

#------------------------------#
__all__ = ["args","func"]

args={
"rule"                      : "/set_search/<ID>",
"methods"                   : ["POST"],
"endpoint"                  : "set_search",
#"strict_slashes"            : ,
#"provide_automatic_options" : ,
#"defaults"                  : ,
}
#------------------------------#

from flask import render_template,session,request,redirect,url_for
def func(ID):
	session["tag"]=request.form.get("tag").split()
	session["inQ"]=request.form.get("inQ")
	session["inC"]=request.form.get("inC")
	if ID=="J":
		return redirect(url_for("infiniteQ_Judge"))
	if ID=="P":
		return redirect(url_for("infiniteQ_Phrase"))
