import pdb

target_array = ['user-filters']

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
print(array_bytes == b'\x01\x00\x00\x00\x07\x00\xff\xff')

int32_bytes = b''
string_bytes = b''
utf8_bytes = b''
null_bytes = b''
for i in range(len(target_array)):
	int32_int = (INT32 << 32) | i
	int32_bytes = int32_int.to_bytes(length=8, byteorder="little")
	print(int32_bytes == b'\x00\x00\x00\x00\x03\x00\xff\xff')

	string_bytes = STRING.to_bytes(length=8, byteorder="little")
	print(string_bytes == b'\x0c\x00\x00\x80\x04\x00\xff\xff')

	utf8_bytes = target_array[i].encode("utf-8")
	print(utf8_bytes == b'user-filters')

	null_bytes = INITIALIZE.to_bytes(length=4, byteorder="little")
	print(null_bytes == b'\x00\x00\x00\x00')

end_bytes = END_OF_KEYS.to_bytes(length=8, byteorder="little")
print(end_bytes == b'\x00\x00\x00\x00\x13\x00\xff\xff')

complete_bytes = head_bytes+array_bytes+int32_bytes+string_bytes+utf8_bytes+null_bytes+end_bytes
print(complete_bytes == b'\x03\x00\x00\x00\x00\x00\xf1\xff\x01\x00\x00\x00\x07\x00\xff\xff\x00\x00\x00\x00\x03\x00\xff\xff\x0c\x00\x00\x80\x04\x00\xff\xffuser-filters\x00\x00\x00\x00\x00\x00\x00\x00\x13\x00\xff\xff')
