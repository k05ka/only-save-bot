from instacapture import InstaPost
import os 
import logging
import time
import shutil

logging.basicConfig(level=logging.INFO)


def catch_reel(url):
    try:
        reel = InstaPost()
        reel.reel_id = url
        probe = reel.make_initial_request()
        return probe is not None
        
    except:
        return False
    
def download_reels(url):
    reel = InstaPost()
    reel.reel_id = url
    download_info = reel.media_download()
    meta_data = next(iter(download_info.values()))
    filepath = meta_data['Media Data'][0]['Link']
    print(filepath)


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
    download_reels(url='https://www.instagram.com/reel/DVTo7R4DNO8/?utm_source=ig_web_copy_link&igsh=MzRlODBiNWFlZA==')

    time.sleep(3)
    cleanup_temp_post()
    pass


if __name__ == '__main__':
    main()