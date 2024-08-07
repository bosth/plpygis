.PHONY: test

build: plpygis/*.py
	python -m build

test:
	pytest

cov:
	pytest --cov=plpygis --cov-report term-missing

clean:
	find . -name "*.pyc" -print0 | xargs -0 rm -rf
	find . -name "__pycache__" -print0 | xargs -0 rm -rf
	rm -rf dist plpygis.egg-info
	rm -rf build doc/build
