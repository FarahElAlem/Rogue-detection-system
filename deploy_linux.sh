#!/bin/bash

################################################################################
# Rogue Detection System - Linux Deployment Script
# Supports: Ubuntu 20.04+, Debian 10+, CentOS 8+
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="rogue-detection"
APP_USER="roguedetect"
APP_DIR="/home/$APP_USER/rogue_detection_system"
SERVICE_FILE="/etc/systemd/system/$APP_NAME.service"

################################################################################
# Helper Functions
################################################################################

print_header() {
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

check_root() {
    if [ "$EUID" -ne 0 ]; then
        print_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$ID
        VER=$VERSION_ID
    else
        print_error "Cannot detect OS"
        exit 1
    fi
    print_info "Detected OS: $OS $VER"
}

################################################################################
# Installation Steps
################################################################################

step1_update_system() {
    print_header "Step 1: Updating System"
    
    case $OS in
        ubuntu|debian)
            apt update && apt upgrade -y
            print_success "System updated"
            ;;
        centos|rhel|fedora)
            yum update -y
            print_success "System updated"
            ;;
        *)
            print_warning "Unknown OS, skipping system update"
            ;;
    esac
}

step2_install_dependencies() {
    print_header "Step 2: Installing Dependencies"
    
    case $OS in
        ubuntu|debian)
            apt install -y \
                python3 \
                python3-pip \
                python3-venv \
                git \
                sqlite3 \
                nginx \
                ufw \
                curl \
                wget
            ;;
        centos|rhel|fedora)
            yum install -y \
                python3 \
                python3-pip \
                python3-virtualenv \
                git \
                sqlite \
                nginx \
                firewalld \
                curl \
                wget
            ;;
        *)
            print_error "Unsupported OS"
            exit 1
            ;;
    esac
    
    print_success "Dependencies installed"
}

step3_create_user() {
    print_header "Step 3: Creating Application User"
    
    if id "$APP_USER" &>/dev/null; then
        print_warning "User $APP_USER already exists"
    else
        useradd -m -s /bin/bash $APP_USER
        print_success "User $APP_USER created"
    fi
}

step4_setup_application() {
    print_header "Step 4: Setting Up Application"
    
    # Create directory
    mkdir -p $APP_DIR
    
    # Copy files
    print_info "Copying application files..."
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    cp -r $SCRIPT_DIR/* $APP_DIR/
    
    # Set ownership
    chown -R $APP_USER:$APP_USER $APP_DIR
    
    # Create virtual environment
    print_info "Creating virtual environment..."
    sudo -u $APP_USER python3 -m venv $APP_DIR/venv
    
    # Install Python packages
    print_info "Installing Python packages..."
    sudo -u $APP_USER $APP_DIR/venv/bin/pip install --upgrade pip
    sudo -u $APP_USER $APP_DIR/venv/bin/pip install -r $APP_DIR/requirements.txt
    
    print_success "Application setup complete"
}

step5_configure() {
    print_header "Step 5: Configuration"
    
    if [ ! -f "$APP_DIR/config.json" ]; then
        if [ -f "$APP_DIR/config.json.example" ]; then
            cp $APP_DIR/config.json.example $APP_DIR/config.json
            print_warning "Created config.json from example"
            print_warning "IMPORTANT: Edit $APP_DIR/config.json with your settings!"
        else
            print_error "No config.json.example found"
            exit 1
        fi
    else
        print_info "config.json already exists"
    fi
    
    # Set permissions
    chmod 600 $APP_DIR/config.json
    chown $APP_USER:$APP_USER $APP_DIR/config.json
    
    print_success "Configuration complete"
}

step6_create_service() {
    print_header "Step 6: Creating Systemd Service"
    
    cat > $SERVICE_FILE <<EOF
[Unit]
Description=Rogue Detection System
After=network.target

[Service]
Type=simple
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/python3 app.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=$APP_NAME

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$APP_DIR

[Install]
WantedBy=multi-user.target
EOF
    
    # Reload systemd
    systemctl daemon-reload
    
    # Enable service
    systemctl enable $APP_NAME
    
    print_success "Systemd service created"
}

step7_configure_firewall() {
    print_header "Step 7: Configuring Firewall"
    
    case $OS in
        ubuntu|debian)
            # UFW
            ufw --force enable
            ufw allow 22/tcp
            ufw allow 80/tcp
            ufw allow 443/tcp
            ufw allow 5000/tcp
            print_success "UFW configured"
            ;;
        centos|rhel|fedora)
            # Firewalld
            systemctl start firewalld
            systemctl enable firewalld
            firewall-cmd --permanent --add-service=ssh
            firewall-cmd --permanent --add-service=http
            firewall-cmd --permanent --add-service=https
            firewall-cmd --permanent --add-port=5000/tcp
            firewall-cmd --reload
            print_success "Firewalld configured"
            ;;
    esac
}

step8_setup_nginx() {
    print_header "Step 8: Configuring Nginx (Optional)"
    
    read -p "Do you want to configure Nginx reverse proxy? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Enter your domain name (e.g., rogue.example.com): " DOMAIN
        
        cat > /etc/nginx/sites-available/$APP_NAME <<EOF
server {
    listen 80;
    server_name $DOMAIN;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    location /static {
        alias $APP_DIR/static;
        expires 30d;
    }
}
EOF
        
        # Enable site
        ln -sf /etc/nginx/sites-available/$APP_NAME /etc/nginx/sites-enabled/
        
        # Test configuration
        nginx -t
        
        # Reload Nginx
        systemctl reload nginx
        
        print_success "Nginx configured for $DOMAIN"
        
        # Offer SSL setup
        read -p "Do you want to setup SSL with Let's Encrypt? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            if command -v certbot &> /dev/null; then
                certbot --nginx -d $DOMAIN
                print_success "SSL certificate installed"
            else
                print_warning "Certbot not installed. Install with: apt install certbot python3-certbot-nginx"
            fi
        fi
    else
        print_info "Skipping Nginx configuration"
    fi
}

step9_setup_logging() {
    print_header "Step 9: Setting Up Logging"
    
    # Create log directory
    mkdir -p /var/log/$APP_NAME
    chown $APP_USER:$APP_USER /var/log/$APP_NAME
    
    # Create logrotate configuration
    cat > /etc/logrotate.d/$APP_NAME <<EOF
/var/log/$APP_NAME/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 $APP_USER $APP_USER
    sharedscripts
    postrotate
        systemctl reload $APP_NAME > /dev/null 2>&1 || true
    endscript
}
EOF
    
    print_success "Logging configured"
}

step10_setup_backup() {
    print_header "Step 10: Setting Up Automated Backup"
    
    # Create backup directory
    mkdir -p $APP_DIR/backups
    chown $APP_USER:$APP_USER $APP_DIR/backups
    
    # Create backup script
    cat > $APP_DIR/backup.sh <<'EOF'
#!/bin/bash
BACKUP_DIR="/home/roguedetect/rogue_detection_system/backups"
APP_DIR="/home/roguedetect/rogue_detection_system"
DATE=$(date +%Y-%m-%d_%H-%M-%S)
RETENTION_DAYS=30

mkdir -p "$BACKUP_DIR/$DATE"
sqlite3 "$APP_DIR/rogue_monitor.db" ".backup '$BACKUP_DIR/$DATE/rogue_monitor.db'"
cp "$APP_DIR/config.json" "$BACKUP_DIR/$DATE/config.json"
cd "$BACKUP_DIR"
tar -czf "$DATE.tar.gz" "$DATE"
rm -rf "$DATE"
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete
echo "Backup completed: $DATE.tar.gz"
EOF
    
    chmod +x $APP_DIR/backup.sh
    chown $APP_USER:$APP_USER $APP_DIR/backup.sh
    
    # Add to crontab
    (crontab -u $APP_USER -l 2>/dev/null; echo "0 2 * * * $APP_DIR/backup.sh >> /var/log/$APP_NAME/backup.log 2>&1") | crontab -u $APP_USER -
    
    print_success "Automated backup configured (daily at 2 AM)"
}

step11_start_service() {
    print_header "Step 11: Starting Service"
    
    systemctl start $APP_NAME
    sleep 2
    
    if systemctl is-active --quiet $APP_NAME; then
        print_success "Service started successfully"
    else
        print_error "Service failed to start"
        print_info "Check logs with: journalctl -u $APP_NAME -n 50"
        exit 1
    fi
}

step12_verify() {
    print_header "Step 12: Verification"
    
    # Check service status
    if systemctl is-active --quiet $APP_NAME; then
        print_success "Service is running"
    else
        print_error "Service is not running"
    fi
    
    # Check if port is listening
    if netstat -tuln | grep -q ":5000"; then
        print_success "Application is listening on port 5000"
    else
        print_warning "Port 5000 is not listening"
    fi
    
    # Check web interface
    if curl -s http://localhost:5000 > /dev/null; then
        print_success "Web interface is responding"
    else
        print_warning "Web interface is not responding"
    fi
}

################################################################################
# Main Installation
################################################################################

main() {
    clear
    print_header "Rogue Detection System - Linux Deployment"
    echo
    print_info "This script will install and configure the Rogue Detection System"
    print_warning "This script must be run as root (use sudo)"
    echo
    read -p "Do you want to continue? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Installation cancelled"
        exit 0
    fi
    
    check_root
    detect_os
    
    step1_update_system
    step2_install_dependencies
    step3_create_user
    step4_setup_application
    step5_configure
    step6_create_service
    step7_configure_firewall
    step8_setup_nginx
    step9_setup_logging
    step10_setup_backup
    step11_start_service
    step12_verify
    
    print_header "Installation Complete!"
    echo
    print_success "Rogue Detection System has been installed successfully!"
    echo
    print_info "Next steps:"
    echo "  1. Edit configuration: sudo nano $APP_DIR/config.json"
    echo "  2. Restart service: sudo systemctl restart $APP_NAME"
    echo "  3. Check status: sudo systemctl status $APP_NAME"
    echo "  4. View logs: sudo journalctl -u $APP_NAME -f"
    echo "  5. Access web interface: http://your-server-ip:5000"
    echo "  6. Default login: admin / admin123"
    echo
    print_warning "IMPORTANT: Change the default admin password!"
    print_warning "IMPORTANT: Edit $APP_DIR/config.json with your switch credentials!"
    echo
}

# Run main function
main "$@"

