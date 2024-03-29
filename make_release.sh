#!/bin/sh

current_version='1.0a1'

if git rev-parse "$current_version" >/dev/null 2>&1; then
  echo "It looks like there is already a tag named '$current_version'! \nDid you forget to update the package version?";
  exit 1
fi

# Cleanup
find . -name '*.pyc' -exec rm -rf {} +
find . -name '__pycache__' -exec rm -rf {} +
find . -name '*.egg-info' -exec rm -rf {} +
rm -rf dist/ build/

# Build wheels and source distributions
python3 -m pip install --upgrade build
python3 -m build

# Sanity check wheel contents
# W004: silence warnings about migration files not being importable
check-wheel-contents --ignore W004 dist/*.whl

echo "\nFabulous! $current_version is ready to be released ;)"
echo "1. Create a git tag first: git tag $current_version"
echo "   or use 'git tag -s $current_version' to create a GPG-signed tag."
echo "2. Don't forget to push tags: git push --tags"
echo "3. When you are ready, publish the package to PyPi: python3 -m twine upload dist/*"
