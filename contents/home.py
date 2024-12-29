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

from libs.DATABASE import DB
import contents.__parts as parts

def func():
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
		a = url_for('tagchange',word = e[0])
		#print(a)
		tmp+=f"""<a href="{a}"> {e[0]} </a><br><br>\n"""	

	# 画像データをHTMLに埋め込む
	page = render_template(
		'home.html',
		headlinks   = parts.headlink(), 
		graph       = 'data:image/png;base64,{}'.format(graph_url),
		graph2      = 'data:image/png;base64,{}'.format(graph_url2),
		taglink     = tmp,
	)

	matplotlib.pyplot.close()

	return page


