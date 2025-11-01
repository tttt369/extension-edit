import configparser

# ファイルを読み込む
config = configparser.ConfigParser()
config.read('/home/asdf/.floorp/profiles.ini')

sec_list = config.sections()
for sec in sec_list:
	if config[sec].get('Name') == 'test':
		config.remove_section(sec)

# ファイルを書き込みモードで開いて保存
with open('/home/asdf/.floorp/profiles.ini', 'w') as f:
    config.write(f)
