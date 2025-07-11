#!/bin/bash
# Virtual Environment Management Script for The Boring Agents

VENV_DIR="venv"
PYTHON_VERSION="3.8"

show_help() {
    echo "🐍 Virtual Environment Management for The Boring Agents"
    echo ""
    echo "Usage: ./venv.sh [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  create     Create a new virtual environment"
    echo "  activate   Activate the virtual environment"
    echo "  deactivate Deactivate the virtual environment"
    echo "  install    Install dependencies in the virtual environment"
    echo "  update     Update dependencies in the virtual environment"
    echo "  clean      Remove the virtual environment"
    echo "  status     Show virtual environment status"
    echo "  help       Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./venv.sh create"
    echo "  ./venv.sh activate"
    echo "  source venv/bin/activate  # Alternative activation"
}

check_python() {
    python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
    if [ "$(echo "$python_version $PYTHON_VERSION" | tr " " "\n" | sort -V | head -n1)" != "$PYTHON_VERSION" ]; then
        echo "❌ Python $PYTHON_VERSION+ is required. Current version: $python_version"
        exit 1
    fi
    echo "✅ Python version check passed: $python_version"
}

create_venv() {
    echo "🐍 Creating virtual environment..."
    check_python
    
    if [ -d "$VENV_DIR" ]; then
        echo "⚠️  Virtual environment already exists at $VENV_DIR/"
        read -p "Do you want to recreate it? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "❌ Virtual environment creation cancelled"
            exit 1
        fi
        rm -rf "$VENV_DIR"
    fi
    
    python3 -m venv "$VENV_DIR"
    echo "✅ Virtual environment created: $VENV_DIR/"
    
    # Activate and upgrade pip
    source "$VENV_DIR/bin/activate"
    pip install --upgrade pip
    echo "✅ Pip upgraded"
    
    # Install dependencies
    if [ -f "requirements.txt" ]; then
        echo "📦 Installing dependencies..."
        pip install -r requirements.txt
        echo "✅ Dependencies installed"
    else
        echo "⚠️  No requirements.txt found"
    fi
    
    echo ""
    echo "🎉 Virtual environment setup complete!"
    echo "To activate: source $VENV_DIR/bin/activate"
    echo "To deactivate: deactivate"
}

activate_venv() {
    if [ ! -d "$VENV_DIR" ]; then
        echo "❌ Virtual environment not found. Run './venv.sh create' first."
        exit 1
    fi
    
    echo "🔧 Activating virtual environment..."
    source "$VENV_DIR/bin/activate"
    echo "✅ Virtual environment activated"
    echo "💡 To deactivate, run: deactivate"
}

deactivate_venv() {
    if [ -n "$VIRTUAL_ENV" ]; then
        deactivate
        echo "✅ Virtual environment deactivated"
    else
        echo "ℹ️  No virtual environment is currently active"
    fi
}

install_deps() {
    if [ ! -d "$VENV_DIR" ]; then
        echo "❌ Virtual environment not found. Run './venv.sh create' first."
        exit 1
    fi
    
    source "$VENV_DIR/bin/activate"
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
    echo "✅ Dependencies installed"
}

update_deps() {
    if [ ! -d "$VENV_DIR" ]; then
        echo "❌ Virtual environment not found. Run './venv.sh create' first."
        exit 1
    fi
    
    source "$VENV_DIR/bin/activate"
    echo "⬆️  Updating dependencies..."
    pip install --upgrade -r requirements.txt
    echo "✅ Dependencies updated"
}

clean_venv() {
    if [ -d "$VENV_DIR" ]; then
        echo "🗑️  Removing virtual environment..."
        rm -rf "$VENV_DIR"
        echo "✅ Virtual environment removed"
    else
        echo "ℹ️  No virtual environment found to remove"
    fi
}

show_status() {
    echo "🐍 Virtual Environment Status"
    echo "=========================="
    
    if [ -d "$VENV_DIR" ]; then
        echo "✅ Virtual environment exists: $VENV_DIR/"
        
        if [ -n "$VIRTUAL_ENV" ]; then
            echo "✅ Virtual environment is ACTIVE"
            echo "📍 Active environment: $VIRTUAL_ENV"
        else
            echo "ℹ️  Virtual environment is NOT active"
        fi
        
        # Show Python version in venv
        if [ -f "$VENV_DIR/bin/python" ]; then
            venv_python_version=$("$VENV_DIR/bin/python" --version 2>&1)
            echo "🐍 Python version: $venv_python_version"
        fi
        
        # Show installed packages
        if [ -n "$VIRTUAL_ENV" ]; then
            echo ""
            echo "📦 Installed packages:"
            pip list --format=columns
        fi
    else
        echo "❌ Virtual environment does not exist"
        echo "💡 Run './venv.sh create' to create one"
    fi
}

# Main script logic
case "${1:-help}" in
    "create")
        create_venv
        ;;
    "activate")
        activate_venv
        ;;
    "deactivate")
        deactivate_venv
        ;;
    "install")
        install_deps
        ;;
    "update")
        update_deps
        ;;
    "clean")
        clean_venv
        ;;
    "status")
        show_status
        ;;
    "help"|*)
        show_help
        ;;
esac 