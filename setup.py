from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="pdf2md-core",
    version="1.0.0",
    author="Chris Raad",
    description="High-performance PDF to Markdown converter with advanced features",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/chrisraad/pdf2md-core",
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
        "Topic :: Text Processing :: Markup",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "pdf2md=src.cli:main",
            "pdf2md-web=src.web.app:run_server",
        ],
    },
    package_data={
        "src.web": ["templates/*", "static/*"],
    },
    include_package_data=True,
)
