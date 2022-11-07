from setuptools import setup, find_packages

setup(
    name="willkronberg",
    version="0.1",
    packages=find_packages(),
    setup_requires=["pytest-runner", "flake8"],
    tests_require=["pytest"],
)
