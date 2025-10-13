import io
import struct
import sqlite3
import cramjam

def start_read(stream):
	cutoff_bytes1 = stream.read(16)
	#
	# v = struct.unpack("<q", stream.read(8))[0]
	# data  = (v >> 0) & 0xFFFFFFFF
	# length = data & 0x7FFFFFFF
	result = stream.read(9)
	cutoff_bytes2 = stream.read(8)

	return result, cutoff_bytes1, cutoff_bytes2

sqlite_path = "./idb/3647222921wleabcEoxlt-eengsairo.sqlite"
with sqlite3.connect(sqlite_path) as conn:
	cur = conn.cursor()
	cur.execute("SELECT key, data, file_ids FROM object_data WHERE ('' || key || '') LIKE '0dpnqjmfeNbhjd';")
	for row in cur:
		decompressed = cramjam.snappy.decompress_raw(row[1])
		stream = (io.BufferedReader(io.BytesIO(decompressed)))
		result, c1, c2 = start_read(stream)
		x = cramjam.snappy.compress_raw(c1+result+c2)
		if bytes(x) == row[1]:
			print("same!")
		else:
			print(row[1])
			print(bytes(x))
			print("differ")

#16バイト目から25バイト目

