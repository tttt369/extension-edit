import io
import pdb
import json
import struct
import cramjam
import sqlite3
from typing import Tuple

INT32     = 0xFFFF0003
STRING    = 0xFFFF0004
def check(b_objs, stream) -> io.BufferedReader:
	readed_stream = stream.read()

	for key, value in b_objs.items():
		key_int = int.from_bytes(value, "little")
		print(key, value)
		print(key, hex(key_int))

	stream_int = int.from_bytes(readed_stream, "little")
	print("stream", readed_stream)
	print("stream", hex(stream_int))
	return io.BufferedReader(io.BytesIO(readed_stream))

def peek_pair(stream) -> Tuple[int, int]:
	v = struct.unpack_from("<q", stream.peek(8))[0]
	return ((v >> 32) & 0xFFFFFFFF, (v >> 0) & 0xFFFFFFFF)

def read_pair(stream, b_objs) -> Tuple[int, int]:
	read_bytes = stream.read(8)
	b_objs["b" + str(len(b_objs))] = read_bytes
	v = struct.unpack("<q", read_bytes)[0]
	return ((v >> 32) & 0xFFFFFFFF, (v >> 0) & 0xFFFFFFFF)

def read_string(stream, info: int, b_objs) -> (str):
	length = info & 0x7FFFFFFF
	latin1 = bool(info & 0x80000000)

	if latin1:
		result = stream.read(length)
		if len(result) < length:
			raise EOFError()
		read_length = 8 - ((length - 1) % 8) - 1
		cut_bytes = stream.read(read_length)

		b_objs["b" + str(len(b_objs))] = result
		b_objs["b" + str(len(b_objs))] = cut_bytes
		return result.decode("latin-1")
	else:
		result = stream.read(length)
		if len(result) < length:
			raise EOFError()
		read_length = 8 - ((length - 1) % 8) - 1
		cut_bytes = stream.read(read_length)

		b_objs["b" + str(len(b_objs))] = result
		b_objs["b" + str(len(b_objs))] = cut_bytes
		return result.decode("utf-16le")

def start_read(stream, b_objs) -> int | str | list:
	tag, data = read_pair(stream, b_objs)

	if tag == INT32:
		if data > 0x7FFFFFFF:
			data -= 0x80000000
		return data

	elif tag == STRING:
		result = read_string(stream, data, b_objs) 
		b_objs["string_format_type"] = data
		return result

	else:
		obj = []
		return  obj

def read_main(stream) -> Tuple[list, dict]:
	b_objs = {}

	_, hf4 = read_pair(stream, b_objs)
	b_objs["head_first_4bytes"] = hf4

	result = start_read(stream, b_objs)
	if isinstance(result, list):
		xlist = result
		while True:
			tag, _ = peek_pair(stream)
			if tag == 0xFFFF0013:
				read_pair(stream, b_objs)
				return xlist, b_objs

			key = start_read(stream, b_objs)
			val = start_read(stream, b_objs)
			if not isinstance(key, int) or key < 0:
				continue

			if isinstance(val, str):
				xlist.append(val)

			# stream = check(b_objs, stream)
	return [], b_objs

def decode_caesar_shift1(text) -> str:
    result = ''
    for c in text:
        if 'a' <= c <= 'z':
            result += chr((ord(c) - ord('a') - 1) % 26 + ord('a'))
        elif 'A' <= c <= 'Z':
            result += chr((ord(c) - ord('A') - 1) % 26 + ord('A'))
        else:
            result += c
    return result.lstrip('0')  # ← 先頭の0を削除


result_josn = {}
sqlite_path = "./idb/3647222921wleabcEoxlt-eengsairo.sqlite"
with sqlite3.connect(sqlite_path) as conn:
	cur = conn.cursor()
	cur.execute("SELECT key, data, file_ids FROM object_data WHERE ('' || key || '') LIKE '0tfmfdufeGjmufsMjtut';")
	for row in cur:
		ijson = {}
		decompressed = cramjam.snappy.decompress_raw(row[1])
		stream = (io.BufferedReader(io.BytesIO(decompressed)))

		ijson["data"] , b_objs= read_main(stream)
		ijson["head_first_4bytes"] = b_objs["head_first_4bytes"]
		ijson["string_format_type"] = b_objs["string_format_type"]
		decoded_key = decode_caesar_shift1(row[0].decode())
		result_josn[decoded_key] = ijson
with open("./test.json", "w") as f:
	json.dump(result_josn, f, ensure_ascii=False, indent=4)
print(result_josn)

