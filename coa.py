import os
import platform
import sys
from functools import partial
from textwrap import dedent

"""
Command Operate Assistant

cuiでの関数の実行をサポート

onechoice/repchoice
func    : 実行する関数
options : funcに渡す第一引数の選択肢,又はfuncの選択肢
f       : 事前に実行する関数(引数なし),主に表示機能をつけておく、
message : 操作のメモ
rep     : 空白で入力時に前回と同じ操作をするかのbool
を設定

funcの関数又はoptionsに関数を設定する場合には、
ｺﾏﾝﾄﾞを引数として渡せるようにfunc(*arg)で可変長引数を設定しておくと良いが
せずにｴﾗｰが起きても、一応継続して利用できる

choicerはitemsは関数以外もstr,list,tupleなど渡せて
入力番号と入力したｺﾏﾝﾄﾞを返す
"""

def main():
	pass

#ﾒﾆｭｰを開かず一回実行
def execute(func,*args,**kwargs):
	func(*args,**kwargs)
		
#ｻﾌﾞﾒﾆｭｰを開いて、一回のみ実行
def onechoice(func,options,f=None,message="",exopt="back"):
	code,arg = choicer(options,f=f,message=message,exopt=exopt)
	clear()	
	if code==None:return
	try:
		if not arg:func(code)
		else      :func(code,*arg)
	except Exception as e:
		print(f"Error! : {e}")
	
#ｻﾌﾞﾒﾆｭｰを開いて、繰り返し実行
#選択肢が変わりうるものは、optionsを関数で渡す
def repchoice(func,options,f=None,message="",exopt="back",rep=False):
	previous = None
	call     = callable(options)
	while True:		
		if call:code,arg = choicer(options(),f=f,message=message,exopt=exopt,blank=rep)
		else   :code,arg = choicer(options  ,f=f,message=message,exopt=exopt,blank=rep)
		clear()

		#終了・正常動作・前回と同じ
		if code==None:
			return

		elif code!=0:
			try:
				if not arg:previous=partial(func,code)
				else      :previous=partial(func,code,*arg)
				previous()
			except Exception as e:
				print(f"Error! : {e}")

		elif rep and previous!=None and code==0:
			previous()

#ﾒﾆｭｰを開いて、入力を返す
def choicer(items,f=None,message="",exopt="back",blank=False):
	guide=["-"*10,
		   '\n'.join([f"0 : {exopt}"]+[f"{i+1} : {e.__name__ if callable(e) else e}" for i,e in enumerate(items)]),
		   "-"*10,"input:"]
	if message!="":
		message=f"{message}\n"
		guide.insert(1,message)

	guide="\n".join(guide)

	commands = {str(i+1): e for i,e in enumerate(items)}

	while True:
		print()
		if callable(f):
			try:
				f()
				print()
			except Exception as e:
				print(f"Error! : {e}")

		code=input(guide).split()
		
		if not code:
			if blank            : return 0,0
			else                : clear()
		elif code[0] == "0"     : return None,None
		elif code[0] in commands: return commands[code[0]] , code[1:]
		else:
			clear()
			print(f"input:{' '.join(code)}")
			print("input code is Undefined")
			

#ｾﾙﾌ入力して入力を返す
def inputer(note,isvalid,escape="0"):
	note=tx(
		f"""
		{"-"*10}
		{note}

		{escape}:back
		{"-"*10}
		input:
		""")

	while True:
		val = input(note)
		if val==escape:
			clear() 
			return None
		elif isvalid(val):
			clear()
			break
		else: 
			clear()
			print("error!\n")

	return val

#表示のﾘｾｯﾄ
def clear():
	os_name = platform.system()

	if os_name == "Windows":os.system('cls')
	else                   :os.system('clear')

#複数行の覚書
def tx(txt):
	return dedent(txt).strip()

if __name__ =="__main__":
	main()






