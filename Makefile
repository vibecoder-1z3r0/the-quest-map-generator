# Quest Map Generator. The shipped artifact is a single dist/index.html.
PY ?= $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)
DENO ?= $(if $(wildcard .venv/bin/deno),.venv/bin/deno,deno)

.PHONY: build lint test check clean setup screenshots baselines

build:            ## combine src/ into dist/index.html
	$(PY) scripts/build.py

lint: build       ## deno lint (JS), HTML check, ruff (Python)
	$(DENO) lint
	$(PY) scripts/lint_html.py
	$(PY) -m ruff check scripts tests
	$(PY) -m ruff format --check scripts tests

test: build       ## run the Playwright suite against dist/index.html
	$(PY) -m pytest

check: lint test  ## what CI runs

screenshots: build ## regenerate README screenshots from the real editor
	$(PY) scripts/screenshots.py

baselines: build  ## regenerate the visual baselines
	QMG_UPDATE_BASELINES=1 $(PY) -m pytest tests/test_visual.py

setup:            ## install the dev tooling (Python only) and the Playwright browser
	python3 -m venv .venv && .venv/bin/pip install -e '.[dev]'
	.venv/bin/python -m playwright install chromium

clean:
	rm -rf dist test-artifacts
