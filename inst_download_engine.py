from instacapture import InstaPost
import os 
import logging
import time
import shutil
import asyncio
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level=logging.INFO)

executor = ThreadPoolExecutor(max_workers=4)

def catch_reel(url):
    try:
        reel = InstaPost()
        reel.reel_id = url
        probe = reel.make_initial_request()
        return probe is not None
        
    except:
        return False

def download_post(url, user_id):
    reel = InstaPost()
    reel.reel_id = url
    download_info = reel.media_download()
    meta_data = next(iter(download_info.values()))
    filepath = meta_data['Media Data'][0]['Link']
    return filepath
    
async def download_reels(user_id, url):
    loop = asyncio.get_event_loop()
    filename = await loop.run_in_executor(executor, download_post, url, user_id)
    return filename


def cleanup_temp_post():
    temp_dir = f"post"
    try:
        if os.path.exists(temp_dir):
            for file in os.listdir(temp_dir):
                if os.path.isdir(f'{temp_dir}/{file}'):
                    shutil.rmtree(os.path.join(temp_dir, file))
                elif os.path.isfile(f'{temp_dir}/{file}'):
                    os.remove(os.path.join(temp_dir, file))
    except Exception as e:
        logging.info(f"Ошибка при очистке временных файлов: {e}")


def main():
    url = 'https://www.instagram.com/reel/DVY7o4Qjf3y/?utm_source=ig_web_copy_link&igsh=MzRlODBiNWFlZA=='
    download_reels(url=url, user_id='1')


if __name__ == '__main__':
    main()