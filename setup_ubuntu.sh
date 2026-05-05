#!/bin/bash

# --- Ubuntu Server Setup Script for Grizli Chat Bot ---
# This script installs Java, Python, Node.js, and PM2, then starts the bot.

# Exit on error
set -e

echo "Updating system..."
sudo apt update && sudo apt upgrade -y

echo "Installing Java (OpenJDK 17)..."
sudo apt install -y openjdk-17-jdk

echo "Installing Python 3 and venv..."
sudo apt install -y python3 python3-pip python3-venv

echo "Setting up Python virtual environment..."
python3 -m venv venv
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

# Ensure .env exists
if [ ! -f .env ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "!!! WARNING: Please edit .env and add your BOT_TOKEN and MONGO_URL before the bot can work properly !!!"
fi

echo "Starting the bot with PM2..."
pm2 start main.py --name "grizli-chat-bot" --interpreter ./venv/bin/python

echo "Configuring PM2 to save process list..."
pm2 save

echo "--------------------------------------------------"
echo "Setup complete!"
echo "Java version: $(java -version 2>&1 | head -n 1)"
echo "Python version: $(python3 --version)"
echo "Node version: $(node -v)"
echo "PM2 version: $(pm2 -v)"
echo "--------------------------------------------------"
echo "Check bot status: pm2 status"
echo "Check bot logs: pm2 logs grizli-chat-bot"
echo "--------------------------------------------------"
