import yt_dlp
import discord
from discord.ext import commands

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')
        self.duration = data.get('duration')
        self.thumbnail = data.get('thumbnail')
        self.requester = data.get('requester')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False, requester=None, ytdl_options=None):
        loop = loop or commands.bot.loop
        ytdl = yt_dlp.YoutubeDL(ytdl_options)
        
        data = await loop.run_in_executor(
            None, 
            lambda: ytdl.extract_info(url, download=not stream)
        )

        if 'entries' in data:
            entries = []
            for entry in data['entries']:
                entry_data = {
                    'title': entry.get('title'),
                    'url': entry.get('url'),
                    'duration': entry.get('duration'),
                    'thumbnail': entry.get('thumbnail'),
                    'requester': requester
                }
                entries.append(entry_data)
            return entries
        
        data['requester'] = requester
        filename = data['url'] if stream else ytdl.prepare_filename(data)
        
        ffmpeg_options = {
            'options': '-vn -b:a 128k -ar 44100',
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -threads 2'
        }
        
        return cls(
            discord.FFmpegPCMAudio(filename, **ffmpeg_options), 
            data=data
        )