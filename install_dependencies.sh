#!/bin/bash
# System dependencies
brew install poppler tesseract ghostscript libvips

# Python environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
