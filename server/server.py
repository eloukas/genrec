import asyncio
import websockets
import youtube_dl

ydl_opts = { # options for youtube_dl
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'outtmpl': 'downloadedsongs/%(title)s.%(ext)s'
}

async def check_link(websocket, path):
    video = await websocket.recv()
    print("< {}".format(video))
    with youtube_dl.YoutubeDL(youtube_dl_opts) as ydl:
        info_dict = ydl.extract_info(video, download=False)
        video_url = info_dict.get("url", None)
        video_id = info_dict.get("id", None)
        video_title = info_dict.get('title', None)

    await websocket.send('It looks ok')

start_server = websockets.serve(check_link, 'localhost', 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
