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

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Set up environment file
if [ ! -f .env ]; then
    echo "🔧 Creating .env file from template..."
    cp .env.example .env
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
    echo "1. Edit .env file and add your OpenAI API key"
    echo "2. Test the CLI: python main.py status"
    echo "3. Generate your first content: python main.py content course-outline --topic 'Python Basics'"
    echo ""
    echo "📚 For more information, see README.md"
else
    echo "❌ Installation test failed. Please check the error messages above."
    exit 1
fi