from pytubefix import YouTube
import os
import asyncio
import ffmpeg
from concurrent.futures import ThreadPoolExecutor
import logging

logging.basicConfig(level=logging.INFO)

executor = ThreadPoolExecutor(max_workers=4)
TARGET_RES = ['360p', '480p', '720p', '1080p', '1440p', '2160p']
vcodec_priority = {
    'vp09': 0,
    'avc1': 1,  
    'av01': 2,
    'vp9': 0,
}


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


def download_sync(stream, user_id):
    try:
        temp_dir = f"media/youtube"
        os.makedirs(temp_dir, exist_ok=True)
        filename = stream.download(output_path=temp_dir)
        return filename
    except Exception as e:
        raise Exception(f"Ошибка при скачивании: {str(e)}")
    

def merge_streams(video, audio):
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


async def download_video(stream, user_id, url):
    loop = asyncio.get_event_loop()
    width, height = stream.width, stream.height
    if stream.video_codec and stream.audio_codec:
        filename = await loop.run_in_executor(executor, download_sync, stream, user_id)
    else:
        audio_stream = YouTube(url=url).streams.get_audio_only()
        video_stream = stream
        video_filename = await loop.run_in_executor(executor, download_sync, video_stream, user_id)
        audio_filename = await loop.run_in_executor(executor, download_sync, audio_stream, user_id)
        filename = merge_streams(video_filename, audio_filename)
    return filename, width, height


def cleanup_temp_files():
    temp_dir = f"media/youtube"
    try:
        if os.path.exists(temp_dir):
            for file in os.listdir(temp_dir):
                os.remove(os.path.join(temp_dir, file))
    except Exception as e:
        logging.info(f"Ошибка при очистке временных файлов: {e}")


def main():
    #For debug purposes
    pass


if __name__ == '__main__':
    main()