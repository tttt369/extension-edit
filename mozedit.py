import json
import sqlite3
import snappy
import mozencode

def extract_keys(obj, result):
	unnecessarily_keys = ["timeStamp", "version"]
	if isinstance(obj, dict):
		for key, value in obj.items():
			if key in unnecessarily_keys:
				continue

			if key == "userSettings":
				extract_keys(obj[key], result)
				continue

			if key == "whitelist":
				result["netWhitelist"] = value
				extract_keys(obj[key], result)
				continue

			if key == "userFilters":
				result["user.filters"] = value
				extract_keys(obj[key], result)
				continue

			result[key] = value
			extract_keys(obj[key], result)

sqlite_path = "/home/asdf/.floorp/5u0hark7.a/storage/default/moz-extension+++8f56cad7-4cf1-495e-818f-bafd4d2898bd^userContextId=4294967295/idb/3647222921wleabcEoxlt-eengsairo.sqlite"
backup_file = "/home/asdf/Downloads/my-ublock-backup_2025-10-29_15.12.26.txt"

with open(backup_file, "r") as f:
	original_data = json.loads(f.read())

filtered_dict = {}
extract_keys(original_data, filtered_dict)

changed_keys = set()
object_store_id = None

with sqlite3.connect(sqlite_path) as conn:
	cur = conn.cursor()
	conn.create_function("update_refcount", 2, lambda x, y: None)  # 2 args, do nothing
	
	for key, value in filtered_dict.items():
		# if not key == "selectedFilterLists":
		# 	continue
		encrpyt_key = mozencode.encode_caesar_shift1(key)
		key_result = encrpyt_key.encode()
		cur.execute("SELECT object_store_id FROM object_data WHERE key = ?", (key_result,))
		row = cur.fetchone()
		
		encoded_value = mozencode.encode_main(value)
		result = snappy.compress(encoded_value)
		
		if row:
			object_store_id = row[0]
			cur.execute("UPDATE object_data SET data = ? WHERE key = ?", (result, key_result))
			changed_keys.add(key)
		else:
			if object_store_id is None:
				cur.execute("SELECT object_store_id FROM object_data LIMIT 1;")
				obj_row = cur.fetchone()
				object_store_id = obj_row[0] if obj_row else 1
			
			cur.execute(
			    "INSERT INTO object_data (object_store_id, key, index_data_values, data) VALUES (?, ?, ?, ?)",
			    (object_store_id, key_result, None, result)
			)
	
conn.commit()

