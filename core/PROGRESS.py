from flask import Blueprint,render_template,session,request,redirect

from core.TAG import TAG
from libs.DATABASE import DB
from setting import DB_PATH

DB.dbname=DB_PATH

class PROGRESS:
	def get(user,mode,ID):
		return DB().Table("Progress").Record(f"user='{user}' AND type='{mode}' AND id={ID}").fetchone()


	def make_record(user,mode,ID):		
		if mode=="note":
			qcount = DB().Table("note").Record(f"ID = {ID}").fetchone("qcount")[0]
		elif mode=="tag":
			qcount = DB().Table("tag").Record(f"ID = {ID}").fetchone("qcount")[0]
		else:
			raise ValueError

		insdata={
			"user"  :user,
			"type"  :mode,
			"id"    :ID,
			"point" :0,
			"qcount":qcount,
		}

		DB().Table("Progress").add_record(insdata)

	def update(user,mode,ID,points):
		if None==PROGRESS.get(user,mode,ID):
			PROGRESS.make_record(user,mode,ID)

		if mode=="note":
			qcount = DB().Table("note").Record(f"ID = '{ID}'").fetchone("qcount")[0]
		elif mode=="tag":
			qcount = TAG.get_qcnt(ID)
		else:
			raise ValueError

		pre_qcount = DB().Table("Progress").Record(f"user = '{user}' AND type = '{mode}' AND id = {ID}").fetchone("qcount")[0]

		p = DB().Table("Progress").Record(f"user = '{user}' AND type = '{mode}' AND id = {ID}").fetchone("point")[0]

		insdata=dict()

		if qcount!=pre_qcount:
			if qcount > pre_qcount:
				p = int(p*(pre_qcount/(qcount+pre_qcount)))
				insdata["qcount"]=qcount
			else:
				insdata["qcount"]=qcount

		p-=p//100
		p+=points
		insdata["point"]=p

		#print(insdata)
		#print(qcount,pre_qcount)

		DB().Table("Progress").Record(f"user = '{user}' AND type = '{mode}' AND id = {ID}").update(insdata)
		

	

