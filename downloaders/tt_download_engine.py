import pyktok
import os
import logging
import asyncio
import re
import shutil
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level=logging.INFO)

executor = ThreadPoolExecutor(max_workers=4)
rx_file = re.compile(r'tiktok\.com\/(?P<name>(@(.+\/){2}\d+|[a-zA-Z0-9]+(\/|)))(\?.+|)')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEDIA_DIR = os.path.join(BASE_DIR, 'media', 'tiktok')


def catch_tiktok(url):
    try:
        pyktok.save_tiktok(video_url=url, save_video=False, metadata_fn='media/tiktok/probe.csv')
        return os.path.exists('media/tiktok/probe.csv')
    except:
        return False


def download_tiktok(url, user_id):
    os.makedirs(MEDIA_DIR, exist_ok=True) 
    filepath_re = rx_file.search(url).group('name')
    filepath = re.sub(r'\/', '_', filepath_re) + '.mp4'
    pyktok.save_tiktok(video_url=url, save_video=True, metadata_fn='media/tiktok/probe.csv')
    filename = os.path.basename(filepath)
    new_path = os.path.join(MEDIA_DIR, filename)
    shutil.move(filepath, new_path)

    return new_path


async def download_async_tiktok(user_id, url):
    loop = asyncio.get_event_loop()
    filename = await loop.run_in_executor(executor, download_tiktok, url, user_id)
    return filename
    

def cleanup_temp_tiktok():
    temp_dir = f"media/tiktok"
    try:
        if os.path.exists(temp_dir):
            for file in os.listdir(temp_dir):
                os.remove(os.path.join(temp_dir, file))
    except Exception as e:
        logging.info(f"Ошибка при очистке временных файлов: {e}")


def main():
    download_tiktok(url='url', user_id='1')


if __name__ == '__main__':
    main()