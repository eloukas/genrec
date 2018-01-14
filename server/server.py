import asyncio
import websockets
import youtube_dl

 # Options for youtube_dl
ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'outtmpl': 'downloadedsongs/%(title)s.%(ext)s'
}

'''
    check_youtube_link(websocket, path)

    -1- Gets a video from the websocket
    -2- Checks if valid
    -3- Sends appropriate response ('OK/'NOT OK')
'''
async def check_youtube_link(websocket, path):
    videoURL = await websocket.recv()
    print("< Youtube link given: {}".format(videoURL))

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:

            # Get information about the YouTube video/song
            info_dict = ydl.extract_info(videoURL, download=False)
            video_ref_url = info_dict.get("url", None)
            video_id = info_dict.get("id", None)
            video_title = info_dict.get('title', None)

            print("< Sending OK to client..")
            await websocket.send('OK')

            # Download the song
            #ydl.download([video_url]) # videoplayback.mp3
            ydl.download([videoURL])
            print("< Video just got downloaded")

        except Exception as e: # Catch all exceptions
            #print(e.__class__.__name__) # (youtube-dl's is named DownloadError)
            print("Sending NOT OK to client..")
            await websocket.send('NOT OK')

start_server = websockets.serve(check_youtube_link, 'localhost', 8765)
print("Server started!")

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
