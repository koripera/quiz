from textwrap import dedent
from datetime import datetime,timedelta

from libs.DATABASE import DB
from setting import DB_PATH

DB.dbname=DB_PATH

class SCORE:
	#回答の記録
	def insert(username,ID,chara,result):
		data = {
			"datetime" : datetime.now().strftime('%Y-%m-%d %H:%M'),
			"user"     : username,
			"mode"     : "Judge" if chara==None else "Phrase",
			"ID"       : ID,
			"chara"    : chara,
			"result"   : result
		}
		DB().Table("Score").add_record(data)

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
