#!/bin/bash

echo "Setting up Python environment..."
# Remove existing virtual environment if it exists
if [ -d ".venv" ]; then
    echo "Removing existing virtual environment..."
    rm -rf .venv
fi

# Create new virtual environment
echo "Creating new virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

# Upgrade pip and install basic build tools
echo "Upgrading pip and installing build tools..."
pip install --upgrade pip wheel setuptools

# Install PyMuPDF with special handling for Apple Silicon
echo "Installing PyMuPDF..."
if [[ "$OSTYPE" == "darwin"* ]] && [[ $(uname -m) == "arm64" ]]; then
    pip install PyMuPDF==1.22.5  # Known to work on ARM64
else
    pip install PyMuPDF==1.22.5  # Use same version for consistency
fi

# Install remaining dependencies
echo "Installing remaining dependencies..."
pip install -r requirements.txt

echo "Installation complete!"
echo ""
echo "Next steps:"
echo "1. Activate the virtual environment in new terminals:"
echo "   source .venv/bin/activate"
echo ""
echo "2. Test the installation:"
echo "   python src/cli.py tests/sample_pdfs/test.pdf"
