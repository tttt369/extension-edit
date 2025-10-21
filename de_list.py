import io
import pdb
import cramjam
import sqlite3
import struct

def check(b_objs, stream):
	readed_stream = stream.read()

	for key, value in b_objs.items():
		key_int = int.from_bytes(value, "little")
		print(key, value)
		print(key, hex(key_int))

	stream_int = int.from_bytes(readed_stream, "little")
	print("stream", readed_stream)
	print("stream", hex(stream_int))
	return io.BufferedReader(io.BytesIO(readed_stream))

def peek_pair(stream) -> (int, int):
	v = struct.unpack_from("<q", stream.peek(8))[0]
	return ((v >> 32) & 0xFFFFFFFF, (v >> 0) & 0xFFFFFFFF)

def read_pair(stream, b_objs, skip = False) -> (int, int):
	read_bytes = stream.read(8)
	b_objs["b" + str(len(b_objs))] = read_bytes
	v = struct.unpack("<q", read_bytes)[0]
	if skip:
		return
	else:
		return ((v >> 32) & 0xFFFFFFFF, (v >> 0) & 0xFFFFFFFF)

def read_string(stream, info: int, b_objs) -> (bytes):
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

def start_read(stream, objs, b_objs):
	tag, data = read_pair(stream, b_objs)

	if tag == 0xFFFF0003:#
		if data > 0x7FFFFFFF:
			data -= 0x80000000
		return False, data

	elif tag == 0xFFFF0004:#
		result = read_string(stream, data, b_objs) 
		return False, result

	else:
		obj = []
		objs.append(obj)
		return True, obj

def read_main(stream):
	all_objs = []
	b_objs = {}
	objs = []

	read_pair(stream, b_objs, skip=True)
	add_obj, result = start_read(stream, objs, b_objs)
	if add_obj:
		all_objs.append(result)

	while len(objs) > 0:
		obj = objs[-1]

		tag, _ = peek_pair(stream)
		if tag == 0xFFFF0013:
			read_pair(stream, b_objs, skip=True)
			objs.pop()
			pdb.set_trace()
			continue

		add_obj, key = start_read(stream, objs, b_objs)
		if add_obj:
			all_objs.append(key)

		add_obj, val = start_read(stream, objs, b_objs)
		if add_obj:
			all_objs.append(val)
		else:
			if isinstance(obj, list):#
				if not isinstance(key, int) or key < 0:
					continue

				while key >= len(obj):
					obj.append(None)

			obj[key] = val

		stream = check(b_objs, stream)
	all_objs.clear()

	return result

sqlite_path = "/home/asdf/.mozilla/firefox/21if9f71.default-release/storage/default/moz-extension+++1eab4c3c-cb03-4aed-9010-4a478ba9be01^userContextId=4294967295/idb/3647222921wleabcEoxlt-eengsairo.sqlite"
with sqlite3.connect(sqlite_path) as conn:
	cur = conn.cursor()
	cur.execute("SELECT key, data, file_ids FROM object_data WHERE ('' || key || '') LIKE '0tfmfdufeGjmufsMjtut';")
	for row in cur:
		decompressed = cramjam.snappy.decompress_raw(row[1])
		stream = (io.BufferedReader(io.BytesIO(decompressed)))
		# print(stream.read())
		result = read_main(stream)
		print((result))
