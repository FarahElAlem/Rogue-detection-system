#!/bin/bash

################################################################################
# Rogue Detection System - Google Cloud Deployment Script
# Deploys to Google Compute Engine with SSL and monitoring
################################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
PROJECT_ID=""
INSTANCE_NAME="rogue-detection"
ZONE="us-central1-a"
MACHINE_TYPE="e2-small"
BOOT_DISK_SIZE="20GB"
DOMAIN=""

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

check_gcloud() {
    if ! command -v gcloud &> /dev/null; then
        print_error "gcloud CLI not found"
        print_info "Install from: https://cloud.google.com/sdk/docs/install"
        exit 1
    fi
    print_success "gcloud CLI found"
}

################################################################################
# Configuration
################################################################################

configure() {
    print_header "Configuration"
    
    # Get project ID
    if [ -z "$PROJECT_ID" ]; then
        read -p "Enter your Google Cloud Project ID: " PROJECT_ID
    fi
    
    # Set project
    gcloud config set project $PROJECT_ID
    print_success "Project set to: $PROJECT_ID"
    
    # Get domain (optional)
    read -p "Enter your domain name (optional, press Enter to skip): " DOMAIN
    
    # Confirm configuration
    echo
    print_info "Configuration:"
    echo "  Project ID: $PROJECT_ID"
    echo "  Instance Name: $INSTANCE_NAME"
    echo "  Zone: $ZONE"
    echo "  Machine Type: $MACHINE_TYPE"
    echo "  Disk Size: $BOOT_DISK_SIZE"
    if [ -n "$DOMAIN" ]; then
        echo "  Domain: $DOMAIN"
    fi
    echo
    
    read -p "Continue with this configuration? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Deployment cancelled"
        exit 0
    fi
}

################################################################################
# Deployment Steps
################################################################################

step1_enable_apis() {
    print_header "Step 1: Enabling Required APIs"
    
    gcloud services enable compute.googleapis.com
    gcloud services enable logging.googleapis.com
    gcloud services enable monitoring.googleapis.com
    
    print_success "APIs enabled"
}

step2_create_firewall_rules() {
    print_header "Step 2: Creating Firewall Rules"
    
    # Check if rules exist
    if gcloud compute firewall-rules describe allow-rogue-detection-web &>/dev/null; then
        print_info "Firewall rules already exist"
    else
        gcloud compute firewall-rules create allow-rogue-detection-web \
            --allow=tcp:5000,tcp:80,tcp:443 \
            --source-ranges=0.0.0.0/0 \
            --target-tags=http-server,https-server \
            --description="Allow web traffic to Rogue Detection System"
        
        print_success "Firewall rules created"
    fi
}

step3_create_instance() {
    print_header "Step 3: Creating Compute Engine Instance"
    
    # Check if instance exists
    if gcloud compute instances describe $INSTANCE_NAME --zone=$ZONE &>/dev/null; then
        print_warning "Instance $INSTANCE_NAME already exists"
        read -p "Do you want to delete and recreate it? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            gcloud compute instances delete $INSTANCE_NAME --zone=$ZONE --quiet
        else
            print_info "Using existing instance"
            return
        fi
    fi
    
    print_info "Creating instance..."
    gcloud compute instances create $INSTANCE_NAME \
        --zone=$ZONE \
        --machine-type=$MACHINE_TYPE \
        --image-family=ubuntu-2004-lts \
        --image-project=ubuntu-os-cloud \
        --boot-disk-size=$BOOT_DISK_SIZE \
        --boot-disk-type=pd-standard \
        --tags=http-server,https-server \
        --metadata=startup-script='#!/bin/bash
apt update
apt install -y python3 python3-pip python3-venv git nginx certbot python3-certbot-nginx'
    
    print_success "Instance created"
    
    # Wait for instance to be ready
    print_info "Waiting for instance to be ready..."
    sleep 30
}

step4_get_external_ip() {
    print_header "Step 4: Getting External IP"
    
    EXTERNAL_IP=$(gcloud compute instances describe $INSTANCE_NAME --zone=$ZONE --format='get(networkInterfaces[0].accessConfigs[0].natIP)')
    
    print_success "External IP: $EXTERNAL_IP"
    
    if [ -n "$DOMAIN" ]; then
        print_warning "Configure DNS A record:"
        echo "  $DOMAIN → $EXTERNAL_IP"
        read -p "Press Enter when DNS is configured..."
    fi
}

step5_upload_files() {
    print_header "Step 5: Uploading Application Files"
    
    print_info "Creating directory on instance..."
    gcloud compute ssh $INSTANCE_NAME --zone=$ZONE --command="mkdir -p /tmp/rogue_detection_system"
    
    print_info "Uploading files..."
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    gcloud compute scp --recurse $SCRIPT_DIR/* $INSTANCE_NAME:/tmp/rogue_detection_system/ --zone=$ZONE
    
    print_success "Files uploaded"
}

step6_install_application() {
    print_header "Step 6: Installing Application"
    
    print_info "Running installation script..."
    
    gcloud compute ssh $INSTANCE_NAME --zone=$ZONE --command="
        set -e
        
        # Move files to proper location
        sudo mkdir -p /opt/rogue_detection_system
        sudo mv /tmp/rogue_detection_system/* /opt/rogue_detection_system/
        sudo chown -R \$USER:\$USER /opt/rogue_detection_system
        
        # Setup virtual environment
        cd /opt/rogue_detection_system
        python3 -m venv venv
        source venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
        
        # Create configuration
        if [ ! -f config.json ]; then
            cp config.json.example config.json
        fi
        
        echo 'Installation complete'
    "
    
    print_success "Application installed"
}

step7_configure_systemd() {
    print_header "Step 7: Configuring Systemd Service"
    
    gcloud compute ssh $INSTANCE_NAME --zone=$ZONE --command="
        sudo tee /etc/systemd/system/rogue-detection.service > /dev/null <<EOF
[Unit]
Description=Rogue Detection System
After=network.target

[Service]
Type=simple
User=\$USER
Group=\$USER
WorkingDirectory=/opt/rogue_detection_system
Environment=\"PATH=/opt/rogue_detection_system/venv/bin\"
ExecStart=/opt/rogue_detection_system/venv/bin/python3 app.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

        sudo systemctl daemon-reload
        sudo systemctl enable rogue-detection
        sudo systemctl start rogue-detection
        
        echo 'Service configured and started'
    "
    
    print_success "Systemd service configured"
}

step8_configure_nginx() {
    print_header "Step 8: Configuring Nginx"
    
    if [ -z "$DOMAIN" ]; then
        print_info "No domain specified, using IP address"
        SERVER_NAME=$EXTERNAL_IP
    else
        SERVER_NAME=$DOMAIN
    fi
    
    gcloud compute ssh $INSTANCE_NAME --zone=$ZONE --command="
        sudo tee /etc/nginx/sites-available/rogue-detection > /dev/null <<EOF
server {
    listen 80;
    server_name $SERVER_NAME;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \\\$host;
        proxy_set_header X-Real-IP \\\$remote_addr;
        proxy_set_header X-Forwarded-For \\\$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \\\$scheme;
        
        proxy_http_version 1.1;
        proxy_set_header Upgrade \\\$http_upgrade;
        proxy_set_header Connection \"upgrade\";
    }
    
    location /static {
        alias /opt/rogue_detection_system/static;
        expires 30d;
    }
}
EOF

        sudo ln -sf /etc/nginx/sites-available/rogue-detection /etc/nginx/sites-enabled/
        sudo nginx -t
        sudo systemctl reload nginx
        
        echo 'Nginx configured'
    "
    
    print_success "Nginx configured"
}

step9_setup_ssl() {
    print_header "Step 9: Setting Up SSL Certificate"
    
    if [ -z "$DOMAIN" ]; then
        print_warning "No domain specified, skipping SSL setup"
        return
    fi
    
    print_info "Getting SSL certificate from Let's Encrypt..."
    
    gcloud compute ssh $INSTANCE_NAME --zone=$ZONE --command="
        sudo certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN
        echo 'SSL certificate installed'
    "
    
    print_success "SSL certificate installed"
}

step10_setup_monitoring() {
    print_header "Step 10: Setting Up Cloud Monitoring"
    
    print_info "Installing Cloud Ops Agent..."
    
    gcloud compute ssh $INSTANCE_NAME --zone=$ZONE --command="
        curl -sSO https://dl.google.com/cloudagents/add-google-cloud-ops-agent-repo.sh
        sudo bash add-google-cloud-ops-agent-repo.sh --also-install
        rm add-google-cloud-ops-agent-repo.sh
        
        echo 'Cloud Ops Agent installed'
    "
    
    print_success "Monitoring configured"
}

step11_setup_backup() {
    print_header "Step 11: Setting Up Automated Backup"
    
    gcloud compute ssh $INSTANCE_NAME --zone=$ZONE --command="
        mkdir -p /opt/rogue_detection_system/backups
        
        cat > /opt/rogue_detection_system/backup.sh <<'EOF'
#!/bin/bash
BACKUP_DIR=\"/opt/rogue_detection_system/backups\"
APP_DIR=\"/opt/rogue_detection_system\"
DATE=\\\$(date +%Y-%m-%d_%H-%M-%S)
RETENTION_DAYS=30

mkdir -p \"\\\$BACKUP_DIR/\\\$DATE\"
sqlite3 \"\\\$APP_DIR/rogue_monitor.db\" \".backup '\\\$BACKUP_DIR/\\\$DATE/rogue_monitor.db'\"
cp \"\\\$APP_DIR/config.json\" \"\\\$BACKUP_DIR/\\\$DATE/config.json\"
cd \"\\\$BACKUP_DIR\"
tar -czf \"\\\$DATE.tar.gz\" \"\\\$DATE\"
rm -rf \"\\\$DATE\"
find \"\\\$BACKUP_DIR\" -name \"*.tar.gz\" -mtime +\\\$RETENTION_DAYS -delete

# Upload to Cloud Storage (optional)
# gsutil cp \"\\\$BACKUP_DIR/\\\$DATE.tar.gz\" gs://your-bucket/backups/

echo \"Backup completed: \\\$DATE.tar.gz\"
EOF

        chmod +x /opt/rogue_detection_system/backup.sh
        
        # Add to crontab
        (crontab -l 2>/dev/null; echo \"0 2 * * * /opt/rogue_detection_system/backup.sh >> /var/log/backup.log 2>&1\") | crontab -
        
        echo 'Backup configured'
    "
    
    print_success "Automated backup configured"
}

step12_verify() {
    print_header "Step 12: Verification"
    
    # Check service status
    gcloud compute ssh $INSTANCE_NAME --zone=$ZONE --command="
        if systemctl is-active --quiet rogue-detection; then
            echo '✓ Service is running'
        else
            echo '✗ Service is not running'
        fi
        
        if curl -s http://localhost:5000 > /dev/null; then
            echo '✓ Web interface is responding'
        else
            echo '✗ Web interface is not responding'
        fi
    "
    
    print_success "Verification complete"
}

################################################################################
# Main Deployment
################################################################################

main() {
    clear
    print_header "Rogue Detection System - Google Cloud Deployment"
    echo
    print_info "This script will deploy the Rogue Detection System to Google Cloud"
    echo
    
    check_gcloud
    configure
    
    step1_enable_apis
    step2_create_firewall_rules
    step3_create_instance
    step4_get_external_ip
    step5_upload_files
    step6_install_application
    step7_configure_systemd
    step8_configure_nginx
    step9_setup_ssl
    step10_setup_monitoring
    step11_setup_backup
    step12_verify
    
    print_header "Deployment Complete!"
    echo
    print_success "Rogue Detection System has been deployed successfully!"
    echo
    print_info "Access Information:"
    if [ -n "$DOMAIN" ]; then
        echo "  URL: https://$DOMAIN"
    else
        echo "  URL: http://$EXTERNAL_IP"
    fi
    echo "  Default login: admin / admin123"
    echo
    print_info "Management Commands:"
    echo "  SSH to instance: gcloud compute ssh $INSTANCE_NAME --zone=$ZONE"
    echo "  Check service: gcloud compute ssh $INSTANCE_NAME --zone=$ZONE --command='sudo systemctl status rogue-detection'"
    echo "  View logs: gcloud compute ssh $INSTANCE_NAME --zone=$ZONE --command='sudo journalctl -u rogue-detection -f'"
    echo "  Stop instance: gcloud compute instances stop $INSTANCE_NAME --zone=$ZONE"
    echo "  Start instance: gcloud compute instances start $INSTANCE_NAME --zone=$ZONE"
    echo "  Delete instance: gcloud compute instances delete $INSTANCE_NAME --zone=$ZONE"
    echo
    print_warning "IMPORTANT: Edit configuration file with your switch credentials!"
    echo "  gcloud compute ssh $INSTANCE_NAME --zone=$ZONE"
    echo "  nano /opt/rogue_detection_system/config.json"
    echo "  sudo systemctl restart rogue-detection"
    echo
    print_info "Monthly cost estimate: ~\$15-20 USD (e2-small instance)"
    echo
}

# Run main function
main "$@"

