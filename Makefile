.PHONY: test

test:
	python -m test -v

clean:
	find . -name "*.pyc" -print0 | xargs -0 rm -rf
	find . -name "__pycache__" -print0 | xargs -0 rm -rf
	rm -rf dist plpygis.egg-info
	rm -rf build doc/build
