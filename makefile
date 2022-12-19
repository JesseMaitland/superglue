#!/usr/bin/env bash

export REQ_FILE = requirements/development.txt
export PROJECT_DIR = superglue
export PROJECT_NAME = superglue
export TEST_DIR = tests
export EMAIL = jesse.maitland@heyjobs.de
export USER = "Jesse Maitland"


#############################################################
#              Commands for Python environment              #
#############################################################

.PHONY: dev-init
dev-init:
	if [[ -d ./venv ]]; then rm -rf venv; fi \
	&& python3 -m venv venv \
	&& . venv/bin/activate \
	&& pip install --upgrade pip setuptools wheel --progress-bar off \
	&& pip install -r ${REQ_FILE} --progress-bar off


.PHONY: dev-requirements
dev-requirements:
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


.PHONY: install-dev
install-dev:
	pip install -e ".[dev]"


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
	make init
	make rm-zip
	make rm-egg
	make unlink

.PHONY: build
build:
	. venv/bin/activate \
	&& python setup.py sdist bdist_wheel


#############################################################
#              Commands for testing                         #
#############################################################

.PHONY: lint
lint:
	black ${PROJECT_DIR} ${TEST_DIR} --check


.PHONY: format
format:
	black ${PROJECT_DIR} ${TEST_DIR}


.PHONY: test
test:
	pytest ${TEST_DIR} -p no:warnings -s -vv


.PHONY: qa
qa:
	make test
	make lint
