from setuptools import setup, find_packages
import os

def read_file(fname):
    with open(os.path.join(os.path.dirname(__file__), fname), encoding='utf-8') as f:
        return f.read()

setup(
    name="yorichecker",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A CLI tool to check Crunchyroll login credentials",
    long_description=read_file("README.md"),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/yorichecker",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "playwright>=1.40.0",
    ],
    entry_points={
        "console_scripts": [
            "yorichecker=yorichecker.cli:main",
        ],
    },
    include_package_data=True,
)