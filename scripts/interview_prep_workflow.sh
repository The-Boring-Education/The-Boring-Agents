#!/bin/bash

# =============================================================================
# Interview Prep Sheets - Professional Workflow Automation
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
readonly LAB_DIR="$PROJECT_ROOT/lab/interview-prep"
readonly OUTPUT_DIR="$PROJECT_ROOT/output"
readonly LOG_FILE="$PROJECT_ROOT/logs/workflow_$(date +%Y%m%d_%H%M%S).log"

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
        "ERROR") echo -e "${RED}❌ $message${NC}" ;;
        "SUCCESS") echo -e "${GREEN}✅ $message${NC}" ;;
        "INFO") echo -e "${BLUE}ℹ️  $message${NC}" ;;
        "WARN") echo -e "${YELLOW}⚠️  $message${NC}" ;;
        "PROGRESS") echo -e "${PURPLE}🔄 $message${NC}" ;;
    esac
}

show_header() {
    clear
    echo -e "${PURPLE}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║${GREEN}                    🚀 Interview Prep Sheets - Pro Workflow                  ${PURPLE}║${NC}"
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
    
    printf "\r${CYAN}Progress: ["
    printf "%${completed}s" | tr ' ' '█'
    printf "%$((width - completed))s" | tr ' ' '░'
    printf "] %d%% (%d/%d)${NC}" $percentage $current $total
    
    if [ $current -eq $total ]; then
        echo ""
    fi
}

detect_technology_type() {
    local skill=$1
    skill=$(echo "$skill" | tr '[:upper:]' '[:lower:]')
    
    case $skill in
        *python*) echo "tech" ;;
        *java*) echo "tech" ;;
        *javascript*|*js*|*node*|*react*|*vue*|*angular*) echo "tech" ;;
        *devops*|*docker*|*kubernetes*|*aws*|*cloud*) echo "tech" ;;
        *dsa*|*algorithm*|*data*structure*|*leetcode*) echo "dsa" ;;
        *system*design*|*architecture*) echo "generic" ;;
        *) echo "tech" ;;  # Default to tech for most skills
    esac
}

generate_requirements_content() {
    local skill_name=$1
    local technology=$2
    
    cat > /tmp/requirements_template.mdx << EOF
# ${skill_name} Tech Interview Questions - AI Agent Instructions

## MISSION STATEMENT

Create a comprehensive, production-ready ${skill_name} interview preparation sheet for Indian college students and working professionals. Focus on practical ${skill_name} knowledge, real-world scenarios, and hands-on implementation skills that directly translate to job requirements in Indian tech companies.

## TARGET AUDIENCE

-   College students preparing for ${skill_name} developer roles
-   Working professionals transitioning to ${skill_name}
-   Entry-level and mid-level ${skill_name} developers
-   Full-stack developers focusing on ${skill_name}
-   Professionals seeking ${skill_name} expertise

## CONTENT REQUIREMENTS

### 1. EXPLANATION STYLE

-   Use real-world ${skill_name} examples from Indian tech companies
-   Write in simple, practical language with code demonstrations
-   Include performance tips and production best practices
-   Focus on hands-on implementation over theoretical concepts
-   Provide step-by-step coding approaches with explanations
-   Include common ${skill_name} pitfalls and debugging strategies

### 2. FORMATTING REQUIREMENTS

-   Use MDX format with proper ${skill_name} syntax highlighting
-   Include practical ${skill_name} code examples for every concept
-   Provide working code snippets that can be tested immediately
-   Add performance benchmarks and optimization considerations
-   Include version-specific differences where applicable

### 3. QUESTION STRUCTURE

For each topic, provide:

1. **5 Interview Questions** (50:30:20 ratio for Easy:Medium:Hard)
2. **Practical Code Implementation** (with explanations)
3. **Real-world Use Cases** (Indian company scenarios)
4. **Performance Considerations** (optimization tips)
5. **Common Mistakes** (and debugging techniques)
6. **Interview Tips** (what interviewers look for)

## TOPIC BREAKDOWN

### Core ${skill_name} Fundamentals (25 questions)
- Basic syntax and concepts
- Data structures and algorithms specific to ${skill_name}
- Object-oriented programming concepts
- Error handling and debugging
- Testing methodologies

### ${skill_name} Frameworks and Libraries (25 questions)
- Popular frameworks and their use cases
- Configuration and setup
- Best practices and patterns
- Integration with other technologies
- Performance optimization

### Advanced ${skill_name} Concepts (25 questions)
- Memory management and optimization
- Concurrency and parallelism
- Security best practices
- Design patterns implementation
- Deployment and DevOps

### Production and Real-world Applications (25 questions)
- System design with ${skill_name}
- Scalability considerations
- Monitoring and logging
- Database integration
- API design and implementation

## INTERVIEW CONTEXT REQUIREMENTS

### Question Distribution by Company Type

-   **Startups**: Focus on practical implementation, quick prototyping
-   **Mid-size Companies**: Emphasis on scalable solutions, best practices
-   **MNCs**: Enterprise patterns, documentation, maintainability
-   **FAANG**: Performance optimization, system design integration

### Difficulty Distribution

-   **Easy Questions**: 50% (Basic syntax, simple implementations)
-   **Medium Questions**: 30% (Framework usage, moderate complexity)
-   **Hard Questions**: 20% (Performance optimization, advanced concepts)

## SUCCESS CRITERIA

-   Candidates can write production-ready ${skill_name} code
-   Questions test both theoretical knowledge and practical skills
-   Content prepares for real-world ${skill_name} development scenarios
-   Each topic includes multiple implementation approaches
-   Covers both development and deployment aspects
-   Includes Indian market context and company examples

## OUTPUT FORMAT

For each question, provide:

1. **Question Statement** (clear, practical scenario)
2. **Difficulty Level** (Easy/Medium/Hard)
3. **Code Implementation** (working ${skill_name} code with comments)
4. **Explanation** (step-by-step breakdown)
5. **Real-world Application** (Indian company use case)
6. **Performance Considerations** (optimization tips)
7. **Common Mistakes** (debugging strategies)
8. **Interview Tips** (what interviewers expect)
9. **Follow-up Questions** (potential extensions)

## QUALITY ASSURANCE CHECKLIST

-   [ ] All topics covered comprehensively
-   [ ] 50:30:20 ratio for Easy:Medium:Hard questions maintained
-   [ ] Working ${skill_name} code examples provided for each concept
-   [ ] Performance considerations and optimization tips included
-   [ ] Real-world Indian company scenarios incorporated
-   [ ] Security best practices covered
-   [ ] Testing strategies and examples provided
-   [ ] Deployment and production aspects addressed
-   [ ] Common pitfalls and debugging strategies covered

## DELIVERABLE SPECIFICATIONS

-   **Format**: MDX with ${skill_name} syntax highlighting
-   **Language**: Simple, practical English with code focus
-   **Target**: Indian ${skill_name} developer job market
-   **Focus**: Production-ready implementation skills
-   **Approach**: Hands-on coding with real-world examples
-   **Application**: Direct job relevance for Indian tech companies
EOF

    echo "/tmp/requirements_template.mdx"
}

# =============================================================================
# MAIN WORKFLOW FUNCTIONS
# =============================================================================

setup_environment() {
    log "INFO" "Setting up environment..."
    
    # Create necessary directories
    mkdir -p "$LAB_DIR" "$OUTPUT_DIR" "$(dirname "$LOG_FILE")"
    
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
    
    log "SUCCESS" "Environment setup complete"
}

get_user_input() {
    show_header
    
    echo -e "${GREEN}🎯 Welcome to the Interview Prep Sheet Generator!${NC}"
    echo -e "${BLUE}I'll create a complete interview preparation sheet for any technology.${NC}"
    echo ""
    echo -e "${CYAN}Examples: Python, Java, React, DevOps, Node.js, Angular, etc.${NC}"
    echo ""
    
    while true; do
        read -p "$(echo -e ${YELLOW}Enter the skill/technology name: ${NC})" SKILL_NAME
        
        if [[ -n "$SKILL_NAME" && ${#SKILL_NAME} -ge 2 ]]; then
            break
        else
            echo -e "${RED}Please enter a valid skill name (at least 2 characters)${NC}"
        fi
    done
    
    # Auto-detect agent type and technology
    AGENT_TYPE=$(detect_technology_type "$SKILL_NAME")
    TECHNOLOGY="$SKILL_NAME"
    
    # Create normalized names
    SKILL_LOWER=$(echo "$SKILL_NAME" | tr '[:upper:]' '[:lower:]' | tr ' ' '-')
    SKILL_DIR="$LAB_DIR/$SKILL_LOWER"
    
    echo ""
    echo -e "${GREEN}✅ Configuration:${NC}"
    echo -e "${BLUE}   📝 Skill: $SKILL_NAME${NC}"
    echo -e "${BLUE}   🤖 Agent Type: $AGENT_TYPE${NC}"
    echo -e "${BLUE}   💻 Technology: $TECHNOLOGY${NC}"
    echo -e "${BLUE}   📁 Directory: $SKILL_DIR${NC}"
    echo ""
    
    read -p "$(echo -e ${YELLOW}Proceed with this configuration? [Y/n]: ${NC})" confirm
    if [[ $confirm =~ ^[Nn]$ ]]; then
        log "INFO" "Workflow cancelled by user"
        exit 0
    fi
}

create_directory_structure() {
    log "PROGRESS" "Creating directory structure..."
    
    mkdir -p "$SKILL_DIR"
    
    log "SUCCESS" "Directory structure created: $SKILL_DIR"
}

generate_requirements_file() {
    log "PROGRESS" "Generating requirements MDX file..."
    
    local requirements_file="$SKILL_DIR/${SKILL_LOWER}_requirements.mdx"
    local temp_template=$(generate_requirements_content "$SKILL_NAME" "$TECHNOLOGY")
    
    cp "$temp_template" "$requirements_file"
    rm "$temp_template"
    
    log "SUCCESS" "Requirements file created: $requirements_file"
    echo "$requirements_file"
}

run_workflow_step() {
    local step_name=$1
    local command=$2
    local step_num=$3
    local total_steps=$4
    
    log "PROGRESS" "Step $step_num/$total_steps: $step_name"
    show_progress_bar $step_num $total_steps
    
    if eval "$command" >> "$LOG_FILE" 2>&1; then
        log "SUCCESS" "$step_name completed"
        return 0
    else
        log "ERROR" "$step_name failed. Check log: $LOG_FILE"
        return 1
    fi
}

execute_main_workflow() {
    local requirements_file=$1
    local total_steps=4
    
    echo ""
    log "INFO" "Starting automated workflow..."
    echo ""
    
    # Step 1: Generate questions from requirements
    local questions_file="${requirements_file%_requirements.mdx}_requirements_questions.mdx"
    if run_workflow_step "Generating interview questions" \
       "python3 main.py interview generate-questions-from-mdx --mdx-file '$requirements_file' --agent-type '$AGENT_TYPE' --technology '$TECHNOLOGY'" \
       1 $total_steps; then
        
        # Step 2: Add metadata to questions
        local metadata_file="${questions_file%_questions.mdx}_questions_with_metadata.mdx"
        if run_workflow_step "Adding metadata to questions" \
           "python3 main.py interview add-metadata-to-mdx --mdx-file '$questions_file' --agent-type '$AGENT_TYPE' --technology '$TECHNOLOGY'" \
           2 $total_steps; then
            
            # Step 3: Generate answers
            if run_workflow_step "Generating detailed answers" \
               "python3 main.py interview generate-answers-from-mdx --mdx-file '$metadata_file' --agent-type '$AGENT_TYPE' --technology '$TECHNOLOGY'" \
               3 $total_steps; then
                
                # Step 4: Fix formatting
                local output_pattern="$OUTPUT_DIR/complete_sheet_${SKILL_LOWER}*.json"
                local output_file=$(ls $output_pattern 2>/dev/null | head -1)
                
                if [ -n "$output_file" ]; then
                    run_workflow_step "Fixing MDX formatting" \
                       "python3 main.py interview fix-mdx-formatting --json-file '$output_file'" \
                       4 $total_steps
                else
                    log "WARN" "Output file not found matching pattern: $output_pattern"
                fi
            fi
        fi
    fi
    
    show_progress_bar $total_steps $total_steps
    echo ""
}

show_results() {
    echo ""
    log "SUCCESS" "🎉 Interview Prep Sheet Generation Complete!"
    echo ""
    
    echo -e "${GREEN}📁 Generated Files:${NC}"
    find "$SKILL_DIR" -name "*.mdx" -exec echo -e "${BLUE}   📄 {}${NC}" \;
    echo ""
    
    echo -e "${GREEN}📊 Output Files:${NC}"
    find "$OUTPUT_DIR" -name "*${SKILL_LOWER}*" -exec echo -e "${BLUE}   📈 {}${NC}" \;
    echo ""
    
    echo -e "${GREEN}📝 Log File:${NC}"
    echo -e "${BLUE}   📋 $LOG_FILE${NC}"
    echo ""
    
    echo -e "${PURPLE}🚀 Your $SKILL_NAME interview prep sheet is ready!${NC}"
    echo -e "${CYAN}Use the generated files for comprehensive interview preparation.${NC}"
}

# =============================================================================
# MAIN EXECUTION
# =============================================================================

main() {
    trap 'log "ERROR" "Script interrupted"; exit 1' INT TERM
    
    setup_environment
    get_user_input
    create_directory_structure
    
    local requirements_file=$(generate_requirements_file)
    execute_main_workflow "$requirements_file"
    
    show_results
    
    log "SUCCESS" "Workflow completed successfully"
}

# Run main function
main "$@" 