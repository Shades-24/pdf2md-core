#!/bin/bash

echo "Installing system dependencies..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    if ! command -v brew &> /dev/null; then
        echo "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    
    echo "Installing macOS dependencies..."
    brew install \
        poppler \
        tesseract \
        ghostscript \
        libvips \
        pkg-config \
        tesseract-lang
else
    # Linux
    echo "Installing Linux dependencies..."
    sudo apt-get update
    sudo apt-get install -y \
        poppler-utils \
        tesseract-ocr \
        ghostscript \
        libvips42 \
        pkg-config \
        tesseract-ocr-all
fi

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

# Install core dependencies first
echo "Installing core dependencies..."
pip install numpy pillow

# Install remaining dependencies
echo "Installing remaining dependencies..."
pip install -r requirements.txt

echo "Installation complete!"
echo ""
echo "Next steps:"
echo "1. Create a .env file with your Gemini API key:"
echo "   echo \"GEMINI_API_KEY=your_key_here\" > .env"
echo ""
echo "2. Activate the virtual environment in new terminals:"
echo "   source .venv/bin/activate"
echo ""
echo "3. Test the installation:"
echo "   python src/cli.py tests/sample_pdfs/test.pdf"
