# 0nly_save_bot
## About
This is pet-project for downloading video's from different platform, such as YouTube, Instagram, TikTok, Pinterest, etc.

## Requirements
Basic python packages, used in repo:
- aiogram 3
- fixpytube
- instacapture
- pyktok

### Important
If size of media files that will send to Telegram is more than 20~50Mb ([source](https://core.telegram.org/bots/api#sendvideo)), ordinary using Telegram API is not possible. For large files need to use self compiled and hosted API server

## Installation
### Clone repository

```bash
git clone https://github.com/k05ka/only-save-bot.git
# rename bot dir if neded
cd only-save-bot
```
### Install python packages (create and use venv before it)
```bash
pip install -r requirements.txt
```
### Create .env file in bot directory with next variables
1. TOKEN= #Bot auth token
2. admin_ids= # Administrator Tg id for support and notifications
3. API_ID= # ID from my.telegram.org APP setting
4. API_HASH= # HASH from my.telegram.org APP setting

### Telegram Bot API installation
I use that repo - https://github.com/tdlib/telegram-bot-api

```bash
git clone --recursive https://github.com/tdlib/telegram-bot-api.git
cd telegram-bot-api
mkdir build
cd build
cmake -DCMAKE_BUILD_TYPE=Release ..
cmake --build . --target install
```
 ### Create telegram-bot-api service

```bash
# /etc/systemd/system/telegram-bot-api.service
[Unit]
Description=Telegram Bot API Local Server
After=network.target

[Service]
#Use your own user and group
User=user
Group=group

#Use your own dir path
WorkingDirectory=/path/to/telegram-bot-api 
#Use your own dir path for env
EnvironmentFile=/path/to/.env

ExecStart=/usr/local/bin/telegram-bot-api \
    --api-id=${API_ID} \
    --api-hash=${API_HASH} \
    --local \
    --http-port=8081 \
    --dir=/path/to/telegram-bot-api \
    --temp-dir=/path/to/telegram-bot-api

Restart=on-failure
RestartSec=5
LimitNOFILE=4096

[Install]
WantedBy=multi-user.target

```

### Create Telegram Bot service


```bash
# /etc/systemd/system/bot-name.service
[Unit]
Description=Your description
After=network.target telegram-bot-api.service
Requires=telegram-bot-api.service

[Service]
# Use your own user and group
User=user
Group=group
# Use your own directory
WorkingDirectory=/opt/dir/to/bot

EnvironmentFile=/opt/path/to/.env

ExecStart=/path/to/venv/bin/python3 /path/to/main.py

Restart=always
RestartSec=5

PrivateTmp=true
NoNewPrivileges=true

LimitNOFILE=8192

[Install]
WantedBy=multi-user.target
```

### Start services and validate

```bash
systemctl daemon-reload
systemctl start telegram-bot-api
# The port specified in the service file should be displayed
ss -tulpan | grep telegram
systemctl start bot-name
```
If all work properly, you must receive message "Bot is started" from your Bot in direct chat

