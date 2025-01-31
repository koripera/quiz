#ﾙｰﾃｨﾝｸﾞに必要な要素をargs,funcに記述する
#関数名"func"は変えないこと
#基本はﾌｧｲﾙ名,rule,endpointは同一にすること
#不要要素はｺﾒﾝﾄｱｳﾄすること

#------------------------------#
__all__ = ["args","func"]

args={
"rule"                      : "/tagchange/<word>/<link>",
"methods"                   : ["GET"],
"endpoint"                  : "tagchange",
#"strict_slashes"            : ,
#"provide_automatic_options" : ,
#"defaults"                  : ,
}
#------------------------------#

from flask import render_template,session,request,redirect,url_for
import contents.__parts as parts

def func(word,link):
	session["inQ"]=""
	session["inC"]=""
	session["tag"]=[word,]
	return redirect(url_for(link))

