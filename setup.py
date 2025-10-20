from setuptools import setup, find_packages

setup(
    name="quickshift",
    version="0.1.0",
    description="A Python-based DSL for local file-structure data manipulation",
    author="ByteMeDirk",
    author_email="bytemedirk@proton.me",
    packages=find_packages(),
    install_requires=[
        "ply>=3.11",
    ],
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "quickshift=quickshift.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
