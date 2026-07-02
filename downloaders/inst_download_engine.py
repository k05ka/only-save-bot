# from instacapture import InstaPost
import os 
import logging
import ffmpeg
# import time
import shutil
import asyncio
import yt_dlp
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level=logging.INFO)

executor = ThreadPoolExecutor(max_workers=4)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEDIA_DIR = os.path.join(BASE_DIR, 'media', 'instagram')
COOKIE_FILE = os.path.join(BASE_DIR, 'instagram_cookies.txt')

def catch_reel(url):
    try:
        ydl_opts = {
            'quiet': True,
            'cookiefile': COOKIE_FILE,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info is not None
    except:
        return False

def download_post(url, user_id):
    os.makedirs(MEDIA_DIR, exist_ok=True) 
    
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': os.path.join(MEDIA_DIR, '%(title)s.%(ext)s'),
        'merge_output_format': 'mp4',
        'cookiefile': COOKIE_FILE,
        'quiet': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        title = info.get('title', 'reel')
        ydl.download([url])
    
    filepath = os.path.join(MEDIA_DIR, f"{title}.mp4")
    return filepath

async def download_reels(user_id, url):
    loop = asyncio.get_event_loop()
    filename = await loop.run_in_executor(executor, download_post, url, user_id)
    video = ffmpeg.probe(filename)
    stream = next((s for s in video['streams'] if s['codec_type'] == 'video'), None)
    width, height = stream['width'], stream['height']

    return filename, width, height

def cleanup_temp_post():
    try:
        if os.path.exists(MEDIA_DIR):
            for file in os.listdir(MEDIA_DIR):
                os.remove(os.path.join(MEDIA_DIR, file))
        instacapture_dir = os.path.join(BASE_DIR, 'post')
        if os.path.exists(instacapture_dir):
            shutil.rmtree(instacapture_dir)
    except Exception as e:
        logging.info(f"Ошибка при очистке временных файлов: {e}")

def main():
    download_reels(url='url', user_id='1')

if __name__ == '__main__':
    main()