.PHONY = all install uninstall
install_path = /usr/local/bin/ascli

all: install

install: main.py requirements.txt
	@echo [ SETUP ] Installing ascli, made by ZKutury.
	cp main.py $(install_path)
	pip3 install -r requirements.txt
	chmod 755 /usr/local/bin/ascli

uninstall:
	@echo [ SETUP ] Uninstalling, thanks for using ascli.
	rm $(install_path)