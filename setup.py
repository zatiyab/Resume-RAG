from setuptools import setup, find_packages

# Read requirements.txt and use as install_requires
with open("requirements.txt", encoding="utf-8") as f:
    requirements = f.read().splitlines()

setup(
    name="HireMind",
    version="0.1.0",
    packages=find_packages(),
    install_requires=requirements,
    include_package_data=True,
    zip_safe=False,
)
