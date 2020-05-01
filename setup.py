import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="staticsql",
    version="0.9.3",
    author="Frederik Siegumfeldt",
    author_email="siegumfeldt@gmail.com",
    description="Library for working with StaticSQL entity metadata files.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/iteg-hq/staticsql",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
