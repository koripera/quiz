#ﾙｰﾃｨﾝｸﾞに必要な要素をargs,funcに記述する
#関数名"func"は変えないこと
#基本はﾌｧｲﾙ名,rule,endpointは同一にすること
#不要要素はｺﾒﾝﾄｱｳﾄすること

#------------------------------#
__all__ = ["args","func"]

args={
"rule"                      : "/download",
"methods"                   : ["GET"],
"endpoint"                  : "download",
#"strict_slashes"            : ,
#"provide_automatic_options" : ,
#"defaults"                  : ,
}
#------------------------------#

from flask import render_template,session,request,redirect,url_for,send_file
import contents.__parts as parts

def func():
	file_path = "../DATA/DATA.db"#ルートパス設定？
	return send_file(file_path,as_attachment=True)


