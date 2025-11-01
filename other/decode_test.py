import io
import pdb
import json
import snappy
import struct
import sqlite3
from typing import Tuple

INT32                 = 0xFFFF0003
STRING                = 0xFFFF0004
ARRAY_OBJECT          = 0xFFFF0007
OBJECT_OBJECT         = 0xFFFF0008

def check(b_objs, stream) -> io.BufferedReader:
	readed_stream = stream.read()
	for key, value in b_objs.items():
		key_int = int.from_bytes(value, "little")
		print(key, value)
		print(key, hex(key_int))

	stream_int = int.from_bytes(readed_stream, "little")
	print("stream", readed_stream)
	print("stream", hex(stream_int), "\n")
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

def start_read(stream, b_objs, meta_objs) -> int | str | list | dict:
	tag, data = read_pair(stream, b_objs)

	if tag == INT32:
		if data > 0x7FFFFFFF:
			data -= 0x80000000
		return data

	elif tag == STRING:
		result = read_string(stream, data, b_objs) 
		meta_objs["string_format_int"] = data
		return result

	elif tag == ARRAY_OBJECT:
		xlist = []
		return xlist
	
	elif tag == OBJECT_OBJECT:
		xdict = {}
		return xdict

	else:
		raise ValueError()

def read_main(stream, metad_objs) -> list | dict | str:
	b_objs = {}

	_, hf4 = read_pair(stream, b_objs)
	metad_objs["header_type_int"] = hf4

	result = start_read(stream, b_objs, metad_objs)
	if isinstance(result, list):
		xlist = result
		while True:
			tag, _ = peek_pair(stream)
			if tag == 0xFFFF0013:
				read_pair(stream, b_objs)
				return xlist

			key = start_read(stream, b_objs, metad_objs)
			val = start_read(stream, b_objs, metad_objs)
			if not isinstance(key, int) or key < 0:
				continue

			if isinstance(val, str):
				xlist.append(val)

	elif isinstance(result, dict):
		xdict = result
		while True:
			tag, _ = peek_pair(stream)
			if tag == 0xFFFF0013:
				read_pair(stream, b_objs)
				stream = check(b_objs, stream)
				return xdict

			key = start_read(stream, b_objs, metad_objs)
			val = start_read(stream, b_objs, metad_objs)
			if not isinstance(key, int) or key < 0:
				continue

			if isinstance(val, str):
				xdict[key] = val

			return {}
	elif isinstance(result, str):
			return repr(result)
	else:
		print(result)
		raise ValueError()

sqlite_path = "/home/asdf/.floorp/vu2wkrkn.a/storage/default/moz-extension+++7c56243f-bd60-47f3-b659-d1c2ab598ad2^userContextId=4294967295/idb/3647222921wleabcEoxlt-eengsairo.sqlite"
with sqlite3.connect(sqlite_path) as conn:
	cur = conn.cursor()
	cur.execute("SELECT key, data, file_ids FROM object_data WHERE ('' || key || '') LIKE '0ijeefoTfuujoht';")
	for row in cur:
		meta_objs = {}
		pdb.set_trace()
		decompressed = snappy.decompress(row[1])
		if isinstance(decompressed, str):
			decompressed = decompressed.encode()
		stream = (io.BufferedReader(io.BytesIO(decompressed)))
		result = read_main(stream, meta_objs)
		print((result))
		print(decompressed)
