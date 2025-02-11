from setuptools import setup, find_packages

setup(
    name="pdf2md-core",
    version="0.1.0",
    description="Convert PDF to Markdown with embedded base64 images",
    packages=find_packages(),
    install_requires=[
        "PyMuPDF==1.22.5",  # PDF processing
        "Pillow>=11.1.0",   # Image processing and WebP support
        "beautifulsoup4>=4.12.0",  # HTML parsing
    ],
    entry_points={
        'console_scripts': [
            'pdf2md=src.cli:main',
        ],
    },
    python_requires=">=3.8",
)
