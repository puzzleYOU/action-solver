venv:
	python3 -m venv .venv
	.venv/bin/pip3 install poetry
	.venv/bin/python3 setup.py install
