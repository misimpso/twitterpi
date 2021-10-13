PROJ_BASE=$(shell pwd)
PYTHONVENV=$(PROJ_BASE)/venv
VENVPYTHON=$(PYTHONVENV)/bin/python

PHONY: init
init:
	@echo "Creating virtual environment 'venv' for development."
	python3 -m venv venv
	@echo "\nYou may want to activate the virtual environmnent with 'source venv/bin/activate'\n"

PHONY: develop
develop:
	@echo "Installing twitterpi, with editible modules ('python -m pip install --editable .[test]')"
	$(VENVPYTHON) -m pip install --editable .[test]

PHONY: build
build:
	$(VENVPYTHON) -m pip install build
	$(VENVPYTHON) -m build

PHONY: clean
clean:
	@echo "Removing build artifacts"
	rm -rf $(PROJ_BASE)/build
	rm -rf $(PROJ_BASE)/dist
	rm -rf $(PROJ_BASE)/*.egg-info
	rm -rf $(PROJ_BASE)/docs/_build/*
	rm -f $(PROJ_BASE)/.coverage
	rm -rf $(PROJ_BASE)/tests/htmlcov

PHONY: sparkling
sparkling: clean
	rm -rf $(PROJ_BASE)/venv*

PHONY: docs
docs: clean
	$(VENVPYTHON) -m pip install --editable .[doc]
	cd docs && make auto && make html

PHONY: test
test:
	rm -f .coverage
	rm -rf tests/htmlcov
	find tests -name "*_tests.py" | xargs -n1 -t $(VENVPYTHON) -m coverage run -a
	$(VENVPYTHON) -m coverage html
