import io
import cramjam
import sqlite3
import struct

def peek(stream) -> int:
	try:
		return struct.unpack_from("<q", stream.peek(8))[0]
	except struct.error:
		raise EOFError() from None

def peek_pair(stream) -> (int, int):
	v = peek(stream)
	return ((v >> 32) & 0xFFFFFFFF, (v >> 0) & 0xFFFFFFFF)

def read_fmt(stream, fmt="q"):
	try:
		return struct.unpack("<" + fmt, stream.read(8))[0]
	except struct.error:
		raise EOFError() from None

def read_pair(stream) -> (int, int):
	v = read_fmt(stream)
	return ((v >> 32) & 0xFFFFFFFF, (v >> 0) & 0xFFFFFFFF)

def read_header(stream) -> None:
	tag, data = peek_pair(stream)

	scope: int
	if tag == 0xFFF10000:
		tag, data = read_pair(stream)

		# if data == 0:
		# 	data = int(Scope.SAME_PROCESS)

		# scope = data
	# else:  # Old on-disk format
	# 	scope = int(Scope.DIFFERENT_PROCESS_FOR_INDEX_DB)
	#
	# if scope == Scope.DIFFERENT_PROCESS:
	# 	self.compat = False
	# elif scope == Scope.DIFFERENT_PROCESS_FOR_INDEX_DB:#
	# 	self.compat = True
	# elif scope == Scope.SAME_PROCESS:
	# 	raise InvalidHeaderError("Can only parse persistent data")
	# else:
	# 	raise InvalidHeaderError("Invalid scope")

def read_string(stream, info: int) -> str:
	length = info & 0x7FFFFFFF
	latin1 = bool(info & 0x80000000)

	if latin1:
		return read_bytes(stream, length).decode("latin-1")
	else:
		return read_bytes(stream, length * 2).decode("utf-16le")

def drop_padding(stream, read_length):
	length = 8 - ((read_length - 1) % 8) - 1
	result = stream.read(length)
	if len(result) < length:
		raise EOFError()

def read_bytes(stream, length: int) -> bytes:
	result = stream.read(length)
	if len(result) < length:
		raise EOFError()
	drop_padding(stream, length)
	return result

class JSInt32(int):
	"""Type to represent the standard 32-bit signed integer"""
	def __init__(self, value):
		if not (-0x80000000 <= value <= 0x7FFFFFFF):
			raise TypeError("JavaScript integers are signed 32-bit values")

def start_read(stream, objs):
	tag, data = read_pair(stream)

	if tag == 0xFFFF0003:#
		if data > 0x7FFFFFFF:
			data -= 0x80000000
		return False, JSInt32(data)

	elif tag == 0xFFFF0004:#
		return False, read_string(stream, data)

	else:
		obj = []
		objs.append(obj)
		return True, obj

def read_main(stream):
	all_objs = []
	objs = []

	read_header(stream) #8バイト飛ばす
	add_obj, result = start_read(stream, objs)
	if add_obj:
		all_objs.append(result)

	while len(objs) > 0:
		obj = objs[-1]

		tag, data = peek_pair(stream)
		if tag == 0xFFFF0013:
			read_pair(stream)
			objs.pop()
			continue

		add_obj, key = start_read(stream, objs)
		if add_obj:
			all_objs.append(key)

		add_obj, val = start_read(stream, objs)
		if add_obj:
			all_objs.append(val)
		else:
			if isinstance(obj, list):#
				if not isinstance(key, int) or key < 0:
					continue

				while key >= len(obj):
					obj.append(None)

			obj[key] = val
			import pdb; pdb.set_trace()

	all_objs.clear()

	return result

sqlite_path = "./idb/3647222921wleabcEoxlt-eengsairo.sqlite"
with sqlite3.connect(sqlite_path) as conn:
	cur = conn.cursor()
	cur.execute("SELECT key, data, file_ids FROM object_data WHERE ('' || key || '') LIKE '0tfmfdufeGjmufsMjtut';")
	for row in cur:
		decompressed = cramjam.snappy.decompress_raw(row[1])
		stream = (io.BufferedReader(io.BytesIO(decompressed)))
		result = read_main(stream)
		print((result))
