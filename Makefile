.DEFAULT_GOAL := help


.PHONY: clean
clean: clean-build clean-pyc clean-test		## Clean temp files


.PHONY: clean-build
clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +


.PHONY: clean-pyc
clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +


.PHONY: clean-test
clean-test:
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/


# ============================================================================
#
#	project specific config


.PHONY: fmt
fmt:                                  ## Lint and format code. Modifies files in-place.
	black src/


.PHONY: tdd
tdd:                                  ## Watch source files and run tests on change
	watchexec -e py pytest


.PHONY: test
test:                                 ## Invoke tests
	pytest -v tests/


.PHONY: install-all
install-all:                          ## Install all packages for editable local development
	pip3 install -e .


.PHONY: uninstall-all
uninstall-all:                        ## Remove all install pip3 packages
	pip3 freeze | sed 's/^-e.*//g' | xargs pip3 uninstall -y
	pip3 uninstall -y sixtydb


# ============================================================================
#
#	these exist to aid manual testing with the tool
#	they may be removed in the future


.PHONY: dc-rm
dc-rm:                                ## DEMO: remove all containers
	docker rm -f simdev-a
	docker rm -f simdev-b
	docker rm -f simdev-c


.PHONY: dc-up
dc-up:                                ## DEMO: bring up all containers
	docker run -d --volume ${PWD}:/simdev --name simdev-a simdev
	docker run -d --volume ${PWD}:/simdev --name simdev-b simdev
	docker run -d --volume ${PWD}:/simdev --name simdev-c simdev


.PHONY: dc-rmi
dc-rmi:                               ## DEMO: remove image
	docker rmi -f simdev


.PHONY: dc-build
dc-build:                             ## DEMO: build image
	# docker-compose build
	docker build . -t simdev


.PHONY: dc-rebuild
dc-rebuild:dc-rm dc-rmi dc-build      ## DEMO: teardown containers, image and and rebuild image


.PHONY: run-a
run-a:                                ## DEMO: exec container A
	docker exec -it simdev-a /bin/bash


.PHONY: run-b
run-b:                                ## DEMO: exec container B
	docker exec -it simdev-b /bin/bash


.PHONY: run-c
run-c:                                ## DEMO: exec container C
	docker exec -it simdev-c /bin/bash


# ============================================================================
#
#	help


.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}'
