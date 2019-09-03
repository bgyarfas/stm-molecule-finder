# # This populates TAGGED_VERSION from git
# TAGGED_VERSION = $(shell git describe | sed "s/-g[a-z0-9]\{7,\}//")
# # Now TAGGED_VERSION should be something like "v0.1.0-34" - number of commits from tag in current branch
# $(info TAGGED_VERSION is $(TAGGED_VERSION))

.PHONY: bootstrap
bootstrap:
ifeq ($(shell which python3),)
$(error "You need to install python3!!")
endif

ifeq ($(shell which pip3),)
$(error "You need pip3!!")
endif

	@if ! pip3 list --disable-pip-version-check | grep -E "^virtualenv"; then \
		pip3 install virtualenv; \
	else \
		echo "virtualenv already installed"; \
	fi

.PHONY: install-venv
install-venv: bootstrap
	python3 -m virtualenv venv
	venv/bin/pip3 install -r requirements.txt

.PHONY: launch
launch: install-venv
	source ./venv/bin/activate && \
		bokeh serve --allow-websocket-origin="*" ./