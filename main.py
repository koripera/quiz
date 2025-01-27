import os
import socket

from waitress import serve

from contents import app
from libs.DATABASE import DB
from core.init_DB import init_DB
from core.testdata import testdata
from setting import DB_PATH
from util.tools import clear

def main():
	DB.dbname=DB_PATH
	

	if False:
		#ﾃﾞｰﾀ削除
		try:
			os.remove(DB.dbname)
		except:
			pass

	#ﾃﾞｰﾀ初期化
	if not os.path.isfile(DB.dbname):
		init_DB()

		#testﾃﾞｰﾀの挿入
		testdata()

	#ipの取得
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.connect(("192.168.100.1", 80))
		ip = s.getsockname()[0]
		s.close()
	except:
		ip = None

	#入力でﾎｽﾄを選択
	#app.run(port=8000 ,debug=True)
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

if 0:
	@app.route('/routes')
	def routes():
		routes = []
		for rule in app.url_map.iter_rules():
			routes.append({
				"endpoint" : rule.endpoint,
				"methods " : list(rule.methods),
				"url     " : str(rule)
			})

		textlist = ["".join([f"{k} : {v}\n" for k,v in e.items()]) for e in routes]
		txt = "\n".join(textlist)
		return txt 

if __name__ == '__main__':
	main()
