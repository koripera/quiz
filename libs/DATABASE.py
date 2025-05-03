import sqlite3
from textwrap import dedent

def main():
	#ﾃﾞｰﾀﾍﾞｰｽの作成・接続名登録
	data = DATABASE("aaa.db")

	#ﾃﾞｰﾀﾍﾞｰｽを一個しか使わないなら
	#DATABASEを継承したDBを使う、使用毎に名前の入力はいらない
	DB.dbname = "aaa.db"
	data2 = DB()#->DATABASE("aaa.db")

	#ﾃｰﾌﾞﾙの追加(tablename,columnlist,f=既存のﾃｰﾌﾞﾙを上書するか否か)
	data.add_table("A",["aaa","iii","uuu"],f=True)
	data.add_table("B",["aaa","iii","uuu"],f=True)
	data.add_table("C",["aaa","iii","uuu"],f=True)

	#ﾃｰﾌﾞﾙの削除(tablename,f=存在無でｴﾗｰを出すが、無視するか否か)
	data.del_table("A",f=True)

	#ﾃｰﾌﾞﾙの存在確認
	print(data.exists_table("A"))

	#ﾃｰﾌﾞﾙ名のﾘｽﾄ出力
	print(f"tables  :{data.tables}")



	#ﾃｰﾌﾞﾙを指定する
	table = data.add_table("A",["aaa","iii","uuu"],f=True)
	table = data.Table("A")
	
	#ﾃｰﾌﾞﾙのｺﾗﾑ名・ﾚｺｰﾄﾞのﾘｽﾄ出力
	print(f"columns :{table.columns}")
	print(f"data    :{table.records}")#全ｺﾗﾑ全行を出力する

	#ﾚｺｰﾄﾞの追加
	for i in range(10):
		table.add_record()                             #全ｺﾗﾑNone
		table.add_record({"aaa":i,"iii":i*2,"uuu":i*3})#指定ｺﾗﾑ以外None

	#ｺﾗﾑを追加(columnname,val=既存ﾚｺｰﾄﾞの初期値)
	table.add_column("eee",val=100)

	#ｺﾗﾑを削除
	table.del_column("eee")



	#ﾚｺｰﾄﾞを指定する(key=ﾌｨﾙﾀﾘﾝｸﾞ・SQL文)
	allrecords = table.Record()
	records    = table.Record(key="aaa IS NULL")
		
	#ﾚｺｰﾄﾞの取得(取得するｺﾗﾑを指定する、strorﾘｽﾄorﾀﾌﾟﾙ)
	#ﾘｽﾄで出力,各ﾚｺｰﾄﾞはﾀﾌﾟﾙ
	print("\n-----allrecords-----")
	print(*allrecords.fetch(),sep="\n",end="\n\n")
	print("-----aaa=NULL-----")
	print(*records.fetch("aaa,iii,uuu"),sep="\n",end="\n\n")
	
	#ﾚｺｰﾄﾞの更新
	records.update({"iii":300})
	print("update")
	print("-----allrecords-----")
	print(*allrecords.fetch(),sep="\n",end="\n\n")

	#ﾚｺｰﾄﾞの削除
	records.delete()
	print("delete")
	print("-----allrecords-----")
	print(*allrecords.fetch(),sep="\n",end="\n\n")

	#printの動作
	print(data)
	print(table)
	print(allrecords)

	#細かい作業はこれで行う
	with data.connect as d:
		conn,cur = d

		

class Error(Exception):
	pass

class Connect:
	def __init__(self,dbname):
		self.dbname = dbname

	def __enter__(self):
		self.connect = sqlite3.connect(self.dbname)
		self.cursor  = self.connect.cursor()
		return self.connect,self.cursor

	def __exit__(self, exc_type, exc_value, traceback):
		self.cursor.close()
		self.connect.close()

class DATABASE:
	def __init__(self,dbname):
		self.dbname  = dbname
		self.connect = Connect(dbname)
		with self.connect as d:
			pass

	def __repr__(self):
		return f"DATABASE('{self.dbname}')"

	def Table(self,tablename):
		return TABLE(self,tablename)

	@property
	def tables(self):
		#ﾃｰﾌﾞﾙ名のﾘｽﾄを返す
		select = dedent(
		'''
		SELECT name FROM sqlite_master WHERE type='table';
		''')
		with self.connect as d:
			conn,cur = d
			cur.execute(select)
			rows=cur.fetchall()
		return [i[0] for i in rows]	

	def exists_table(self,tablename):
		#ﾃｰﾌﾞﾙの有無の確認
		q="SELECT 1 FROM sqlite_master WHERE type='table' AND name=?"

		with self.connect as d:
			conn,cur = d
			cur.execute(q,(tablename,))
			res = cur.fetchone()
		return False if res==None else True		

	def add_table(self,tablename,colnamelist,f=False):
		#ﾃｰﾌﾞﾙの追加を行う,fで上書
		exist=self.exists_table(tablename)
		if exist:
			if f:self.del_table(tablename)
			else:raise Error(f"The name '{tablename}' is already in use.")

		query = dedent(
		f'''
		CREATE TABLE {tablename} ({",".join(colnamelist)})
		''')

		with self.connect as d:
			conn,cur = d
			cur.execute(query)
			conn.commit()

		return self.Table(tablename)

	def del_table(self,tablename,f=False):
		#ﾃｰﾌﾞﾙの削除,fはｴﾗｰ停止させない、空きの保障として使う
		exist=self.exists_table(tablename)
		if not exist:
			if f:return
			else:raise Error(f"The name '{tablename}' does not exist.")
			
		q=f"DROP TABLE {tablename};"
		with self.connect as d:
			conn,cur = d
			cur.execute(q)
			conn.commit()

class TABLE:
	def __init__(self,DB,tablename):
		self.dbname = DB.dbname
		self.tablename= tablename
		self.connect = DB.connect

	def __repr__(self):
		return f"TABLE(DATABASE('{self.dbname}'),'{self.tablename}')"

	@property
	def columns(self):
		#ﾃｰﾌﾞﾙのｶﾗﾑ名ﾘｽﾄを返す
		q = f"SELECT * FROM {self.tablename};"

		with self.connect as d:
			conn,cur = d
			cur.execute(q)
			desc = cur.description
		
		return [description[0] for description in desc]
	
	@property
	def records(self):
		#ﾃｰﾌﾞﾙのﾚｺｰﾄﾞを返す
		q = f"SELECT * FROM {self.tablename};"

		with self.connect as d:
			conn,cur = d
			cur.execute(q)
			data = cur.fetchall()
		
		return data

	def Record(self,key=""):
		return RECORD(self,key)

	def add_record(self,val=None):
		#ﾃｰﾌﾞﾙにﾃﾞｰﾀを追加

		#辞書で追加
		if val != None:
			keys = []
			vals = []
			for k,v in val.items():
				keys.append(k)
				vals.append(v)

			k = f'({",".join(keys)})'
			v = f'({",".join("?"*len(keys))})'
			q = f"INSERT INTO {self.tablename} {k} VALUES {v}"
			with self.connect as d:
				conn,cur = d
				cur.execute(q,tuple(vals))
				conn.commit()

		#空のﾃﾞｰﾀ
		else:
			v = f'({",".join(["NULL" for _ in range(len(self.columns))])})'
			q = f"INSERT INTO {self.tablename} VALUES {v}"
			with self.connect as d:
				conn,cur = d
				cur.execute(q)
				conn.commit()

	def add_column(self,columnname,val=None):
		#ﾃｰﾌﾞﾙにｶﾗﾑを追加、valは初期値
		q = f"ALTER TABLE {self.tablename} ADD COLUMN {columnname};"
	
		with self.connect as d:
			conn,cur = d
			cur.execute(q)
			conn.commit()

		if val!=None:
			q = f"UPDATE {self.tablename} SET {columnname} = ? WHERE {columnname} IS NULL;"

			with self.connect as d:
				conn,cur = d
				cur.execute(q,(val,))
				conn.commit()

	def del_column(self,columnname):
		#不要なｺﾗﾑ以外のﾃｰﾌﾞﾙを再作成
		columnnamelist = self.columns
		columnnamelist.remove(columnname)
		DATABASE(self.dbname).add_table("temp",columnnamelist)

		query = dedent(
		f'''\
		INSERT INTO temp ({",".join(columnnamelist)}) SELECT {",".join(columnnamelist)} FROM {self.tablename};
		DROP TABLE {self.tablename};
		ALTER TABLE temp RENAME TO {self.tablename};
		''')

		with self.connect as d:
			conn,cur = d
			for i in query.split("\n"):
				cur.executescript(i)
			conn.commit()

class RECORD:
	def __init__(self,TABLE,key=""):
		self.dbname = TABLE.dbname
		self.tablename= TABLE.tablename
		self.connect = TABLE.connect
		self.key    = key

	def __repr__(self):
		return f"RECORD(TABLE(DATABASE('{self.dbname}'),'{self.tablename}'),key='{self.key}')"

	def fetch(self,column = "*"):
		#column:欲しい列名を指定する,基本は全列
		#該当の行を[(column1),(column2),...]のlist(tuple,)で返す
		if type(column) in (list,tuple):
			column=",".join(column)
				
		select = f"SELECT {column} FROM {self.tablename}"

		if self.key!="":
			key = f" WHERE {self.key}"
			select+=key

		with self.connect as d:
			conn,cur = d
			cur.execute(select)
			rows = cur.fetchall()#ﾘｽﾄに、該当をﾀﾌﾟﾙで格納[(a,),(b,)...]
	
		return rows

	def fetchone(self,column="*"):
		#fecthのうちひとつ返す:q
		res = self.fetch(column)
		return res[0] if res else None

	def update(self,val):
		#辞書で追加
		keys = []
		vals = []
		for k,v in val.items():
			keys.append(k)
			vals.append(v)

		keys = [f"{e} = ?" for e in keys]
		k = f'{",".join(keys)}'
		v = f'({",".join("?"*len(keys))})'
		q = f"UPDATE {self.tablename} SET {k}"

		if self.key!="":
			key = f" WHERE {self.key}"
			q+=key

		with self.connect as d:
			conn,cur = d
			cur.execute(q,tuple(vals))
			conn.commit()

	def delete(self):
		q = f"DELETE FROM {self.tablename}"

		if self.key!="":
			key = f" WHERE {self.key}"
			q+=key

		with self.connect as d:
			conn,cur = d
			cur.execute(q)
			conn.commit()

class DB(DATABASE):
	dbname = ""
	def __init__(self):
		super().__init__(self.dbname)


if __name__ =="__main__":
	main()


