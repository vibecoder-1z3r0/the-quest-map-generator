# Quest Map Generator. The shipped artifact is a single dist/index.html.
PY ?= $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)

.PHONY: build lint test check clean setup screenshots baselines

build:            ## combine src/ into dist/index.html
	$(PY) scripts/build.py

lint: build       ## ESLint, html-validate, ruff
	npx --no-install eslint src
	npx --no-install html-validate dist/index.html
	$(PY) -m ruff check scripts tests
	$(PY) -m ruff format --check scripts tests

test: build       ## run the Playwright suite against dist/index.html
	$(PY) -m pytest

check: lint test  ## what CI runs

screenshots: build ## regenerate README screenshots from the real editor
	$(PY) scripts/screenshots.py

baselines: build  ## regenerate the visual baselines
	QMG_UPDATE_BASELINES=1 $(PY) -m pytest tests/test_visual.py

setup:            ## install dev tooling
	npm install
	python3 -m venv .venv && .venv/bin/pip install -e '.[dev]'

clean:
	rm -rf dist test-artifacts
