import pdb

target_array = ['user-filters', 'ublock-filters', 'ublock-badware', 'ublock-privacy', 'ublock-quick-fixes', 'ublock-unbreak']

#headとstringはハードコードの必要あり
HEAD = 0xfff1000000000003
ARRAY_OBJECT = 0xFFFF0007
INT32 = 0xFFFF0003
STRING    = 0xffff00048000000c
INITIALIZE = 0x0
END_OF_KEYS = 0xFFFF001300000000

head_bytes = HEAD.to_bytes(length=8, byteorder="little")
print(head_bytes == b'\x03\x00\x00\x00\x00\x00\xf1\xff')

array_int = (ARRAY_OBJECT << 32) | len(target_array)
array_bytes = array_int.to_bytes(length=8, byteorder="little")
print(array_bytes == b'\x02\x00\x00\x00\x07\x00\xff\xff')

int32_bytes = b''
string_bytes = b''
utf8_bytes = b''
null_bytes = b''
loop_bytes = b''
for i in range(len(target_array)):
	int32_int = (INT32 << 32) | i
	int32_bytes = int32_int.to_bytes(length=8, byteorder="little")
	if i == 0:
		print(int32_bytes == b'\x00\x00\x00\x00\x03\x00\xff\xff')
	elif i == 1:
		print(int32_bytes == b'\x01\x00\x00\x00\x03\x00\xff\xff')

	string_bytes = STRING.to_bytes(length=8, byteorder="little")
	utf8_bytes = target_array[i].encode("utf-8")
	new_first = (len(utf8_bytes)).to_bytes(1, 'big')
	string_bytes = new_first + string_bytes[1:]
	if i == 0:
		print(string_bytes == b'\x0c\x00\x00\x80\x04\x00\xff\xff')
	elif i == 1:
		print(string_bytes == b'\x0e\x00\x00\x80\x04\x00\xff\xff')

	if i == 0:
		print(utf8_bytes == b'user-filters')
	elif i == 1:
		print(utf8_bytes == b'ublock-filters')

	null_length = 8 - ((len(utf8_bytes) - 1) % 8) - 1
	null_bytes = INITIALIZE.to_bytes(length=null_length, byteorder="little")
	if i == 0:
		print(null_bytes == b'\x00\x00\x00\x00')
	elif i == 1:
		print(null_bytes == b'\x00\x00')
	loop_bytes +=int32_bytes+string_bytes+utf8_bytes+null_bytes

end_bytes = END_OF_KEYS.to_bytes(length=8, byteorder="little")
print(end_bytes == b'\x00\x00\x00\x00\x13\x00\xff\xff')

complete_bytes = head_bytes+array_bytes+loop_bytes+end_bytes
correct_bytes = b'\x03\x00\x00\x00\x00\x00\xf1\xff\x06\x00\x00\x00\x07\x00\xff\xff\x00\x00\x00\x00\x03\x00\xff\xff\x0c\x00\x00\x80\x04\x00\xff\xffuser-filters\x00\x00\x00\x00\x01\x00\x00\x00\x03\x00\xff\xff\x0e\x00\x00\x80\x04\x00\xff\xffublock-filters\x00\x00\x02\x00\x00\x00\x03\x00\xff\xff\x0e\x00\x00\x80\x04\x00\xff\xffublock-badware\x00\x00\x03\x00\x00\x00\x03\x00\xff\xff\x0e\x00\x00\x80\x04\x00\xff\xffublock-privacy\x00\x00\x04\x00\x00\x00\x03\x00\xff\xff\x12\x00\x00\x80\x04\x00\xff\xffublock-quick-fixes\x00\x00\x00\x00\x00\x00\x05\x00\x00\x00\x03\x00\xff\xff\x0e\x00\x00\x80\x04\x00\xff\xffublock-unbreak\x00\x00\x00\x00\x00\x00\x13\x00\xff\xff'

print(complete_bytes == correct_bytes)
