
import sqlite3
from textwrap import dedent
from datetime import datetime,timedelta

from pickle import dumps,loads

from libs.DATABASE import DB

from core.QUESTION import QUESTION
from core.SCORE import SCORE

DB.dbname = "DATA/DATA.db"

def main():
	datalist=DB().Table("tag").Record().fetch("name")

	#print(datalist)

	if 1:
		for data in datalist:
			name = data[0]
			jid = QUESTION.JUDGE.valid_id(tag=[name])
			pid = QUESTION.PHRASE.valid_id(tag=[name])

			r=DB().Table("tag").Record(f"name = '{name}'")

			r.update({"qcount":len(jid)+len(pid)})

			print(name,len(jid)+len(pid))
		

if __name__ =="__main__":
	main()	





