#!/bin/bash
set -euo pipefail

# Intelligent Request Router - Verification Script
# This script verifies the installation and health of all services

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

PASS_COUNT=0
FAIL_COUNT=0

check_pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((PASS_COUNT++))
}

check_fail() {
    echo -e "${RED}✗${NC} $1"
    ((FAIL_COUNT++))
}

# Check Python environment
check_python() {
    log_info "Checking Python environment..."
    
    if command -v python3 &> /dev/null; then
        check_pass "Python 3 is installed: $(python3 --version)"
    else
        check_fail "Python 3 is not installed"
        return 1
    fi
    
    if [ -d "${SCRIPT_DIR}/venv" ]; then
        check_pass "Virtual environment exists"
        
        if [ -f "${SCRIPT_DIR}/venv/bin/activate" ]; then
            source "${SCRIPT_DIR}/venv/bin/activate"
            check_pass "Virtual environment is activatable"
        else
            check_fail "Virtual environment activation script missing"
        fi
    else
        log_warn "Virtual environment not found (Docker mode?)"
    fi
}

# Check dependencies
check_dependencies() {
    log_info "Checking Python dependencies..."
    
    REQUIRED_PACKAGES=("aiohttp" "requests" "prometheus-client" "python-dotenv")
    
    for package in "${REQUIRED_PACKAGES[@]}"; do
        if python3 -c "import ${package//-/_}" 2>/dev/null; then
            check_pass "Package installed: ${package}"
        else
            check_fail "Package missing: ${package}"
        fi
    done
}

# Check configuration
check_configuration() {
    log_info "Checking configuration..."
    
    if [ -f "${SCRIPT_DIR}/.env.example" ]; then
        check_pass "Environment template exists"
    else
        check_fail "Environment template missing"
    fi
    
    if [ -f "${SCRIPT_DIR}/.env" ]; then
        check_pass "Environment configuration exists"
        
        # Check required variables
        REQUIRED_VARS=("HOST" "PORT" "CPU_BACKEND_URL" "GPU_BACKEND_URL")
        for var in "${REQUIRED_VARS[@]}"; do
            if grep -q "^${var}=" "${SCRIPT_DIR}/.env" 2>/dev/null; then
                check_pass "Environment variable set: ${var}"
            else
                check_fail "Environment variable missing: ${var}"
            fi
        done
    else
        log_warn ".env file not found - using defaults"
    fi
}

# Check database
check_database() {
    log_info "Checking database..."
    
    if [ -f "${SCRIPT_DIR}/ai_proxy.db" ]; then
        check_pass "Database file exists"
        
        # Try to connect and query
        if python3 -c "from core.database import get_database; db = get_database(); print('OK')" 2>/dev/null; then
            check_pass "Database connection successful"
        else
            check_fail "Database connection failed"
        fi
    else
        log_warn "Database file not found - will be created on first run"
    fi
}

# Check services health (if running)
check_services_health() {
    log_info "Checking service health..."
    
    # Load environment variables
    if [ -f "${SCRIPT_DIR}/.env" ]; then
        export $(grep -v '^#' "${SCRIPT_DIR}/.env" | xargs)
    fi
    
    PROXY_PORT="${PORT:-8000}"
    CPU_PORT="8001"
    GPU_PORT="8002"
    
    # Check Proxy
    if curl -sf "http://localhost:${PROXY_PORT}/health" &> /dev/null; then
        check_pass "Proxy service is healthy (port ${PROXY_PORT})"
    else
        log_warn "Proxy service not responding (may not be running)"
    fi
    
    # Check CPU Backend
    if curl -sf "http://localhost:${CPU_PORT}/health" &> /dev/null; then
        check_pass "CPU backend is healthy (port ${CPU_PORT})"
    else
        log_warn "CPU backend not responding (may not be running)"
    fi
    
    # Check GPU Backend
    if curl -sf "http://localhost:${GPU_PORT}/health" &> /dev/null; then
        check_pass "GPU backend is healthy (port ${GPU_PORT})"
    else
        log_warn "GPU backend not responding (may not be running)"
    fi
    
    # Check UI Dashboard
    if curl -sf "http://localhost:8080/" &> /dev/null; then
        check_pass "UI dashboard is accessible (port 8080)"
    else
        log_warn "UI dashboard not responding (may not be running)"
    fi
}

# Check Docker setup
check_docker() {
    log_info "Checking Docker setup..."
    
    if command -v docker &> /dev/null; then
        check_pass "Docker is installed: $(docker --version)"
        
        if command -v docker-compose &> /dev/null || docker compose version &> /dev/null; then
            check_pass "Docker Compose is available"
        else
            check_fail "Docker Compose is not installed"
        fi
        
        if [ -f "${SCRIPT_DIR}/docker-compose.yml" ]; then
            check_pass "Docker Compose configuration exists"
        else
            check_fail "Docker Compose configuration missing"
        fi
    else
        log_warn "Docker not installed - local mode only"
    fi
}

# Check file permissions
check_permissions() {
    log_info "Checking file permissions..."
    
    SCRIPTS=("install.sh" "uninstall.sh" "verify.sh")
    for script in "${SCRIPTS[@]}"; do
        if [ -x "${SCRIPT_DIR}/${script}" ]; then
            check_pass "Script executable: ${script}"
        elif [ -f "${SCRIPT_DIR}/${script}" ]; then
            check_fail "Script not executable: ${script}"
        fi
    done
}

# Check documentation
check_documentation() {
    log_info "Checking documentation..."
    
    DOCS=("README.md" "CHANGELOG.md" "CONTRIBUTING.md" "SECURITY.md" "LICENSE")
    for doc in "${DOCS[@]}"; do
        if [ -f "${SCRIPT_DIR}/${doc}" ]; then
            check_pass "Documentation exists: ${doc}"
        else
            check_fail "Documentation missing: ${doc}"
        fi
    done
}

# Print summary
print_summary() {
    echo ""
    echo "========================================"
    echo "Verification Summary"
    echo "========================================"
    echo -e "${GREEN}Passed:${NC} ${PASS_COUNT}"
    echo -e "${RED}Failed:${NC} ${FAIL_COUNT}"
    echo ""
    
    if [ ${FAIL_COUNT} -eq 0 ]; then
        echo -e "${GREEN}All checks passed!${NC} System is ready."
        return 0
    else
        echo -e "${YELLOW}Some checks failed.${NC} Review the issues above."
        return 1
    fi
}

# Main verification
main() {
    echo "========================================"
    echo "Intelligent Request Router Verification"
    echo "========================================"
    echo ""
    
    check_python
    echo ""
    
    if [ -d "${SCRIPT_DIR}/venv" ]; then
        check_dependencies
        echo ""
    fi
    
    check_configuration
    echo ""
    
    check_database
    echo ""
    
    check_services_health
    echo ""
    
    check_docker
    echo ""
    
    check_permissions
    echo ""
    
    check_documentation
    echo ""
    
    print_summary
}

main "$@"
