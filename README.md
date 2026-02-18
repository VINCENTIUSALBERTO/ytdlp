# Telegram YouTube Playlist Downloader Bot

A Telegram bot that downloads videos from YouTube playlists and sends them directly to users. Built with Python, python-telegram-bot, and yt-dlp.

## Features

- 🎵 **Playlist Processing** — Send a YouTube playlist URL and get a list of all videos
- 📥 **Flexible Downloads** — Download all videos or select specific ones
- 🎚️ **Quality Selection** — Choose from 360p, 480p, 720p, 1080p, best, or audio-only (MP3)
- 📊 **Progress Tracking** — Real-time download progress with speed and ETA
- 📁 **Direct Delivery** — Videos are sent directly through Telegram
- 🗄️ **Download History** — SQLite database tracks users and downloads
- 🧹 **Auto Cleanup** — Temporary files are automatically removed after 1 hour

## Prerequisites

- Python 3.10+
- FFmpeg installed and available in PATH
- A Telegram Bot Token (get one from [@BotFather](https://t.me/BotFather))

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/VINCENTIUSALBERTO/ytdlp.git
   cd ytdlp
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and set your `TELEGRAM_BOT_TOKEN`.

5. **Run the bot:**
   ```bash
   python main.py
   ```

## Configuration

| Variable | Description | Default |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | Your Telegram bot token | *(required)* |
| `DOWNLOAD_PATH` | Directory for temporary downloads | `./temp/downloads` |
| `MAX_FILE_SIZE` | Max file size in MB (Telegram limit) | `2000` |
| `MAX_CONCURRENT_DOWNLOADS` | Max parallel downloads per session | `3` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `DATABASE_URL` | SQLite database URL | `sqlite:///bot.db` |

## Usage

1. Start a chat with your bot on Telegram
2. Send `/start` for a welcome message
3. Send a YouTube playlist URL
4. Choose **All Videos** or **Select Specific**
5. Pick your preferred quality
6. Wait for the bot to download and send the videos

### Commands

| Command | Description |
|---|---|
| `/start` | Welcome message and instructions |
| `/help` | Show available commands and usage |
| `/cancel` | Cancel the current download operation |

## Project Structure

```
├── .env.example              # Environment variable template
├── .gitignore                # Git ignore rules
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── main.py                   # Application entry point
├── config/
│   ├── __init__.py
│   └── settings.py           # Configuration management
├── bot/
│   ├── handlers/
│   │   ├── start.py          # /start and /help commands
│   │   ├── playlist.py       # Playlist URL handling
│   │   └── download.py       # Download flow and quality selection
│   ├── downloader/
│   │   ├── youtube.py        # yt-dlp integration
│   │   └── progress.py       # Download progress tracking
│   ├── keyboards/
│   │   └── inline.py         # Inline keyboard builders
│   └── utils/
│       ├── validators.py     # URL validation utilities
│       └── file_manager.py   # File management utilities
├── database/
│   ├── models.py             # SQLAlchemy models
│   └── operations.py         # Database CRUD operations
├── tests/                    # Unit tests
├── temp/                     # Temporary download files
└── logs/                     # Log files
```

## Error Handling

- Invalid URLs are rejected with helpful messages
- Private/unavailable videos are skipped gracefully
- Network errors trigger automatic retries (up to 3 attempts)
- Files exceeding Telegram's 2 GB limit are skipped with a notification
- All errors are logged to `logs/bot.log`

## Running Tests

```bash
pip install pytest pytest-asyncio
pytest tests/ -v
```

## License

This project is provided as-is for educational purposes.