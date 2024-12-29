import platform
import os

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

def clear():
	os_name = platform.system()

	if os_name == "Windows":os.system('cls')
	else                   :os.system('clear')
