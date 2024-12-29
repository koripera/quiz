import pickle
import bisect

from werkzeug.security import generate_password_hash, check_password_hash

from core.QUESTION import QUESTION
from libs.DATABASE import DB
from setting import DB_PATH,KEY,testuser,testpass

DB.dbname=DB_PATH

def testdata():
	testusername = testuser
	testpassword = testpass

	DB().Table("users").add_record({
		"name" : testusername,
		"pass" : generate_password_hash(testpassword),
	})

	#Judge問題
	ID=1
	IDlist=pickle.loads(DB().Table("common").Record().fetch("IDlist_J")[0][0])
	bisect.insort_left(IDlist, ID)
	DB().Table("common").Record().update({"IDlist_J":pickle.dumps(IDlist)})
	candidate = ["1","2","3","4","5"]
	A         = ["x","o","x","x","x"]

	insdata={
		"ID"    : ID,
		"about" : pickle.dumps(["math"]),
		"name"  : "足し算",
		"Q"     : "1+1={x}",
		"A"     : pickle.dumps( tuple((c,a) for c,a in zip(candidate,A)) ),
		"C"     : "comment",
	}
	DB().Table("Question_J").add_record(insdata)

	taglist = ["math"]

	for tag in taglist:
		if tag!="":QUESTION.addtag("Judge",ID,tag)
	
	#Phrase問題
	ID=1
	IDlist = pickle.loads(DB().Table("common").Record().fetch("IDlist_P")[0][0])
	bisect.insort_left(IDlist, ID)
	DB().Table("common").Record().update({"IDlist_P":pickle.dumps(IDlist)})

	insdata={
		"ID"    : ID,
		"about" : pickle.dumps(["math"]),
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
