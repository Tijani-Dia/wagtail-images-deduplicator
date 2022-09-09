default: format

SRC_FILES = src/wagtail_images_deduplicator tests setup.py

format:
	isort $(SRC_FILES)
	black $(SRC_FILES)
	flake8 $(SRC_FILES)

lint:
	isort --check-only --diff $(SRC_FILES)
	black --check --diff $(SRC_FILES)
	flake8 $(SRC_FILES)

test:
	pytest --cov wagtail_images_deduplicator

clean:
	rm -rf dist/ build/ .pytest_cache/ .tox/ images/
	find . -name '*.pyc' -exec rm -rf {} +
	find . -name '__pycache__' -exec rm -rf {} +
	find . -name '*.egg-info' -exec rm -rf {} +
