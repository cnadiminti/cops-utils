all: clean tests

build: cops_utils/* tests/*
	@echo '======== RUNNING build ========'
	python setup.py sdist

tests: build
	@echo '======== RUNNING tests ========'
	tox -vvv

docker-build: build
	@echo '======== RUNNING docker-build ========'
	docker build -t cops-utils:0.0.1dev0 .

clean:
	@echo '======== RUNNING clean ========'
	rm -rf .tox .coverage coverage-html
	rm -rf build dist *.egg-info
	find . -name '*.pyc' -delete
