import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mlangpy",
    version="0.0.6",
    author="Jamie Muir",
    author_email="jam10@hw.ac.uk",
    description="A package for parsing and manipulating some standard metalanguages.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rium9/mlangpy",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    include_package_data=True
)