import os
from dotenv import load_dotenv

def load_config():
    load_dotenv()
    
    # Get the base directory of the application
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cookies_file = os.path.join(base_dir, 'cookies.txt')
    
    return {
        'DISCORD_TOKEN': os.getenv('DISCORD_TOKEN'),
        'YOUTUBE_API_KEY': os.getenv('YOUTUBE_API_KEY'),
        'FFMPEG_OPTIONS': {
            'options': '-vn -b:a 128k -ar 44100',
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -threads 2'
        },
        'YTDL_OPTIONS': {
            'format': 'bestaudio/best',
            'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
            'restrictfilenames': True,
            'noplaylist': False,
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
            'quiet': True,
            'no_warnings': True,
            'default_search': 'auto',
            'source_address': '0.0.0.0',
            'force-ipv4': True,
            'buffer-size': '16K',
            'concurrent_fragment_downloads': 3,
            'http_chunk_size': '10485760',
            'retries': 10,
            'fragment_retries': 10,
            # Add cookies file if it exists
            'cookiefile': cookies_file if os.path.exists(cookies_file) else None,
            # Use alternative client as fallback
            'extractor_args': {'youtube': {'player_client': 'android'}},
        }
    }