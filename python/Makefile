INSTALL_DIR = $(HOME)/opt


all: package

.PHONY: package
package: dist/roosterize/roosterize
dist/roosterize/roosterize: roosterize/main.py
	pyinstaller $^ -n roosterize \
		-y --log-level WARN

.PHONY: install
install: package
	rm -rf $(INSTALL_DIR)/roosterize
	mkdir -p $(INSTALL_DIR)/roosterize
	cp -r dist/roosterize $(INSTALL_DIR)/roosterize/bin

.PHONY: clean
clean:
	-rm -rf dist/ build/
