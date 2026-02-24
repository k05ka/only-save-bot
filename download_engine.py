from pytubefix import YouTube

def catch_video(url):
    try:
        youtube = YouTube(url=url)
        print(youtube.streams)
        return youtube.streams is not None
    except:
        return False

# youtube = YouTube(url="https://www.youtube.com/shorts/DsxE171V_OU")
# streams = youtube.streams
# print(str(streams))

