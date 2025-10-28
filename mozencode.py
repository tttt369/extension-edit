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

def encode_main(target, data_objs={}) -> bytes:
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
