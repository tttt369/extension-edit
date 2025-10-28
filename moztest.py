import io
import pdb
import json
import snappy
import struct
import sqlite3
import mozencode
from typing import Tuple

INT32                 = 0xFFFF0003
STRING                = 0xFFFF0004
BOOLEAN               = 0xFFFF0002
ARRAY_OBJECT          = 0xFFFF0007
OBJECT_OBJECT         = 0xFFFF0008

def check(stream, b_objs) -> io.BufferedReader:
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

	elif tag == BOOLEAN:
		return bool(data)

	else:
		raise ValueError()

def read_main(stream, metad_objs) -> list | dict | str | bool | int:
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
				return xdict

			key = start_read(stream, b_objs, metad_objs)
			val = start_read(stream, b_objs, metad_objs)
			xdict[key] = val
	elif isinstance(result, str):
			# check(stream, b_objs)
			return result

	elif isinstance(result, bool):
			# check(stream, b_objs)
			return result

	elif isinstance(result, int):
			# check(stream, b_objs)
			return result
	else:
		print("result", result)
		raise ValueError()


def decode_caesar_shift1(text) -> str:
	result = ''
	for c in text:
		if 'a' <= c <= 'z':
			result += chr((ord(c) - ord('a') - 1) % 26 + ord('a'))
		elif 'A' <= c <= 'Z':
			result += chr((ord(c) - ord('A') - 1) % 26 + ord('A'))
		else:
			result += c
	return result.lstrip('0')


def read_ublock_backup(file) -> Tuple[list, dict]:
	with open(file, "r") as f:
		original_data = json.loads(f.read())

	valid_keys = ["userSettings", "whitelist", "userFilters", "selectedFilterLists", "hiddenSettings", "dynamicFilteringString", "urlFilteringString", "hostnameSwitchesString"]
	valid_list = []
	for key in dict(original_data).keys():
		if key in valid_keys:
			if key == "userSettings":
				key = original_data["userSettings"]
				valid_list.extend(list(key.keys())) 
				continue

			if key == "whitelist":
				key = "netWhitelist"

			if key == "userFilters":
				key = "user.filters"
			valid_list.append(key)
	return valid_list, original_data

sqlite_path = "/home/asdf/.floorp/bkmxod65.a/storage/default/moz-extension+++1982fe76-589f-4eb1-b41a-ed916c444988^userContextId=4294967295/idb/3647222921wleabcEoxlt-eengsairo.sqlite"
backup_file = "/home/asdf/Downloads/my-ublock-backup_2025-10-27_14.47.28.txt"

test_json = {}

valid_list, original_data= read_ublock_backup(backup_file)
print(valid_list)
added_list = []
for key in valid_list:
	# if not key == "popupPanelSections":
	# 	continue
	enc_key = mozencode.encode_caesar_shift1(key)

	with sqlite3.connect(sqlite_path) as conn:
		cur = conn.cursor()
		cur.execute(f"SELECT key, data, file_ids FROM object_data WHERE ('' || key || '') LIKE '{enc_key}';")
		for row in cur:
			added_list.append(key)
			meta_objs = {}
			decompressed = snappy.decompress(row[1])
			if isinstance(decompressed, str):
				decompressed = decompressed.encode()

			stream = (io.BufferedReader(io.BytesIO(decompressed)))
			print(key)
			result = read_main(stream, meta_objs)

			# print(key, result, meta_objs, "\n")
			test_json[key] = meta_objs
			with open("./test.json", "w") as f:
				json.dump(test_json, f, ensure_ascii=False, indent=4)

			enc_bytes = mozencode.encode_main(result, meta_objs)
			snappy_eb = snappy.compress(enc_bytes)
			# print(enc_bytes, "\n")
			# print(decompressed)
			print(enc_bytes == decompressed)
