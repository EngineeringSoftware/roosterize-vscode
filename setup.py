import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="roosterize",
    version="1.0.0",
    author="Pengyu Nie, Karl Palmskog, Junyi Jessy Li, Milos Gligoric",
    author_email="pynie@utexas.edu",
    description="Roosterize: code conventions helper for Coq",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/EngineeringSoftware/roosterize",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ],
    install_requires=[
        "configargparse~=1.2.3",
        "nltk~=3.5",
        "numpy~=1.19.2",
        "future",
        "seutil>=0.5.3",
        "six",
        "torch==1.1.0",
        "torchtext==0.4.0",
        "tqdm~=4.30.0",
    ]
)