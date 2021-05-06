.PHONY: clean correct docs pytests tests coverage-html release
.ONESHELL: release

clean:
	find . -name '*.pyc' -delete
	rm -fr build/ dist/ htmlcov/ __pycache__
	poetry run make -C docs clean

correct:
	poetry run isort centralauth tests
	poetry run black -q centralauth tests

docs:
	poetry run make -C docs html

pytests:
	@PYTHONPATH=$(CURDIR):${PYTHONPATH} poetry run pytest

tests:
	@PYTHONPATH=$(CURDIR):${PYTHONPATH} poetry run pytest --cov --isort --flake8 --black

coverage-html: pytests
	poetry run coverage html

release:
	@echo About to release `poetry version -s`
	@echo [ENTER] to continue; read
	git tag -a "`poetry version -s`" -m "Version `poetry version -s`" && git push --follow-tags
