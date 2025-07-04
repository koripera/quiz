#ﾙｰﾃｨﾝｸﾞに必要な要素をargs,funcに記述する
#関数名"func"は変えないこと
#基本はﾌｧｲﾙ名,rule,endpointは同一にすること
#不要要素はｺﾒﾝﾄｱｳﾄすること

#------------------------------#
__all__ = ["args","func"]

args={
"rule"                      : "/home",
"methods"                   : ["GET"],
"endpoint"                  : "home",
#"strict_slashes"            : ,
#"provide_automatic_options" : ,
#"defaults"                  : ,
}
#------------------------------#

from datetime import datetime,timedelta
import matplotlib.pyplot as plt
import matplotlib
from flask import render_template, session,url_for
matplotlib.use('Agg')  # GUIバックエンドを使わない設定
import io
import base64

from core.QUESTION import QUESTION
from core.SCORE import SCORE

from libs.DATABASE import DB
import contents.__parts as parts

import random

def func():
	#回答率・正答率のグラフの作成
	graph_url,graph_url2=make_pic()

	#達成度を示すタグのリンク(一部停止)
	tag=taglink()

	# 画像データをHTMLに埋め込む
	page = render_template(
		'home.html',
		graph       = 'data:image/png;base64,{}'.format(graph_url),
		graph2      = 'data:image/png;base64,{}'.format(graph_url2),
		taglink     = tag,
	)

	return page

def make_pic():
	#過去60日の日付の取得
	today = datetime.now()
	dates = list(reversed([(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(60)]))

	result=[]   #日付と正答数と誤答数を格納
	result2=[]  #日付と二択正答率を格納
	result3=[]  #日付と短答正答率を格納

	highest=100 #表の上限値、最低100、100超えたらその値

	#検索するﾕｰｻﾞ
	username = session.get("username","")

	for date in dates:
		res = DB().Table("Dairy").Record(f"user = '{username}' AND date ='{date}'").fetchone("J_ac,J_wa,P_ac,P_wa")
		
		if res==None:
			res=(0,0,0,0)

		#表の上限値をﾃﾞｰﾀ量で変える
		if highest < sum(res) : highest = sum(res)

		result.append((date,res[0]+res[2],res[1]+res[3]))

		if res[0]+res[1]!=0:
			result2.append((date,res[0]/(res[0]+res[1])))
		else:
			result2.append((date,None))

		if res[2]+res[3]!=0:
			result3.append((date,res[2]/(res[2]+res[3])))
		else:
			result3.append((date,None))

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

	#
	x=[i for i,e in enumerate(result2) if e[1]!=None]
	y=[e[1] for e in result2 if e[1]!=None]
	ax.plot(x,y,marker="o")

	#
	x=[i for i,e in enumerate(result3) if e[1]!=None]
	y=[e[1] for e in result3 if e[1]!=None]
	ax.plot(x,y,marker="o")

	img2 = io.BytesIO()
	plt.savefig(img2, format='png')
	img2.seek(0)
	graph_url2 = base64.b64encode(img2.getvalue()).decode()

	matplotlib.pyplot.close()

	return graph_url,graph_url2

def taglink():
	#tagを設定するリンクを作る
	#ﾀｸﾞ名のﾘｽﾄを取得する
	username = session.get("username","")
	names = DB().Table("tag").Record().fetch("name")
	tmp = ""

	#一時ﾃｰﾌﾞﾙを作る
	with DB().connect as d:
		conn,cur = d		
		cur.execute(f'''
			CREATE TEMPORARY TABLE temp AS
			SELECT * FROM per_user WHERE user = '{username}'
		''')

	#各ﾀｸﾞに変更するﾘﾝｸを作成する
	for e in names:
		a = url_for('tagchange',word = e[0],link="infiniteQ_Judge")

		#達成率を表す値をいれる
		v=0
		if False:#実行に時間がかかるので一旦停止
			if username!="":
				#tag付きの問題を取る
				ids = QUESTION.JUDGE.valid_id(tag=[e[0]])
				ids = [e[0] for e in ids]

				placeholders = ','.join(['?'] * len(ids))
				query = f"SELECT rate FROM temp WHERE id IN ({placeholders})"
				with DB().connect as d:
					conn,cur = d
					cur.execute(f'''
					CREATE TEMPORARY TABLE temp AS
					SELECT * FROM per_user WHERE user = '{username}'
					''')

					cur.execute(query,ids)
					rows = cur.fetchall()

				values = [row[0] for row in rows if row[0] is not None]

				if len(ids):
					v=int((sum(values)/len(ids))*100)
				else:
					v=0

			else:
				v=0

		tmp+=f"""<a class="tag-progress" href="{a}" style="--percent: {v}%;order:{v}"> {e[0]} </a>\n"""

	
	return tmp
