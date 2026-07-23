#!/bin/bash
set -euo pipefail

# Intelligent Request Router - Installation Script
# This script installs the AI Proxy system and its dependencies

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_NAME="intelligent-request-router"
VERSION="1.0.0"

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

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is required but not installed"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    log_info "Found Python ${PYTHON_VERSION}"
    
    # Check Docker (optional but recommended)
    if command -v docker &> /dev/null; then
        log_info "Docker is available"
        HAS_DOCKER=true
    else
        log_warn "Docker not found - will install in local mode only"
        HAS_DOCKER=false
    fi
    
    # Check pip
    if ! python3 -m pip --version &> /dev/null; then
        log_error "pip is required but not installed"
        exit 1
    fi
}

# Create virtual environment
setup_venv() {
    log_info "Setting up Python virtual environment..."
    
    if [ -d "${SCRIPT_DIR}/venv" ]; then
        log_warn "Virtual environment already exists, removing..."
        rm -rf "${SCRIPT_DIR}/venv"
    fi
    
    python3 -m venv "${SCRIPT_DIR}/venv"
    source "${SCRIPT_DIR}/venv/bin/activate"
    
    log_info "Virtual environment created successfully"
}

# Install Python dependencies
install_dependencies() {
    log_info "Installing Python dependencies..."
    
    pip install --upgrade pip
    pip install -r "${SCRIPT_DIR}/requirements.txt"
    
    log_info "Dependencies installed successfully"
}

# Setup environment file
setup_env() {
    log_info "Setting up environment configuration..."
    
    if [ -f "${SCRIPT_DIR}/.env" ]; then
        log_warn ".env file already exists, skipping setup"
        return
    fi
    
    cp "${SCRIPT_DIR}/.env.example" "${SCRIPT_DIR}/.env"
    log_info "Environment file created from template"
    log_info "Please review and customize ${SCRIPT_DIR}/.env before running"
}

# Initialize database
init_database() {
    log_info "Initializing database..."
    
    # Import to create tables
    source "${SCRIPT_DIR}/venv/bin/activate"
    python3 -c "from core.database import get_database; get_database()"
    
    log_info "Database initialized successfully"
}

# Create systemd service (Linux only)
setup_systemd_service() {
    if [ "$(uname)" != "Linux" ]; then
        log_warn "Systemd service setup only available on Linux"
        return
    fi
    
    if [ "$EUID" -ne 0 ]; then
        log_warn "Run as root to install systemd service"
        return
    fi
    
    log_info "Creating systemd service..."
    
    cat > /etc/systemd/system/ai-proxy.service << EOF
[Unit]
Description=Intelligent Request Router - AI Proxy
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=${SCRIPT_DIR}
Environment=PATH=${SCRIPT_DIR}/venv/bin
ExecStart=${SCRIPT_DIR}/venv/bin/python -m core.proxy
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
    
    systemctl daemon-reload
    systemctl enable ai-proxy.service
    
    log_info "Systemd service installed. Start with: systemctl start ai-proxy"
}

# Docker installation mode
install_docker_mode() {
    if [ "$HAS_DOCKER" = false ]; then
        log_error "Docker mode requires Docker to be installed"
        exit 1
    fi
    
    log_info "Setting up Docker Compose environment..."
    
    if [ ! -f "${SCRIPT_DIR}/.env" ]; then
        cp "${SCRIPT_DIR}/.env.example" "${SCRIPT_DIR}/.env"
    fi
    
    log_info "Docker setup complete. Run with: docker compose up -d"
}

# Main installation
main() {
    echo "========================================"
    echo "Intelligent Request Router Installer"
    echo "Version: ${VERSION}"
    echo "========================================"
    echo ""
    
    check_prerequisites
    
    INSTALL_MODE="${1:-local}"
    
    case "$INSTALL_MODE" in
        local)
            setup_venv
            install_dependencies
            setup_env
            init_database
            ;;
        docker)
            install_docker_mode
            ;;
        full)
            setup_venv
            install_dependencies
            setup_env
            init_database
            setup_systemd_service
            ;;
        *)
            log_error "Unknown installation mode: ${INSTALL_MODE}"
            echo "Usage: $0 [local|docker|full]"
            exit 1
            ;;
    esac
    
    echo ""
    log_info "Installation completed successfully!"
    echo ""
    echo "Next steps:"
    if [ "$INSTALL_MODE" = "docker" ]; then
        echo "  1. Review .env file: nano .env"
        echo "  2. Start services: docker compose up -d"
        echo "  3. Check status: docker compose ps"
    else
        echo "  1. Activate venv: source venv/bin/activate"
        echo "  2. Review .env file: nano .env"
        echo "  3. Start proxy: python -m core.proxy"
        echo "  4. Or run all services: docker compose up -d"
    fi
    echo ""
}

main "$@"
