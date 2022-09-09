default: clean

clean:
	find . -name '*.pyc' -exec rm -rf {} +
	find . -name '__pycache__' -exec rm -rf {} +
	find . -name '*.egg-info' -exec rm -rf {} +
	rm -rf dist/ build/ .pytest_cache/

format:
	isort src/wagtail_images_deduplicator typings tests setup.py
	black src/wagtail_images_deduplicator typings tests setup.py
	flake8 src/wagtail_images_deduplicator typings tests setup.py

lint:
	isort --check-only --diff src/wagtail_images_deduplicator typings tests setup.py
	black --check --diff src/wagtail_images_deduplicator typings tests setup.py
	flake8 src/wagtail_images_deduplicator typings tests setup.py

test:
	pytest --cov wagtail_images_deduplicator
