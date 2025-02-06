__all__ = ["headlink"]

from textwrap import dedent
from flask import session,render_template
from core.myurl_for import myurl_for

def headlink():
	A=f'<a href="{myurl_for("auth.logout")}">　ログアウト　</a>'
	B=f'<a href="{myurl_for("auth.login")}">　ログイン　</a>'

	item = render_template(
		"parts/headlinks.html",
		home   = myurl_for("home"),
		Judge  = myurl_for("infiniteQ_Judge"),
		Phrase = myurl_for("infiniteQ_Phrase"),
		note   = myurl_for("note"),
		login  = A if "username" in session else B,
	)

	return item

