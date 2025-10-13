import io
import struct
import sqlite3
import cramjam

# def read_string(info: int, stream) -> str:
# 	length = info & 0x7FFFFFFF
# 	latin1 = bool(info & 0x80000000)
#
# 	if latin1:
# 		return read_bytes(length, stream).decode("latin-1")
# 	else:
# 		return read_bytes(length * 2, stream).decode("utf-16le")
#
# def read_bytes(length: int, stream) -> bytes:
# 	result = stream.read(length)
# 	if len(result) < length:
# 		raise EOFError()
# 	drop_padding(length, stream)
# 	return result
#
# def drop_padding(read_length, stream):
# 	length = 8 - ((read_length - 1) % 8) - 1
# 	result = stream.read(length)
# 	if len(result) < length:
# 		raise EOFError()

# def read_pair(stream) -> (int, int):
# 	v = stream.read()
# 	return ((v >> 32) & 0xFFFFFFFF, (v >> 0) & 0xFFFFFFFF)
#
# def read(stream, fmt="q"):
# 	try:
# 		return struct.unpack("<" + fmt, stream.read(8))[0]
# 	except struct.error:
# 		raise EOFError() from None

# def read_header(stream) -> None:
# 	tag, data = peek_pair(stream)
# 	v = struct.unpack("<q", self.stream.read(8))[0]
# 	tag, data =  ((v >> 32) & 0xFFFFFFFF, (v >> 0) & 0xFFFFFFFF)
# 	scope = data
# 	compat = True
# 	tag, data = peek_pair(stream)

# def peek(stream) -> int:
# 	try:
# 		return struct.unpack_from("<q", stream.peek(8))[0]
# 	except struct.error:
# 		raise EOFError() from None
#
# def peek_pair(stream) -> (int, int):
# 	v = peek(stream)
# 	return ((v >> 32) & 0xFFFFFFFF, (v >> 0) & 0xFFFFFFFF)

# def read_header(stream) -> None:
# 	v = struct.unpack_from("<q", stream.peek(8))[0]
# 	tag, data = ((v >> 32) & 0xFFFFFFFF, (v >> 0) & 0xFFFFFFFF)
# 	v = struct.unpack("<q", stream.read(8))[0]
# 	tag, data =  ((v >> 32) & 0xFFFFFFFF, (v >> 0) & 0xFFFFFFFF)
# 	scope = data
# 	compat = True
# 	v = struct.unpack_from("<q", stream.peek(8))[0]
# 	tag, data = ((v >> 32) & 0xFFFFFFFF, (v >> 0) & 0xFFFFFFFF)

def start_read(stream):
	v = struct.unpack("<q", stream.read(8))[0]
	v = struct.unpack("<q", stream.read(8))[0]
	_, data  = ((v >> 32) & 0xFFFFFFFF, (v >> 0) & 0xFFFFFFFF)

	length = data & 0x7FFFFFFF
	result = stream.read(length)

	return result

sqlite_path = "./idb/3647222921wleabcEoxlt-eengsairo.sqlite"
with sqlite3.connect(sqlite_path) as conn:
	cur = conn.cursor()
	cur.execute("SELECT key, data, file_ids FROM object_data WHERE ('' || key || '') LIKE '0dpnqjmfeNbhjd';")
	for row in cur:
		decompressed = cramjam.snappy.decompress_raw(row[1])
		reader = (io.BufferedReader(io.BytesIO(decompressed)))
		# import pdb; pdb.set_trace()
		# read_header(reader)
		result = start_read(reader)
		result = result.decode('utf-8')
		print((result))
