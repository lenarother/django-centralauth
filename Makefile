.PHONY: clean tests cov docs release

VERSION = $(shell pipenv run python -c "print(__import__('centralauth').__version__)")

clean:
	rm -fr docs/_build build/ dist/
	pipenv run make -C docs clean

tests:
	pipenv run py.test --cov

cov: tests
	pipenv run coverage html
	@echo open htmlcov/index.html

apidoc:
	pipenv run make -C docs apidoc

docs:
	pipenv run make -C docs html
	@echo open docs/_build/html/index.html

release:
	@echo About to release ${VERSION}; read
	pipenv run python setup.py sdist upload
	pipenv run python setup.py bdist_wheel upload
	git tag -a "${VERSION}" -m "Version ${VERSION}" && git push --follow-tags
