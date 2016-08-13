all: clean tests

build: cops_utils/* tests/*
	@echo "======== RUNNING $@ ========"
	python setup.py sdist

tests: build
	@echo "======== RUNNING $@ ========"
	tox -vvv

docker-build: build
	@echo "======== RUNNING $@ ========"
	docker build -t cops-utils:0.0.1dev0 .

docker-run: docker-build
	@echo "======== RUNNING $@ ========"
	docker run --rm cops-utils:0.0.1dev0 dockercompose2run

clean:
	@echo "======== RUNNING $@ ========"
	rm -rf .tox .coverage coverage-html
	rm -rf build dist *.egg-info
	find . -name '*.pyc' -delete

dev-setup:
	@echo "======== RUNNING $@ ========"
	sudo pip install tox