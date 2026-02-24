from pytubefix import YouTube
import os
import asyncio
import ffmpeg
from concurrent.futures import ThreadPoolExecutor

TARGET_RES = ['360p', '480p', '720p', '1080p', '1440p', '2160p']

vcodec_priority = {
    'vp09': 0,    # Самый высокий приоритет
    'avc1': 1,    # Средний приоритет  
    'av01': 2,    # Низкий приоритет
    'vp9': 0,     # Альтернативное название для vp09
}

# Создаем пул потоков для скачивания
executor = ThreadPoolExecutor(max_workers=4)

def catch_video(url):
    try:
        youtube = YouTube(url=url)
        return youtube.streams is not None
    except:
        return False
    
def compile_available_streams(url):
    possible_video_streams = {}
    youtube = YouTube(url=url)
    possible_video_streams['title'] = youtube.title
    possible_video_streams['resolutions'] = {}
    
    for res in TARGET_RES:
        res_stream = youtube.streams.filter(res=res, file_extension='mp4')
        candidate = None
        for codec in ['vp9', 'avc1', 'av01']:
            try:
                candidate = next(x for x in res_stream if codec in x.video_codec)
                break
            except StopIteration:
                continue
        if not candidate and res_stream:
            candidate = res_stream.first()
        if candidate:
            possible_video_streams['resolutions'][res] = candidate
    
    return possible_video_streams

# def compile_available_audio(url):
#     possible_audio_streams = {}
#     youtube = YouTube(url=url)
#     possible_video_streams['title'] = youtube.title

def get_resolution(filename):
    try:
        video_info = ffmpeg.probe(filename)['streams']
        video_stream = next(s for s in video_info if s['codec_type'] == 'video')
        return int(video_stream['width']), int(video_stream['height'])
    except (StopIteration, KeyError, ffmpeg.Error):
        return None
    

def download_video_sync(stream, user_id):
    """
    Синхронная функция для скачивания видео
    """
    try:
        temp_dir = f"media"
        os.makedirs(temp_dir, exist_ok=True)
        filename = stream.download(output_path=temp_dir)
        return filename
    except Exception as e:
        raise Exception(f"Ошибка при скачивании: {str(e)}")


async def download_video(stream, user_id):
    """
    Асинхронная обертка для скачивания видео
    """
    loop = asyncio.get_event_loop()
    filename = await loop.run_in_executor(executor, download_video_sync, stream, user_id)
    width, height = get_resolution(filename)
    return filename, width, height

def cleanup_temp_files():
    """
    Очистка временных файлов пользователя
    """
    temp_dir = f"media"
    try:
        if os.path.exists(temp_dir):
            for file in os.listdir(temp_dir):
                os.remove(os.path.join(temp_dir, file))
    except Exception as e:
        print(f"Ошибка при очистке временных файлов: {e}")
