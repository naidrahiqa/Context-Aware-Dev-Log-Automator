#!/bin/bash
# DevPulse Linux/Mac Service Installer
# Installs DevPulse as a systemd service

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo ""
echo "=========================================="
echo "  DevPulse Systemd Service Installer"
echo "=========================================="
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    echo -e "${RED}❌ Error: Do not run this script as root${NC}"
    echo -e "${YELLOW}Run as your regular user. It will ask for sudo when needed.${NC}"
    exit 1
fi

# Check if systemd is available
if ! command -v systemctl &> /dev/null; then
    echo -e "${RED}❌ Error: systemd not found${NC}"
    echo -e "${YELLOW}This script is for systemd-based systems only${NC}"
    exit 1
fi

# Get DevPulse executable path
DEVPULSE_PATH=$(which devpulse 2>/dev/null)

if [ -z "$DEVPULSE_PATH" ]; then
    echo -e "${YELLOW}⚠️  devpulse command not found in PATH${NC}"
    read -p "Enter full path to devpulse executable: " DEVPULSE_PATH
    
    if [ ! -f "$DEVPULSE_PATH" ]; then
        echo -e "${RED}❌ Error: File not found: $DEVPULSE_PATH${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✓ Found DevPulse at: $DEVPULSE_PATH${NC}"

# Get API configuration
echo ""
echo -e "${CYAN}Enter your DevPulse configuration:${NC}"
read -p "API Key: " API_KEY
read -p "AI Provider (groq/openai) [groq]: " PROVIDER
PROVIDER=${PROVIDER:-groq}
read -p "Privacy Mode (true/false) [false]: " PRIVACY_MODE
PRIVACY_MODE=${PRIVACY_MODE:-false}

# Get current user
CURRENT_USER=$(whoami)
WORKING_DIR=$(pwd)

# Create service file
SERVICE_FILE="/tmp/devpulse.service"

cat > "$SERVICE_FILE" << EOF
[Unit]
Description=DevPulse - Automated Dev Log Tracker
After=network.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$WORKING_DIR

# Environment variables
Environment="DEVPULSE_API_KEY=$API_KEY"
Environment="DEVPULSE_AI_PROVIDER=$PROVIDER"
Environment="DEVPULSE_PRIVACY_MODE=$PRIVACY_MODE"

# Path to DevPulse executable
ExecStart=$DEVPULSE_PATH start --daemon

# Restart policy
Restart=always
RestartSec=10

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=devpulse

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}✓ Service file created${NC}"

# Install service file
echo ""
echo -e "${CYAN}Installing systemd service...${NC}"
sudo cp "$SERVICE_FILE" /etc/systemd/system/devpulse.service
sudo chmod 644 /etc/systemd/system/devpulse.service

# Reload systemd
sudo systemctl daemon-reload

echo -e "${GREEN}✓ Service installed${NC}"

# Enable service
echo -e "${CYAN}Enabling service to start on boot...${NC}"
sudo systemctl enable devpulse

echo -e "${GREEN}✓ Service enabled${NC}"

echo ""
echo "=========================================="
echo -e "  ${GREEN}Installation Complete!${NC}"
echo "=========================================="
echo ""

echo -e "${YELLOW}Service Commands:${NC}"
echo -e "  ${CYAN}Start:   sudo systemctl start devpulse${NC}"
echo -e "  ${CYAN}Stop:    sudo systemctl stop devpulse${NC}"
echo -e "  ${CYAN}Restart: sudo systemctl restart devpulse${NC}"
echo -e "  ${CYAN}Status:  sudo systemctl status devpulse${NC}"
echo -e "  ${CYAN}Logs:    sudo journalctl -u devpulse -f${NC}"
echo -e "  ${CYAN}Disable: sudo systemctl disable devpulse${NC}"
echo ""

# Ask if user wants to start the service now
read -p "Start DevPulse service now? (Y/n): " START_NOW
START_NOW=${START_NOW:-Y}

if [[ "$START_NOW" =~ ^[Yy]$ ]]; then
    echo ""
    echo -e "${CYAN}Starting DevPulse service...${NC}"
    sudo systemctl start devpulse
    
    sleep 2
    
    if sudo systemctl is-active --quiet devpulse; then
        echo -e "${GREEN}✓ DevPulse service started successfully!${NC}"
        echo ""
        echo -e "${GREEN}DevPulse is now running in the background 🚀${NC}"
        echo ""
        echo -e "View logs with: ${CYAN}sudo journalctl -u devpulse -f${NC}"
    else
        echo -e "${RED}❌ Failed to start service${NC}"
        echo -e "Check status with: ${CYAN}sudo systemctl status devpulse${NC}"
    fi
else
    echo ""
    echo -e "${YELLOW}Service installed but not started.${NC}"
    echo -e "Run '${CYAN}sudo systemctl start devpulse${NC}' when ready."
fi

echo ""

# Cleanup
rm "$SERVICE_FILE"
