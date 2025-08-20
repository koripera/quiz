from textwrap import dedent

from util.tools import missingnum
from libs.DATABASE import DB
from setting import DB_PATH

DB.dbname=DB_PATH

class TAG:
	def make(name):
		#新規作成用のIDを探す
		with DB().connect as (conn,cur):
			cur.execute("SELECT id FROM tag")
			idlist=sorted([e[0] for e in cur.fetchall()])

		tagID = missingnum(idlist)

		#ﾀｸﾞﾃﾞｰﾀに追加
		with DB().connect as (conn,cur):
			cur.execute(f'INSERT INTO tag VALUES (?,?)',(tagID,name))
			conn.commit()

		#作成したIDを返す
		return tagID

	def id_to_name():
		pass

	def name_to_id(name):
		q=dedent(
			f"""
			SELECT ID
			FROM tag
			WHERE name = ?
			""")
		with DB().connect as (conn,cur):
			cur.execute(q,(name,))
			res = cur.fetchone()
		return res[0]

	def get_qcnt(ID=None,name=None):
		if ID  :return DB().Table("tag").Record(f"ID = {ID}").fetchone("qcount")[0]
		if name:return DB().Table("tag").Record(f"ID = {TAG.name_to_id(name)}").fetchone("qcount")[0]
		raise ValueError

	def add_qcnt(ID=None,name=None,n=1):
		cnt = TAG.get_qcnt(ID,name)
		insdata={"qcount":cnt+n}
		if ID:DB().Table("tag").Record(f"id = {ID}").update(insdata)
		elif name:DB().Table("tag").Record(f"name = '{name}'").update(insdata)

	def sub_qcnt(ID=None,name=None,n=1):
		cnt = TAG.get_qcnt(ID,name)
		insdata={"qcount":cnt-n}
		if ID:DB().Table("tag").Record(f"id = {ID}").update(insdata)
		elif name:DB().Table("tag").Record(f"name = '{name}'").update(insdata)

