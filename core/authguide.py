from flask import session,url_for

def loguide():
	#ﾛｸﾞｲﾝﾛｸﾞｱｳﾄ表示の切替
	aa,bb=url_for("auth.logout"),url_for("auth.login")
	A=f'<a href="{aa}">　ログアウト　</a>'
	B=f'<a href="{bb}">　ログイン　</a>'
	return A if "username" in session else B
