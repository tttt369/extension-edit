import io
import cramjam
import sqlite3
import struct

# def drop_padding(stream, read_length):
# 	length = 8 - ((read_length - 1) % 8) - 1
# 	result = stream.read(length)
# 	if len(result) < length:
# 		raise EOFError()
#
# def read_bytes(stream, length: int) -> bytes:
# 	result = stream.read(length)
# 	if len(result) < length:
# 		raise EOFError()
# 	drop_padding(stream, length)
# 	return result

def peek(stream) -> int:
	try:
		return struct.unpack_from("<q", stream.peek(8))[0]
	except struct.error:
		raise EOFError() from None

def peek_pair(stream) -> (int, int):
	v = peek(stream)
	return ((v >> 32) & 0xFFFFFFFF, (v >> 0) & 0xFFFFFFFF)

def read_fmt(read_bytes, fmt="q"):
	try:
		return struct.unpack("<" + fmt, read_bytes)[0]
	except struct.error:
		raise EOFError() from None

def read_pair(stream, skip = False) -> (int, int):
	read_bytes = stream.read(8)
	v = read_fmt(read_bytes)
	if skip:
		return read_bytes
	else:
		return (read_bytes, (v >> 32) & 0xFFFFFFFF, (v >> 0) & 0xFFFFFFFF)

def read_header(stream) -> None:
	tag, _ = peek_pair(stream)
	if tag == 0xFFF10000:
		tag, _ = read_pair(stream)


def read_string(stream, info: int) -> (bytes, str):
	length = info & 0x7FFFFFFF
	latin1 = bool(info & 0x80000000)

	if latin1:
		result = stream.read(length)
		if len(result) < length:
			raise EOFError()
		read_length = 8 - ((length - 1) % 8) - 1
		cut_bytes = stream.read(read_length)
		return result, cut_bytes, result.decode("latin-1")
	else:
		result = stream.read(length)
		if len(result) < length:
			raise EOFError()
		read_length = 8 - ((length - 1) % 8) - 1
		cut_bytes = stream.read(read_length)
		return result, cut_bytes, result.decode("utf-16le")

def start_read(stream, objs):
	cutbytes, tag, data = read_pair(stream)

	if tag == 0xFFFF0003:#
		if data > 0x7FFFFFFF:
			data -= 0x80000000
		return False, data, cutbytes, None

	elif tag == 0xFFFF0004:#
		cutbytes2, cutbytes3, result = read_string(stream, data) 
		return False, result, cutbytes, cutbytes2, cutbytes3

	else:
		obj = []
		objs.append(obj)
		return True, obj, cutbytes, None

def check(c1, c2, c3, c4, c5, c6, c7, stream):
	# if c+stream.read() == b'\x03\x00\x00\x00\x00\x00\xf1\xff\x01\x00\x00\x00\x07\x00\xff\xff\x00\x00\x00\x00\x03\x00\xff\xff\x0c\x00\x00\x80\x04\x00\xff\xffuser-filters\x00\x00\x00\x00\x00\x00\x00\x00\x13\x00\xff\xff':
	# 	print("true")
	# else:
	# 	print("false")
	readed_stream = stream.read()
	print(c1)
	c1_int = int.from_bytes(c1, "little")
	c2_int = int.from_bytes(c2, "little")
	c3_int = int.from_bytes(c3, "little")
	c4_int = int.from_bytes(c4, "little")
	c5_int = int.from_bytes(c5, "little")
	c6_int = int.from_bytes(c6, "little")
	c7_int = int.from_bytes(c7, "little")
	stream_int = int.from_bytes(readed_stream, "little")
	print("c1", hex(c1_int))
	print("c2", hex(c2_int))
	print("c3", hex(c3_int))
	print("c4", hex(c4_int))
	print("c5", hex(c5_int))
	print("c6", hex(c6_int))
	print("c7", hex(c7_int))
	print("stream", hex(stream_int))
	return io.BufferedReader(io.BytesIO(readed_stream))


def read_main(stream):

	all_objs = []
	objs = []

	# read_header(stream) #8バイト飛ばす
	c1 = read_pair(stream, skip=True) #8バイト飛ばす

	add_obj, result, c2, _ = start_read(stream, objs)
	if add_obj:
		all_objs.append(result)

	while len(objs) > 0:
		obj = objs[-1]

		tag, _ = peek_pair(stream)
		c3 = b''
		if tag == 0xFFFF0013:
			c3 = read_pair(stream, skip=True)
			objs.pop()
			continue

		add_obj, key, c4, _ = start_read(stream, objs)
		if add_obj:
			all_objs.append(key)

		add_obj, val, c5, c6, c7 = start_read(stream, objs)
		import pdb; pdb.set_trace()
		if add_obj:
			all_objs.append(val)
		else:
			if isinstance(obj, list):#
				if not isinstance(key, int) or key < 0:
					continue

				while key >= len(obj):
					obj.append(None)

			obj[key] = val

		stream = check(c1, c2, c3, c4, c5, c6, c7, stream)
	all_objs.clear()

	return result

sqlite_path = "./idb/3647222921wleabcEoxlt-eengsairo.sqlite"
with sqlite3.connect(sqlite_path) as conn:
	cur = conn.cursor()
	cur.execute("SELECT key, data, file_ids FROM object_data WHERE ('' || key || '') LIKE '0tfmfdufeGjmufsMjtut';")
	for row in cur:
		decompressed = cramjam.snappy.decompress_raw(row[1])
		stream = (io.BufferedReader(io.BytesIO(decompressed)))
		print(stream.read())
		result = read_main(stream)
		print((result))
