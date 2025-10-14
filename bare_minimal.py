import io
import snappy
import struct
import sqlite3
import cramjam

def start_read(data):
	print(len(data))
	cutoff_bytes1 = data[:16] 
	result = data[16:25]
	cutoff_bytes2 = data[25:]

	return result, cutoff_bytes1, cutoff_bytes2

sqlite_path = "./idb/3647222921wleabcEoxlt-eengsairo.sqlite"
with sqlite3.connect(sqlite_path) as conn:
	cur = conn.cursor()
	cur.execute("SELECT key, data, file_ids FROM object_data WHERE ('' || key || '') LIKE '0dpnqjmfeNbhjd';")
	for row in cur:
		decompressed = snappy.decompress(row[1])
		# import pdb; pdb.set_trace()
		result, c1, c2 = start_read(decompressed)
		x = snappy.compress(c1+result+c2)
		if bytes(x) == row[1]:
			print("same!")
		else:
			print(row[1])
			print(bytes(x))
			print("differ")

#16バイト目から25バイト目

