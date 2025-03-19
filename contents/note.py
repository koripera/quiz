#ﾙｰﾃｨﾝｸﾞに必要な要素をargs,funcに記述する
#関数名"func"は変えないこと
#基本はﾌｧｲﾙ名,rule,endpointは同一にすること
#不要要素はｺﾒﾝﾄｱｳﾄすること

#------------------------------#
__all__ = ["args","func"]

args={
"rule"                      : "/note",
"methods"                   : ["GET"],
"endpoint"                  : "note",
#"strict_slashes"            : ,
#"provide_automatic_options" : ,
#"defaults"                  : ,
}
#------------------------------#

from flask import render_template,session,request,redirect,url_for
import contents.__parts as parts
from core.NOTE import NOTE

def func():
	if "inQ" not in session:session["inQ"]=""
	if "inC" not in session:session["inC"]=""
	if "tag" not in session:session["tag"]=[]
	
	if False:
		idlist = [e[0] for e in NOTE.valid_id(tag=session["tag"])]

		links=""
		for ID in idlist:
			data = NOTE.get(ID)
			url = url_for("edit.note",ID=ID)
			links += f"""<li><a href="{url}">{data["name"]}</a></li>\n"""

		links = f"<ul>{links}</ul>"

		if not idlist:
			links = "No relevant data"
		
	return render_template(
		"note.html",
		tag=" ".join(session["tag"]),
	)


