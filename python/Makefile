INSTALL_DIR = $(HOME)/opt


all: package

.PHONY: package
package: dist/roosterize/roosterize dist/roosterize.tgz

dist/roosterize/roosterize: roosterize/main.py
	pyinstaller $^ -n roosterize \
		-y --log-level WARN

dist/roosterize.tgz: dist/roosterize/roosterize
	cd dist && tar czf roosterize.tgz roosterize/

.PHONY: install
install: package
	rm -rf $(INSTALL_DIR)/roosterize
	mkdir -p $(INSTALL_DIR)/roosterize
	cp -r dist/roosterize $(INSTALL_DIR)/roosterize/bin

.PHONY: clean
clean:
	-rm -rf dist/ build/
