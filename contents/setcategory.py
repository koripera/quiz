#ﾙｰﾃｨﾝｸﾞに必要な要素をargs,funcに記述する
#関数名"func"は変えないこと
#基本はﾌｧｲﾙ名,rule,endpointは同一にすること
#不要要素はｺﾒﾝﾄｱｳﾄすること

#------------------------------#
__all__ = ["args","func"]

args={
"rule"                      : "/setcategory",
"methods"                   : ["POST"],
"endpoint"                  : "setcategory",
#"strict_slashes"            : ,
#"provide_automatic_options" : ,
#"defaults"                  : ,
}
#------------------------------#

from flask import render_template,session,request,redirect,url_for,jsonify

from libs.DATABASE import DB
from setting import DB_PATH

DB.dbname=DB_PATH

def func():
	data = request.get_json()
	txt = data.get('query1', '').strip()

	common = DB().Table("Common").Record()
	#common.fetch("categoryrule")[0][0]

	common.update({"categoryrule":txt})
	return jsonify({})
