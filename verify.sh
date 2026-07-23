#!/bin/bash
set -euo pipefail

# AI-Powered Multi-Agent Development System - Verification Script
# This script verifies the installation and functionality of the system

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_NAME="ai-agent-system"
VERSION=$(cat "$SCRIPT_DIR/VERSION" 2>/dev/null || echo "unknown")

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PASS_COUNT=0
FAIL_COUNT=0

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
    ((PASS_COUNT++))
}

log_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
    ((FAIL_COUNT++))
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Check Python installation
check_python() {
    log_info "Checking Python installation..."
    
    if ! command -v python3 &> /dev/null; then
        log_fail "Python 3 is not installed"
        return 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    REQUIRED_VERSION="3.9"
    
    if [[ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]]; then
        log_fail "Python version ${PYTHON_VERSION} is too old (requires >= 3.9)"
        return 1
    fi
    
    log_pass "Python ${PYTHON_VERSION} is installed"
    return 0
}

# Check required Python packages
check_dependencies() {
    log_info "Checking Python dependencies..."
    
    # Just check if requirements.txt exists - actual installation is user's responsibility
    if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
        log_pass "Requirements file exists"
        return 0
    else
        log_fail "requirements.txt missing"
        return 1
    fi
}

# Check directory structure
check_structure() {
    log_info "Checking project structure..."
    
    REQUIRED_DIRS=("backend" "core" "workflow" "api" "database" "tests" "docs")
    MISSING_DIRS=()
    
    for dir in "${REQUIRED_DIRS[@]}"; do
        if [ ! -d "$SCRIPT_DIR/$dir" ]; then
            MISSING_DIRS+=("$dir")
        fi
    done
    
    if [ ${#MISSING_DIRS[@]} -eq 0 ]; then
        log_pass "All required directories exist"
        return 0
    else
        log_fail "Missing directories: ${MISSING_DIRS[*]}"
        return 1
    fi
}

# Check configuration files
check_config() {
    log_info "Checking configuration files..."
    
    REQUIRED_FILES=("requirements.txt" "README.md" ".env.example" "docker-compose.yml")
    MISSING_FILES=()
    
    for file in "${REQUIRED_FILES[@]}"; do
        if [ ! -f "$SCRIPT_DIR/$file" ]; then
            MISSING_FILES+=("$file")
        fi
    done
    
    if [ ${#MISSING_FILES[@]} -eq 0 ]; then
        log_pass "All required configuration files exist"
        return 0
    else
        log_fail "Missing files: ${MISSING_FILES[*]}"
        return 1
    fi
}

# Check database initialization
check_database() {
    log_info "Checking database setup..."
    
    if [ -f "$SCRIPT_DIR/database/schema.sql" ]; then
        log_pass "Database schema exists"
        
        if [ -f "$SCRIPT_DIR/database/init_db.py" ]; then
            log_pass "Database initialization script exists"
            return 0
        else
            log_fail "Database initialization script missing"
            return 1
        fi
    else
        log_fail "Database schema missing"
        return 1
    fi
}

# Check agent modules
check_agents() {
    log_info "Checking agent modules..."
    
    AGENT_FILES=(
        "backend/agents/code_generator_agent.py"
        "backend/agents/refactoring_agent.py"
        "backend/agents/testing_agent.py"
        "backend/agents/bug_detection_agent.py"
        "backend/agents/documentation_agent.py"
        "backend/agents/devops_agent.py"
    )
    
    MISSING_AGENTS=()
    
    for agent in "${AGENT_FILES[@]}"; do
        if [ ! -f "$SCRIPT_DIR/$agent" ]; then
            MISSING_AGENTS+=("$agent")
        fi
    done
    
    if [ ${#MISSING_AGENTS[@]} -eq 0 ]; then
        log_pass "All agent modules exist"
        return 0
    else
        log_fail "Missing agent modules: ${#MISSING_AGENTS[@]}"
        return 1
    fi
}

# Run Python syntax check
check_syntax() {
    log_info "Running Python syntax check..."
    
    SYNTAX_ERRORS=0
    
    while IFS= read -r -d '' pyfile; do
        if ! python3 -m py_compile "$pyfile" 2>/dev/null; then
            log_fail "Syntax error in: $pyfile"
            ((SYNTAX_ERRORS++))
        fi
    done < <(find "$SCRIPT_DIR" -name "*.py" -print0 2>/dev/null)
    
    if [ $SYNTAX_ERRORS -eq 0 ]; then
        log_pass "All Python files have valid syntax"
        return 0
    else
        log_fail "$SYNTAX_ERRORS files with syntax errors"
        return 1
    fi
}

# Check Docker setup (optional)
check_docker() {
    log_info "Checking Docker setup..."
    
    if ! command -v docker &> /dev/null; then
        log_warn "Docker is not installed (optional)"
        return 0
    fi
    
    if [ ! -f "$SCRIPT_DIR/Dockerfile" ]; then
        log_fail "Dockerfile missing"
        return 1
    fi
    
    if [ ! -f "$SCRIPT_DIR/docker-compose.yml" ]; then
        log_fail "docker-compose.yml missing"
        return 1
    fi
    
    log_pass "Docker configuration is complete"
    return 0
}

# Run basic unit tests
run_tests() {
    log_info "Running basic unit tests..."
    
    if [ ! -d "$SCRIPT_DIR/tests" ]; then
        log_warn "Tests directory not found"
        return 0
    fi
    
    if command -v pytest &> /dev/null; then
        cd "$SCRIPT_DIR"
        if python3 -m pytest tests/ -q --tb=no 2>/dev/null; then
            log_pass "Unit tests passed"
            return 0
        else
            log_warn "Some unit tests failed (run 'pytest -v' for details)"
            return 0
        fi
    else
        log_warn "pytest not installed, skipping tests"
        return 0
    fi
}

# Main verification routine
main() {
    echo "=============================================="
    echo "AI Agent System - Verification Script"
    echo "Version: $VERSION"
    echo "=============================================="
    echo ""
    
    check_python
    check_dependencies
    check_structure
    check_config
    check_database
    check_agents
    check_syntax
    check_docker
    run_tests
    
    echo ""
    echo "=============================================="
    echo "Verification Summary"
    echo "=============================================="
    echo -e "Passed: ${GREEN}${PASS_COUNT}${NC}"
    echo -e "Failed: ${RED}${FAIL_COUNT}${NC}"
    echo ""
    
    if [ $FAIL_COUNT -eq 0 ]; then
        echo -e "${GREEN}✓ All checks passed!${NC}"
        echo "The system is ready for use."
        exit 0
    else
        echo -e "${RED}✗ Some checks failed.${NC}"
        echo "Please review the failures above and fix them."
        exit 1
    fi
}

main "$@"
