#ﾙｰﾃｨﾝｸﾞに必要な要素をargs,funcに記述する
#関数名"func"は変えないこと
#基本はﾌｧｲﾙ名,rule,endpointは同一にすること
#不要要素はｺﾒﾝﾄｱｳﾄすること

#------------------------------#
__all__ = ["args","func"]

args={
"rule"                      : "/note",
"methods"                   : ["GET","POST"],
"endpoint"                  : "note",
#"strict_slashes"            : ,
#"provide_automatic_options" : ,
#"defaults"                  : ,
}
#------------------------------#

from textwrap import dedent
from flask import render_template,session,request,redirect,url_for
import contents.__parts as parts
from core.NOTE import NOTE

from libs.DATABASE import DB
from setting import DB_PATH

DB.dbname=DB_PATH

def func():
	if request.method == 'GET':
		if "inQ" not in session:session["inQ"]=""
		if "inC" not in session:session["inC"]=""
		if "tag" not in session:session["tag"]=[]
		
		return render_template(
			"note.html",
			tag=" ".join(session["tag"]),
			category=DB().Table("Common").Record().fetch("categoryrule")[0][0],
		)
	if request.method == 'POST':
		return taglist()

def taglist():
	allitem = Filter(None)
	
	common = DB().Table("Common").Record()
	txt = common.fetch("categoryrule")[0][0]

	allitem.make("" if txt==None else txt)

	html=""

	#全体のIDリストを取得する
	id_title = DB().Table("note").Record().fetch(["id","name"])
	id_title.sort(key=lambda x:x[1])
	idlist = [e[0] for e in id_title]

	#filterを適用する
	for ID in idlist:
		allitem.categorize(ID)

	return allitem.makehtml()










class Filter:
	def __init__(self,filt):
		self.filt = filt
		self.subfilt = []
		self.items=[]

	def make(self,q):
		q=q.strip("\n").split("\n")

		#print(q)
		baselevel=0
		d=[self,]#操作中
		for s in q:
			words = s.strip().split(",")
			level = s.rstrip().count("\t")
			fi=Filter(words)

			#print(words,baselevel,level,fi.filt)

			if baselevel==level:
				d[-1].add_sub(fi);#print(d[-1].filt)
				d.append(fi)
				baselevel+=1
			elif baselevel>level:
				for i in range(baselevel-level):
					d.pop()
					baselevel-=1
				d[-1].add_sub(fi);#print(d[-1].filt)
				d.append(fi)
				baselevel+=1
			#elif baselevel<level:
			#	pass#一段ずつ登るので無視

	def add_sub(self,Fil):
		self.subfilt.append(Fil)

	def categorize(self,ID,tags=None):
		if tags==None:
			tags=set(get_tag(ID))

		if self.filt==None:	f = True
		else              : f = all(1 if e in tags else 0 for e in self.filt) 

		if f:
			ff=False
			for e in self.subfilt:
				if e.categorize(ID,tags=tags):
					ff=True

			if not ff:#子にカテゴリできないとき
				self.items.append(ID)

			return True

		else:
			return False

	def printout(self):
		print(f"{self.filt}:{self.items}")
		for e in self.subfilt:
			e.printout()
		

	def makehtml(self):
		child=""
		selfs=""
		for e in self.subfilt:
			child+=e.makehtml()

		for e in self.items:
			url   = url_for("edit.note",ID=e)
			title = DB().Table("note").Record(f"id='{e}'").fetch("name")[0][0]
			selfs+=f'<a class="links_o" href="{url}" target="_blank">{title}</a>'

		txt=f"{child}{selfs}"

		if self.filt!=None:
			txt=dedent(
				f"""
				<details>
				<summary>{",".join(self.filt)}</summary>
				<div class="inner_details">
				{txt}
				</div>
				</details>
				""")

		return txt

def get_tag(ID):
	#付与しているタグ名リストを返す
	tagidlist = DB().Table("note_tag").Record(f"nid='{ID}'").fetch("tagID")			
	taglist = DB().Table("tag").Record(f"id IN ({','.join([str(i[0]) for i in tagidlist])})").fetch("name")
	return [e[0] for e in taglist]	

