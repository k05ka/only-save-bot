from instacapture import InstaPost
import os 
import logging
import time
import shutil
import asyncio
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level=logging.INFO)

executor = ThreadPoolExecutor(max_workers=4)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEDIA_DIR = os.path.join(BASE_DIR, 'media', 'instagram')

def catch_reel(url):
    try:
        reel = InstaPost()
        reel.reel_id = url
        probe = reel.make_initial_request()
        return probe is not None
        
    except:
        return False

def download_post(url, user_id):
    os.makedirs(MEDIA_DIR, exist_ok=True) 
    reel = InstaPost()
    reel.reel_id = url
    download_info = reel.media_download()
    meta_data = next(iter(download_info.values()))
    filepath = meta_data['Media Data'][0]['Link']
    filename = os.path.basename(filepath)
    new_path = os.path.join(MEDIA_DIR, filename)
    shutil.move(filepath, new_path)

    return new_path
    
async def download_reels(user_id, url):
    loop = asyncio.get_event_loop()
    filename = await loop.run_in_executor(executor, download_post, url, user_id)
    return filename


def cleanup_temp_post():
    temp_dir = MEDIA_DIR 
    instacapture_dir = os.path.join(BASE_DIR, 'post')
    try:
        if os.path.exists(temp_dir):
            for file in os.listdir(temp_dir):
                os.remove(os.path.join(temp_dir, file))
        if os.path.exists(instacapture_dir):
            shutil.rmtree(instacapture_dir)
    except Exception as e:
        logging.info(f"Ошибка при очистке временных файлов: {e}")


def main():
    download_reels(url='url', user_id='1')


if __name__ == '__main__':
    main()