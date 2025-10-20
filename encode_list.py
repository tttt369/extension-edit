import pdb

target_array = ['user-filters', 'ublock-filters', 'ublock-badware', 'ublock-privacy', 'ublock-quick-fixes', 'ublock-unbreak']

head_first_4bytes = b'\x03\x00\x00\x00'
string_format_type = b'\x00\x00\x80'

HEAD = head_first_4bytes + b'\x00\x00\xf1\xff'
ARRAY_OBJECT = b'\x07\x00\xff\xff'
INT32 = b'\x03\x00\xff\xff'
STRING = string_format_type + b'\x04\x00\xff\xff'
END_OF_KEYS = b'\x00\x00\x00\x00\x13\x00\xff\xff'

array_first_4bytes = len(target_array).to_bytes(length=4, byteorder="little")
array_bytes = array_first_4bytes + ARRAY_OBJECT

int32_bytes = b''
string_bytes = b''
utf8_bytes = b''
null_bytes = b''
loop_bytes = b''
for i in range(len(target_array)):
	int32_first_4bytes = i.to_bytes(length=4, byteorder="little")
	int32_bytes = int32_first_4bytes + INT32

	utf8_bytes = target_array[i].encode("utf-8")

	string_first_bytes = (len(utf8_bytes)).to_bytes(1, 'big')
	string_bytes = string_first_bytes + STRING

	null_length = 8 - ((len(utf8_bytes) - 1) % 8) - 1
	null_bytes = b'\x00' * null_length

	loop_bytes +=int32_bytes+string_bytes+utf8_bytes+null_bytes


complete_bytes = HEAD+array_bytes+loop_bytes+END_OF_KEYS
correct_bytes = b'\x03\x00\x00\x00\x00\x00\xf1\xff\x06\x00\x00\x00\x07\x00\xff\xff\x00\x00\x00\x00\x03\x00\xff\xff\x0c\x00\x00\x80\x04\x00\xff\xffuser-filters\x00\x00\x00\x00\x01\x00\x00\x00\x03\x00\xff\xff\x0e\x00\x00\x80\x04\x00\xff\xffublock-filters\x00\x00\x02\x00\x00\x00\x03\x00\xff\xff\x0e\x00\x00\x80\x04\x00\xff\xffublock-badware\x00\x00\x03\x00\x00\x00\x03\x00\xff\xff\x0e\x00\x00\x80\x04\x00\xff\xffublock-privacy\x00\x00\x04\x00\x00\x00\x03\x00\xff\xff\x12\x00\x00\x80\x04\x00\xff\xffublock-quick-fixes\x00\x00\x00\x00\x00\x00\x05\x00\x00\x00\x03\x00\xff\xff\x0e\x00\x00\x80\x04\x00\xff\xffublock-unbreak\x00\x00\x00\x00\x00\x00\x13\x00\xff\xff'

print(complete_bytes == correct_bytes)
