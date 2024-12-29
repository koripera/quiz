from coa import execute,onechoice,repchoice,tx

import sqlite3
from textwrap import dedent
from datetime import datetime,timedelta

from pickle import dumps,loads

from DATABASE import DB

DB.dbname = "DATA.db"


def main():
	mainmanu()

def mainmanu():
	funcs=[
		edit_database,
	]
	repchoice(execute,funcs,exopt="exit")
	
def edit_database():
	funcs=[
		add_table,
		drop_table,
		add_column,
		drop_column,
		check_records,
	]
	repchoice(execute,funcs,f=check_table)

def add_table(*arg):
	if len(arg)<=1:
		print("Enter the following after the code\ntablename column1 column2...")
		return

	execute(DB().add_table,arg[0],arg[1:])

def drop_table(*arg):
	func = lambda *arg:DB().del_table(arg[0])

	message=tx(
		"""
		Please select the table you wish to delete	
		""")

	repchoice(func,lambda:DB().tables,f=check_table,message=message)

def add_column(*arg):
	def addcol(*arg):
		tablename=arg[0]
		col=arg[1:]
		for name in col:
			DB().Table(tablename).add_column(name)

	message=tx(
		"""
		Enter the following after the code
		column_name	
		""")

	repchoice(addcol,DB().tables,f=check_table,message=message)

def drop_column(*arg):
	def dropcol(*arg):
		tablename=arg[0]
		col=arg[1:]
		for name in col:
			DB().Table(tablename).del_column(name)

	message=tx(
		"""
		Enter the following after the code
		column_name	
		""")

	repchoice(dropcol,DB().tables,f=check_table,message=message)

def check_records(*arg):
	def crec(*arg):
		tablename=arg[0]
		col=arg[1:]
		print(tablename)

		col=[e.replace("_"," ") for e in col]

		select = "*"
		if col: select = col[0]
		where=False
		if 2<=len(col):where=True


		with DB().connect as d:
			conn,cur = d
			q=f"SELECT {select} FROM {tablename}"
			if where:q+=f" WHERE {' '.join(col[1:])}"

			try:
				cur.execute(q)
				print("----------")
				print("\n".join((str(i) for i in cur.fetchall())) )
				print("----------")

			except:
				print("error!")

	message=tx(
		"""
		If necessary, Enter the following after the code
		projection filtering
		""")

	repchoice(crec,DB().tables,f=check_table,message=message)




	
def check_table(*arg):#ﾃｰﾌﾞﾙ名とｶﾗﾑ名を表示する
	table_name = DB().tables

	mlen = max([len(i) for i in table_name])

	print("-"*10)
	for name in table_name:
		print(f"{name}{' '*(mlen-len(name))} : {', '.join(DB().Table(name).columns)}")
	print("-"*10)

if __name__ =="__main__":
	main()	





