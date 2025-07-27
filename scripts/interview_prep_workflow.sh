#!/bin/bash

# =============================================================================
# Interview Prep Sheets - Quick Launcher
# Run this from the project root: ./interview-prep.sh
# =============================================================================

set -euo pipefail

# Colors
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly BLUE='\033[0;34m'
readonly PURPLE='\033[0;35m'
readonly NC='\033[0m'

# Check if we're in the right directory
if [ ! -f "main.py" ] || [ ! -f "scripts/interview_prep_workflow.sh" ]; then
    echo -e "${RED}❌ Please run this script from The-Boring-Agents root directory${NC}"
    exit 1
fi

echo -e "${PURPLE}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${PURPLE}║${GREEN}                    🚀 Interview Prep Sheets Launcher                         ${PURPLE}║${NC}"
echo -e "${PURPLE}║${GREEN}                      Professional Workflow Automation                       ${PURPLE}║${NC}"
echo -e "${PURPLE}╚══════════════════════════════════════════════════════════════════════════════╝${NC}\n"

echo -e "${BLUE}This launcher will guide you through creating comprehensive interview prep sheets${NC}"
echo -e "${BLUE}with automated question generation, metadata, and answer creation.${NC}\n"

echo -e "${GREEN}🎯 What you'll get:${NC}"
echo -e "${BLUE}  ✅ Automated folder structure creation${NC}"
echo -e "${BLUE}  ✅ Requirements template generation${NC}"
echo -e "${BLUE}  ✅ AI-powered question generation${NC}"
echo -e "${BLUE}  ✅ Intelligent metadata addition${NC}"
echo -e "${BLUE}  ✅ Detailed answer generation${NC}"
echo -e "${BLUE}  ✅ Professional formatting${NC}"
echo -e "${BLUE}  ✅ Optional database publishing${NC}\n"

read -p "Ready to start? (y/n): " start_choice
if [[ ! $start_choice =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}👋 Come back when you're ready!${NC}"
    exit 0
fi

# Execute the main workflow script
exec ./scripts/interview_prep_workflow.sh  