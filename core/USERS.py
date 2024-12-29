from flask import Blueprint,render_template,session,request,redirect
from werkzeug.security import generate_password_hash, check_password_hash

from core.authguide import loguide

from libs.DATABASE import DB
from setting import DB_PATH

DB.dbname=DB_PATH

class USERS:
	def login():
		#ﾛｸﾞｲﾝ処理
		if request.form.get("login")!=None:
			name,password = request.form.get("name"),request.form.get("pass")

			#ﾕｰｻﾞｰがあるか
			if (matched:=DB().Table("users").Record(f"name='{name}'").fetch("pass")):
				#ﾊﾟｽが合うか
				if check_password_hash(matched[0][0],password):
					session['username'] = name
					return redirect("home")

				#ﾊﾟｽ不一致			
				else:
					message = "Password is incorrect."
					return render_template("login.html",
											login=loguide(),
											message=message)
			#ﾕｰｻﾞｰなし
			else:
				message = "User does not exist"
				return render_template("login.html",
										login=loguide(),
										message=message)
