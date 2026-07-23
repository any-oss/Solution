#!/bin/bash
set -euo pipefail

# Intelligent Request Router - Uninstallation Script
# This script removes the AI Proxy system and its components

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

# Confirm uninstallation
confirm() {
    echo -e "${YELLOW}WARNING: This will remove the Intelligent Request Router installation.${NC}"
    echo "The following will be removed:"
    echo "  - Python virtual environment"
    echo "  - Database files (ai_proxy.db)"
    echo "  - Log files"
    echo "  - Environment configuration (.env)"
    echo "  - Systemd service (if installed)"
    echo ""
    read -p "Are you sure you want to continue? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Uninstallation cancelled"
        exit 0
    fi
}

# Stop running services
stop_services() {
    log_info "Stopping running services..."
    
    # Stop systemd service if exists
    if systemctl is-active --quiet ai-proxy.service 2>/dev/null; then
        systemctl stop ai-proxy.service
        systemctl disable ai-proxy.service
        log_info "Systemd service stopped and disabled"
    fi
    
    # Stop Docker Compose services if running
    if command -v docker &> /dev/null && [ -f "${SCRIPT_DIR}/docker-compose.yml" ]; then
        if docker compose ps &> /dev/null; then
            docker compose down
            log_info "Docker Compose services stopped"
        fi
    fi
    
    # Kill any running Python processes for this app
    pkill -f "python.*core.proxy" 2>/dev/null || true
    pkill -f "python.*core.backend" 2>/dev/null || true
    pkill -f "python.*ui.app" 2>/dev/null || true
    
    log_info "All services stopped"
}

# Remove installation files
remove_files() {
    log_info "Removing installation files..."
    
    # Remove virtual environment
    if [ -d "${SCRIPT_DIR}/venv" ]; then
        rm -rf "${SCRIPT_DIR}/venv"
        log_info "Virtual environment removed"
    fi
    
    # Remove database files
    if [ -f "${SCRIPT_DIR}/ai_proxy.db" ]; then
        rm -f "${SCRIPT_DIR}/ai_proxy.db"
        log_info "Database file removed"
    fi
    if [ -f "${SCRIPT_DIR}/ai_proxy.db-wal" ]; then
        rm -f "${SCRIPT_DIR}/ai_proxy.db-wal"
    fi
    if [ -f "${SCRIPT_DIR}/ai_proxy.db-shm" ]; then
        rm -f "${SCRIPT_DIR}/ai_proxy.db-shm"
    fi
    
    # Remove log files
    rm -f "${SCRIPT_DIR}"/*.log 2>/dev/null || true
    log_info "Log files removed"
    
    # Remove environment file (optional, keep .env.example)
    if [ -f "${SCRIPT_DIR}/.env" ]; then
        rm -f "${SCRIPT_DIR}/.env"
        log_info "Environment configuration removed"
    fi
    
    # Remove Python cache
    find "${SCRIPT_DIR}" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find "${SCRIPT_DIR}" -type f -name "*.pyc" -delete 2>/dev/null || true
    log_info "Python cache removed"
    
    # Remove coverage reports
    rm -rf "${SCRIPT_DIR}/.coverage" "${SCRIPT_DIR}/htmlcov" "${SCRIPT_DIR}/coverage" 2>/dev/null || true
}

# Remove systemd service
remove_systemd_service() {
    if [ "$(uname)" != "Linux" ]; then
        return
    fi
    
    if [ -f "/etc/systemd/system/ai-proxy.service" ]; then
        log_info "Removing systemd service..."
        systemctl stop ai-proxy.service 2>/dev/null || true
        systemctl disable ai-proxy.service 2>/dev/null || true
        rm -f /etc/systemd/system/ai-proxy.service
        systemctl daemon-reload
        log_info "Systemd service removed"
    fi
}

# Remove Docker images (optional)
remove_docker_images() {
    if ! command -v docker &> /dev/null; then
        return
    fi
    
    echo ""
    read -p "Also remove Docker images? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Removing Docker images..."
        docker rmi anydockerhub/summy:latest 2>/dev/null || true
        docker rmi anydockerhub/summy 2>/dev/null || true
        docker volume rm intelligent-request-router_proxy_data 2>/dev/null || true
        docker volume rm intelligent-request-router_prometheus_data 2>/dev/null || true
        log_info "Docker images and volumes removed"
    fi
}

# Main uninstallation
main() {
    echo "========================================"
    echo "Intelligent Request Router Uninstaller"
    echo "========================================"
    echo ""
    
    # Check if installed
    if [ ! -d "${SCRIPT_DIR}/core" ]; then
        log_error "Installation not found in ${SCRIPT_DIR}"
        exit 1
    fi
    
    UNINSTALL_MODE="${1:-interactive}"
    
    if [ "$UNINSTALL_MODE" = "force" ]; then
        stop_services
        remove_files
        remove_systemd_service
    else
        confirm
        stop_services
        remove_files
        remove_systemd_service
        remove_docker_images
    fi
    
    echo ""
    log_info "Uninstallation completed successfully!"
    echo ""
    echo "The following were preserved:"
    echo "  - Source code files"
    echo "  - Configuration templates (.env.example)"
    echo "  - Documentation"
    echo ""
    echo "To reinstall, run: ./install.sh"
}

main "$@"
