.PHONY: clean correct docs pytests tests coverage-html

clean:
	rm -fr build/ dist/ htmlcov/
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
