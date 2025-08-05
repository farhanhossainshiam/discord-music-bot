import requests
import re

class APIClients:
    def __init__(self, config):
        self.youtube_api_key = config.get('YOUTUBE_API_KEY')
    
    async def search_youtube(self, query):
        if not self.youtube_api_key:
            print("YouTube API key not provided")
            return None
        
        try:
            url = "https://www.googleapis.com/youtube/v3/search"
            params = {
                'part': 'snippet',
                'q': query,
                'type': 'video',
                'videoCategoryId': '10',
                'maxResults': 5,
                'key': self.youtube_api_key
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if 'items' in data and len(data['items']) > 0:
                video_id = data['items'][0]['id']['videoId']
                video_title = data['items'][0]['snippet']['title']
                print(f"YouTube API found: {video_title} ({video_id})")
                return f"https://www.youtube.com/watch?v={video_id}"
            else:
                print(f"No results found for query: {query}")
                return None
                
        except Exception as e:
            print(f"YouTube API error: {e}")
            return None