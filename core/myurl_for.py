from flask import url_for

def myurl_for(endpoint):
	try:
		res = url_for(endpoint)
	except:
		print(f"endpoint: '{endpoint}' is invalid !")
		res = ""

	return res
