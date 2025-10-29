import sqlite3

sql = "/home/asdf/.floorp/9ky1rq5e.a/storage/default/moz-extension+++7c90f06b-0181-4a13-a36b-4e4abb59d4b2^userContextId=4294967295/idb/3647222921wleabcEoxlt-eengsairo.sqlite"
with sqlite3.connect(sql) as conn:
	cursor = conn.cursor()
	# cursor.execute("SELECT object_store_id, key, data FROM object_data WHERE ('' || key || '') LIKE '0ijeefoTfuujoht';")
	cursor.execute("SELECT object_store_id, key, data FROM object_data")
	for row in cursor:
		print(row[1])

