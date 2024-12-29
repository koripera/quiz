#.pyﾌｧｲﾙからfuncを、ﾃﾞｨﾚｸﾄﾘからblueprintを取得して、blueprintを作る
#ﾌｧｲﾙ,ﾃﾞｨﾚｸﾄﾘ名先頭が"_"のものは対象としない
#------------------------------#
__all__ = ["bp",]

#BPの名前とprefix Noneならﾃﾞｨﾚｸﾄﾘ名が使われる
endpoint_name = None
prefix        = None
#------------------------------#

import os
import importlib

from flask import Blueprint

# 現ﾃﾞｨﾚｸﾄﾘを取得
current_dir = os.path.dirname(__file__)

#blueprintの作成
dirname = os.path.basename(current_dir)
name = endpoint_name if endpoint_name != None else dirname
fix  = prefix if prefix != None else f"/{dirname}"
bp = Blueprint(name, __name__,url_prefix=fix)

#ﾓｼﾞｭｰﾙ名を入れる
bp_names   = []
func_names = []

# ﾃﾞｨﾚｸﾄﾘ内要素を取得する
for name in os.listdir(current_dir):

	#対象外ﾓｼﾞｭｰﾙにする
	if name.startswith("_"):
		continue

	#.pyならfunc
	elif name.endswith('.py') and name != '__init__.py':
		module_name = name[:-3]  # 拡張子を除外
		func_names.append(module_name)

	#dirならblueprints
	elif os.path.isdir(os.path.join(current_dir, name)) and name.isidentifier() and name != '__pycache__':
		module_name = name
		bp_names.append(module_name)

	else:
		continue

	# モジュールを動的にインポート
	importlib.import_module(f'.{module_name}', package=__name__)

	
#各ﾓｼﾞｭｰﾙ名(str)からﾓｼﾞｭｰﾙの要素を取得する

#ﾙｰﾃｨﾝｸﾞの追加
for name in func_names:
	args = vars()[name].args
	args["view_func"] = vars()[name].func
	bp.add_url_rule(**args)

#BluePrintsの結合
for sub_bp_name in bp_names:
	bp.register_blueprint(vars()[sub_bp_name].bp)

