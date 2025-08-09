# Discord Music Bot

## Overview
A Discord bot for playing music in voice channels with YouTube integration.

## Features
- Play music from YouTube
- Queue management
- Volume control
- Playlist support

## Requirements
- Python 3.8+
- Discord Bot Token
- YouTube API Key
- FFmpeg

## Installation

### Windows
1. Clone this repository
2. Install required packages:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your Discord token and YouTube API key
4. Run the bot:
   ```
   python run.py
   ```

### Ubuntu
1. Update your system:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. Install required packages:
   ```bash
   sudo apt install python3 python3-pip python3-venv git ffmpeg -y
   ```

3. Clone the repository or upload your files:
   ```bash
   https://github.com/farhanhossainshiam/discord-music-bot.git
   cd discord-music-bot
   ```

4. Set up Python environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

5. Configure your bot:
   - Create a `.env` file with your Discord token and YouTube API key
   - Set up YouTube cookies (see below)

6. Run the bot:
   ```bash
   python3 run.py
   ```

7. Keep the bot running (choose one):
   - Using screen:
     ```bash
     sudo apt install screen -y
     screen -S discord-bot
     source venv/bin/activate
     python3 run.py
     # Press Ctrl+A, then D to detach
     ```
   - Using systemd service:
     ```bash
     sudo nano /etc/systemd/system/discord-bot.service
     ```
     Add this content (adjust paths):
     ```ini
     [Unit]
     Description=Discord Music Bot
     After=network.target

     [Service]
     User=your_username
     WorkingDirectory=/path/to/discord-music-bot
     Environment="PATH=/path/to/discord-music-bot/venv/bin"
     ExecStart=/path/to/discord-music-bot/venv/bin/python3 run.py
     Restart=always
     RestartSec=10

     [Install]
     WantedBy=multi-user.target
     ```
     Enable and start the service:
     ```bash
     sudo systemctl enable discord-bot.service
     sudo systemctl start discord-bot.service
     ```

## YouTube Authentication

YouTube now requires authentication to verify you're not a bot. Follow these steps to set up cookies:

### Method 1: Using yt-dlp's Built-in Feature (Recommended)

This is the safest and most reliable method as it doesn't require third-party extensions that might compromise your security.

1. **Log in to YouTube** in your browser (Firefox recommended due to recent Chrome encryption changes)
2. **Close your browser** completely
3. **Run this command** in your terminal or command prompt:

```
yt-dlp --cookies cookies.txt --cookies-from-browser firefox
```

Replace `firefox` with `chrome`, `edge`, or other browsers as needed. This command will:
- Extract cookies from your browser
- Save them to a file named `cookies.txt` in your current directory

**Note for Chrome users:** Due to recent changes in Chrome, you might encounter issues with cookie extraction. If using Chrome, try one of these workarounds:

- Add `--disable-features=LockProfileCookieDatabase` to your Chrome shortcut to prevent cookie database locking
- Use the yt-dlp-ChromeCookieUnlock plugin
- Or simply use Firefox instead

### Method 2: Using Browser Extensions

#### For Firefox:
1. Install the [cookies.txt](https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/) extension
2. Log in to YouTube
3. Click the extension icon
4. Select "Export" to save the cookies.txt file

#### For Chrome:
1. Install the [Get cookies.txt LOCALLY](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc) extension
   - Note: Make sure to use this specific extension as there have been security concerns with other similar extensions
2. Log in to YouTube
3. Click the extension icon
4. Select the export option to save the cookies.txt file

### Using the cookies.txt File

1. Place the `cookies.txt` file in the root directory of your Discord music bot
2. The bot will automatically use this file for authentication when downloading YouTube videos

### Important Security Notes

1. **Keep your cookies.txt file secure** - it contains your authentication information
2. **Don't share your cookies.txt file** - someone could use it to access your YouTube account
3. **Cookies expire** - you may need to regenerate this file periodically
4. **Use a dedicated YouTube account** for your bot rather than your personal account

## Commands
- `!play [song]` - Play a song or add it to the queue
- `!skip` - Skip the current song
- `!pause` - Pause playback
- `!resume` - Resume playback
- `!stop` - Stop playback and clear the queue
- `!queue` - Show the current queue
- `!volume [0-100]` - Set the volume

## Troubleshooting

### YouTube Bot Verification Error
If you see an error like: "Sign in to confirm you're not a bot", make sure you've set up the cookies.txt file correctly.

### FFmpeg Issues
Make sure ffmpeg is properly installed:
```bash
sudo apt install ffmpeg -y
```

### Voice Connection Issues
Install additional dependencies if needed:
```bash
sudo apt install libffi-dev libnacl-dev python3-dev -y
pip install PyNaCl
```

### Credit
- Full Bot Development by Vibe Coding

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
