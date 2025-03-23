#ﾙｰﾃｨﾝｸﾞに必要な要素をargs,funcに記述する
#関数名"func"は変えないこと
#基本はﾌｧｲﾙ名,rule,endpointは同一にすること
#不要要素はｺﾒﾝﾄｱｳﾄすること

#------------------------------#
__all__ = ["args","func"]

args={
"rule"                      : "/judge_get",
"methods"                   : ["POST"],
"endpoint"                  : "judge_get",
#"strict_slashes"            : ,
#"provide_automatic_options" : ,
#"defaults"                  : ,
}
#------------------------------#

from flask import render_template,session,request,redirect,url_for
import contents.__parts as parts
from core.QUESTION import QUESTION

def func():
	data = request.get_json()
	ID = int(data.get('id', ''))
	return QUESTION.JUDGE.to_html(ID)

