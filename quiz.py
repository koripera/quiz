from textwrap import dedent
import random
import socket
import pickle
from pickle import dumps,loads
import os
import re
import sys
import bisect
from operator import itemgetter as iget
from datetime import datetime,timedelta
import platform

import json
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # GUIバックエンドを使わない設定

import io
import base64

from flask import Flask,render_template,send_file,request,redirect,session,url_for
from werkzeug.exceptions import NotFound
from werkzeug.security import generate_password_hash, check_password_hash

import logging
from waitress import serve

#DB操作
from DATABASE import DB

"""
tagの簡易切り替え
"""
#--------------------------------------------

#ﾃﾞｰﾀﾍﾞｰｽの構成

#table:"users"
#(name:str,pass:str)

#table:"Score"
#(datetime:datetime,user:str,mode:str,ID:int,chara:str,result:1or0)

#table:"common"
#(IDlist_J:picklelist,IDlist_P:picklelist)
#IDlist_J:[int,int...]
#IDlist_P:[int,int...]

#table:"Question_J"
#(ID:int, about:pickle&list, name:str, Q:str, A:pickle&taple, C:str)
#about:[str,str,...]
#tag  :[str,str,...]
#A    :(("answer","〇"),("badanswer","×"),)

#table:"Question_P"
#(ID:int, about:pickle&list, name:str, Q:str, C:str)

#table:"Question_P_v"
#(ID:int,chara:str,answer:str)

#table:"Question_J_tag"
#(QID:int,tagID:int)

#table:"Question_P_tag"
#(QID:int,tagID:int)

#table:"tag"
#(ID:int,name:str)

#--------------------------------------------

#--------------------------------------------
DB.dbname="DATA.db"
key="testkey"
testusername ="testuser"
testpassword ="password"
test=True

def testdata():
	DB().Table("users").add_record({
		"name" : testusername,
		"pass" : generate_password_hash(testpassword),
	})

	#Judge問題
	ID=1
	IDlist=loads(DB().Table("common").Record().fetch("IDlist_J")[0][0])
	bisect.insort_left(IDlist, ID)
	DB().Table("common").Record().update({"IDlist_J":dumps(IDlist)})
	candidate = ["1","2","3","4","5"]
	A         = ["x","o","x","x","x"]

	insdata={
		"ID"    : ID,
		"about" : dumps(["math"]),
		"name"  : "足し算",
		"Q"     : "1+1={x}",
		"A"     : dumps( tuple((c,a) for c,a in zip(candidate,A)) ),
		"C"     : "comment",
	}
	DB().Table("Question_J").add_record(insdata)

	taglist = ["math"]

	for tag in taglist:
		if tag!="":QUESTION.addtag("Judge",ID,tag)
	
	#Phrase問題
	ID=1
	IDlist = loads(DB().Table("common").Record().fetch("IDlist_P")[0][0])
	bisect.insort_left(IDlist, ID)
	DB().Table("common").Record().update({"IDlist_P":dumps(IDlist)})

	insdata={
		"ID"    : ID,
		"about" : dumps(["math"]),
		"name"  : "足し算",
		"Q"     : "1+1={A}\n2+2={B}\n3+3={C}\n4+4={D}\n5+5={E}",
		"C"     : "comment",
	}

	DB().Table("Question_P").add_record(insdata)

	taglist = ["math"]
	for tag in taglist:
		if tag!="":QUESTION.addtag("Phrase",ID,tag)

	A={"A":"2","B":"4","C":"6","D":"8","E":"10"}
	
	for chara,answer in A.items():
		insdata={
			"ID"    : ID,
			"chara" : chara,
			"answer": answer,
		}
		DB().Table("Question_P_v").add_record(insdata)
#--------------------------------------------

app = Flask(__name__)
app.secret_key = key

def main():
	global app

	#初期ﾃﾞｰﾀの作成
	if not os.path.isfile(DB.dbname):
		setup()
		testdata()#test用

	#ipの取得
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.connect(("192.168.100.1", 80))
		ip = s.getsockname()[0]
		s.close()
	except:
		ip = None

	#入力でﾎｽﾄを選択
	#app.run(port=8000 ,debug=False)
	while True:
		val = input("y:local  n:open:")

		if val=="y":
			clear()
			print("http://localhost:8000/home")
			serve(app,port=8000)
			break

		elif val=="n":
			clear()
			print(f"http://{ip}:8000/home")
			serve(app,host=ip,port=8000)
			break

def setup():
	#DBﾌｧｲﾙがないときの設定を行う
	data = DB()

	user   = data.add_table("Users"          ,["name","pass"])
	score  = data.add_table("Score"          ,["datetime","user","mode","ID","chara","result"])
	common = data.add_table("Common"         ,["IDlist_J","IDlist_P"])
	QJ     = data.add_table("Question_J"     ,["ID","about","name","Q","A","C"])
	QJ_tag = data.add_table("Question_J_tag" ,["QID","tagID"])
	QP     = data.add_table("Question_P"     ,["ID","about","name","Q","C"])
	QP_tag = data.add_table("Question_P_tag" ,["QID","tagID"])
	QP_v   = data.add_table("Question_P_v"   ,["ID","chara","answer"])
	tag    = data.add_table("tag"            ,["ID","name"])

	#scoreの日付にｲﾝﾃﾞｯｸｽ
	with DB().connect as d:
		conn,cur = d
		cur.execute("CREATE INDEX datetime_idx ON Score(datetime)")

	#IDlistに空のﾘｽﾄ	
	common.add_record({
		"IDlist_J":pickle.dumps([]),
		"IDlist_P":pickle.dumps([]),
	})

#GETの処理まとめ	
@app.route('/<mode>', methods=["GET"])
@app.route('/<mode>/<ID>', methods=["GET"])
def guide_get(mode="",ID=""):
	page={
		"home"            : home,      #学習履歴の表示
		"login"           : login,     #ﾛｸﾞｲﾝ画面の表示
		"logout"          : logout,    #ﾛｸﾞｱｳﾄしてhomeに移動
		"infiniteQ_Judge" : Q_Judge,   #二択問題の出題
		"infiniteQ_Phrase": Q_Phrase,  #短答問題の出題
		"Edit_Judge"      : Edit_J_get,#二択問題の編集画面
		"Edit_Phrase"     : Edit_P_get,#短答問題の編集画面
		"tagchange"       : tagchange, #セッションのタグを設定
	}

	if mode in page  : return page[mode]([mode,ID])
	else             : return "nopage" ,404

#POSTの処理まとめ
@app.route('/<mode>', methods=["POST"])
@app.route('/<mode>/<ID>', methods=["POST"])
def guide_post(mode="",ID=""):
	items={
		"login"           : USERS.login,#ﾛｸﾞｲﾝ情報の確認
		"add_J"           : add_J,      #二択問題の追加
		"add_P"           : add_P,      #短答問題の追加
		"check_J"         : check_J,    #二択問題の回答ﾁｪｯｸ
		"check_P"         : check_P,    #短答問題の回答ﾁｪｯｸ
		"Edit_Judge"      : Edit_J_post,#二択問題の編集入力処理
		"Edit_Phrase"     : Edit_P_post,#短答問題の編集入力処理
		"set_search"      : set_search, #出題問題の検索の設定
	}

	if mode in items : return items[mode]([mode,ID])

def home(path):#/*{{{*/
	#過去60日の日付の取得
	today = datetime.now()
	dates = list(reversed([(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(60)]))

	result=[]   #日付と正答数と誤答数を格納
	result2=[]  #日付と正答率を格納
	highest=100 #表の上限値、最低100、100超えたらその値

	#検索するﾕｰｻﾞ
	username = session["username"] if "username" in session else ""

	with DB().connect as d:
		conn,cur = d

		#一時ﾃｰﾌﾞﾙを作る
		cur.execute(f'''
			CREATE TEMPORARY TABLE temp AS
			SELECT * FROM Score WHERE user = '{username}' AND datetime >= DATE('now', '-60 days')
		''')

		#正答と誤答のｶｳﾝﾄ
		for date in dates:
			cur.execute("""
				SELECT 	SUM(CASE WHEN result = 1 THEN 1 ELSE 0 END) AS ac,
						SUM(CASE WHEN result = 0 THEN 1 ELSE 0 END) AS wa
				FROM temp
				WHERE datetime BETWEEN ? AND ?;
			""",(date+" 00:00",date+" 23:59"))
			res=cur.fetchone()

			res = list(res)
			if res[0] == None : res[0]=0 
			if res[1] == None : res[1]=0 

			#表の上限値をﾃﾞｰﾀ量で変える
			if highest < res[0]+res[1] : highest = res[0]+res[1]

			result.append((date,res[0],res[1]))
			if res[0]+res[1]!=0:
				result2.append((date,res[0]/(res[0]+res[1])))
			else:
				result2.append((date,None))
			
	#正答緑、誤答ｵﾚﾝｼﾞの積上棒ｸﾞﾗﾌを作成する
	fig, ax = plt.subplots(figsize=(16, 9))
	fig.patch.set_facecolor((0, 0, 0, 0))
	fig.subplots_adjust(left=0.05, right=1, top=0.95, bottom=0.05)
	ax.set_facecolor((0, 0, 0, 0))
	ax.grid(axis="y",color=(0.5, 0.5, 0.5, 1),linestyle=':')
	ax.spines["right"].set_visible(False)
	ax.spines["top"].set_visible(False)
	ax.tick_params(labelsize=15,bottom=False,labelbottom=False)
	ax.set_xlim(-2, 63)
	ax.set_ylim(bottom=0,top=max(max([i[1]+i[2] for i in result]),100))

	left=[i for i in range(60)]
	plt.bar(left, [i[1] for i in result], color="green",width=0.5)
	plt.bar(left, [i[2] for i in result], bottom=[i[1] for i in result], color="orange",width=0.5)

	img = io.BytesIO()
	plt.savefig(img, format='png')
	img.seek(0)
	graph_url = base64.b64encode(img.getvalue()).decode()

	#正答率の折れ線グラフを作成する
	plt.close()

	fig, ax = plt.subplots(figsize=(16, 9))
	fig.patch.set_facecolor((0, 0, 0, 0))
	fig.subplots_adjust(left=0.05, right=1, top=0.95, bottom=0.05)
	ax.set_facecolor((0, 0, 0, 0))
	ax.grid(axis="y",color=(0.5, 0.5, 0.5, 1),linestyle=':')
	ax.spines["right"].set_visible(False)
	ax.spines["top"].set_visible(False)
	ax.tick_params(labelsize=15,bottom=False,labelbottom=False)
	ax.set_xlim(-2, 63)
	ax.set_ylim(bottom=0,top=1)
	ax.set_yticks([i/10 for i in range(11)])
	
	x=[i for i,e in enumerate(result2) if e[1]!=None]
	y=[e[1] for e in result2 if e[1]!=None]
	ax.plot(x,y,marker="o")

	img2 = io.BytesIO()
	plt.savefig(img2, format='png')
	img2.seek(0)
	graph_url2 = base64.b64encode(img2.getvalue()).decode()

	#tagを設定するリンクを作る
	#ﾀｸﾞ名のﾘｽﾄを取得する
	names = DB().Table("tag").Record().fetch("name")
	tmp = ""	

	#各ﾀｸﾞに変更するﾘﾝｸを作成する
	for e in names:
		#print(e)
		a = url_for('guide_get', mode = 'tagchange',ID = e[0])
		#print(a)
		tmp+=f"""<a href="{a}"> {e[0]} </a><br><br>\n"""	

	# 画像データをHTMLに埋め込む
	data = render_template(
		'home.html',
		login=loguide(), 
		graph='data:image/png;base64,{}'.format(graph_url),
		graph2='data:image/png;base64,{}'.format(graph_url2),
		taglink = tmp,
	)

	matplotlib.pyplot.close()

	return data#/*}}}*/

def tagchange(path):
	session["inQ"]=""
	session["inC"]=""
	session["tag"]=[path[1],]
	return redirect(url_for("guide_get",mode="infiniteQ_Judge"))

def login(path):
	return render_template("login.html",login=loguide())

def logout(path):
	session.clear()
	return redirect(url_for('guide_get',mode="login"))

def Q_Judge(path):
	#ﾍﾟｰｼﾞ内で使うので、ｾｯﾃｨﾝｸﾞ
	if "inQ" not in session:session["inQ"]=""
	if "inC" not in session:session["inC"]=""
	if "tag" not in session:session["tag"]=[]
	return render_template('infiniteQ_Judge.html',login=loguide(),tag=" ".join(session["tag"]),inQ=session["inQ"],inC=session["inC"])

def Q_Phrase(path):
	#ﾍﾟｰｼﾞ内で使うので、ｾｯﾃｨﾝｸﾞ
	if "inQ" not in session:session["inQ"]=""
	if "inC" not in session:session["inC"]=""
	if "tag" not in session:session["tag"]=[]
	return render_template('infiniteQ_Phrase.html',login=loguide(),tag=" ".join(session["tag"]),inQ=session["inQ"],inC=session["inC"])

def Edit_J_get(path):
	ID = path[1]

	if ID == "new":#新規ﾃﾞｰﾀ
		return render_template('Edit_Judge.html',login = loguide())
	
	else:#既存ﾃﾞｰﾀの表示
		#問題の辞書ﾃﾞｰﾀ取得
		Question = QUESTION.JUDGE.get(ID)

		#該当IDがなければ、404ｴﾗｰ
		if Question==None:return "nopage",404		

		
		result_html = render_template(
			'Edit_Judge.html',
			about     = ",".join(Question["about"]),
			title     = Question["name"],
			tag       = ",".join(Question["tag"]),
			Q         = Question["Q"],
			candidate = "\n".join([c for c,a in Question["A"]]),
			A         = "\n".join([a for c,a in Question["A"]]),
			comment   = Question["C"],
			login     = loguide()
		)

		return result_html

def Edit_J_post(arg):
	ID = arg[1]
	if request.form.get("addnew") != None:
		#新ﾃﾞｰﾀ追加後、その編集ﾍﾟｰｼﾞへ移動
		ID = QUESTION.JUDGE.make(request)
		return redirect(f'../Edit_Judge/{ID}')

	elif request.form.get("update") != None:
		#ﾃﾞｰﾀの更新後、その編集ﾍﾟｰｼﾞに移動
		QUESTION.JUDGE.update(ID,request)
		return redirect(f'../Edit_Judge/{ID}')

	elif request.form.get("delete") != None:
		#ﾃﾞｰﾀ削除後、新規作成ﾍﾟｰｼﾞに移動			
		QUESTION.JUDGE.delete(ID)
		return redirect(f'../Edit_Judge/new')


def Edit_P_get(path):
	mode,ID = path

	if ID == "new":#新規ﾃﾞｰﾀ
		return render_template('Edit_Phrase.html',login = loguide())
	
	else:#既存ﾃﾞｰﾀの表示
		#問題の辞書ﾃﾞｰﾀ取得
		Question = QUESTION.PHRASE.get(ID)			

		"""
		log = {}
		#ﾛｸﾞｲﾝ時回答履歴を編集可能にする
		if "username" in session:
			for chara,answer in Question["A"].items():	
				data = QUESTION.PHRASE.SCORE.get(session["username"],(ID,chara))
				log[f"log{chara}"] = "".join(["〇" if e else "×" for e in data])
		"""
		
		result_html = render_template(
			'/Edit_Phrase.html',
			login   = loguide(),
			about   = ",".join(Question["about"]),
			title   = Question["name"],
			tag     = ",".join(Question["tag"]),
			Q       = Question["Q"],
			comment = Question["C"],
			**Question["A"],#{"A":ans1,"B":ans2,"C":ans3}
			#**log,	#{"logA":log1,"logB":log2,"logC":log3}										
		)
		return result_html

def Edit_P_post(arg):
	ID=arg[1]
	if request.form.get("addnew") != None:
		#新ﾃﾞｰﾀ追加後、その編集ﾍﾟｰｼﾞへ移動
		ID = QUESTION.PHRASE.make(request)
		return redirect(f'../Edit_Phrase/{ID}')

	elif request.form.get("update") != None:
		#ﾃﾞｰﾀの更新後、その編集ﾍﾟｰｼﾞに移動
		QUESTION.PHRASE.update(ID,request)
		return redirect(f'../Edit_Phrase/{ID}')

	elif request.form.get("delete") != None:
		#ﾃﾞｰﾀ削除後、新規作成ﾍﾟｰｼﾞに移動			
		QUESTION.PHRASE.delete(ID)
		return redirect(f'../Edit_Phrase/new')


def set_search(arg):
	ID=arg[1]
	session["tag"]=request.form.get("tag").split()
	session["inQ"]=request.form.get("inQ")
	session["inC"]=request.form.get("inC")
	if ID=="J":
		return redirect(url_for('guide_get',mode="infiniteQ_Judge"))
	if ID=="P":
		return redirect(url_for('guide_get',mode="infiniteQ_Phrase"))


def loguide():
	#ﾛｸﾞｲﾝﾛｸﾞｱｳﾄ表示の切替
	aa,bb=url_for("guide_get",mode="logout"),url_for("guide_get",mode="login")
	A=f'<a href="{aa}">　ログアウト　</a>'
	B=f'<a href="{bb}">　ログイン　</a>'
	return A if "username" in session else B

def add_J(arg):
	#問題の追加を行う
	#session inQ,inCは出題ﾍﾟｰｼﾞ遷移時にﾃﾞﾌｫﾙﾄ設定	

	#出題可能なIDの取得[ID,ID...]
	all_ID = QUESTION.JUDGE.valid_id(tag=session["tag"],inQ=session["inQ"],inC=session["inC"])

	#出題可能な問題がなければ、処理しない
	if not all_ID:return "noQuestion"

	#画面下部、問題の一覧を作って表示する
	QSET10=""

	for i in range(10):		
		if "username" in session:
			#10問ﾗﾝﾀﾞﾑで取る[ID,ID...]
			IDs = random.choices(all_ID,k=10)

			#2**(10-直近10の正解数)[1024, 512, 256, 128, 64, 32, 16, 8, 4, 2, 1]
			w = [2**(10 - SCORE.result(session["username"],ID[0],None)[-10:].count(1)) for ID in IDs]

			#choicesはﾘｽﾄで返る
			ID  = random.choices(IDs,weights=w)[0]

		else:
			ID = random.choice(all_ID)
	
		#問題ﾃﾞｰﾀの取得
		Question = QUESTION.JUDGE.get(ID[0])

		#問題ﾃﾞｰﾀの一部の置き換え
		num = random.randrange(len(Question["A"]))
		Q_txt = Question["Q"].replace("{x}",Question["A"][num][0])

		#ID,部分変換のindex,問題文等をHTMLに記入
		QSET10 += render_template(
			'QSET_Judge.html',
			Q_id          = ID[0],
			Q_num         = num,
			about         = f"< {' '.join(Question['about'])} >",
			Q_txt         = Q_txt,								  
		)

	return QSET10

def check_J(arg):
	#答え合わせを行う#jsonを受け取り、jsonを返す
	#Qid,num,answerを受け取る#inputDataはdict
	QID    = int(request.json["Qid"])#pathに使用するID
	num    = int(request.json["num"])#1問題中のﾗﾝﾀﾞﾑ
	answer = 1 if request.json["answer"]=="〇" else 0 #押したﾎﾞﾀﾝ

	#問題ﾃﾞｰﾀの取得
	Qdata = QUESTION.JUDGE.get(QID)
	ans   = 1 if Qdata["A"][num][1]=="o" else 0
	A      = "〇を押しました" if answer else "×を押しました"
	result = "<font color='red'>正解</font>" if ans==answer else "<font color='blue'>不正解</font>"

	ret = {
		"result1" : A,
		"result2" : result,
		"Comment" : f"{Qdata['C']}\n\ntag:{','.join(Qdata['tag'])}"
	}

	#回答を記録
	if "username" in session:
		SCORE.insert(session['username'],QID,None,1 if ans==answer else 0)
		ret["logg"] = "".join(["〇" if e else "×" for e in SCORE.result(session['username'],QID,None)])

	else:
		ret["logg"] = ""

	return ret



def add_P(arg):
	#画面下部、問題の一覧を作って表示する

	#出題可能なIDの取得[(ID,chara),(ID,chara)...]
	all_ID = QUESTION.PHRASE.valid_id(tag=session["tag"],inQ=session["inQ"],inC=session["inC"])

	if not all_ID:return "noQuestion"

	QSET10=""

	for i in range(10):
		#ﾛｸﾞｲﾝ時は問題の出題重みを定める
		if "username" in session:
			#10問ﾗﾝﾀﾞﾑで取る[(ID,chara)(ID,chara)...]
			datas = random.choices(all_ID,k=10)

			#2**(10-直近10の正解数)[1024, 512, 256, 128, 64, 32, 16, 8, 4, 2,1] 
			w = [2**(10 - SCORE.result(session["username"],data[0],data[1])[-10:].count(1)) for data in datas]
			data  = random.choices(datas,weights=w)[0]

		else:
			#IDをﾗﾝﾀﾞﾑに選択ID=(ID,chara)
			data = random.choice(all_ID)

		#出題するIDと文字
		ID,chara=data

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


		QSET10 += render_template('QSET_Phrase.html',
						  about = f"< {' '.join( Question['about']) } >",
						  Q     = Question["Q"],
						  A     = "答："+answer,
						  C     = Question["C"],
						  Q_id  = ID,
						  abc   = f"'{chara}'"
						  )		

	return QSET10


def check_P(arg):
	inputData = request.json

	#Qid,abc,answerを受け取る
	QID    = int(inputData["Qid"])#pathに使用するID
	abc    = inputData["abc"]     #問題中の出題箇所
	answer = inputData["answer"]  #自己申告の○×

	#ﾛｸﾞｲﾝ状態
	if "username" in session:
		SCORE.insert(session['username'],QID,abc,1 if answer=="〇" else 0)
		return {"log":"".join(["〇" if e else "×" for e in SCORE.result(session['username'],QID,abc)])}

	#ﾛｸﾞｱｳﾄ状態
	else:
		return {"log":""}

def get_east_asian_width_count(text):
	from unicodedata import east_asian_width as str_w
	return sum(2 if str_w(c) in "FWA" else 1 for c in text)

def missingnum(sortedlist):
	#数値のみのリストから欠番を探す
	data = sortedlist

	#欠番無
	if len(data) == 0            : ID = 1
	elif len(data) == data[-1]   : ID = data[-1]+1

	#欠番有
	else:
		ok  = -1      #index最小-1			
		ng = len(data)#index最大+1

		while 1 < (ng-ok):
			mid = (ok+ng) // 2

			#番号とdata(index)-1が
			#　同一　→　手前に欠番無し　→　okをmidに
			#非同一　→　手前に欠番有り　→　ngをmidに
			#欠番がなければ、data[0]=1.data[1]=2.data[2]=3...
			#print(ok,"//",f"index:{mid} num:{data[mid]-1}","//",ng)
			if mid == data[mid]-1 : ok = mid
			else                  : ng = mid
			
		#ok,mid,ngはｲﾝﾃﾞｯｸｽを示す
		#okは最終の正常なｲﾝﾃﾞｯｸｽ→ok+1に挿入する→数値はok+2
		#print(ok,ng)
		ID = ok + 2

	return ID


class USERS:
	def login(arg):
		#ﾛｸﾞｲﾝ処理
		if request.form.get("login")!=None:
			name,password = request.form.get("name"),request.form.get("pass")

			#ﾕｰｻﾞｰがあるか
			if (matched:=DB().Table("users").Record(f"name='{name}'").fetch("pass")):
				#ﾊﾟｽが合うか
				if check_password_hash(matched[0][0],password):
					session['username'] = name
					return redirect("home")

				#ﾊﾟｽ不一致			
				else:
					message = "Password is incorrect."
					return render_template("login.html",
											login=loguide(),
											message=message)
			#ﾕｰｻﾞｰなし
			else:
				message = "User does not exist"
				return render_template("login.html",
										login=loguide(),
										message=message)


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

			#judge側でタグ利用されているか
			q=dedent(
			f"""
			SELECT DISTINCT Question_J.ID FROM Question_J
			JOIN Question_J_tag ON Question_J.id = Question_J_tag.QID
			JOIN tag ON Question_J_tag.tagID = tag.ID
			WHERE tag.name = "{name}"
			""")

			cur.execute(q)

			jtag = cur.fetchall()#ﾚｺｰﾄﾞがなければ空のﾘｽﾄ

			if not jtag:
				q=dedent(
				f"""
				SELECT DISTINCT Question_P.ID FROM Question_P
				JOIN Question_P_tag ON Question_P.id = Question_P_tag.QID
				JOIN tag ON Question_P_tag.tagID = tag.ID
				WHERE tag.name = "{name}"
				""")
				cur.execute(q)
				ptag = cur.fetchall()
				if not ptag:
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
			IDlist = loads(common.fetch("IDlist_J")[0][0])
			ID = missingnum(IDlist)

			#使用したIDをｿｰﾄしてﾘｽﾄに入れﾃﾞｰﾀﾍﾞｰｽを更新
			bisect.insort_left(IDlist, ID)
			common.update({"IDlist_J":dumps(IDlist)})

			#挿入ﾃﾞｰﾀの作成し、入力をﾃﾞｰﾀﾍﾞｰｽに入れる
			candidate = request.form.get("candidate").replace('\r\n','\n').strip().split("\n")
			A         = request.form.get("A").replace('\r\n','\n').strip().split("\n")

			insdata={
				"ID"    : ID,
				"about" : dumps(re.split("[、,]",request.form.get("about"))),
				"name"  : request.form.get("title"),
				"Q"     : request.form.get("Q").replace('\r\n','\n').strip(),
				"A"     : dumps( tuple((c,a) for c,a in zip(candidate,A)) ),
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
			candidate = request.form.get("candidate").replace('\r\n','\n').strip().split("\n")
			A         = request.form.get("A").replace('\r\n','\n').strip().split("\n")

			insdata={
				"ID"    : ID,
				"about" : dumps( re.split("[、,]",request.form.get("about")) ),
				"name"  : request.form.get("title"),
				"Q"     : request.form.get("Q").replace('\r\n','\n').strip(),
				"A"     : dumps( tuple((c,a) for c,a in zip(candidate,A)) ),
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
			IDlist = loads(common.fetch("IDlist_J")[0][0])
			IDlist.remove(ID)
			common.update({"IDlist_J":dumps(IDlist)})

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
			IDlist = loads(common.fetch("IDlist_P")[0][0])
			ID = missingnum(IDlist)

			#使用したIDをｿｰﾄしてﾘｽﾄに入れﾃﾞｰﾀﾍﾞｰｽを更新
			bisect.insort_left(IDlist, ID)
			common.update({"IDlist_P":dumps(IDlist)})

			#挿入ﾃﾞｰﾀの作成し、入力をﾃﾞｰﾀﾍﾞｰｽに入れる
			insdata={
				"ID"    : ID,
				"about" : dumps( re.split("[、,]",request.form.get("about")) ),
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
				"about" : dumps( re.split("[、,]",request.form.get("about")) ),
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
			IDlist = loads(common.fetch("IDlist_P")[0][0])
			IDlist.remove(ID)
			common.update({"IDlist_P":dumps(IDlist)})

			#問題と部分問題と回答をそれぞれ削除
			DB().Table("Question_P").Record(f"ID={ID}").delete()
			DB().Table("Question_P_v").Record(f"ID={ID}").delete()

			#ﾕｰｻﾞｰの回答履歴を削除
			DB().Table("Score").Record(f"mode='Phrase' AND ID={ID}").delete()






def clear():
	os_name = platform.system()

	if os_name == "Windows":os.system('cls')
	else                   :os.system('clear')

if __name__ =="__main__":
	main()



