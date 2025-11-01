import re
import shutil
import configparser
import subprocess
import json
import io
import lz4.block
import os

# def check():
#     with open("search.json.mozlz4", "rb") as f:
#         data = f.read()
#
#     with open("search_modified.json.mozlz4", "rb") as f:
#         data2 = f.read()
#     original = [data[i:i+8] for i in range(0, len(data), 8)]
#     processd = [data[i:i+8] for i in range(0, len(data), 8)]
#
#     for obytes, pbytes in zip(original, processd):
#         print("o:", obytes, "p:", pbytes)

BASEDIR = "/home/asdf/.floorp/"

def edit_searchlz4(profile_path):
	with open(f"{profile_path}search.json.mozlz4", "rb") as f:
		data = f.read()
	stream = io.BytesIO(data)
	header = stream.read(8)
	compressed_data = stream.read()

	decompressed_bytes = lz4.block.decompress(compressed_data)
	search_dict = json.loads(decompressed_bytes.decode())

	search_dict["metaData"]["defaultEngineId"] = "ddg"
	search_dict["metaData"]["defaultEngineIdHash"] = "ERqX1Dw7n8pqTw0CUQQfELb5tBTASjX/IbR5TNOXSK8="

	json_string = json.dumps(search_dict)
	json_bytes = json_string.encode()

	compressed_modified = lz4.block.compress(json_bytes)
	output_stream = header + compressed_modified

	with open(f"{profile_path}search.json.mozlz4", "wb") as f:
		f.write(output_stream)

def get_profile_name():
	profile_path = ''
	for dir_name in os.listdir(BASEDIR):
		rematch = re.match(r"(.*)\.test$", dir_name)
		if rematch:
			profile_path = BASEDIR+rematch.group(1)+'.test/'
	return profile_path

def removedir():
	def write_ini_preserve_format(config, filepath):
		with open(filepath, 'w', encoding='utf-8') as f:
			for section in config.sections():
				f.write(f"[{section}]\n")
				for key, value in config[section].items():
					# 値が None または空文字列なら = のみ、それ以外は =value（スペースなし）
					if value is None:
						f.write(f"{key}=\n")
					else:
						f.write(f"{key}={value}\n")
				f.write("\n")  # セクション間の空行

	ini_paht = BASEDIR + "profiles.ini"

	config = configparser.ConfigParser()
	config.optionxform = lambda optionstr: optionstr
	config.read(ini_paht)

	sec_list = config.sections()
	for sec in sec_list:
		if config[sec].get('Name') == 'test':
			config.remove_section(sec)

	write_ini_preserve_format(config, ini_paht)

	profile_path = get_profile_name()
	if not profile_path == '':
		shutil.rmtree(profile_path)

removedir()
cmd = "floorp -CreateProfile test && floorp -P test"
result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
# print("returncode:", result.returncode)
# print("stdout:\n", result.stdout)
# print("stderr:\n", result.stderr)

profile_path = get_profile_name()
shutil.copyfile("./data/prefs.js", profile_path+'prefs.js')
edit_searchlz4(profile_path)
