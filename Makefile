all:
	. $(HOME)/.virtualenvs/dict/bin/activate && python gen-hxl-dict.py > docs/hxl-hashtags-and-attributes.html
