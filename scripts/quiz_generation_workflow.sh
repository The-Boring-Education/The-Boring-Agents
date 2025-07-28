#!/bin/bash

# =============================================================================
# Quiz Generation - Professional Workflow Automation
# The Boring Education - AI Agent Orchestrator  
# =============================================================================

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Colors for beautiful output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly PURPLE='\033[0;35m'
readonly CYAN='\033[0;36m'
readonly WHITE='\033[1;37m'
readonly NC='\033[0m' # No Color

# Configuration
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
readonly OUTPUT_DIR="$PROJECT_ROOT/output"
readonly LOG_FILE="$PROJECT_ROOT/logs/quiz_workflow_$(date +%Y%m%d_%H%M%S).log"

# Ensure we're in the right directory
cd "$PROJECT_ROOT"

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

log() {
    local level=$1
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    mkdir -p "$(dirname "$LOG_FILE")"
    echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
    
    case $level in
        "ERROR") echo -e "${RED}❌ $message${NC}" >&2 ;;
        "SUCCESS") echo -e "${GREEN}✅ $message${NC}" >&2 ;;
        "INFO") echo -e "${BLUE}ℹ️  $message${NC}" >&2 ;;
        "WARN") echo -e "${YELLOW}⚠️  $message${NC}" >&2 ;;
        "PROGRESS") echo -e "${PURPLE}🔄 $message${NC}" >&2 ;;
        "DEBUG") echo -e "${CYAN}🔧 $message${NC}" >&2 ;;
    esac
}

show_header() {
    clear
    echo -e "${PURPLE}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║${GREEN}                    🎯 Quiz Generation - Pro Workflow                         ${PURPLE}║${NC}"
    echo -e "${PURPLE}║${GREEN}                         The Boring Education AI Agents                       ${PURPLE}║${NC}"
    echo -e "${PURPLE}╚══════════════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

show_progress_bar() {
    local current=$1
    local total=$2
    local width=50
    local percentage=$((current * 100 / total))
    local completed=$((current * width / total))
    
    printf "\r${CYAN}Progress: [" >&2
    printf "%${completed}s" | tr ' ' '█' >&2
    printf "%$((width - completed))s" | tr ' ' '░' >&2
    printf "] %d%% (%d/%d)${NC}" $percentage $current $total >&2
    
    if [ $current -eq $total ]; then
        echo "" >&2
    fi
}

# =============================================================================
# MAIN WORKFLOW FUNCTIONS
# =============================================================================

setup_environment() {
    log "INFO" "Setting up environment..."
    
    # Create necessary directories
    mkdir -p "$OUTPUT_DIR" "$(dirname "$LOG_FILE")"
    
    # Validate Python environment
    if ! command -v python3 &> /dev/null; then
        log "ERROR" "Python3 is required but not installed"
        exit 1
    fi
    
    # Check if main.py exists
    if [ ! -f "$PROJECT_ROOT/main.py" ]; then
        log "ERROR" "main.py not found. Please run from The-Boring-Agents directory"
        exit 1
    fi
    
    # Test system status
    log "DEBUG" "Testing system status..."
    if ! python3 main.py status >/dev/null 2>&1; then
        log "ERROR" "System check failed. Please ensure all dependencies are installed."
        exit 1
    fi
    
    log "SUCCESS" "Environment setup complete"
}

get_user_input() {
    show_header
    
    echo -e "${GREEN}🎯 Welcome to the Quiz Generator!${NC}"
    echo -e "${BLUE}Create comprehensive quizzes for any technology topic.${NC}"
    echo ""
    echo -e "${CYAN}Available Topics:${NC}"
    echo -e "${WHITE}React.js, Node.js, MongoDB, Express.js, HTML, CSS, JavaScript,"
    echo -e "Python, Java, C++, Redux, SQL, NoSQL, Data Science, Machine Learning,"
    echo -e "Deep Learning, AI, Cloud Computing, DevOps, Cyber Security${NC}"
    echo ""
    
    # Get topic
    while true; do
        read -p "$(echo -e ${YELLOW}Enter the quiz topic: ${NC})" TOPIC
        
        if [[ -n "$TOPIC" && ${#TOPIC} -ge 2 ]]; then
            break
        else
            echo -e "${RED}Please enter a valid topic (at least 2 characters)${NC}"
        fi
    done
    
    # Get question count
    while true; do
        read -p "$(echo -e ${YELLOW}Number of questions [10-50, default: 20]: ${NC})" QUESTION_COUNT
        
        if [[ -z "$QUESTION_COUNT" ]]; then
            QUESTION_COUNT=20
            break
        elif [[ "$QUESTION_COUNT" =~ ^[0-9]+$ ]] && [ "$QUESTION_COUNT" -ge 10 ] && [ "$QUESTION_COUNT" -le 50 ]; then
            break
        else
            echo -e "${RED}Please enter a number between 10 and 50${NC}"
        fi
    done
    
    # Get target audience
    echo ""
    echo -e "${CYAN}Target Audience:${NC}"
    echo -e "${BLUE}   1. ${WHITE}beginners${BLUE} - New to the technology${NC}"
    echo -e "${BLUE}   2. ${WHITE}developers${BLUE} - Working professionals (default)${NC}"
    echo -e "${BLUE}   3. ${WHITE}experts${BLUE} - Advanced users${NC}"
    echo ""
    
    read -p "$(echo -e ${YELLOW}Select target audience [1-3, default: 2]: ${NC})" audience_choice
    
    case $audience_choice in
        1|beginners) TARGET_AUDIENCE="beginners" ;;
        3|experts) TARGET_AUDIENCE="experts" ;;
        *) TARGET_AUDIENCE="developers" ;;
    esac
    
    # Create normalized names
    TOPIC_LOWER=$(echo "$TOPIC" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr '.' '-')
    
    echo ""
    echo -e "${GREEN}✅ Configuration Summary:${NC}"
    echo -e "${BLUE}   📝 Topic: $TOPIC${NC}"
    echo -e "${BLUE}   🔢 Questions: $QUESTION_COUNT${NC}"
    echo -e "${BLUE}   👥 Audience: $TARGET_AUDIENCE${NC}"
    echo ""
    
    read -p "$(echo -e ${YELLOW}Generate this quiz? [Y/n]: ${NC})" confirm
    if [[ $confirm =~ ^[Nn]$ ]]; then
        log "INFO" "Quiz generation cancelled by user"
        exit 0
    fi
}

run_quiz_generation() {
    local total_steps=3
    
    echo ""
    log "INFO" "Starting quiz generation..."
    echo ""
    
    # Step 1: Generate quiz
    log "PROGRESS" "Step 1/$total_steps: Generating quiz questions..."
    echo -e "${BLUE}This includes:${NC}"
    echo -e "${WHITE}  • Researching ${TOPIC} topics${NC}"
    echo -e "${WHITE}  • Creating ${QUESTION_COUNT} questions${NC}"
    echo -e "${WHITE}  • Adding explanations${NC}"
    echo -e "${WHITE}  • Quality review${NC}"
    echo ""
    
    local quiz_output=$(python3 main.py quiz generate \
        --topic "$TOPIC" \
        --question-count "$QUESTION_COUNT" \
        --target-audience "$TARGET_AUDIENCE" \
        --save 2>&1 | tee -a "$LOG_FILE")
    
    # Extract output file from the output
    local output_file=$(echo "$quiz_output" | grep -o "output/quiz_.*\.json" | tail -1)
    
    if [ -z "$output_file" ] || [ ! -f "$output_file" ]; then
        log "ERROR" "Quiz generation failed - no output file found"
        return 1
    fi
    
    log "SUCCESS" "Quiz generated successfully"
    show_progress_bar 1 $total_steps
    
    # Step 2: Validate quiz
    log "PROGRESS" "Step 2/$total_steps: Validating quiz quality..."
    if python3 main.py quiz validate --quiz-file "$output_file" >> "$LOG_FILE" 2>&1; then
        log "SUCCESS" "Quiz validation passed"
        show_progress_bar 2 $total_steps
    else
        log "WARN" "Quiz validation had warnings, but continuing"
        show_progress_bar 2 $total_steps
    fi
    
    # Step 3: Ask about upload
    log "PROGRESS" "Step 3/$total_steps: Upload to database (optional)"
    echo ""
    read -p "$(echo -e ${YELLOW}Upload quiz to database? [y/N]: ${NC})" upload_choice
    
    if [[ $upload_choice =~ ^[Yy]$ ]]; then
        # Get API URL
        read -p "$(echo -e ${YELLOW}API URL [default: http://localhost:3000]: ${NC})" API_URL
        API_URL=${API_URL:-"http://localhost:3000"}
        
        # Get admin secret
        read -p "$(echo -e ${YELLOW}Admin secret [default: TBEAdmin]: ${NC})" ADMIN_SECRET
        ADMIN_SECRET=${ADMIN_SECRET:-"TBEAdmin"}
        
        # Upload quiz
        if python3 main.py quiz upload \
            --quiz-file "$output_file" \
            --api-url "$API_URL" \
            --admin-secret "$ADMIN_SECRET" >> "$LOG_FILE" 2>&1; then
            log "SUCCESS" "Quiz uploaded to database"
        else
            log "ERROR" "Failed to upload quiz"
            log "INFO" "Quiz saved locally at: $output_file"
        fi
    else
        log "INFO" "Quiz saved locally (not uploaded)"
    fi
    
    show_progress_bar 3 $total_steps
    
    # Store output file for results
    FINAL_OUTPUT_FILE="$output_file"
}

show_results() {
    echo ""
    log "SUCCESS" "🎉 Quiz Generation Complete!"
    echo ""
    
    if [ -n "${FINAL_OUTPUT_FILE:-}" ] && [ -f "$FINAL_OUTPUT_FILE" ]; then
        echo -e "${GREEN}📁 Generated Quiz:${NC}"
        echo -e "${BLUE}   📄 $FINAL_OUTPUT_FILE${NC}"
        echo ""
        
        # Show quiz summary
        local question_count=$(python3 -c "import json; data=json.load(open('$FINAL_OUTPUT_FILE')); print(len(data.get('quiz', {}).get('questions', [])))")
        local category_name=$(python3 -c "import json; data=json.load(open('$FINAL_OUTPUT_FILE')); print(data.get('quiz', {}).get('categoryName', 'Unknown'))")
        
        echo -e "${GREEN}📊 Quiz Summary:${NC}"
        echo -e "${BLUE}   📚 Category: $category_name${NC}"
        echo -e "${BLUE}   🔢 Questions: $question_count${NC}"
        echo -e "${BLUE}   👥 Target: $TARGET_AUDIENCE${NC}"
    fi
    
    echo ""
    echo -e "${GREEN}📝 Log File:${NC}"
    echo -e "${BLUE}   📋 $LOG_FILE${NC}"
    echo ""
    
    echo -e "${PURPLE}🚀 Your $TOPIC quiz is ready!${NC}"
    echo ""
    echo -e "${GREEN}🎯 Next Steps:${NC}"
    echo -e "${BLUE}   1. Review the generated quiz in the output file${NC}"
    echo -e "${BLUE}   2. Test the quiz with sample users${NC}"
    echo -e "${BLUE}   3. Upload to your quiz platform when ready${NC}"
    echo -e "${BLUE}   4. Monitor quiz performance and iterate${NC}"
}

cleanup_on_exit() {
    if [ -n "${TEMP_DIR:-}" ] && [ -d "$TEMP_DIR" ]; then
        rm -rf "$TEMP_DIR"
    fi
}

# =============================================================================
# MAIN EXECUTION
# =============================================================================

main() {
    # Set up error handling and cleanup
    trap 'log "ERROR" "Script interrupted at line $LINENO"; exit 1' INT TERM
    trap 'log "ERROR" "Script failed at line $LINENO with exit code $?"; exit 1' ERR
    trap cleanup_on_exit EXIT
    
    setup_environment
    get_user_input
    
    if run_quiz_generation; then
        show_results
        log "SUCCESS" "Workflow completed successfully"
    else
        log "ERROR" "Workflow failed. Check log file: $LOG_FILE"
        echo ""
        echo -e "${RED}❌ Quiz generation failed. Check the log file for details:${NC}"
        echo -e "${BLUE}   📋 $LOG_FILE${NC}"
        exit 1
    fi
}

# Run main function
main "$@" 