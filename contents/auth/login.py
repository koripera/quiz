#ﾙｰﾃｨﾝｸﾞに必要な要素をargs,funcに記述する
#関数名"func"は変えないこと
#基本はﾌｧｲﾙ名,rule,endpointは同一にすること
#不要要素はｺﾒﾝﾄｱｳﾄすること

#------------------------------#
__all__ = ["args","func"]

args={
"rule"                      : "/login",
"methods"                   : ["GET","POST"],
"endpoint"                  : "login",
#"strict_slashes"            : ,
#"provide_automatic_options" : ,
#"defaults"                  : ,
}
#------------------------------#

from flask import Blueprint,render_template,session,request,redirect,url_for

from werkzeug.security import generate_password_hash, check_password_hash

import contents.__parts as parts
from core.authguide import loguide
from core.USERS import USERS

from libs.DATABASE import DB

from setting import DB_PATH

DB.dbname=DB_PATH

def func():
	if request.method == 'GET':

		page = render_template(
			"login.html",
			headlinks = parts.headlink()
		)

		return page

	if request.method == 'POST':
		if request.form.get("login")!=None:
			name,password = request.form.get("name"),request.form.get("pass")

			#ﾕｰｻﾞｰがあるか
			if (matched:=DB().Table("users").Record(f"name='{name}'").fetch("pass")):
				#ﾊﾟｽが合うか
				if check_password_hash(matched[0][0],password):
					session['username'] = name
					return redirect(url_for("home"))

				#ﾊﾟｽ不一致			
				else:
					message = "Password is incorrect."
					page = render_template(
						"login.html",
						headlinks = parts.headlink(),
						message=message,
					)

					return page

			#ﾕｰｻﾞｰなし
			else:
				message = "User does not exist"
				page = render_template(
					"login.html",
					headlinks = parts.headlink(),
					message=message,
				)

				return page

