import asyncio
import websockets
import youtube_dl

 # options for youtube_dl
ydl_opts = {
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
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            info_dict = ydl.extract_info(video, download=False)
            video_url = info_dict.get("url", None)
            video_id = info_dict.get("id", None)
            video_title = info_dict.get('title', None)

            await websocket.send('OK')
        except Exception as exception: # Catch all exceptions
            print(exception)
            await websocket.send('NOT OK')

start_server = websockets.serve(check_link, 'localhost', 8765)
print("Server started!")

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
