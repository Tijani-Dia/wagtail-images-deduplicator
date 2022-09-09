from setuptools import find_packages, setup

__version__ = "1.0a1"

with open("README.md", "r") as fh:
    long_description = fh.read()

install_requires = [
    "wagtail>=3.0,<5.0",
    "imagehash",
]

test_requires = [
    "pytest",
    "pytest-cov",
    "pytest-django",
    "black",
    "isort",
    "flake8",
    "dj-database-url",
]

build_requires = [
    "twine",
    "check-wheel-contents",
]

setup(
    name="wagtail-images-deduplicator",
    version=__version__,
    description="Detect duplicates in the Wagtail images library.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Tidiane Dia, Jacob Topp-Mugglestone",
    author_email="atdia97@gmail.com",
    url="https://github.com/tijani-dia/wagtail-images-deduplicator/",
    project_urls={
        "Source": "https://github.com/tijani-dia/wagtail-images-deduplicator/",
        "Issue tracker": "https://github.com/tijani-dia/wagtail-images-deduplicator/issues/",
    },
    install_requires=install_requires,
    tests_require=test_requires,
    extras_require={
        "test": test_requires,
        "build": build_requires,
    },
    package_dir={"": "src"},
    packages=find_packages("src"),
    include_package_data=True,
    zip_safe=False,
    license="BSD-3-Clause",
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3",
        "Framework :: Django",
        "Framework :: Wagtail",
        "Topic :: Internet :: WWW/HTTP",
    ],
)
