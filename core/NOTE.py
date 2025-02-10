from textwrap import dedent

import pickle
import bisect
import re
import random
from operator import itemgetter as iget

from libs.DATABASE import DB
from setting import DB_PATH
from util.tools import missingnum

DB.dbname=DB_PATH

class NOTE:
	def addtag(NID,name):#任意のidにタグを追加{{{
		
		#ﾀｸﾞのﾘｽﾄから、追加したいﾀｸﾞがあるか確認する
		q=dedent(
			f"""
			SELECT ID
			FROM tag
			WHERE name = ?
			""")

		with DB().connect as d:
			conn,cur = d
			cur.execute(q,(name,))
			res = cur.fetchone()

		#無いﾀｸﾞなら、新規に追加して、IDを取る
		if res == None:
			#新規作成用のIDを探す
			with DB().connect as d:
				conn,cur = d
				cur.execute("SELECT id FROM tag")
				idlist=sorted([e[0] for e in cur.fetchall()])

			tagID = missingnum(idlist)

			#ﾀｸﾞﾃﾞｰﾀに追加
			with DB().connect as d:
				conn,cur = d
				cur.execute(f'INSERT INTO tag VALUES (?,?)',(tagID,name))
				conn.commit()

		#既存ﾀｸﾞならそのIDを取得する
		else:
			tagID=res[0]

		#itemIDとﾀｸﾞIDを結びつける
		table = "note_tag"
		with DB().connect as d:
			conn,cur = d
			cur.execute(f'INSERT INTO {table} VALUES (?,?)',(NID,tagID))
			conn.commit()
	#}}}

	def deltag(name):#タグが1個もなくなるとき、タグを消す{{{
		with DB().connect as d:
			conn,cur = d

			#judgeのﾀｸﾞ利用ﾁｪｯｸ
			q=dedent(
			f"""
			SELECT DISTINCT Question_J.ID FROM Question_J
			JOIN Question_J_tag ON Question_J.id = Question_J_tag.QID
			JOIN tag ON Question_J_tag.tagID = tag.ID
			WHERE tag.name = "{name}"
			""")
			cur.execute(q)
			jtag = cur.fetchall()#ﾚｺｰﾄﾞがなければ空のﾘｽﾄ
			if jtag:return#ﾚｺｰﾄﾞ有りなら中断

			#phraseのﾀｸﾞ利用ﾁｪｯｸ
			q=dedent(
			f"""
			SELECT DISTINCT Question_P.ID FROM Question_P
			JOIN Question_P_tag ON Question_P.id = Question_P_tag.QID
			JOIN tag ON Question_P_tag.tagID = tag.ID
			WHERE tag.name = "{name}"
			""")
			cur.execute(q)
			ptag = cur.fetchall()
			if ptag:return

			#noteのﾀｸﾞ利用ﾁｪｯｸ
			q=dedent(
			f"""
			SELECT DISTINCT note.ID FROM note
			JOIN note_tag ON note.id = note_tag.NID
			JOIN tag ON note_tag.tagID = tag.ID
			WHERE tag.name = "{name}"
			""")
			cur.execute(q)
			ntag = cur.fetchall()
			if ntag:return

		#judge.phrase.noteいずれでも使われてないなら、ﾀｸﾞのﾚｺｰﾄﾞを削除
		DB().Table("tag").Record(f"name='{name}'").delete()
	#}}}
	
	def valid_id(tag=None,search=""):#{{{
		#noteのIDﾘｽﾄを返す
		#タグ検索→文字列検索の順で行い、それぞれ、onoffが出来るように
		if tag==None:tag=[]
		word = 1 if search!="" else 0
		
		#通常
		q=dedent(
			"""
			SELECT DISTINCT note.ID FROM note
			""")

		#ﾀｸﾞかつ文字列
		if tag and word:
			q=dedent(
			f"""
			SELECT id 
			FROM note
			WHERE ID IN (
				SELECT note.ID
				FROM note
				JOIN note_tag ON note.id = note_tag.NID
				JOIN tag ON note_tag.tagID = tag.ID
				WHERE tag.name IN ({",".join("?"*len(tag))})
				GROUP BY note.ID
				HAVING COUNT(note.ID) = {len(tag)})
			AND (content LIKE '%{search}%')
			""")

		#tagのみ
		elif tag:
			q+=dedent(
			f"""
			JOIN note_tag ON note.id = note_tag.NID
			JOIN tag ON note_tag.tagID = tag.ID
			WHERE tag.name IN ({",".join("?"*len(tag))})
			GROUP BY note.id
			HAVING COUNT(note.id) = {len(tag)}
			""")

		#文字列のみ
		elif word:
			q+=dedent(
			f"""
			WHERE content LIKE '%{search}%'
			""")

		with DB().connect as d:
			conn,cur = d
			if tag:cur.execute(q,tuple(tag))
			else  :cur.execute(q)

			#ﾀﾌﾟﾙのまま返す			
			return cur.fetchall()

	#}}}

	def get(ID):#{{{
		#辞書を返す
		key = ["NID","name","content"]
		val = DB().Table("note").Record(f"ID='{ID}'").fetch()
		if val==[]:return None
		val = val[0]

		notedata = {k:v for k,v in zip(key,val)}

		#問題につけられているタグのIDを取得 →　タグのIDから、タグの名前を取得
		tagidlist = DB().Table("note_tag").Record(f"NID='{ID}'").fetch("tagID")			
		taglist = DB().Table("tag").Record(f"ID IN ({','.join([str(i[0]) for i in tagidlist])})").fetch("name")

		notedata["tag"]   = [e[0] for e in taglist]	

		return notedata

	#}}}

	def make(request):#{{{
		#新規作成

		#使うIDを探す
		idlist = DB().Table("note").Record().fetch("ID")
		idset = set([i[0] for i in idlist])

		komoji = [chr(i) for i in range(97,123)]
		oomoji = [chr(i) for i in range(65,91)]
		moji   = komoji+oomoji

		while True:
			ID = "".join([random.choice(moji) for _ in range(8)])
			if ID not in idset:break

		#挿入ﾃﾞｰﾀの作成し、入力をﾃﾞｰﾀﾍﾞｰｽに入れる
		insdata={
			"ID"      : ID,
			"name"    : request.form.get("title"),
			"content" : request.form.get("content").replace('\r\n','\n').strip(),
		}
		DB().Table("note").add_record(insdata)

		#ﾀｸﾞを追加する
		taglist = [s.strip() for s in re.split('[、,]',request.form.get("tag"))]

		for tag in taglist:
			if tag!="":NOTE.addtag(ID,tag)

		return ID
	#}}}

	def update(ID,request):
		#問題ﾃﾞｰﾀの更新を行う

		#旧ﾃﾞｰﾀのﾀｲﾄﾙを取得しておく	
		name = NOTE.get(ID)["name"]
		
		#挿入ﾃﾞｰﾀを作成し、入力をﾃﾞｰﾀﾍﾞｰｽに入れる
		insdata={
			"ID"      : ID,
			"name"    : request.form.get("title"),
			"content" : request.form.get("content").replace('\r\n','\n').strip(),
		}

		#judge/phraseのｺﾒﾝﾄの参照を置き換えなおす
		for QID,C in DB().Table("Question_J").Record(f"C LIKE '%{name}%'").fetch(["ID","C"]):
			DB().Table("Question_J").Record(f"ID={QID}").update({"C":C.replace("{"+name+"}","{"+request.form.get("title")+"}")})

		for QID,C in DB().Table("Question_P").Record(f"C LIKE '%{name}%'").fetch(["ID","C"]):
			DB().Table("Question_P").Record(f"ID={QID}").update({"C":C.replace("{"+name+"}","{"+request.form.get("title")+"}")})

		#ﾃﾞｰﾀﾍﾞｰｽに反映
		DB().Table("note").Record(f"ID='{ID}'").update(insdata)

		#前タグを取得
		tagnamelist = NOTE.get(ID)["tag"]

		#タグを削除
		DB().Table("note_tag").Record(f"NID='{ID}'").delete()
	
		#修正前タグリストから、タグを消すかチェック
		for tagname in tagnamelist:
			NOTE.deltag(tagname)			

		#ﾀｸﾞを追加する
		taglist = [s.strip() for s in re.split('[、,]',request.form.get("tag"))]
		for tag in taglist:
			if tag!="":NOTE.addtag(ID,tag)
	
	def delete(ID):
		#前タグを取得
		tagnamelist = NOTE.get(ID)["tag"]

		#タグを削除
		DB().Table("note_tag").Record(f"NID='{ID}'").delete()
	
		#修正前タグリストから、タグを消すかチェック
		for tagname in tagnamelist:
			NOTE.deltag(tagname)

		#問題と回答をそれぞれ削除
		DB().Table("note").Record(f"ID='{ID}'").delete()


