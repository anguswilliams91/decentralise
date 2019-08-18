from pathlib import Path

from setuptools import setup, find_packages


def long_description() -> str:
    root = Path(__file__).resolve().parent
    readme = root / "README.md"
    return readme.read_text(encoding="utf-8")


setup(
    name="decentralise",
    description="Make normally distributed parameters non-centered in Stan programs.",
    long_description=long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/anguswilliams91/decentralise",
    download_url="https://github.com/anguswilliams91/decentralise/archive/master.zip",
    author="Angus Williams",
    author_email="anguswilliams91@gmail.com",
    license="MIT",
    packages=find_packages(),
    version="0.0.1",
    python_requires=">=3.6",
    entry_points={"console_scripts": ["decentralise=decentralise.parse_stan:main"]},
    tests_require=["pytest"],
)
