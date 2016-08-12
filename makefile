all: clean build test

build:
	python setup.py build

test:
	tox -vvv

clean:
	rm -rf .tox .coverage coverage-html
	find . -name \*.pyc -exec rm \{\} \;
