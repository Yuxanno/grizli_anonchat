# Grizli Chat Bot

Telegram bot for anonymous chat.

## Deployment on Ubuntu

To quickly deploy the bot on a fresh Ubuntu server, follow these steps:

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd grizli_chat
   ```

2. **Run the setup script**:
   This script will install Java (as requested), Node.js, PM2, Python 3, and setup the virtual environment.
   ```bash
   chmod +x setup_ubuntu.sh
   ./setup_ubuntu.sh
   ```

3. **Configure Environment Variables**:
   Edit the `.env` file and add your credentials:
   ```bash
   nano .env
   ```
   Set `BOT_TOKEN` and `MONGO_URL`.

4. **Restart the bot**:
   After updating `.env`, restart the bot via PM2:
   ```bash
   pm2 restart grizli-chat-bot
   ```

## Useful PM2 Commands

- `pm2 status`: View running processes.
- `pm2 logs grizli-chat-bot`: View bot logs.
- `pm2 restart grizli-chat-bot`: Restart the bot.
- `pm2 stop grizli-chat-bot`: Stop the bot.
