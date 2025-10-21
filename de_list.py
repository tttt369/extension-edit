import io
import pdb
from typing import Tuple
import cramjam
import sqlite3
import struct

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
		return result

	else:
		obj = []
		return  obj

def read_main(stream) -> list:
	b_objs = {}

	read_pair(stream, b_objs)

	result = start_read(stream, b_objs)
	if isinstance(result, list):
		xlist = result
		while True:
			tag, _ = peek_pair(stream)
			if tag == 0xFFFF0013:
				read_pair(stream, b_objs)
				return xlist

			key = start_read(stream, b_objs)
			val = start_read(stream, b_objs)
			if not isinstance(key, int) or key < 0:
				continue

			if isinstance(val, str):
				xlist.append(val)

			stream = check(b_objs, stream)
	return []

sqlite_path = "./idb/3647222921wleabcEoxlt-eengsairo.sqlite"
with sqlite3.connect(sqlite_path) as conn:
	cur = conn.cursor()
	cur.execute("SELECT key, data, file_ids FROM object_data WHERE ('' || key || '') LIKE '0tfmfdufeGjmufsMjtut';")
	for row in cur:
		decompressed = cramjam.snappy.decompress_raw(row[1])
		stream = (io.BufferedReader(io.BytesIO(decompressed)))
		# print(stream.read())
		result = read_main(stream)
		print((result))
