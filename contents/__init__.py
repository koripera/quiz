#contents内を集約してFlaskappを作成する
#.pyﾌｧｲﾙからfuncを、ﾃﾞｨﾚｸﾄﾘからblueprintを取得して、appを作る
#ﾌｧｲﾙ,ﾃﾞｨﾚｸﾄﾘ名先頭が"_"のものは対象としない

#------------------------------#
__all__ = ["app",]

#それぞれNoneなら同ﾃﾞｨﾚｸﾄﾘから探す
template_path = "../templates"
static_path   = "../static"
#------------------------------#

import os
import importlib

from flask import Flask

from setting import KEY

# 現ﾃﾞｨﾚｸﾄﾘを取得
current_dir = os.path.dirname(__file__)

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

#appに各要素を登録する
#各ﾓｼﾞｭｰﾙ名(str)からﾓｼﾞｭｰﾙの要素を取得する

app = Flask(__name__)
if template_path != None : app.template_folder = template_path
if static_path != None   : app.static_folder   = static_path
app.secret_key = KEY

#ﾙｰﾃｨﾝｸﾞの追加
for name in func_names:
	args = vars()[name].args
	args["view_func"] = vars()[name].func
	app.add_url_rule(**args)

#BluePrintsの結合
for sub_bp_name in bp_names:
	app.register_blueprint(vars()[sub_bp_name].bp)


