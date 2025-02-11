from setuptools import setup, find_packages

setup(
    name="pdf2md-core",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'wheel>=0.42.0',
        'setuptools>=69.0.0',
        'numpy>=1.26.0',
        'pillow>=10.0.0',
        'python-dotenv>=1.0.0',
        'google-generativeai>=0.3.1',
        'pytesseract>=0.3.10',
        'pdfplumber>=0.10.2',
        'pytest>=7.4.0',
        'pytest-asyncio>=0.23.0',
        'aiohttp>=3.9.0',
        'pymupdf>=1.22.5'
    ],
    python_requires='>=3.9',
)
