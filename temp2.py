
import sqlite3
from textwrap import dedent
from datetime import datetime,timedelta

from pickle import dumps,loads

from libs.DATABASE import DB

from core.QUESTION import QUESTION
from core.SCORE import SCORE

DB.dbname = "DATA/DATA.db"

def main():
	today = datetime.now()
	dates = list(reversed([(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(365)]))

	with DB().connect as d:
		conn,cur = d

		#一時ﾃｰﾌﾞﾙを作る
		cur.execute(f'''
			CREATE TEMPORARY TABLE temp AS
			SELECT * FROM Score WHERE user = 'koripera' AND datetime >= DATE('now', '-365 days')
		''')

		#正答と誤答のｶｳﾝﾄ
		for date in dates:
			cur.execute("""
				SELECT 	SUM(CASE WHEN mode='Judge' AND result = 1 THEN 1 ELSE 0 END) AS J_ac,
						SUM(CASE WHEN mode='Judge' AND result = 0 THEN 1 ELSE 0 END) AS J_wa,
						SUM(CASE WHEN mode='Phrase' AND result = 1 THEN 1 ELSE 0 END) AS P_ac,
						SUM(CASE WHEN mode='Phrase' AND result = 0 THEN 1 ELSE 0 END) AS P_wa
			FROM temp
				WHERE datetime BETWEEN ? AND ?;
			""",(date+" 00:00",date+" 23:59"))
			res=cur.fetchone()

			res = list(res)
			if res[0] == None : res[0]=0 
			if res[1] == None : res[1]=0
			if res[2] == None : res[2]=0
			if res[3] == None : res[3]=0
			
			if any(res):			
				data={
					"date":date,
					"user":"koripera",
					"J_ac":res[0],
					"J_wa":res[1],
					"P_ac":res[2],
					"P_wa":res[3],
				}

				DB().Table("Dairy").add_record(data)


if __name__ =="__main__":
	main()	





