import io
import pdb
import json
import snappy
import struct
import sqlite3
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

def encode_caesar_shift1(text) -> str:
    result = ''
    result += '0'
    for c in text:
        if 'a' <= c <= 'z':
            result += chr((ord(c) - ord('a') + 1) % 26 + ord('a'))
        elif 'A' <= c <= 'Z':
            result += chr((ord(c) - ord('A') + 1) % 26 + ord('A'))
        else:
            result += c
    return result

def encode_main(target, data_objs) -> bytes:
	data_type = type(target)
	try:
		htint = data_objs["header_type_int"]
	except:
		print("warning: header_type_int is missing fall back to default value")
		htint = 3
	try:
		sfint = data_objs["string_format_int"]
	except:
		sfint = 2147483660
		print("warning: string_format_int is missing fall back to default value")

	sf4bytes = sfint.to_bytes(length=4, byteorder="little")
	header_first_4bytes = htint.to_bytes(length=4, byteorder="little")
	string_format_3bytes = sf4bytes[1:]

	head = header_first_4bytes + b'\x00\x00\xf1\xff'
	array_obj = b'\x07\x00\xff\xff'
	dict_obj = b'\x00\x00\x00\x00\x08\x00\xff\xff'
	int32 = b'\x03\x00\xff\xff'
	string = string_format_3bytes + b'\x04\x00\xff\xff'
	end_of_keys = b'\x00\x00\x00\x00\x13\x00\xff\xff'
	boolean = b'\x02\x00\xff\xff'


	def encode_str(target_str):
		res_obj = {}
		latin1 = bool(sfint & 0x80000000)
		str_format = "latin-1" if latin1 else "utf-16le"
		encoded_str_bytes = target_str.encode(str_format)

		string_first_bytes = (len(encoded_str_bytes)).to_bytes(1, 'big')
		string_meta_bytes = string_first_bytes + string

		null_length = 8 - ((len(encoded_str_bytes) - 1) % 8) - 1
		null_bytes = b'\x00' * null_length
		combined_str_bytes = string_meta_bytes+encoded_str_bytes+null_bytes

		res_obj["smb"] = string_meta_bytes
		res_obj["esb"] = encoded_str_bytes
		res_obj["nb"] = null_bytes
		res_obj["csb"] = combined_str_bytes
		return res_obj

	if isinstance(target, str):
		data_dict = encode_str(target)
		complete_bytes = head+data_dict["csb"]
		return complete_bytes

	elif isinstance(target, list):
		array_lenght_4bytes = len(target).to_bytes(length=4, byteorder="little")
		array_bytes = array_lenght_4bytes + array_obj

		int32_bytes = b''
		loop_bytes = b''
		for i in range(len(target)):
			int32_first_4bytes = i.to_bytes(length=4, byteorder="little")
			int32_bytes = int32_first_4bytes + int32

			data_dict = encode_str(target[i])

			loop_bytes +=int32_bytes+data_dict["csb"]

		complete_bytes = head+array_bytes+loop_bytes+end_of_keys
		return complete_bytes

	elif isinstance(target, dict):
		loop_bytes = b''
		for key, value in target.items():
			data_dict = encode_str(key)
			loop_bytes +=data_dict["csb"]
			if isinstance(value, bool):
				bool_res = int(value).to_bytes(length=4, byteorder="little")
				loop_bytes += bool_res + boolean

		complete_bytes = head+dict_obj+loop_bytes+end_of_keys
		return complete_bytes

	elif isinstance(target, bool):
		bool_res = int(target).to_bytes(length=4, byteorder="little")
		bool_bytes = bool_res+boolean
		complete_bytes = head+bool_bytes
		return complete_bytes

	elif isinstance(target, int):
		int_res = target.to_bytes(length=4, byteorder="little")
		int_bytes = int_res+int32
		complete_bytes = head+int_bytes
		return complete_bytes

	else:
		raise ValueError()

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

sqlite_path = "/home/asdf/.floorp/flyrs71n.a/storage/default/moz-extension+++c8d49f91-102d-4255-849b-665cfe93bb1e^userContextId=4294967295/idb/3647222921wleabcEoxlt-eengsairo.sqlite"
backup_file = "/home/asdf/Downloads/my-ublock-backup_2025-10-26_21.22.51.txt"

test_json = {}

valid_list, original_data= read_ublock_backup(backup_file)
print(valid_list)
for key in valid_list:
	# if not key == "popupPanelSections":
	# 	continue
	enc_key = encode_caesar_shift1(key)

	with sqlite3.connect(sqlite_path) as conn:
		cur = conn.cursor()
		cur.execute(f"SELECT key, data, file_ids FROM object_data WHERE ('' || key || '') LIKE '{enc_key}';")
		for row in cur:
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

			enc_bytes = encode_main(result, meta_objs)
			snappy_eb = snappy.compress(enc_bytes)
			# print(enc_bytes, "\n")
			# print(decompressed)
			print(enc_bytes == decompressed)
