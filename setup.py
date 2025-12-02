from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="cogniguard",
    version="1.0.0",
    author="Louisa Wamuyu Saburi",
    author_email="louisawamuyu@gmail.com",
    description="AI Safety & Misinformation Detection - Detects 6 perturbation types from ACL 2025",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/louisawamuyu/cogniguard",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[],
    entry_points={
        "console_scripts": [
            "cogniguard=cogniguard.cli:main",
        ],
    },
)