import os
import asyncio
import ffmpeg
from concurrent.futures import ThreadPoolExecutor
import logging

import yt_dlp

logging.basicConfig(level=logging.INFO)

executor = ThreadPoolExecutor(max_workers=4)
TARGET_RES = {'360p': '640x360', '480p': '854x480', '720p': '1280x720', 
              '1080p': '1920x1080', '1440p': '2560x1440', '2160p': '3840x2160'}
vcodec_priority = {
    'vp09': 0,
    'avc1': 1,  
    'av01': 2,
    'vp9': 0,
}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEDIA_DIR = os.path.join(BASE_DIR, 'media', 'youtube')
    
    
def compile_available_streams(url):
    video_formats = []
    audio_formats = []
    ydl_opts = {'quiet': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url=url, download=False)
        formats = info.get('formats')
        title = info.get('title')
        for _ in formats:
            if _.get('ext') == 'mp4' and _.get('protocol') == 'https':
                video_formats.append({'format_id': _.get('format_id'),
                                    'format': _.get('format'),
                                    'vcodec': _.get('vcodec'),
                                    'height': _.get('height'),
                                    'width': _.get('width'),
                                    'ext': _.get('ext'),
                                    'filesize': _.get('filesize')})
            elif _.get('ext') == 'm4a' and 'default' in _.get('format_note'):
                audio_formats.append({'format_id': _.get('format_id'),
                                      'format': _.get('format'),
                                      'acodec': _.get('acodec'),
                                      'ext': _.get('ext'),
                                      'filesize': _.get('filesize')})

    possible_streams = {}
    possible_streams['title'] = title
    possible_streams['resolutions'] = {}
    for k,v in TARGET_RES.items():
        res_formats = [x for x in video_formats if k in x.get('format')]
        candidate = None
        for codec in ['vp9', 'avc1', 'av01']:
            try:
                candidate = next(x for x in res_formats if codec in x['vcodec'])
                break
            except StopIteration:
                continue
        possible_streams['resolutions'][k] = candidate or res_formats[0]
    possible_streams['resolutions']['audio'] = audio_formats[-1]

    return possible_streams
    

def merge_audio_and_video(video, audio):
    output_path = video[:-3]+'_merged.mp4'
    video = ffmpeg.input(video)
    audio = ffmpeg.input(audio)
    
    ffmpeg.output(video['v'], 
                  audio['a'], 
                  output_path, 
                  vcodec='copy', 
                  acodec='aac'
                  ).overwrite_output().run()
    
    return output_path


def download_sync(stream, user_id, url, title):
    os.makedirs(MEDIA_DIR, exist_ok=True)
    ydl_opts = {
        'format': stream.get('format_id'),
        'quiet': True,
        'outtmpl': os.path.join(MEDIA_DIR, '%(title)s.%(ext)s')
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    filepath = os.path.join(MEDIA_DIR, f"{title}.{stream.get('ext')}")
    return filepath


async def download_yt(streams, stream, user_id, url, title):
    try:
        loop = asyncio.get_event_loop()
        audio_file = await loop.run_in_executor(executor, download_sync, streams.get('audio'), user_id, url, title)
        if stream.get('ext') == 'm4a':
            return {'file_path': audio_file}
        elif stream.get('ext') == 'mp4':
            if stream.get('filesize') >= 1932735283:
                raise Exception(f'Слишком большой размер файла: {stream.filesize // 1024 // 1024} Mb')
            video_file = await loop.run_in_executor(executor, download_sync, stream, user_id, url, title)
            filename = merge_audio_and_video(video_file, audio_file)
            return {'file_path': filename, 'width': stream.get('width'), 'height': stream.get('height')}
    except Exception as e:
        raise Exception(f"Ошибка при скачивании: {str(e)}")


def cleanup_temp_files():
    try:
        if os.path.exists(MEDIA_DIR):
            for file in os.listdir(MEDIA_DIR):
                file_path = os.path.join(MEDIA_DIR, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
    except Exception as e:
        logging.info(f"Ошибка при очистке временных файлов: {e}")


def main():
    #For debug purposes
    pass


if __name__ == '__main__':
    main()