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
#                  Commands for CI                          #
#############################################################

.PHONY: ci-install-dependencies
ci-install-dependencies:
	pip install --upgrade pip setuptools wheel --progress-bar off \
	&& pip install -r ${REQ_FILE} --progress-bar off


.PHONY: ci-configure-git
ci-configure-git:
	git config --global user.email "${EMAIL}" \
	&& git config --global user.name "${USER}"


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
