from setuptools import find_packages, setup

setup(
    name="action-solver",
    version="0.1.0",
    description="a library helping to structure complex code",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="puzzleYOU GmbH",
    url="https://github.com/puzzleYOU/action-solver/",
    license="MIT",
    platforms=["any"],
    packages=find_packages("."),
    install_requires=["igraph"],
    zip_safe=True,
)
