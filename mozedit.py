import json
import sqlite3
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

sqlite_path = "/home/asdf/.floorp/flyrs71n.a/storage/default/moz-extension+++5abeb9c2-083d-41ea-a9fc-4eecbf02bfa7^userContextId=4294967295/idb/3647222921wleabcEoxlt-eengsairo.sqlite"
backup_file = "/home/asdf/Downloads/my-ublock-backup_2025-10-26_21.22.51.txt"

with open(backup_file, "r") as f:
	original_data = json.loads(f.read())

filtered_dict = {}
extract_keys(original_data, filtered_dict)

changed_keys = set()
object_store_id = None

with sqlite3.connect(sqlite_path) as conn:
    cur = conn.cursor()
    conn.create_function("update_refcount", 2, lambda x, y: None)  # 2 args, do nothing
    conn.create_function("increment_refcount", 1, lambda x: None)
    conn.create_function("decrement_refcount", 1, lambda x: None)

    # 既存キーを確認し、存在すれば UPDATE、なければ INSERT
    for key, value in filtered_dict.items():
        enc_key = mozencode.encode_caesar_shift1(key)
        cur.execute("SELECT object_store_id FROM object_data WHERE key = ?", (enc_key,))
        row = cur.fetchone()

        encoded_value = mozencode.encode_main(value)

        if row:
            # 既存レコード更新
            object_store_id = row[0]
            cur.execute("UPDATE object_data SET data = ? WHERE key = ?", (encoded_value, enc_key))
            changed_keys.add(key)
        else:
            # 新規レコード挿入
            if object_store_id is None:
                # 一度でも既存レコードがあればそのIDを使う
                cur.execute("SELECT object_store_id FROM object_data LIMIT 1;")
                obj_row = cur.fetchone()
                object_store_id = obj_row[0] if obj_row else 1

            cur.execute(
                "INSERT INTO object_data (object_store_id, key, index_data_values, data) VALUES (?, ?, ?, ?)",
                (object_store_id, enc_key, None, encoded_value)
            )

    conn.commit()
