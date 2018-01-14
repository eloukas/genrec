#!/usr/bin/env python

import asyncio
import websockets

# youtube link that causes exception
youtube_link = 'https://www.youtube.com/watch?v=Eq3CuMDXaP'

# youtube link that is OK
#youtube_link = 'https://www.youtube.com/watch?v=BaYATSpDtHA'

# Sends a youtube link to server
# And waits validation
async def send_link():
    async with websockets.connect('ws://localhost:8765') as websocket:
        print("Client started!")
        await websocket.send(youtube_link)

        validation = await websocket.recv()
        print("< {}".format(validation))

asyncio.get_event_loop().run_until_complete(send_link())
