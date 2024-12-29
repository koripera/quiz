#自分のﾃﾞｨﾚｸﾄﾘのﾓｼﾞｭｰﾙの__all__をimportする

import os
import importlib

# 現ﾃﾞｨﾚｸﾄﾘを取得
current_dir = os.path.dirname(__file__)

# ﾃﾞｨﾚｸﾄﾘ内要素を取得する
for name in os.listdir(current_dir):

	#対象外ﾓｼﾞｭｰﾙにする
	if name.startswith("_"):
		continue

	#.pyﾌｧｲﾙ
	elif name.endswith('.py') and name != '__init__.py':
		module_name = name[:-3]  # 拡張子を除外

	#ﾃﾞｨﾚｸﾄﾘ
	elif os.path.isdir(os.path.join(current_dir, name)) and name.isidentifier() and name != '__pycache__':
		module_name = name

	else:
		continue

	# モジュールを動的にインポート
	module = importlib.import_module(f'.{module_name}', package=__name__)

	if hasattr(module, "__all__"):
		names = module.__all__
		globals().update({name: getattr(module, name) for name in names})









