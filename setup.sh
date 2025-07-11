#!/bin/bash
# Development setup script for The Boring Agents

echo "🤖 Setting up The Boring Agents development environment..."

# Check if Python 3.8+ is available
python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
required_version="3.8"

if [ "$(echo "$python_version $required_version" | tr " " "\n" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.8+ is required. Current version: $python_version"
    exit 1
fi

echo "✅ Python version check passed: $python_version"

# Create virtual environment
echo "🐍 Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created: venv/"
else
    echo "✅ Virtual environment already exists: venv/"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Set up environment file
if [ ! -f .env ]; then
    echo "🔧 Creating .env file from template..."
    if [ -f .env.example ]; then
        cp .env.example .env
    else
        echo "# Environment variables for The Boring Agents" > .env
        echo "OPENAI_API_KEY=your_openai_api_key_here" >> .env
        echo "ANTHROPIC_API_KEY=your_anthropic_api_key_here" >> .env
        echo "LOG_LEVEL=INFO" >> .env
        echo "OUTPUT_DIR=./output" >> .env
        echo "DEFAULT_MODEL=gpt-3.5-turbo" >> .env
        echo "TEMPERATURE=0.7" >> .env
        echo "MAX_TOKENS=2000" >> .env
    fi
    echo "📝 Please edit .env file and add your API keys:"
    echo "   - OPENAI_API_KEY=your_api_key_here"
    echo "   - (Optional) ANTHROPIC_API_KEY=your_api_key_here"
else
    echo "✅ .env file already exists"
fi

# Create output directories
echo "📁 Creating output directories..."
mkdir -p output temp logs

# Test the installation
echo "🧪 Testing installation..."
if python test_structure.py; then
    echo ""
    echo "🎉 Setup completed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Activate the virtual environment: source venv/bin/activate"
    echo "2. Edit .env file and add your OpenAI API key"
    echo "3. Test the CLI: python main.py status"
    echo "4. Generate your first content: python main.py content course-outline --topic 'Python Basics'"
    echo ""
    echo "📚 For more information, see README.md"
    echo ""
    echo "💡 To deactivate the virtual environment, run: deactivate"
else
    echo "❌ Installation test failed. Please check the error messages above."
    exit 1
fi