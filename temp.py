
import sqlite3
from textwrap import dedent
from datetime import datetime,timedelta

from pickle import dumps,loads

from libs.DATABASE import DB

from core.QUESTION import QUESTION
from core.SCORE import SCORE

DB.dbname = "DATA/DATA.db"

def main():

	#b=list(range(100))[-10:]
	#print(b)
	#exit()

	idlist=QUESTION.JUDGE.valid_id()
	#print(*idlist)

	t=DB().Table("per_user")

	for e in idlist:
		a=SCORE.result("koripera",e[0],None)[-10:].count(1)
		#print(a)
		t.add_record({
			"user":"koripera",
			"mode":"judge",
			"ID":e[0],
			"chara":"",
			"rate":a/10,
		})
		

if __name__ =="__main__":
	main()	





