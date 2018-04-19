re-build:
	rm -fr ./dist/*
	python setup.py bdist_wheel
	python setup.py sdist
upload-pkgs:
	twine upload ./dist/*.tar.gz
	twine upload ./dist/*.whl
