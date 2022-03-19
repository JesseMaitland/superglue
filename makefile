#!/usr/bin/env bash

export REQ_FILE = requirements.txt
export PROJECT_DIR = glued
export PROJECT_NAME = glued
export TEST_DIR = tests

#############################################################
#              Commands for Python environment              #
#############################################################

.PHONY: py-init
py-init:
	if [[ -d ./venv ]]; then rm -rf venv; fi \
	&& python3.6 -m venv venv \
	&& . venv/bin/activate \
	&& pip install --upgrade pip setuptools wheel --progress-bar off \
	&& pip install -r ${REQ_FILE} --progress-bar off


.PHONY: requirements
requirements:
	if [[ -f ${REQ_FILE} ]]; then rm -f ${REQ_FILE}; fi \
	&& . venv/bin/activate \
	&& pip freeze | grep ${PROJECT_NAME} -v > ${REQ_FILE}


.PHONY: update
update:
	. venv/bin/activate \
	&& pip install --upgrade pip setuptools wheel


.PHONY: install
install:
	pip install -e .


.PHONY: uninstall
uninstall:
	pip uninstall ${PROJECT_NAME} --yes


.PHONY: zip
zip:
	. venv/bin/activate \
	&& python -m zipapp -p ${PWD}/venv/bin/python ${PROJECT_NAME}


.PHONY: rm-zip
rm-zip:
	rm -f ${PROJECT_NAME}.pyz


.PHONY: rm-egg
rm-egg:
	rm -rf ${PROJECT_NAME}.egg-info


.PHONY: clean
clean:
	make py-init
	make rm-zip
	make rm-egg
	make unlink

.PHONY: build
build:
	. venv/bin/activate \
	&& python setup.py sdist bdist_wheel

#############################################################
#              Commands creating links                      #
#############################################################
.PHONY: link
link:
	ln -s ${PWD}/${PROJECT_NAME}.pyz ~/bin/${PROJECT_NAME}

.PHONY: unlink
unlink:
	rm -f ~/bin/${PROJECT_NAME}


#############################################################
#              Commands for testing                         #
#############################################################

.PHONY: lint
lint:
	. venv/bin/activate && python -m black ${PROJECT_DIR} ${TEST_DIR} --check


.PHONY: format
format:
	. venv/bin/activate && python -m black ${PROJECT_DIR} ${TEST_DIR}


.PHONY: test
test:
	. venv/bin/activate && python -m pytest ${TEST_DIR} -p no:warnings -s


.PHONY: qa
qa:
	make test
	make lint
