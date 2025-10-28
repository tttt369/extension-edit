import sqlite3
import mozencode
import json

def read_ublock_backup(file) -> tuple[list, dict]:
	with open(file, "r") as f:
		original_data = json.loads(f.read())

	valid_keys = ["userSettings", "whitelist", "userFilters", "selectedFilterLists", "hiddenSettings", "dynamicFilteringString", "urlFilteringString", "hostnameSwitchesString"]
	valid_list = []
	for key in dict(original_data).keys():
		if key in valid_keys:
			if key == "userSettings":
				key = original_data["userSettings"]
				valid_list.extend(list(key.keys())) 
				continue

			if key == "whitelist":
				key = "netWhitelist"

			if key == "userFilters":
				key = "user.filters"
			valid_list.append(key)
	return valid_list, original_data

sqlite_path = "/home/asdf/.floorp/bkmxod65.a/storage/default/moz-extension+++1982fe76-589f-4eb1-b41a-ed916c444988^userContextId=4294967295/idb/3647222921wleabcEoxlt-eengsairo.sqlite"
backup_file = "/home/asdf/Downloads/my-ublock-backup_2025-10-27_14.47.28.txt"

added_list = []
valid_list, original_data= read_ublock_backup(backup_file)
file_ids = []
for key in valid_list:
	enc_key = mozencode.encode_caesar_shift1(key)
	with sqlite3.connect(sqlite_path) as conn:
		cur = conn.cursor()
		# cur.execute("SELECT key FROM object_data WHERE key = ?", (enc_key,))
		# row = cur.fetchone()
		# if row:
		# 	# 必要なら更新
		# 	cur.execute("UPDATE object_data SET data = ?, file_ids = ? WHERE key = ?", (data, file_ids, enc_key))
		# else:
		# 	# 挿入
		# 	cur.execute("INSERT INTO object_data (key, data, file_ids) VALUES (?, ?, ?)", (enc_key, data, file_ids))
		# conn.commit()
		#
		cur.execute(f"SELECT key, data, object_store_id FROM object_data WHERE ('' || key || '') LIKE '{enc_key}';")
		for row in cur:
			file_ids.append(row[2])
			isSame = len(set(file_ids)) <= 1
			if not isSame:
				print('warning: object_store_id is not same fall back to default value')
				file_ids = [1]
			# added_list.append(key)
			# meta_objs = {}
			# decompressed = snappy.decompress(row[1])
			# if isinstance(decompressed, str):
			# 	decompressed = decompressed.encode()
			#
			# stream = (io.BufferedReader(io.BytesIO(decompressed)))
			# print(key)
			# result = read_main(stream, meta_objs)
			#
			# # print(key, result, meta_objs, "\n")
			# test_json[key] = meta_objs
			# with open("./test.json", "w") as f:
			# 	json.dump(test_json, f, ensure_ascii=False, indent=4)
			#
			# enc_bytes = mozencode.encode_main(result, meta_objs)
			# snappy_eb = snappy.compress(enc_bytes)
			# # print(enc_bytes, "\n")
			# # print(decompressed)
			# print(enc_bytes == decompressed)
print(a)
