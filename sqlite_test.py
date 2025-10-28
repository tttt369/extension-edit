import sqlite3
import mozencode
import json

# def read_ublock_backup(file) -> tuple[list, dict]:
# 	valid_dict = []
# 	valid_keys = ["userSettings", "selectedFilterLists", "hiddenSettings", "whitelist", "dynamicFilteringString", "urlFilteringString", "hostnameSwitchesString", "userFilters"]
#
# 	with open(file, "r") as f:
# 		original_data = json.loads(f.read())
#
# 	filter_keys = [key for key in original_data.keys() if key in valid_keys]
# 	for key in filter_keys:
#
# 		if key == "userSettings":
# 			key = original_data["userSettings"]
# 			valid_list.extend(list(key.keys())) 
# 			continue
#
# 		if key == "whitelist":
# 			key = "netWhitelist"
#
# 		if key == "userFilters":
# 			key = "user.filters"
# 		valid_list.append(key)
#
# 	return valid_list, original_data

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

sqlite_path = "/home/asdf/.floorp/bkmxod65.a/storage/default/moz-extension+++1982fe76-589f-4eb1-b41a-ed916c444988^userContextId=4294967295/idb/3647222921wleabcEoxlt-eengsairo.sqlite"
backup_file = "/home/asdf/Downloads/my-ublock-backup_2025-10-26_21.22.51.txt"

with open(backup_file, "r") as f:
	original_data = json.loads(f.read())

filtered_dict = {}
extract_keys(original_data, filtered_dict)
print(filtered_dict)
# added_list = []
# file_ids = []
# for key in valid_list:
# 	new_list = []
# 	enc_key = mozencode.encode_caesar_shift1(key)
# 	with sqlite3.connect(sqlite_path) as conn:
# 		cur = conn.cursor()
# 		cur.execute(f"SELECT key, data, object_store_id FROM object_data WHERE ('' || key || '') LIKE '{enc_key}';")
# 		for row in cur:
# 			file_ids.append(row[2])
# 			isSame = len(set(file_ids)) <= 1
# 			if not isSame:
# 				print('warning: object_store_id is not same fall back to default value')
# 				file_ids = [1]
# 			mozencode.encode_main()
