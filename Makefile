.PHONY: env
env: env/.done requirements.txt

env/bin/pip:
	virtualenv -p python3 env
	env/bin/pip install --upgrade pip wheel setuptools

env/.done: env/bin/pip setup.py requirements-dev.txt
	env/bin/pip install -r requirements-dev.txt -e .
	touch env/.done

env/bin/pip-compile: env/bin/pip
	env/bin/pip install pip-tools

requirements-dev.txt: env/bin/pip-compile requirements.in requirements-dev.in
	env/bin/pip-compile --no-index requirements.in requirements-dev.in -o requirements-dev.txt

requirements.txt: env/bin/pip-compile requirements.in
	env/bin/pip-compile --no-index requirements.in -o requirements.txt

.PHONY: run
run: env
	env/bin/qvarn run

.PHONY: test
test: env
	env/bin/py.test tests --cov=qvarn --cov-report=term-missing

.PHONY: dist
dist: env/bin/pip
	env/bin/python setup.py sdist bdist_wheel
