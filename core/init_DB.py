import pickle

from libs.DATABASE import DB
from setting import DB_PATH,KEY

def init_DB():#DBﾌｧｲﾙがないときの設定を行う
	DB.dbname=DB_PATH
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
	note   = data.add_table("note"           ,["ID","name","content"])
	N_tag  = data.add_table("note_tag"       ,["NID","tag_id"])
	_      = data.add_table("per_user"       ,["user","mode","ID","Chara","rate"])
	_      = data.add_table("Dairy"          ,["date","user","J_ac","J_wa","P_ac","P_wa"])

	#scoreの日付にｲﾝﾃﾞｯｸｽ
	with data.connect as d:
		conn,cur = d
		cur.execute("CREATE INDEX datetime_idx ON Score(datetime)")

	#IDlistに空のﾘｽﾄ	
	common.add_record({
		"IDlist_J":pickle.dumps([]),
		"IDlist_P":pickle.dumps([]),
	})
