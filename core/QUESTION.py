from textwrap import dedent
import pickle
import bisect
import re
import random
from operator import itemgetter as iget

from flask import render_template,url_for
import markdown

from libs.DATABASE import DB

from core.NOTE import NOTE
from setting import DB_PATH
from util.tools import missingnum
from util.tools import get_east_asian_width_count

DB.dbname=DB_PATH

class QUESTION:
	def addtag(mode,QID,name):#任意のidにタグを追加
		
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
		table = "Question_J_tag" if mode=="Judge" else "Question_P_tag"
		with DB().connect as d:
			conn,cur = d
			cur.execute(f'INSERT INTO {table} VALUES (?,?)',(QID,tagID))
			conn.commit()

	def deltag(name):#タグが1個もなくなるとき、タグを消す
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


	class JUDGE:
		def valid_id(tag=None,inQ="",inC=""):
			#問題のIDﾘｽﾄを返す
			#タグ検索→文字列検索の順で行い、それぞれ、onoffが出来るように
			if tag==None:tag=[]
			word = 1 if inQ!="" or inC!="" else 0
			
			#通常
			q=dedent(
				"""
				SELECT DISTINCT Question_J.ID FROM Question_J
				""")

			#ﾀｸﾞかつ文字列
			if tag and word:
				q=dedent(
				f"""
				SELECT id 
				FROM Question_J
				WHERE ID IN (
					SELECT Question_J.ID
					FROM Question_J
					JOIN Question_J_tag ON Question_J.id = Question_J_tag.QID
					JOIN tag ON Question_J_tag.tagID = tag.ID
					WHERE tag.name IN ({",".join("?"*len(tag))})
					GROUP BY Question_J.ID
					HAVING COUNT(Question_J.ID) = {len(tag)})
				AND (Q LIKE '%{inQ}%' AND C LIKE '%{inC}%')
				""")

			#tagのみ
			elif tag:
				q+=dedent(
				f"""
				JOIN Question_J_tag ON Question_J.id = Question_J_tag.QID
				JOIN tag ON Question_J_tag.tagID = tag.ID
				WHERE tag.name IN ({",".join("?"*len(tag))})
				GROUP BY Question_J.id
				HAVING COUNT(Question_J.id) = {len(tag)}
				""")

			#文字列のみ
			elif word:
				q+=dedent(
				f"""
				WHERE Q LIKE '%{inQ}%' AND C LIKE '%{inC}%'
				""")

			with DB().connect as d:
				conn,cur = d
				if tag:cur.execute(q,tuple(tag))
				else  :cur.execute(q)

				#ﾀﾌﾟﾙのまま返す			
				return cur.fetchall()

		def to_html(ID):
			#IDからhtmlの出題形式で出力

			#問題ﾃﾞｰﾀの取得
			Question = QUESTION.JUDGE.get(ID)

			#問題ﾃﾞｰﾀの一部の置き換え
			if len(Question["A"]):
				num = random.randrange(len(Question["A"]))
				Q_txt = Question["Q"].replace("{x}",Question["A"][num][0])
			else:
				num = None#表示はされる、jsのエラーでcheck_jには伝わらない
				Q_txt = Question["Q"]

			#ID,部分変換のindex,問題文等をHTMLに記入
			return render_template(
				'parts/QSET_Judge.html',
				to_edit       = url_for("edit.judge",ID=ID),
				Q_id          = ID,
				Q_num         = num,
				about         = f"< {' '.join(Question['about'])} >",
				Q_txt         = Q_txt,								  
			)

		def get(ID):
			#問題の辞書を返す
			key = ["ID","about","name","Q","A","C"]
			val = DB().Table("Question_J").Record(f"ID={ID}").fetch()
			if val==[]:return None
			val = val[0]

			Question = {k:v for k,v in zip(key,val)}

			Question["about"] = pickle.loads(Question["about"])

			#問題につけられているタグのIDを取得 →　タグのIDから、タグの名前を取得
			tagidlist = DB().Table("Question_J_tag").Record(f"QID={ID}").fetch("tagID")			
			taglist = DB().Table("tag").Record(f"ID IN ({','.join([str(i[0]) for i in tagidlist])})").fetch("name")
			Question["tag"]   = [e[0] for e in taglist]	

			Question["A"]     = pickle.loads(Question["A"])

			return Question

		def make(request):
			#問題の新規作成

			#使うIDを探す
			common = DB().Table("Common").Record()
			IDlist = pickle.loads(common.fetch("IDlist_J")[0][0])
			ID = missingnum(IDlist)

			#使用したIDをｿｰﾄしてﾘｽﾄに入れﾃﾞｰﾀﾍﾞｰｽを更新
			bisect.insort_left(IDlist, ID)
			common.update({"IDlist_J":pickle.dumps(IDlist)})

			#挿入ﾃﾞｰﾀの作成し、入力をﾃﾞｰﾀﾍﾞｰｽに入れる
			#candidate = request.form.get("candidate").replace('\r\n','\n').strip().split("\n")
			#A         = request.form.get("A").replace('\r\n','\n').strip().split("\n")
			A         = request.form.getlist("ans[]")
			candidate = request.form.getlist("text[]")

			insdata={
				"ID"    : ID,
				"about" : pickle.dumps(re.split("[、,]",request.form.get("about"))),
				"name"  : request.form.get("title"),
				"Q"     : request.form.get("Q").replace('\r\n','\n').strip(),
				"A"     : pickle.dumps( tuple((c,a) for c,a in zip(candidate,A)) ),
				"C"     : request.form.get("comment").replace('\r\n','\n').strip(),
			}

			#問題と回答をそれぞれ追加
			DB().Table("Question_J").add_record(insdata)

			#ﾀｸﾞを追加する
			taglist = [s.strip() for s in re.split('[、,]',request.form.get("tag"))]

			for tag in taglist:
				if tag!="":QUESTION.addtag("Judge",ID,tag)

			return ID

		def update(ID,request):
			#問題ﾃﾞｰﾀの更新を行う

			#使うID
			ID = int(ID)

			#挿入ﾃﾞｰﾀを作成し、入力をﾃﾞｰﾀﾍﾞｰｽに入れる
			#candidate = request.form.get("candidate").replace('\r\n','\n').strip().split("\n")
			#A         = request.form.get("A").replace('\r\n','\n').strip().split("\n")
			A         = request.form.getlist("ans[]")
			candidate = request.form.getlist("text[]")


			insdata={
				"ID"    : ID,
				"about" : pickle.dumps( re.split("[、,]",request.form.get("about")) ),
				"name"  : request.form.get("title"),
				"Q"     : request.form.get("Q").replace('\r\n','\n').strip(),
				"A"     : pickle.dumps( tuple((c,a) for c,a in zip(candidate,A)) ),
				"C"     : request.form.get("comment").replace('\r\n','\n').strip(),
			}

			#ﾃﾞｰﾀﾍﾞｰｽに反映
			DB().Table("Question_J").Record(f"ID={ID}").update(insdata)

			#前タグを取得
			tagnamelist = QUESTION.JUDGE.get(ID)["tag"]

			#タグを削除
			DB().Table("Question_J_tag").Record(f"QID={ID}").delete()
		
			#修正前タグリストから、タグを消すかチェック
			for tagname in tagnamelist:
				QUESTION.deltag(tagname)			
	
			#ﾀｸﾞを追加する
			taglist = [s.strip() for s in re.split('[、,]',request.form.get("tag"))]
			for tag in taglist:
				if tag!="":QUESTION.addtag("Judge",ID,tag)
		
		def delete(ID):
			#使うID
			ID = int(ID)

			#前タグを取得
			tagnamelist = QUESTION.JUDGE.get(ID)["tag"]

			#タグを削除
			DB().Table("Question_J_tag").Record(f"QID={ID}").delete()
		
			#修正前タグリストから、タグを消すかチェック
			for tagname in tagnamelist:
				QUESTION.deltag(tagname)

			#IDlistからIDを削除する
			common = DB().Table("Common").Record()
			IDlist = pickle.loads(common.fetch("IDlist_J")[0][0])
			IDlist.remove(ID)
			common.update({"IDlist_J":pickle.dumps(IDlist)})

			#問題と回答をそれぞれ削除
			DB().Table("Question_J").Record(f"ID={ID}").delete()

			#ﾕｰｻﾞｰの回答履歴を削除
			DB().Table("Score").Record(f"mode='Judge' AND ID={ID}").delete()

	class PHRASE:
		def valid_id(tag=None,inQ="",inC=""):
			#問題のIDﾘｽﾄを返す
			#タグ検索→文字列検索の順で行い、それぞれ、onoffが出来るように
			if tag==None:tag=[]
			word = 1 if inQ!="" or inC!="" else 0
			
			#通常
			q=dedent(
				"""
				SELECT DISTINCT Question_P.ID FROM Question_P
				""")

			#ﾀｸﾞかつ文字列
			if tag and word:
				q=dedent(
				f"""
				SELECT id 
				FROM Question_P
				WHERE ID IN (
					SELECT Question_P.ID
					FROM Question_P
					JOIN Question_P_tag ON Question_P.id = Question_P_tag.QID
					JOIN tag ON Question_P_tag.tagID = tag.ID
					WHERE tag.name IN ({",".join("?"*len(tag))})
					GROUP BY Question_P.ID
					HAVING COUNT(Question_P.ID) = {len(tag)})
				AND (Q LIKE '%{inQ}%' AND C LIKE '%{inC}%')
				""")

			#tagのみ
			elif tag:
				q+=dedent(
				f"""
				JOIN Question_P_tag ON Question_P.id = Question_P_tag.QID
				JOIN tag ON Question_P_tag.tagID = tag.ID
				WHERE tag.name IN ({",".join("?"*len(tag))})
				GROUP BY Question_P.id
				HAVING COUNT(Question_P.id) = {len(tag)}
				""")

			#文字列のみ
			elif word:
				q+=dedent(
				f"""
				WHERE Q LIKE '%{inQ}%' AND C LIKE '%{inC}%'
				""")

			with DB().connect as d:
				conn,cur = d
				if tag:cur.execute(q,tuple(tag))
				else  :cur.execute(q)

				#ﾀﾌﾟﾙのまま返す			
				IDS = cur.fetchall()

			#検索してIDのみを取る,その後ﾃﾞｰﾀを取る
			IDS = tuple(iget(0)(i) for i in IDS)
			if len(IDS)==1:IDS=f"({IDS[0]})"
			return DB().Table("Question_P_v").Record(f"ID IN {IDS}").fetch(["ID","chara"])

		def to_html(ID,chara):
			#IDからhtmlの出題形式で出力

			Question = QUESTION.PHRASE.get(ID)

			#問題文の置き換え作業
			for c,v in Question["A"].items():
				#問題ﾃﾞｰﾀの問題部以外の置き換え
				if chara!=c:
					Question["Q"] = Question["Q"].replace("{"+c+"}",v)
				#問題部分を整える
				else:
					answer = v		
					width = get_east_asian_width_count(answer)-2
					if width < 2:width=2
					long = "__"*(width//2)
					Question["Q"] = Question["Q"].replace("{"+chara+"}",f"[{long}]")

			return render_template(
							'parts/QSET_Phrase.html',
							about     = f"< {' '.join( Question['about']) } >",
							Q         = Question["Q"],
							Q_id      = ID,
							abc       = f"{chara}"
							)	

		def get(ID):
			#問題の辞書を返す
			key = ["ID","about","name","Q","C"]
			val = DB().Table("Question_P").Record(f"ID={ID}").fetch()

			if val==[]:return None
			val = val[0]

			Question = {k:v for k,v in zip(key,val)}
			Question["about"] = pickle.loads(Question["about"])

			#問題につけられているタグのIDを取得 →　タグのIDから、タグの名前を取得
			tagidlist = DB().Table("Question_P_tag").Record(f"QID={ID}").fetch("tagID")			
			taglist = DB().Table("tag").Record(f"ID IN ({','.join([str(i[0]) for i in tagidlist])})").fetch("name")
			Question["tag"]   = [e[0] for e in taglist]

			#問題の問題部を取得#["chara","answer"]
			val = DB().Table("Question_P_v").Record(f"ID={ID}").fetch(["chara","answer"])
			Question["A"] = {k:v for k,v in val}

			return Question

		def make(request):
			#使うIDを探す
			common = DB().Table("Common").Record()
			IDlist = pickle.loads(common.fetch("IDlist_P")[0][0])
			ID = missingnum(IDlist)

			#使用したIDをｿｰﾄしてﾘｽﾄに入れﾃﾞｰﾀﾍﾞｰｽを更新
			bisect.insort_left(IDlist, ID)
			common.update({"IDlist_P":pickle.dumps(IDlist)})

			#挿入ﾃﾞｰﾀの作成し、入力をﾃﾞｰﾀﾍﾞｰｽに入れる
			insdata={
				"ID"    : ID,
				"about" : pickle.dumps( re.split("[、,]",request.form.get("about")) ),
				"name"  : request.form.get("title"),
				"Q"     : request.form.get("Q").replace('\r\n','\n').strip(),
				"C"     : request.form.get("comment").replace('\r\n','\n').strip(),
			}
	
			#ﾃﾞｰﾀﾍﾞｰｽに反映
			DB().Table("Question_P").add_record(insdata)

			#ﾀｸﾞを追加する
			taglist = [s.strip() for s in re.split('[、,]',request.form.get("tag"))]
			
			for tag in taglist:
				if tag!="":QUESTION.addtag("Phrase",ID,tag)

			#解答ﾃﾞｰﾀの作成と挿入
			A={}
			for s in list("ABCDEN"):
				if "" != (ans:=request.form.get(s).strip()):
					A[s] = ans
			
			for chara,answer in A.items():
				insdata={
					"ID"    : ID,
					"chara" : chara,
					"answer": answer,
				}
	
				#ﾃﾞｰﾀﾍﾞｰｽに反映
				DB().Table("Question_P_v").add_record(insdata)

			return ID

		def update(ID,request):
			#使うID
			ID=int(ID)
			
			#挿入ﾃﾞｰﾀの作成し、入力をﾃﾞｰﾀﾍﾞｰｽに入れる
			insdata={
				"ID"    : ID,
				"about" : pickle.dumps( re.split("[、,]",request.form.get("about")) ),
				"name"  : request.form.get("title"),
				"Q"     : request.form.get("Q").replace('\r\n','\n').strip(),
				"C"     : request.form.get("comment").replace('\r\n','\n').strip(),
			}
	
			#ﾃﾞｰﾀﾍﾞｰｽに反映
			DB().Table("Question_P").Record(f"ID={ID}").update(insdata)

			#前タグを取得
			tagnamelist = QUESTION.PHRASE.get(ID)["tag"]

			#タグを削除
			DB().Table("Question_P_tag").Record(f"QID={ID}").delete()
		
			#修正前タグリストから、タグを消すかチェック
			for tagname in tagnamelist:
				QUESTION.deltag(tagname)

			#ﾀｸﾞを追加する
			taglist = [s.strip() for s in re.split('[、,]',request.form.get("tag"))]
			
			for tag in taglist:
				if tag!="":QUESTION.addtag("Phrase",ID,tag)	


			#解答は一度全部消す
			#解答ﾃﾞｰﾀの作成と挿入
			DB().Table("Question_P_v").Record(f"ID={ID}").delete()

			A={}
			#入力ﾃﾞｰﾀを元に整理する
			for s in list("ABCDEN"):
				#入力を確認
				if "" != (ans:=request.form.get(s).strip()):
					A[s] = ans

				#解答がないものは解答履歴も消す
				else:
					DB().Table("Score").Record(f"ID={ID} AND chara='{s}'").delete()
			
			#整理したﾃﾞｰﾀをﾃﾞｰﾀﾍﾞｰｽに入れる
			for chara,answer in A.items():
				insdata={
					"ID"    : ID,
					"chara" : chara,
					"answer": answer,
				}
				DB().Table("Question_P_v").add_record(insdata)


					

		def delete(ID):
			#使うID
			ID = int(ID)

			#前タグを取得
			tagnamelist = QUESTION.PHRASE.get(ID)["tag"]

			#タグを削除
			DB().Table("Question_P_tag").Record(f"QID={ID}").delete()
		
			#修正前タグリストから、タグを消すかチェック
			for tagname in tagnamelist:
				QUESTION.deltag(tagname)

			#IDlistからIDを削除する
			common = DB().Table("Common").Record()
			IDlist = pickle.loads(common.fetch("IDlist_P")[0][0])
			IDlist.remove(ID)
			common.update({"IDlist_P":pickle.dumps(IDlist)})

			#問題と部分問題と回答をそれぞれ削除
			DB().Table("Question_P").Record(f"ID={ID}").delete()
			DB().Table("Question_P_v").Record(f"ID={ID}").delete()

			#ﾕｰｻﾞｰの回答履歴を削除
			DB().Table("Score").Record(f"mode='Phrase' AND ID={ID}").delete()
