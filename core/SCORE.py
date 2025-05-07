from textwrap import dedent
from datetime import datetime,timedelta

from libs.DATABASE import DB
from setting import DB_PATH

DB.dbname=DB_PATH

class SCORE:
	#回答の記録,回答ログを返す
	def insert(username,ID,chara,result):
		res_old = SCORE.result(username,ID,chara)

		data = {
			"datetime" : datetime.now().strftime('%Y-%m-%d %H:%M'),
			"user"     : username,
			"mode"     : "Judge" if chara==None else "Phrase",
			"ID"       : ID,
			"chara"    : chara,
			"result"   : result
		}
		DB().Table("Score").add_record(data)

		res = SCORE.result(username,ID,chara)

		update_count(username,ID,chara,result)#日毎の回答数のカウント

		#回答前後で率が変わる場合
		change = res_old[-10:].count(1) != res[-10:].count(1)
		if change:
			update_rate(username,ID,chara,result)#問毎の正答率の更新

		return res
		


	#回答の参照
	def result(username,ID,chara):
		#Judgeの問題
		if chara == None:
			select = dedent(
				f"""
				SELECT result FROM Score
				WHERE user = ? AND ID = ?
				ORDER BY datetime
				""")

			with DB().connect as d:
				conn,cur = d
				cur.execute(select,(username,ID))
				rows = cur.fetchall()#ﾘｽﾄに、該当をﾀﾌﾟﾙで格納[(a,),(b,)...]

			rows = [e[0] for e in rows]
			data = rows

		#Phraseの問題
		else:
			select = dedent(
				f"""
				SELECT result FROM Score
				WHERE user = ? AND ID = ? AND chara = ?
				ORDER BY datetime
				""")

			with DB().connect as d:
				conn,cur = d
				cur.execute(select,(username,ID,chara))
				rows = cur.fetchall()#ﾘｽﾄに、該当をﾀﾌﾟﾙで格納[(a,),(b,)...]

			rows = [e[0] for e in rows]
			data = rows

		return data	

def update_count(username,ID,chara,result):
	#回答数を日毎に保存しておく
	day = datetime.now().strftime('%Y-%m-%d')
	rec = DB().Table("Dairy").Record(f"user='{username}' AND date='{day}'")

	if rec.fetchone()==None:
		data={
			"date":day,
			"user":username,
			"J_ac":0,
			"J_wa":0,
			"P_ac":0,
			"P_wa":0,
		}
		DB().Table("Dairy").add_record(data)

	col = "J" if chara==None else "P"
	col += "_ac" if result else "_wa"

	with DB().connect as d:
		conn,cur = d
		q=dedent(
		f"""
		UPDATE Dairy
		SET {col} = {col}+1
		WHERE user=? AND date=?
		""")
		cur.execute(q,(username,day))
		conn.commit()


def update_rate(username,ID,chara,result):
	#問題ごとの正答率の作成
	if username=="":return

	if chara==None:
		d=DB().Table("per_user").Record(f"ID={ID} AND Mode='judge'")
		a = d.fetchone()

		rate=SCORE.result(username,ID,None)[-10:].count(1)/10
		if a==None:
			DB().Table("per_user").add_record({
				"User" :username,
				"Mode" :"judge",
				"ID"   :ID,
				"Chara":"",
				"rate" :rate,
			})
		else:
			d.update({
				"rate":rate,
			})

	else:
		d=DB().Table("per_user").Record(f"ID={ID} AND Mode='phrase' AND chara='{chara}'")
		a = d.fetchone()

		rate=SCORE.result(username,ID,chara)[-10:].count(1)/10
		if a==None:
			DB().Table("per_user").add_record({
				"User" :username,
				"Mode" :"phrase",
				"ID"   :ID,
				"Chara":chara,
				"rate" :rate,
			})
		else:
			d.update({
				"rate":rate,
			})


